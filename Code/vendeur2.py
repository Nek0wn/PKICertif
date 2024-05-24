from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
import json
import mqtt
import os
import base64

class Vendor:
    def __init__(self):
        self.certificate = None
        self.symmetric_key = os.urandom(16)
        self.private_key, self.public_key = self.generate_key_pair()

    def generate_key_pair(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        print(public_key)
        return private_key, public_key

    def encrypt_with_public_key(self, public_key, data):
        rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
        encrypted_data = rsa_cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode()

    def encrypt_with_symmetric_key(self, key, data):
        key = base64.b64encode(key)
        cipher = AES.new(key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + encrypted_data).decode()

    def decrypt_with_symmetric_key(self, key, encrypted_data):
        key = base64.b64encode(key)
        encrypted_data = base64.b64decode(encrypted_data)
        cipher = AES.new(key, AES.MODE_CBC, iv=encrypted_data[:16])
        decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted_data

    def request_certificate(self, client, ca_public_key):
        encrypted_key = self.encrypt_with_public_key(ca_public_key, self.symmetric_key)
        mqtt.publish_message(client, "vehicle/ca/request_cert", json.dumps({"vendor": "vendor_1", "symmetric_key": encrypted_key}))
        print("-----Demande de certificat envoyée à la CA . . .")

    def send_public_key(self, client):
        encrypted_public_key = self.encrypt_with_symmetric_key(self.symmetric_key, self.public_key.decode())
        mqtt.publish_message(client, "vehicle/ca/vendor_public_key", json.dumps({"vendor": "vendor_1", "public_key": encrypted_public_key}))
        print("-----Clé publique envoyée à la CA . . .")

    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/ca/key_received":
            print("-----Clé symétrique reçue par la CA . . .")
            self.send_public_key(client)
        elif message.topic == "vehicle/ca/vendor_cert":
            data = json.loads(message.payload.decode())
            encrypted_cert = data['cert']
            cert = self.decrypt_with_symmetric_key(self.symmetric_key, encrypted_cert)
            self.certificate = json.loads(cert)
            print("-----Certificat reçu et déchiffré:", self.certificate)
        elif message.topic == "vehicle/client/verify_cert":
            self.send_certificate(client)

    def send_certificate(self, client):
        mqtt.publish_message(client, "vehicle/client/cert_from_vendor", json.dumps(self.certificate))
        print("-----Envoi du certificat au client . . .")

# Initialisation du vendeur
def main():
    vendor = Vendor()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/key_received")
    client.subscribe("vehicle/ca/vendor_cert")
    client.subscribe("vehicle/client/verify_cert")
    client.on_message = vendor.on_message

    ca_public_key = "-----BEGIN PUBLIC KEY-----\n...CA public key...\n-----END PUBLIC KEY-----"
    vendor.request_certificate(client, ca_public_key)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Arrêt du script...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
