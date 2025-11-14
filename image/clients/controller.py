import time
import yaml
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

#Ensure correct number of inputs are givin
if len(sys.argv) > 2:
    print("Too many arguemnts")
    exit()
filename = sys.argv[1] if len(sys.argv) > 1 else 'input.yaml'

#start timer
start_time = time.time()

#ingest input
with open(filename) as f:
    input = yaml.safe_load(f)
zones = input['zones']
flows = input['flows']

#List of devices in input file
devices = []
#Dict containing ip and hostname for lookup
ip_hostname = {}
#Loop to fill device list and ip hostname dict
for zone_name, zone_data in zones.items():
    for network_name, network_info in zone_data.items():
        for device in network_info['devices']:
            for device_name, ip in device.items():
                devices.append(ip)
                ip_hostname[ip] = device_name

print(f'Agents: {devices}')

#Encode intput file to send
yaml_zones = yaml.dump(zones).encode('utf-8')
yaml_flows = yaml.dump(flows).encode('utf-8')

#Post funtion for thread handler
def post_to_device(device):
    #print(f"send to {device}")
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
    
# set the numbner of threads 
max_workers = min(25, len(devices))  # Max 20 concurrent requests

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(post_to_device, device) for device in devices]
    
    for future in as_completed(futures):
        device, zone_results, error = future.result()
        if error:
            #print(f"{device} : Error - {error}")
            print(f"Failed to connect to host {ip_hostname[device]} ({device})")
            with open(f'reports/{ip_hostname[device]}.txt', 'w') as f:
                f.write(error)
        else:
            print(f"Successfully recieved report from host {ip_hostname[device]} ({device})\n")
            with open(f'reports/{ip_hostname[device]}.txt', 'w') as f:
                #print(device)
                for each in zone_results:
                    f.write(f"{each}\n")
                    #print(each)


print("Reports are located in reports folder.\n")

final_results = []
with os.scandir("/app/reports") as entries:
    for entry in entries:
        if entry.is_file():
            with open(entry.path) as f:
                lines = f.readlines()
                for row in lines:
                    if len(row.split(" ")[-1])>4:
                        final_results.append(row)
"""
with open("/app/reports/final_results.txt", 'w') as f:
    for line in final_results:
        f.write(line)
"""
elasped_time = int(time.time()-start_time)

hours = elasped_time // 3600
minutes = (elasped_time % 3600) // 60
seconds = elasped_time % 60

#Print Elasped Time
#print(f"Execution time: {hours}h {minutes}m {seconds}s")