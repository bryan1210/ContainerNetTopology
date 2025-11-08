import threading
import time
import asyncio
import logging
import os
import subprocess
import socket
import random
import sys
import yaml

# --- Agent --
from flask import Flask, request, jsonify

# --- Modbus (pymodbus 2.5.x) ---
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# --- OPC UA (python-opcua) ---
from opcua import Server, ua

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("ot-all-in-one")

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

    #threading.Thread(target=updater, daemon=True).start()

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

def run_random_port(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))  # Listen on all interfaces, port 8080
    server_socket.listen(1)
    log.info(f"TCP listening on 0.0.0.0:{port}")
    # Accept connections
    while True:
        client_socket, address = server_socket.accept()
        client_socket.recv(1024)
        client_socket.send(b"Hello from server!")
        client_socket.close()

def start_random(exclude, quantity):
    random_ports = []

    while len(random_ports) < quantity:
        num = random.randint(1, 65000)
        if num not in exclude and num not in random_ports:
            random_ports.append(num)
    threads = []
    for each in random_ports:
        thread = threading.Thread(target=run_random_port, args=(each,), daemon=True)
        thread.start()
        threads.append(thread) 

import agent
def run_agent():
    app = Flask(__name__)    
    @app.route('/call_agent', methods=['POST'])
    def call_agent():
        yaml_data = request.data.decode('utf-8')
        #ret = agent.agent(yaml_data)
        return jsonify(agent.agent(yaml_data))
    
    app.run(host='0.0.0.0', port=5000)

# ------------------ Main Orchestrator ------------------- #
if __name__ == "__main__":
    exclude = {502,4840,80,443,5000,23,22}
    
    if len(sys.argv) != 2:
        print("Incorrect amount of arguemnts")
        exit()
    
    hostname = sys.argv[1]

    #Agent
    agent_server = threading.Thread(target=run_agent, daemon=True)
    agent_server.start()

    # HTTP server in thread
    http_server = threading.Thread(target=run_random_port, args=(80,), daemon=True)
    http_server.start()
    # HTTPS server in thread
    https_server = threading.Thread(target=run_random_port, args=(443,), daemon=True)
    https_server.start()

    # SSH server in thread
    ssh_server = threading.Thread(target=run_random_port, args=(22,), daemon=True)
    ssh_server.start()

    # Telnet server in thread
    telnet_server = threading.Thread(target=run_random_port, args=(23,), daemon=True)
    telnet_server.start()

    # OPC UA in thread
    opcua_thread = threading.Thread(target=run_opcua_server, daemon=True)
    opcua_thread.start()

    start_random(exclude, 10)

    try:
        run_modbus_server()
    except KeyboardInterrupt:
        log.info("Shutting down...")
        # Threads are daemonic; container stop will terminate.
