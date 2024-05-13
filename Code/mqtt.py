import paho.mqtt.client as mqtt

# Configuration MQTT
mqtt_broker_ip = "194.57.103.203"
mqtt_broker_port = 1883
base_topic = "vehicle"

# Initialisation du client MQTT
def initialize_mqtt_client():
    client = mqtt.Client()
    client.connect(mqtt_broker_ip, mqtt_broker_port)
    return client

# Publication d'un message MQTT
def publish_message(client, topic, message):
    client.publish(topic, message)

# Souscription à un topic MQTT
def subscribe_topic(client, topic):
    client.subscribe(topic)
