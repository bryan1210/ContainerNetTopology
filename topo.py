#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
import yaml
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

def createNetwork(net,name):
    with open(name) as f:
        network = yaml.safe_load(f)

    for sw_name, devices in network["switches"].items():
        s = net.addSwitch(sw_name)
        for device in devices:
            for name, IP in device.items():
                d = net.addDocker(name, ip=IP, dimage="ubuntu:trusty")
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
    net.pingAll()

    info('*** Loading Rules\n')
    loadRules(net,"policy.yaml")

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    main()