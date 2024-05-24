from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
import base64
import json
import os
import mqtt

class CertificationAuthority:
    def __init__(self):
        self.private_key, self.public_key = self.generate_ca_key_pair()
        self.certificates = {}  # Store issued certificates
        self.revoked_certificates = set()  # Store revoked certificates
        self.symmetric_keys = {}  # Store symmetric keys for vendors

    def generate_ca_key_pair(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        print(public_key)
        return private_key, public_key

    def generate_ca_certificate(self):
        cert = {
            "subject": "CA",
            "public_key": self.public_key.decode()
        }
        return base64.b64encode(json.dumps(cert).encode()).decode()

    def sign_certificate(self, cert):
        cert_str = json.dumps(cert)
        cert_hash = SHA256.new(cert_str.encode())
        signer = pkcs1_15.new(RSA.import_key(self.private_key))
        signature = signer.sign(cert_hash)
        cert['signature'] = base64.b64encode(signature).decode()
        return cert

    def is_revoked(self, vendor_id):
        return vendor_id in self.revoked_certificates

    def revoke_certificate(self, vendor_id):
        self.revoked_certificates.add(vendor_id)

    def decrypt_with_private_key(self, encrypted_data):
        rsa_cipher = PKCS1_OAEP.new(RSA.import_key(self.private_key))
        decrypted_data = rsa_cipher.decrypt(base64.b64decode(encrypted_data))
        return decrypted_data

    def decrypt_with_symmetric_key(self, key, encrypted_data):
        key = base64.b64decode(key)
        encrypted_data = base64.b64decode(encrypted_data)
        cipher = AES.new(key, AES.MODE_CBC, iv=encrypted_data[:16])
        decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted_data

    def encrypt_with_symmetric_key(self, key, data):
        key = base64.b64decode(key)
        cipher = AES.new(key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + encrypted_data).decode()

    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/ca/request_cert":
            data = json.loads(message.payload.decode())
            vendor_id = data['vendor']
            encrypted_key = data['symmetric_key']
            symmetric_key = self.decrypt_with_private_key(encrypted_key)
            self.symmetric_keys[vendor_id] = base64.b64encode(symmetric_key).decode()
            mqtt.publish_message(client, "vehicle/ca/key_received", json.dumps({"vendor": vendor_id}))

        elif message.topic == "vehicle/ca/vendor_public_key":
            data = json.loads(message.payload.decode())
            vendor_id = data['vendor']
            encrypted_public_key = data['public_key']
            symmetric_key = self.symmetric_keys[vendor_id]
            vendor_public_key = self.decrypt_with_symmetric_key(symmetric_key, encrypted_public_key)
            cert = {
                "subject": vendor_id,
                "public_key": vendor_public_key.decode()
            }
            signed_cert = self.sign_certificate(cert)
            encrypted_cert = self.encrypt_with_symmetric_key(symmetric_key, json.dumps(signed_cert))
            mqtt.publish_message(client, "vehicle/ca/vendor_cert", json.dumps({"vendor": vendor_id, "cert": encrypted_cert}))

        elif message.topic == "vehicle/ca/check_revocation":
            vendor_id = message.payload.decode()
            revocation_status = "Revoked" if self.is_revoked(vendor_id) else "Not Revoked"
            mqtt.publish_message(client, "vehicle/ca/revocation_status", revocation_status)

        elif message.topic == "vehicle/ca/revoke_cert":
            vendor_id = message.payload.decode()
            self.revoke_certificate(vendor_id)
            mqtt.publish_message(client, "vehicle/ca/revoke_response", f"Certificate for {vendor_id} revoked")

# Initialisation de la CA
def main():
    ca = CertificationAuthority()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/request_cert")
    client.subscribe("vehicle/ca/vendor_public_key")
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
