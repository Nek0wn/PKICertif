import paho.mqtt.client as mqtt

mqtt_broker_ip = "194.57.103.203"
mqtt_broker_port = 1883
base_topic = "vehicle"

def initialize_mqtt_client():
    client = mqtt.Client()
    client.connect(mqtt_broker_ip, mqtt_broker_port)
    return client

def publish_message(client, topic, message):
    client.publish(topic, message)

def subscribe_topic(client, topic):
    client.subscribe(topic)
