import time
import yaml
import sys
import requests

if len(sys.argv) != 2:
    print("Incorrect amount of arguemnts")
    exit()
print(sys.argv[1])
start_time = time.time()


#ingest input
with open(sys.argv[1]) as f:
    input = yaml.safe_load(f)
zones = input['zones']

devices = []

for zone_name, zone_data in zones.items():
    for network_name, network_info in zone_data.items():
        for device in network_info['devices']:
            for device_name, ip in device.items():
                devices.append(ip)

print(devices)

#do something with flows


#read in input file
#Process Input file

import nmap_client
for each in devices:
    response = requests.post(
        f"http://{each}:5000/run_tests",
        json={'tests': 'test'}
    )
    zone_results = response.json()
    print(f"{each} : {zone_results}")

#hosts = nmap_client.nmap_portscan("10.0.0.0/24")
#hosts = nmap_client.nmap_portscan("10.0.1.0/24")
#hosts = nmap_client.nmap_portscan("10.0.2.0/24")
#hosts = nmap_client.nmap_portscan("10.0.3.0/24")
#hosts = nmap_client.nmap_portscan("10.0.4.0/24")
#hosts = nmap_client.nmap_portscan("10.0.5.0/24")
#rint(hosts)

#generate output file

#Print Elasped Time
print(f"Execution time: {time.time()-start_time:.2f} seconds")

