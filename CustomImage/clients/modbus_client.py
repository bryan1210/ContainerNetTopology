# Simple Modbus TCP client to read coils and holding registers
from pymodbus.client.sync import ModbusTcpClient
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 502

client = ModbusTcpClient(host=host, port=port)
client.connect()

# Read 10 holding registers from address 0
rr = client.read_holding_registers(0, 10, unit=1)
print("Holding Registers[0..9]:", rr.registers if hasattr(rr, "registers") else rr)

# Read 10 coils from address 0
rc = client.read_coils(0, 10, unit=1)
print("Coils[0..9]:", rc.bits if hasattr(rc, "bits") else rc)

client.close()
