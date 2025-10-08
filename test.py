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

def createPod(net, pod_idx, names, numHost):
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
    s1 = net.addSwitch(f's1')
    d1 = net.addDocker(f'd1', ip=f'10.0.1.1', dimage="ubuntu:trusty")
    d2 = net.addDocker(f'd2', ip=f'10.0.1.2', dimage="ubuntu:trusty")

    info('*** Creating switch links\n')
    net.addLink(d1, s1)
    net.addLink(d2, s1)

    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    net.pingAll()

    loadRules(net,"policy.yaml")

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()



if __name__ == '__main__':
    main()