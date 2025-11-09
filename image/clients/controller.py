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
flows = input['flows']
devices = []

for zone_name, zone_data in zones.items():
    for network_name, network_info in zone_data.items():
        for device in network_info['devices']:
            for device_name, ip in device.items():
                devices.append(ip)

print(f'Agents: {devices}')

yaml_zones = yaml.dump(zones).encode('utf-8')
yaml_flows = yaml.dump(flows).encode('utf-8')

def post_to_device(device):
    try:
        response = requests.post(
            f"http://{device}:5000/call_agent",
            data=yaml_zones,
            headers={'Content-Type': 'application/x-yaml'}
        )
        response.raise_for_status()
        return device, response.json(), None
    except requests.Timeout:
        return device, None, "Timeout"
    except requests.RequestException as e:
        return device, None, str(e)
    
# Adjust max_workers based on number of devices
max_workers = min(5, len(devices))  # Max 20 concurrent requests

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(post_to_device, device) for device in devices]
    
    for future in as_completed(futures):
        device, zone_results, error = future.result()
        if error:
            print(f"{device} : Error - {error}")
        else:
            print(f"{device} : {zone_results}")

#Print Elasped Time
print(f"Execution time: {time.time()-start_time:.2f} seconds")