# ca.py
import os
import json
import paho.mqtt.client as mqtt
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.x509.oid import NameOID

# Génère la paire de clés de la CA et crée un certificat auto-signé
def generate_ca_keys():
    ca_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_public_key = ca_private_key.public_key()
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Some-State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"CA"),
    ])
    
    ca_certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_private_key, hashes.SHA256())
    )
    
    return ca_private_key, ca_public_key, ca_certificate

# Fonction de rappel pour la réception de messages MQTT
def on_message(client, userdata, message):
    if message.topic == "vehicle/ca/request_cert":
        data = json.loads(message.payload.decode())
        handle_certificate_request(data, client)

# Gère les demandes de certificat
def handle_certificate_request(data, client):
    ca_private_key = userdata["ca_private_key"]
    ca_public_key = userdata["ca_public_key"]
    
    vendor_public_key = serialization.load_pem_public_key(data["public_key"].encode())
    
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Some-State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Vendor"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"vendor.com"),
    ])
    
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_certificate.subject)
        .public_key(vendor_public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(ca_private_key, hashes.SHA256())
    )
    
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode()
    
    response = {
        "vendor_id": data["vendor_id"],
        "certificate": cert_pem
    }
    
    client.publish("vehicle/ca/cert_response", json.dumps(response))

# Initialise le client MQTT
def initialize_mqtt_client(ca_private_key, ca_public_key, ca_certificate):
    client = mqtt.Client(userdata={
        "ca_private_key": ca_private_key,
        "ca_public_key": ca_public_key,
        "ca_certificate": ca_certificate
    })
    client.on_message = on_message
    client.connect("194.57.103.203", 1883, 60)
    client.subscribe("vehicle/ca/request_cert")
    client.subscribe("vehicle/ca/check_revocation")
    client.loop_start()
    return client

# Main
ca_private_key, ca_public_key, ca_certificate = generate_ca_keys()

client = initialize_mqtt_client(ca_private_key, ca_public_key, ca_certificate)

# Publie la clé publique de la CA sur MQTT
client.publish("vehicle/ca/public_key", ca_public_key.public_bytes(serialization.Encoding.PEM).decode())

while True:
    pass
