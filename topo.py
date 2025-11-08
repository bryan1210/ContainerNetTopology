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
                d = net.addDocker(name, ip=IP, dimage="ot-all-in-one:latest", dcmd=f'python /app/server_all.py {name}', privileged=True)
                net.addLink(d,s)

    for sw_name, links in network["links"].items():
        s = net.addSwitch(sw_name)
        for link in links:
            sw = net.get(link)
            net.addLink(s,sw)


def loadRules(net, name):
    with open(name) as f:
        policy = yaml.safe_load(f)

    for sw_name, commands in policy['flows'].items():
        sw = net.get(sw_name)       # get Mininet switch object
        sw.cmd(f'ovs-ofctl del-flows {sw}')
        for command in commands:
            sw.cmd(f'ovs-ofctl add-flow {sw} "{command}"')

def main():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Creating Network\n')
    createNetwork(net,"network.yaml")

    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    #net.pingAll()

    info('*** Loading Rules\n')
    #loadRules(net,"policy.yaml")

    info('*** Make Xterm\n')
    HMI_1 = net.get("HMI_1")
    makeTerm(HMI_1)

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    main()