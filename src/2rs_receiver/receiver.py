import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("2rsuit/rawdata")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f'Received message on {msg.topic}: {msg.payload.decode("utf-8")}')
    time.sleep(3)
    client.publish("2rsuit/proc", f'Redirect: {msg.payload.decode("utf-8")}')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
