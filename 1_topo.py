#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
import testyaml
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

def hex_dpid(n: int) -> str:
    return f'{n:016x}'  # 16 hex digits, zero-padded

def createPod(net, name, pod_idx, names, numHost):
    info(f'*** Adding Process Switch {pod_idx}\n')
    s = net.addSwitch(name,dpid=hex_dpid(pod_idx))
    hosts = []
    for host in range(numHost):
        i = host
        if host >= len(names):
            host = len(names)-1
        print(names[host])
        d = net.addDocker(f'{names[host]}{pod_idx}{i+1}', ip=f'10.0.{pod_idx}.{i+1}', dimage="ubuntu:trusty")
        net.addLink(d,s)
        hosts.append(d)
    return s, hosts

def loadRules(net, name):
    with open(name) as f:
        policy = testyaml.safe_load(f)

    for sw_name, commands in policy.items():
        sw = net.get(sw_name)       # get Mininet switch object
        sw.cmd(f'ovs-ofctl del-flows {sw}')
        for command in commands:
            sw.cmd(f'ovs-ofctl add-flow {sw} "{command}"')

def main():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Creating Process Cells\n')
    process_names=['PLC','Sen','Act','HMI','Gen']
    process_switch_1, _ = createPod(net,'ps1',1,process_names,4)
    process_switch_2, _ = createPod(net,'ps2',2,process_names,4)

    engineer_names = ['eng']
    engineering_switch, _ = createPod(net,4,engineer_names,4)

    OT_srv_name = ['DC','Hist','IO_srv']
    OT_ser_switch, _ = createPod(net,5,OT_srv_name,3)

    dmz_names = ['Patch','Hist_mir','IO_srv']
    DMZ_switch, _ = createPod(net,6,dmz_names,3)

    enterprise_names = ['ent']
    enterprise_workstations, _ = createPod(net,7,enterprise_names,3)

    enterprise_servers_names = ['email','web','database']
    enterprise_servers, _ = createPod(net,8,enterprise_servers_names,3)

    info('*** Adding switches\n')
    OT_switch = net.addSwitch('OT_s',dpid=hex_dpid(150))
    DMZ_Firewall = net.addSwitch('DMZ_fw',dpid=hex_dpid(151))
    enterprise_switch = net.addSwitch('ent_s', dpid=hex_dpid(152))

    info('*** Creating switch links\n')
    net.addLink(process_switch_1, OT_switch)
    net.addLink(process_switch_2, OT_switch)
    net.addLink(process_switch_3, OT_switch)

    net.addLink(engineering_switch, OT_switch)
    net.addLink(OT_ser_switch, OT_switch)

    net.addLink(DMZ_Firewall, OT_switch)
    net.addLink(DMZ_Firewall, DMZ_switch)
    net.addLink(DMZ_Firewall, enterprise_switch)

    net.addLink(enterprise_switch, enterprise_workstations)
    net.addLink(enterprise_switch, enterprise_servers)

    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    net.pingAll()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()

def testmain():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')
    process_names=['PLC','Sen','Act','HMI','Gen']
    engineer_names=['eng']
    test(net,1,process_names,15)
    test(net,2,engineer_names,15)

    info('*** Stopping network')
    net.stop()

if __name__ == '__main__':
    main()