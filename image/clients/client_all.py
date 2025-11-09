# --- Modbus ---
from pymodbus.client.sync import ModbusTcpClient

def modbus_read_coils(host):
    client = ModbusTcpClient(host=host, port=502)
    try:
        client.connect()
        # Read 10 coils from address 0
        rc = client.read_coils(0, 10, unit=1)
        print("Coils[0..9]:", rc.bits if hasattr(rc, "bits") else rc)

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
        print("Holding Registers[0..9]:", rr.registers if hasattr(rr, "registers") else rr)
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
    nm.scan(host, '1-4999,5001-65000', arguments='-Pn -T4')
    
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

def nmap_port_scan_quick(host):
    """Scan a host and return list of open ports"""    
    # Scan common ports (adjust range as needed)
    nm.scan(host, arguments='-Pn -T4 -F')
    
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
    # Ping scan - checks if hosts are up without port scanning
    nm.scan(hosts=subnet, arguments='-sn')

    hosts = []
    # Check results
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            print(f'Host {host} is up')
            hosts.append(host)
    return hosts

# --- NMAP ---
def input_subnets(data):
    subnet_ips = {}
    for zone_name, zone_data in data['zones'].items():
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
