#!/usr/bin/env python3
from mininet.net import Containernet
from mininet.node import OVSSwitch, Docker
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def main():
    setLogLevel('info')

    # No external controller; we’ll push static flows ourselves
    net = Containernet(controller=None, switch=OVSSwitch)

    # Two Docker hosts (use any image you like)
    d1 = net.addDocker('d1', dimage='ubuntu:trusty', ip='10.0.0.1/24')
    d2 = net.addDocker('d2', dimage='ubuntu:trusty', ip='10.0.0.2/24')

    # One OVS switch in OpenFlow13; standalone so it doesn’t wait for a controller
    s1 = net.addSwitch('s1', protocols='OpenFlow13', failMode='standalone')

    net.addLink(d1, s1)  # d1 on s1-eth1 -> port 1
    net.addLink(d2, s1)  # d2 on s1-eth2 -> port 2
    net.start()

    info('*** Program static OpenFlow rules (default DROP, allow only TCP/502 both ways)\n')
    of = 'ovs-ofctl -O OpenFlow13'
    # Clear anything preexisting
    s1.cmd(f'{of} del-flows s1')

    # Default: drop everything
    s1.cmd(f'{of} add-flow s1 "priority=0,actions=drop"')

    # Allow client -> server when destination is TCP port 502
    s1.cmd(f'{of} add-flow s1 "priority=100,ip,tcp,ipv4_src=10.0.0.1,ipv4_dst=10.0.0.2,tcp_dst=502,actions=output:2"')
    s1.cmd(f'{of} add-flow s1 "priority=100,ip,tcp,ipv4_src=10.0.0.2,ipv4_dst=10.0.0.1,tcp_dst=502,actions=output:1"')

    # Allow server responses (source port 502 back to client)
    s1.cmd(f'{of} add-flow s1 "priority=100,ip,tcp,ipv4_src=10.0.0.2,ipv4_dst=10.0.0.1,tcp_src=502,actions=output:1"')
    s1.cmd(f'{of} add-flow s1 "priority=100,ip,tcp,ipv4_src=10.0.0.1,ipv4_dst=10.0.0.2,tcp_src=502,actions=output:2"')

    # (Optional) print rules
    print(s1.cmd(f'{of} dump-flows s1'))

    info('*** Ready. Use CLI to test.\n')
    CLI(net)
    net.stop()

if __name__ == "__main__":
    main()
