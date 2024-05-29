# vendor.py
import json
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Génère la paire de clés du vendeur
def generate_vendor_keys():
    vendor_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    vendor_public_key = vendor_private_key.public_key()
    return vendor_private_key, vendor_public_key

# Fonction de rappel pour la réception de messages MQTT
def on_message(client, userdata, message):
    if message.topic == "vehicle/ca/cert_response":
        data = json.loads(message.payload.decode())
        if data["vendor_id"] == userdata["vendor_id"]:
            handle_cert_response(data, client)

# Gère la réponse de la CA avec le certificat
def handle_cert_response(data, client):
    userdata["vendor_certificate"] = data["certificate"]
    print("Certificat reçu de la CA:")
    print(data["certificate"])

# Initialise le client MQTT
def initialize_mqtt_client(vendor_id, vendor_public_key_pem):
    client = mqtt.Client(userdata={"vendor_id": vendor_id})
    client.on_message = on_message
    client.connect("194.57.103.203", 1883, 60)
    client.subscribe("vehicle/ca/cert_response")
    client.loop_start()

    # Demande un certificat à la CA
    request = {
        "vendor_id": vendor_id,
        "public_key": vendor_public_key_pem.decode()
    }
    client.publish("vehicle/ca/request_cert", json.dumps(request))
    
    return client

# Main
vendor_id = "vendor_1"
vendor_private_key, vendor_public_key = generate_vendor_keys()
vendor_public_key_pem = vendor_public_key.public_bytes(serialization.Encoding.PEM)

client = initialize_mqtt_client(vendor_id, vendor_public_key_pem)

while True:
    pass
