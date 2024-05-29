# client.py
import os
import json
import paho.mqtt.client as mqtt
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID

# Charge la clé publique de la CA
def load_ca_public_key():
    with open("ca_cert.pem", "rb") as f:
        return x509.load_pem_x509_certificate(f.read()).public_key()

# Vérifie si un certificat est valide
def verify_certificate(cert, ca_public_key):
    try:
        ca_public_key.verify(cert.signature, cert.tbs_certificate_bytes, padding.PKCS1v15(), cert.signature_hash_algorithm)
        print("Certificat valide.")
        return True
    except Exception as e:
        print(f"Erreur de vérification du certificat: {e}")
        return False

# Vérifie si un certificat est révoqué
def is_cert_revoked(cert, crl):
    for revoked_cert in crl:
        if revoked_cert.serial_number == cert.serial_number:
            print("Certificat révoqué.")
            return True
    print("Certificat non révoqué.")
    return False

# Fonction de rappel pour la réception de messages MQTT
def on_message(client, userdata, message):
    if message.topic == "vehicle/client/cert_from_vendor":
        data = json.loads(message.payload.decode())
        vendor_cert = x509.load_pem_x509_certificate(data["cert"].encode())
        ca_public_key = load_ca_public_key()
        
        if verify_certificate(vendor_cert, ca_public_key):
            print("Certificat du vendeur vérifié avec succès.")
            # Simuler la récupération de la liste de révocation (CRL)
            crl = []  # Cette liste doit être remplie avec les certificats révoqués
            is_cert_revoked(vendor_cert, crl)

# Initialise le client MQTT
def initialize_mqtt_client():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("194.57.103.203", 1883, 60)
    client.subscribe("vehicle/client/cert_from_vendor")
    return client

# Publie un message sur un topic MQTT
def publish_message(client, topic, message):
    client.publish(topic, message)

# Main
mqtt_client = initialize_mqtt_client()
mqtt_client.loop_forever()
