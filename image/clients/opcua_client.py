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
