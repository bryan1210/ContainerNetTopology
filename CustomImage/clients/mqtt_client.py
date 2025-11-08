# Simple MQTT pub/sub test against the built-in broker
import time
import threading
import sys
from paho.mqtt import client as mqtt

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 1883
topic = "ot/demo/temp"

recv = []

def on_connect(c, u, f, rc):
    print("[MQTT] Connected with result code", rc)
    c.subscribe(topic)

def on_message(c, u, msg):
    payload = msg.payload.decode("utf-8", errors="ignore")
    print("[MQTT] RX:", msg.topic, payload)
    recv.append(payload)

def sub_thread():
    c = mqtt.Client()
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(host, port, 60)
    c.loop_forever()

t = threading.Thread(target=sub_thread, daemon=True)
t.start()

# Give subscriber time to connect
time.sleep(1.5)

pub = mqtt.Client()
pub.connect(host, port, 60)

for i in range(3):
    msg = f"hello-{i}"
    print("[MQTT] TX:", topic, msg)
    pub.publish(topic, msg, qos=0)
    time.sleep(1)

pub.disconnect()
time.sleep(2)
