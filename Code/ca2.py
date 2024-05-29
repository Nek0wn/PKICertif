from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import base64
import json
import mqtt
import os

class CA:
    def __init__(self):
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()
        self.crl = []  # Certificate Revocation List
        print("CA Public Key (without newlines):")
        print(self.public_key.export_key().decode().replace("\n", ""))

    def decrypt_with_private_key(self, encrypted_data):
        rsa_cipher = PKCS1_OAEP.new(self.private_key)
        decrypted_data = rsa_cipher.decrypt(base64.b64decode(encrypted_data))
        return decrypted_data

    def sign_certificate(self, public_key):
        public_key_bytes = public_key.export_key(format='PEM')
        hash_obj = SHA256.new(public_key_bytes)
        signature = pkcs1_15.new(self.private_key).sign(hash_obj)
        return base64.b64encode(signature).decode()

    def revoke_certificate(self, public_key_pem):
        self.crl.append(public_key_pem)
        print("Certificate revoked and added to CRL.")

    def is_revoked(self, public_key_pem):
        return public_key_pem in self.crl

    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/ca/request_cert":
            data = json.loads(message.payload.decode())
            vendor_id = data['vendor']
            encrypted_key = data['symmetric_key']
            symmetric_key = self.decrypt_with_private_key(encrypted_key)

            vendor_public_key_pem = data.get("public_key")
            if not vendor_public_key_pem:
                vendor_public_key_pem = self.generate_key_pair().public_key().export_key().decode()
            
            if self.is_revoked(vendor_public_key_pem):
                print(f"Certificate for vendor {vendor_id} is revoked.")
                return

            vendor_public_key = RSA.import_key(vendor_public_key_pem)
            signed_cert = self.sign_certificate(vendor_public_key)

            encrypted_cert = self.encrypt_with_symmetric_key(symmetric_key, signed_cert)
            response = {"cert": encrypted_cert}
            mqtt.publish_message(client, "vehicle/ca/vendor_cert", json.dumps(response))
            print(f"-----Certificat envoyé au vendeur {vendor_id} . . .")

    def encrypt_with_symmetric_key(self, key, data):
        cipher = AES.new(key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + encrypted_data).decode()

    def generate_key_pair(self):
        return RSA.generate(2048)

def main():
    ca = CA()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/request_cert")
    client.on_message = ca.on_message

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Arrêt du script...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
