#!/usr/bin/env python3
from mininet.net import Containernet
from mininet.node import OVSSwitch, Docker
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time

OFV = "OpenFlow13"
OFCTL = f'ovs-ofctl -O {OFV}'

def of(sw, cmd):
    return sw.cmd(f"{OFCTL} {cmd}")

def sw_port_for(sw, host):
    """Return switch port number that connects to host"""
    sw_intf, _ = sw.connectionsTo(host)[0]
    return sw.ports[sw_intf]

def add_drop_all(sw):
    of(sw, f'del-flows {sw.name}')
    of(sw, f'add-flow {sw.name} "priority=0,actions=drop"')

def allow_tcp_502_bidir(sw, ip_a, port_to_a, ip_b, port_to_b):
    # A -> B (dst 502) and responses (src 502)
    of(sw, f'add-flow {sw.name} "priority=100,ip,tcp,ipv4_src={ip_a},ipv4_dst={ip_b},tcp_dst=502,actions=output:{port_to_b}"')
    of(sw, f'add-flow {sw.name} "priority=100,ip,tcp,ipv4_src={ip_b},ipv4_dst={ip_a},tcp_src=502,actions=output:{port_to_a}"')
    # B -> A (dst 502) and responses (src 502)
    of(sw, f'add-flow {sw.name} "priority=100,ip,tcp,ipv4_src={ip_b},ipv4_dst={ip_a},tcp_dst=502,actions=output:{port_to_a}"')
    of(sw, f'add-flow {sw.name} "priority=100,ip,tcp,ipv4_src={ip_a},ipv4_dst={ip_b},tcp_src=502,actions=output:{port_to_b}"')

def put_file(node, path, content):
    # Write a file inside a container
    here = f'cat > {path} << "PY"\n{content}\nPY'
    return node.cmd(f'bash -lc \'{here}\'')

SERVER_CODE = r'''
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [10,11,12,13,14,15,16,17,18,19] + [0]*90),
    ir=ModbusSequentialDataBlock(0, [0]*100),
    zero_mode=True
)
context = ModbusServerContext(slaves=store, single=True)

if __name__ == "__main__":
    StartTcpServer(context, address=("0.0.0.0", 502))
'''

CLIENT_CODE = r'''
from pymodbus.client import ModbusTcpClient

server_ip = "10.0.0.1"
client = ModbusTcpClient(server_ip, port=502)
ok = client.connect()
print("connect:", ok)
if not ok:
    raise SystemExit("Failed to connect")
res = client.read_holding_registers(address=0, count=10, unit=1)
print("isError:", res.isError())
if not res.isError():
    print("registers:", res.registers)
client.close()
'''

def main():
    setLogLevel('info')
    net = Containernet(controller=None, switch=OVSSwitch)

    # Docker hosts (Ubuntu 22.04)
    d1 = net.addDocker('d1', dimage='ubuntu:22.04', ip='10.0.0.1/24')
    d2 = net.addDocker('d2', dimage='ubuntu:22.04', ip='10.0.0.2/24')

    # One OVS switch, standalone (no controller), OpenFlow 1.3
    s1 = net.addSwitch('s1', protocols=OFV, failMode='standalone')

    net.addLink(d1, s1)  # s1-eth1
    net.addLink(d2, s1)  # s1-eth2
    net.start()

    info('*** Programming flows: default DROP, allow TCP/502 both ways\n')
    add_drop_all(s1)
    p_d1 = sw_port_for(s1, d1)
    p_d2 = sw_port_for(s1, d2)
    allow_tcp_502_bidir(s1, "10.0.0.1", p_d1, "10.0.0.2", p_d2)
    print(of(s1, f'dump-flows {s1.name}'))

    info('*** Installing Python + pymodbus inside containers\n')
    apt = 'DEBIAN_FRONTEND=noninteractive apt-get -yq'
    for n in (d1, d2):
        n.cmd(f'bash -lc "{apt} update"')
        n.cmd(f'bash -lc "{apt} install python3 python3-pip"')
        n.cmd('bash -lc "python3 -m pip install --no-cache-dir pymodbus==3.6.6"')

    info('*** Writing server/client scripts\n')
    put_file(d1, '/root/modbus_server.py', SERVER_CODE)
    put_file(d2, '/root/modbus_client.py', CLIENT_CODE)

    info('*** Starting Modbus server on d1 (port 502)\n')
    d1.cmd('bash -lc "python3 /root/modbus_server.py > /root/server.log 2>&1 & echo $! > /root/server.pid"')

    # Give the server a moment to bind
    time.sleep(2)

    info('*** Running client on d2\n')
    out = d2.cmd('bash -lc "python3 /root/modbus_client.py"')
    print("\n=== Client output (d2) ===\n" + out)

    info('*** Done. Drop to CLI for manual tests (type exit to quit)\n')
    CLI(net)

    # Cleanup server
    d1.cmd('bash -lc "pkill -f modbus_server.py || true"')
    net.stop()

if __name__ == "__main__":
    main()
