
#!/usr/bin/python
import yaml
with open('network.yaml') as f:
    data = yaml.safe_load(f)

for sw_name, devices in data["switches"].items():
    print(f"\nSwitch: {sw_name}")
    for device in devices:
        for name, ip in device.items():
            print(f"  {name}: {ip}")

for sw_name, devices in data["links"].items():
    print(f"\nSwitch: {sw_name}")
    for device in devices:
        print(f"  {sw_name} -> {device}")


