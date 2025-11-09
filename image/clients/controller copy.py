import time
import yaml
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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
yaml_data = yaml.dump(zones)
for each in devices:
    response = requests.post(
        f"http://{each}:5000/call_agent",
        data=yaml_data
    )
    zone_results = response.json()
    #zone_results = response
    print(f"{each} : {zone_results}")

#Print Elasped Time
print(f"Execution time: {time.time()-start_time:.2f} seconds")