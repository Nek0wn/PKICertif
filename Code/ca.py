from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import json
import mqtt

class CertificationAuthority:
    def __init__(self):
        self.private_key, self.public_key = self.generate_ca_key_pair()
        print("-----Paire de clé générée . . .")
        self.certificates = {}  # Store issued certificates
        self.revoked_certificates = set()  # Store revoked certificates

    # Génération de la paire de clés pour la CA
    def generate_ca_key_pair(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    # Génération d'un certificat auto-signé pour la CA
    def generate_ca_certificate(self):
        cert = {
            "subject": "CA",
            "public_key": self.public_key.decode()
        }
        return base64.b64encode(json.dumps(cert).encode()).decode()

    # Génération d'un certificat pour un vendeur
    def generate_vendor_certificate(self, vendor_id):
        vendor_key = RSA.generate(2048)
        vendor_public_key = vendor_key.publickey().export_key()
        cert = {
            "subject": vendor_id,
            "public_key": vendor_public_key.decode()
        }
        signed_cert = self.sign_certificate(cert)
        self.certificates[vendor_id] = signed_cert
        return signed_cert

    # Signer un certificat
    def sign_certificate(self, cert):
        cert_str = json.dumps(cert)
        cert_hash = SHA256.new(cert_str.encode())
        signer = pkcs1_15.new(RSA.import_key(self.private_key))
        signature = signer.sign(cert_hash)
        cert['signature'] = base64.b64encode(signature).decode()
        return cert

    # Vérifier si un certificat est révoqué
    def is_revoked(self, vendor_id):
        return vendor_id in self.revoked_certificates

    # Révoquer un certificat
    def revoke_certificate(self, vendor_id):
        self.revoked_certificates.add(vendor_id)

    # Gestion des requêtes MQTT pour la CA
    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/ca/request_cert":
            vendor_id = message.payload.decode()
            vendor_cert = self.generate_vendor_certificate(vendor_id)
            mqtt.publish_message(client, "vehicle/ca/response_cert", json.dumps(vendor_cert))
            print("-----Génération du certif Vendeur . . .")
        elif message.topic == "vehicle/ca/check_revocation":
            print("-----Demande de verification de certif . . .")
            vendor_id = message.payload.decode()
            revocation_status = "Revoked" if self.is_revoked(vendor_id) else "Not Revoked"
            mqtt.publish_message(client, "vehicle/ca/revocation_status", revocation_status)
            print("-----Envoi de l'issue de la vérif . . .")
        elif message.topic == "vehicle/ca/revoke_cert":
            print("-----Ajout d'un certificat a la liste révoquée . . .")
            vendor_id = message.payload.decode()
            self.revoke_certificate(vendor_id)
            mqtt.publish_message(client, "vehicle/ca/revoke_response", f"Certificate for {vendor_id} revoked")

# Initialisation de la CA
def main():
    ca = CertificationAuthority()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/request_cert")
    client.subscribe("vehicle/ca/check_revocation")
    client.subscribe("vehicle/ca/revoke_cert")
    client.on_message = ca.on_message

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Arrêt du script...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
