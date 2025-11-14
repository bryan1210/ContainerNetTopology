#!/usr/bin/python
import yaml
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.term import makeTerm
setLogLevel('info')

def createNetwork(net,name):
    with open(name) as f:
        network = yaml.safe_load(f)

    for sw_name, devices in network["switches"].items():
        s = net.addSwitch(sw_name)
        for device in devices:
            for name, IP in device.items():
                d = net.addDocker(name, ip=IP, dimage="ot-all-in-one:latest", dcmd=f'python /app/server_all.py', privileged=True)
                #d = net.addDocker(name, ip=IP, dimage="ot-all-in-one:latest", privileged=True)
                net.addLink(d,s)

    for sw_name, links in network["links"].items():
        s = net.addSwitch(sw_name)
        for link in links:
            sw = net.get(link)
            net.addLink(s,sw)


def loadRules_old(net, name):
    with open(name) as f:
        policy = yaml.safe_load(f)

    for sw_name, commands in policy['flows'].items():
        sw = net.get(sw_name)       # get Mininet switch object
        sw.cmd(f'ovs-ofctl del-flows {sw}')
        for command in commands:
            sw.cmd(f'ovs-ofctl add-flow {sw} "{command}"')

def loadRules(net, name):
    with open(name) as f:
        policy = yaml.safe_load(f)
    #print("Here")
    flows = policy['flows']
    sw = net.get("firewall_1")
    sw.cmd(f'ovs-ofctl del-flows firewall_1')
    sw.cmd('ovs-ofctl add-flow firewall_1 "priority=100,arp,actions=NORMAL"')
    sw.cmd('ovs-ofctl add-flow firewall_1 "priority=200,tcp,tp_dst=5000,actions=NORMAL"')
    sw.cmd('ovs-ofctl add-flow firewall_1 "priority=200,tcp,tp_src=5000,actions=NORMAL"')
    for each in flows:
        #print(each)
        rule = each.split(" ")
        if len(rule) == 2:
            sw.cmd(f"ovs-ofctl add-flow firewall_1 priority=0,actions=drop")
        elif len(rule) == 5:
            source_ip = rule[0]
            drop_allow = rule[1]
            if drop_allow == "x":
                drop_allow = "drop"
            elif drop_allow == ">":
                drop_allow = "NORMAL"
            else:
                exit()
            dest_ip = rule[2]
            dest_port = rule[4]
            #print(f"Drop allow : {drop_allow}")
            sw.cmd(f"ovs-ofctl add-flow firewall_1 priority=100,tcp,nw_src={source_ip},nw_dst={dest_ip},tp_dst={dest_port},actions={drop_allow}")
            sw.cmd(f"ovs-ofctl add-flow firewall_1 priority=100,tcp,nw_src={dest_ip},nw_dst={source_ip},tp_src={dest_port},actions={drop_allow}")

def main():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Creating Network\n')
    createNetwork(net,"network.yaml")

    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    net.pingAll()

    info('*** Loading Rules\n')
    under = "overly_permissive_policy.yaml.yaml"
    right = "right_sized_policy.yaml"
    over = "overly_restrictive_policy.yaml"
    test= "test_policy.yaml"
    loadRules(net,right)

    #info('*** Testing connectivity\n')
    #net.pingAll()

    info('*** Make Xterm\n')
    HMI_1 = net.get("HMI_1")
    makeTerm(HMI_1)
    #Patch_1 = net.get("patch_1")
    #makeTerm(Patch_1)
    #HMI_2 = net.get("HMI_2")
    #makeTerm(HMI_2)

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    main()