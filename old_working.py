#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

def hex_dpid(n: int) -> str:
    return f'{n:016x}'  # 16 hex digits, zero-padded

def createDMZ(net, pod_idx):
    info(f'*** Adding DMZ Switch\n') 
    s = net.addSwitch(f'sDMZ',dpid=hex_dpid(pod_idx))   

    info(f'*** Adding DMZ Nodes\n')
    d1 = net.addDocker(f'Patch{pod_idx}1', ip=f'10.0.{pod_idx}.251', dimage="ubuntu:trusty")
    d2 = net.addDocker(f'HistMir{pod_idx}2', ip=f'10.0.{pod_idx}.252', dimage="ubuntu:trusty")
    d3 = net.addDocker(f'IOServer{pod_idx}3', ip=f'10.0.{pod_idx}.253', dimage="ubuntu:trusty") 

    info('*** Creating links\n')
    net.addLink(d1, s)
    net.addLink(d2, s)
    net.addLink(d3, s)  
    
    return s, [d1,d2,d3]

def createEngineering(net,pod_idx):
    info(f'*** Adding Engineering Switch {pod_idx}\n')
    s = net.addSwitch(f's{pod_idx}',dpid=hex_dpid(pod_idx))

    info(f'*** Adding Engineering Nodes {pod_idx}\n')
    d1 = net.addDocker(f'Eng{pod_idx}1', ip=f'10.0.{pod_idx}.251', dimage="ubuntu:trusty")
    d2 = net.addDocker(f'Eng{pod_idx}2', ip=f'10.0.{pod_idx}.252', dimage="ubuntu:trusty")
    d3 = net.addDocker(f'Eng{pod_idx}3', ip=f'10.0.{pod_idx}.253', dimage="ubuntu:trusty")
    d4 = net.addDocker(f'Eng{pod_idx}4', ip=f'10.0.{pod_idx}.254', dimage="ubuntu:trusty")

    info('*** Creating links\n')
    net.addLink(d1, s)
    net.addLink(d2, s)
    net.addLink(d3, s)
    net.addLink(d4, s)

    return s, [d1,d2,d3,d4]


def mainProcessCell(net, pod_idx, numHost):
    info(f'*** Adding Process Switch {pod_idx}\n')
    s = net.addSwitch(f's{pod_idx}',dpid=hex_dpid(pod_idx))
    names = ['PLC','Sen','Act','HMI',"Gen"]
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


def test(net, pod_idx, names, numHost):
    info(f'*** Adding Process Switch {pod_idx}\n')
    s = net.addSwitch(f's{pod_idx}',dpid=hex_dpid(pod_idx))
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

def main():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Creating Process Cells\n')
    process_switch_1, _ = mainProcessCell(net,1,4)
    process_switch_2, _ = mainProcessCell(net,2,4)
    process_switch_3, _ = mainProcessCell(net,3,4)

    engineering_switch, _ = createEngineering(net, 4)

    DMZ_switch, _ = createDMZ(net,5)

    info('*** Adding switches\n')
    OT_switch = net.addSwitch('OT_s',dpid=hex_dpid(150))
    DMZ_Firewall = net.addSwitch('DMZ_fw',dpid=hex_dpid(151))
    enterprise_switch = net.addSwitch('ent_s', dpid=hex_dpid(152))

    info('*** Creating switch links\n')
    net.addLink(process_switch_1, OT_switch)
    net.addLink(process_switch_2, OT_switch)
    net.addLink(process_switch_3, OT_switch)

    net.addLink(engineering_switch, OT_switch)

    net.addLink(DMZ_Firewall, OT_switch)
    net.addLink(DMZ_Firewall, DMZ_switch)
    net.addLink(DMZ_Firewall, enterprise_switch)

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
    testmain()