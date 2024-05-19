from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from OpenSSL import crypto
import mqtt

# Génération de la paire de clés pour la CA
def generate_ca_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Génération d'un certificat auto-signé pour la CA
def generate_ca_certificate(private_key):
    cert = crypto.X509()
    cert.get_subject().CN = "CA"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(crypto.load_publickey(crypto.FILETYPE_PEM, private_key))
    cert.sign(crypto.load_privatekey(crypto.FILETYPE_PEM, private_key), 'sha256')
    return crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

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