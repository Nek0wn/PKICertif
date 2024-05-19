from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import mqtt

# Génération de la paire de clés pour la CA
def generate_ca_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Génération d'un certificat auto-signé pour la CA
def generate_ca_certificate(private_key):
    key = RSA.import_key(private_key)
    cert = {
        "subject": "CA",
        "public_key": key.publickey().export_key().decode()
    }
    return base64.b64encode(str(cert).encode()).decode()

# Gestion des requêtes MQTT pour la CA
def on_message(client, userdata, message):
    if message.topic == "vehicle/ca/request_cert":
        # Génération d'un certificat pour le vendeur
        private_key, public_key = generate_ca_key_pair()
        vendor_cert = generate_ca_certificate(private_key)
        mqtt.publish_message(client, "vehicle/ca/response_cert", vendor_cert)
    elif message.topic == "vehicle/ca/check_revocation":
        # Répondre à une requête de vérification de révocation
        mqtt.publish_message(client, "vehicle/ca/revocation_status", "Not Revoked")

# Initialisation de la CA
def main():
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/request_cert")
    client.subscribe("vehicle/ca/check_revocation")
    client.on_message = on_message
    client.loop_forever()

if __name__ == "__main__":
    main()
