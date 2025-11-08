# Simple Modbus TCP client to read coils and holding registers
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