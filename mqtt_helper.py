# mqtt_helper.py
import paho.mqtt.client as mqtt

def publish_message(client, topic, message):
    client.publish(topic, message)

def on_connect(client, userdata, flags, rc):
    print("Connecté au broker MQTT avec le code de retour: " + str(rc))

def initialize_mqtt_client(on_message_callback, broker_address):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message_callback
    client.connect(broker_address)
    return client
