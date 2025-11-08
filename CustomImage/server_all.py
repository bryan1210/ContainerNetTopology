import threading
import time
import asyncio
import logging
import os
import subprocess

# --- Modbus (pymodbus 2.5.x) ---
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# --- OPC UA (python-opcua) ---
from opcua import Server, ua

# --- MQTT broker (amqtt) ---
from amqtt.broker import Broker


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("ot-all-in-one")

# ------------------ MQTT Broker ------------------ #
def run_mqtt_broker():
    config = {
        "listeners": {
            "default": {"type": "tcp", "bind": "0.0.0.0:1883"}
        },
        "sys_interval": 10,
        "auth": {"allow-anonymous": True}
    }
    broker = Broker(config)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(broker.start())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(broker.shutdown())
        loop.close()

# ------------------ EtherNet/IP (ENIP/CIP) ------------------ #
def run_enip_server():
    """
    Launch cpppo's ENIP adapter server exposing a few demo tags.
    Ports default to 44818/TCP and 2222/UDP (override via env).
    """
    host = os.getenv("ENIP_HOST", "0.0.0.0")
    tcp_port = os.getenv("ENIP_TCP", "44818")
    udp_port = os.getenv("ENIP_UDP", "2222")

    # Demo tags: NAME=TYPE:VALUE
    tags = [
        #"Pump1:Speed=REAL:42.0",
        "Pump1=BOOL[0]",
        "Tank1=DINT[1234]",
    ]

    cmd = [
        os.sys.executable, "-m", "cpppo.server.enip",
        "-a", host,
        "-t", "-T", str(tcp_port)
    ] + tags
    log.info(cmd)
    #log.info(f"ENIP listening on {host}:{tcp_port}/tcp and {host}:{udp_port}/udp")
    # Run in this thread; blocks here until container stops
    subprocess.run(cmd, check=True)

# ------------------ Modbus TCP ------------------- #
def run_modbus_server():
    # Simple holding/input coils/registers 0..99
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [10]*100),
        ir=ModbusSequentialDataBlock(0, [20]*100),
        zero_mode=True
    )
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = "OT All-in-One"
    identity.ProductCode = "OAO"
    identity.VendorUrl = "https://example.local"
    identity.ProductName = "OT Combined Server"
    identity.ModelName = "OT-ALL"
    identity.MajorMinorRevision = "1.0"

    # Periodically bump a few registers so clients can see changes
    def updater():
        i = 0
        while True:
            i += 1
            # Update holding registers 0..3
            rr = context[0x00].getValues(3, 0, count=4)  # 3 = holding registers
            rr = [(x + 1) % 1000 for x in rr]
            context[0x00].setValues(3, 0, rr)
            time.sleep(2)

    threading.Thread(target=updater, daemon=True).start()

    log.info("Modbus TCP listening on 0.0.0.0:502")
    StartTcpServer(context, identity=identity, address=("0.0.0.0", 502))

# ------------------ OPC UA ------------------- #
def run_opcua_server():
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840")
    server.set_server_name("OT All-in-One OPC UA Server")

    # Namespace & nodes
    uri = "urn:ot-all-in-one:server"
    idx = server.register_namespace(uri)
    objects = server.get_objects_node()
    dev = objects.add_object(idx, "Device1")
    temp_var = dev.add_variable(idx, "Temperature", 25.0, varianttype=ua.VariantType.Double)
    temp_var.set_writable()  # allow clients to write

    # Start server
    server.start()
    log.info("OPC UA listening on opc.tcp://0.0.0.0:4840")

    # Periodically update the temperature
    try:
        t = 25.0
        while True:
            t += 0.1
            temp_var.set_value(ua.Variant(t, ua.VariantType.Double))
            time.sleep(2)
    finally:
        server.stop()


# ------------------ Main Orchestrator ------------------- #
if __name__ == "__main__":
    # MQTT broker (asyncio) in its own thread
    #mqtt_thread = threading.Thread(target=run_mqtt_broker, daemon=True)
    #mqtt_thread.start()

    # ENIP server in thread
    #enip_thread = threading.Thread(target=run_enip_server, daemon=True)
    #enip_thread.start()
    run_enip_server()
    # OPC UA in thread
    #opcua_thread = threading.Thread(target=run_opcua_server, daemon=True)
    #opcua_thread.start()

    # Modbus in main thread (blocks). If you’d prefer, swap roles.
    """
    try:
        run_modbus_server()
    except KeyboardInterrupt:
        log.info("Shutting down...")
        # Threads are daemonic; container stop will terminate.
    """