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

    with open('network.yaml') as f:
        network = yaml.safe_load(f)

    for sw_name, devices in network["switches"].items():
        print(f"\nSwitch: {sw_name}")
        for device in devices:
            for name, ip in device.items():
                print(f"  {name}: {ip}")


def loadRules(net, name):
    with open(name) as f:
        policy = yaml.safe_load(f)

    for sw_name, commands in policy.items():
        sw = net.get(sw_name)       # get Mininet switch object
        sw.cmd(f'ovs-ofctl del-flows {sw}')
        for command in commands:
            sw.cmd(f'ovs-ofctl add-flow {sw} "{command}"')

def main():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')





    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    net.pingAll()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    main()