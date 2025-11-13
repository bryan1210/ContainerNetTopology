import socket
import time

# --- Modbus ---
from pymodbus.client.sync import ModbusTcpClient

def modbus_read_coils(host):
    client = ModbusTcpClient(host=host, port=502)
    try:
        client.connect()
        # Read 10 coils from address 0
        rc = client.read_coils(0, 10, unit=1)
        client.close()
        return True
    except:
        return False

def modbus_read_registers(host):
    client = ModbusTcpClient(host=host, port=502)
    try:
        client.connect()
        # Read 10 holding registers from address 0
        rr = client.read_holding_registers(0, 10, unit=1)
        client.close()
        return True
    except:
        return False
    
# --- Modbus ---
# --- opcua ---
from opcua import Client, ua

def opcua_read(host):
    endpoint = f"opc.tcp://{host}:4840"
    client = Client(endpoint)
    client.set_user("")  # anonymous
    client.set_password("")
    try: 
        client.connect()
        print("[OPC UA] Connected to", endpoint)
        objects = client.get_objects_node()
        for obj in objects.get_children():
            try:
                name = obj.get_browse_name().Name
                if name == "Device1":
                    temp = [n for n in obj.get_children() if n.get_browse_name().Name == "Temperature"][0]
                    val = temp.get_value()
                    print("Temperature :", val)
                    break
            except Exception:
                pass

        client.disconnect()
        return True
    except:
        return False

# --- opcua ---


# --- NMAP ---

import nmap
nm = nmap.PortScanner()

def nmap_port_scan(host):
    """Scan a host and return list of open ports"""    
    # Scan common ports (adjust range as needed)
    #nm.scan(host, '1-4999,5001-65000', arguments='-Pn -T5')
    nm.scan(host, arguments='-Pn -T4 -n --top-ports 500 --exclude-ports 5000')
    open_ports = []
    # Check if host is up
    if host in nm.all_hosts():
        # Get all protocols (usually 'tcp')
        for proto in nm[host].all_protocols():
            # Get all ports for this protocol
            ports = nm[host][proto].keys()
            
            # Filter only open ports
            for port in ports:
                if nm[host][proto][port]['state'] == 'open':
                    open_ports.append(port)
    return sorted(open_ports)

def host_discovery(subnet):
    nm.scan(hosts=subnet, arguments='-sn -T4 -n')
    hosts = []
    # Check results
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            hosts.append(host)
    return hosts
# --- NMAP ---

# Get local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address (doesn't actually send data)
        s.connect(('10.0.0.1', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_ips_by_zone(data):
    #Dict containing ip and hostname for lookup
    ip_zones = {}
    #Loop to fill device list and ip hostname dict
    for zone_name, zone_data in data.items():
        ip_zones[zone_name] = []
        for network_name, network_info in zone_data.items():
            for device in network_info['devices']:
                for device_name, ip in device.items():
                    ip_zones[zone_name].append(ip)
    return ip_zones

def get_subnet_ips(data):
    subnet_ips = {}
    for zone_name, zone_data in data.items():
        for network_name, network_data in zone_data.items():
            subnet = network_data['subnet']
            
            # Extract IPs from devices list
            ips = []
            for device in network_data['devices']:
                # Each device is a dict with one key-value pair
                for device_name, ip in device.items():
                    ips.append(ip)
            subnet_ips[subnet] = ips
    return subnet_ips

def generate_name_lookup(data):
    #Dict containing ip and hostname for lookup
    ip_hostname = {}
    #Loop to fill device list and ip hostname dict
    for zone_name, zone_data in data.items():
        for network_name, network_info in zone_data.items():
            for device in network_info['devices']:
                for device_name, ip in device.items():
                    ip_hostname[ip] = device_name
    return ip_hostname

def host_discover(data):
    undocumented_hosts = []
    discovered_hosts = []
    for subnet, ip in data.items():
        ret = host_discovery(subnet)
        discovered_hosts.extend(ret)
        if sorted(ip) != sorted(ret):
            undocumented_hosts.append(set(ret)-set(ip))
    return f"Undocumented Hosts : {undocumented_hosts}", discovered_hosts

def test_connections(data,ip_by_zone):
    results = {}
    report = []
    my_zone = ""
    my_ip = get_local_ip()
    for key, value in ip_by_zone.items():
        print(value)
        if my_ip in value:
            my_zone = key
            break
    print(my_ip)
    print(my_zone)
    for each in data:
        if each in ip_by_zone[my_zone]:
            continue
        print(f"Test connection each = {each}")
        results[each] = nmap_port_scan(each)
        report.append(f"{my_ip} -> {each} : port {results[each]}")
    return report, results


def agent(data):
    results= []
    ips_by_zone = get_ips_by_zone(data)
    ip_hostname = generate_name_lookup(data)
    input_subnets = get_subnet_ips(data)
    #discover hosts
    host_discover_report, discovered_hosts = host_discover(input_subnets)
    results.append(host_discover_report)
    print(f'Type of discover host = {discovered_hosts}')
    #Test segementation
    test_connections_report, test_connections_results = test_connections(discovered_hosts,ips_by_zone)
    results.extend(test_connections_report)
    print(test_connections_results)
    #results.append(test_connections_results)
    modbus_hosts = [key for key, value in test_connections_results.items() if 502 in value]
    opcua_hosts = [key for key, value in test_connections_results.items() if 4840 in value]

    print(results)
    return results
