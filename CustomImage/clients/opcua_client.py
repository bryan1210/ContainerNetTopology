# Simple OPC UA client: read & write Device1.Temperature
from opcua import Client, ua
import sys

endpoint = f"opc.tcp://{sys.argv[1]}:{sys.argv[2]}" if len(sys.argv) > 2 else "opc.tcp://127.0.0.1:4840"

client = Client(endpoint)
client.set_user("")  # anonymous
client.set_password("")
client.connect()
print("[OPC UA] Connected to", endpoint)

# Browse to find our node (or use a hardcoded NodeId if you prefer)
objects = client.get_objects_node()
for obj in objects.get_children():
    try:
        name = obj.get_browse_name().Name
        if name == "Device1":
            temp = [n for n in obj.get_children() if n.get_browse_name().Name == "Temperature"][0]
            val = temp.get_value()
            print("Temperature (before):", val)
            temp.set_value(ua.Variant(val + 1.23, ua.VariantType.Double))
            print("Temperature (after):", temp.get_value())
            break
    except Exception:
        pass

client.disconnect()
