import time

def hold():
    start_time = time.time()

    import hold.nmap_client as nmap_client
    import hold.modbus_client as modbus_client
    import hold.opcua_client as opcua_client

    target = "10.0.0.1"
    open_ports = nmap_client.nmap_port_scan(target)
    if 502 in open_ports:
        print(modbus_client.modbus_read_coils(target))
        print(modbus_client.modbus_read_registers(target))
    if 4840 in open_ports:
        print(opcua_client.opcua_read(target))


    print(f"Elaseped Time : {time.time() - start_time}")

