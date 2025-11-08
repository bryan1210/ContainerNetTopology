import nmap
nm = nmap.PortScanner()

def nmap_port_scan(host):
    """Scan a host and return list of open ports"""    
    # Scan common ports (adjust range as needed)
    nm.scan(host, '1-65000', arguments='-Pn -T4')
    
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

def hold(subnet):
    print("Nmap_test")
    # Create a PortScanner object
    #nm = nmap.PortScanner()

    # Scan a host
    nm.scan(subnet, '1-65000', arguments='-Pn -T4')
    print("done")
    # Get all hosts that were scanned
    for host in nm.all_hosts():
        print("loop")
        print(f'Host: {host} ({nm[host].hostname()})')
        print(f'State: {nm[host].state()}')
        
        # Iterate through each protocol (tcp, udp, etc.)
        for proto in nm[host].all_protocols():
            print(f'Protocol: {proto}')
            
            # Get all scanned ports
            ports = nm[host][proto].keys()
            for port in ports:
                print(f'Port: {port}\tState: {nm[host][proto][port]["state"]}')

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

if __name__ == "__main__":
    pass