#!/usr/bin/python
"""
This is the most simple example to showcase Containernet.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.term import makeTerm
setLogLevel('info')

def hex_dpid(n: int) -> str:
    return f'{n:016x}'  # 16 hex digits, zero-padded

def createDMZ(net, pod_idx):
    info(f'*** Adding DMZ Switch\n') 
    s = net.addSwitch(f'sDMZ',dpid=hex_dpid(pod_idx))   

    info(f'*** Adding DMZ Nodes\n')
    d1 = net.addDocker(f'Patch{pod_idx}1', ip=f'10.0.{pod_idx}.251', dimage="ot-all-in-one:latest")
    d2 = net.addDocker(f'HistMir{pod_idx}2', ip=f'10.0.{pod_idx}.252', dimage="ot-all-in-one:latest")
    d3 = net.addDocker(f'IOServer{pod_idx}3', ip=f'10.0.{pod_idx}.253', dimage="ot-all-in-one:latest") 

    info('*** Creating links\n')
    net.addLink(d1, s)
    net.addLink(d2, s)
    net.addLink(d3, s)  
    
    return s, [d1,d2,d3]

def createEngineering(net,pod_idx):
    info(f'*** Adding Engineering Switch {pod_idx}\n')
    s = net.addSwitch(f's{pod_idx}',dpid=hex_dpid(pod_idx))

    info(f'*** Adding Engineering Nodes {pod_idx}\n')
    d1 = net.addDocker(f'Eng{pod_idx}1', ip=f'10.0.{pod_idx}.251', dimage="ot-all-in-one:latest")
    d2 = net.addDocker(f'Eng{pod_idx}2', ip=f'10.0.{pod_idx}.252', dimage="ot-all-in-one:latest")
    d3 = net.addDocker(f'Eng{pod_idx}3', ip=f'10.0.{pod_idx}.253', dimage="ot-all-in-one:latest")
    d4 = net.addDocker(f'Eng{pod_idx}4', ip=f'10.0.{pod_idx}.254', dimage="ot-all-in-one:latest")

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
        d = net.addDocker(f'{names[host]}{pod_idx}{i+1}', ip=f'10.0.{pod_idx}.{i+1}', dimage="ot-all-in-one:latest")
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
        d = net.addDocker(f'{names[host]}{pod_idx}{i+1}', ip=f'10.0.{pod_idx}.{i+1}', dimage="ot-all-in-one:latest")
        net.addLink(d,s)
        hosts.append(d)
    return s, hosts

def main():
    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    d1 = net.addDocker('d1', ip="10.0.0.1", dimage="ot-all-in-one:latest", dcmd='python /app/server_all.py', privileged=True)
    d2 = net.addDocker('d2', ip="10.0.0.2", dimage="ot-all-in-one:latest", dcmd='python /app/server_all.py', privileged=True)
    #d1 = net.addDocker('d1', ip="10.0.0.1", dimage="ot-all-in-one:latest", privileged=True)
    d3 = net.addDocker('d3', ip="10.0.0.3", dimage="ot-all-in-one:latest", privileged=True)


    info('*** Creating switch links\n')
    net.addLink(d1, s1)
    net.addLink(d2, s1)
    net.addLink(d3, s1)
    #net.addLink(d1, s1, bw=10000)
    #net.addLink(d2, s1, bw=10000)



    info('*** Starting network\n')
    net.start()

    info('*** Testing connectivity\n')
    net.pingAll()

    info('*** Make Xterm\n')
    makeTerm(d3)

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    main()