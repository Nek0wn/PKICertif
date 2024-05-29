from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
import json
import mqtt
import os
import base64

def generate_key_pair():
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    print("Vendor Public Key (without newlines):")
    print(public_key.export_key().decode().replace("\n", ""))
    return private_key, public_key

class Vendor:
    def __init__(self):
        private_key, public_key = generate_key_pair()
        self.private_key = private_key
        self.public_key = public_key
        self.certificate = None
        self.symmetric_key = os.urandom(16)

    def encrypt_with_public_key(self, public_key, data):
        rsa_key = RSA.import_key(public_key)
        print("Clé publique importée avec succès :", rsa_key)
        rsa_cipher = PKCS1_OAEP.new(rsa_key)
        encrypted_data = rsa_cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode()

    def encrypt_with_symmetric_key(self, key, data):
        cipher = AES.new(key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + encrypted_data).decode()

    def decrypt_with_symmetric_key(self, key, encrypted_data):
        encrypted_data = base64.b64decode(encrypted_data)
        cipher = AES.new(key, AES.MODE_CBC, iv=encrypted_data[:16])
        decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted_data

    def request_certificate(self, client, ca_public_key_pem):
        print("CA Public Key (received):")
        print(ca_public_key_pem.replace("\n", ""))
        ca_public_key = RSA.import_key(ca_public_key_pem)
        print("Etape 1 : Bonne")
        encrypted_key = self.encrypt_with_public_key(ca_public_key, self.symmetric_key)
        print("Etape 2 : Bonne")
        mqtt.publish_message(client, "vehicle/ca/request_cert", json.dumps({"vendor": "vendor_1", "symmetric_key": encrypted_key, "public_key": self.public_key.export_key().decode()}))
        print("-----Demande de certificat envoyée à la CA . . .")
        print("Etape 3 : Termine")


    def send_public_key(self, client):
        encrypted_public_key = self.encrypt_with_symmetric_key(self.symmetric_key, self.public_key.export_key().decode())
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

def main():
    vendor = Vendor()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/key_received")
    client.subscribe("vehicle/ca/vendor_cert")
    client.subscribe("vehicle/client/verify_cert")
    client.on_message = vendor.on_message

    # Replace with the actual CA public key

    with open('ca_public_key.pem', 'r') as file:
        ca_public_key_pem = file.read()

#     ca_public_key_pem = """-----BEGIN PUBLIC KEY-----
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApTKh3f+vesPXTljr4yj7
# 7KIxtcd5ZjdkJEIqUEPG1ktmVGcoQ1KIFq0iWst0QB1QQmyPDxZQie8xg/9DModU
# BgnZo7rAoFt4/pGn1U8kjzls7FUm2+8bbay4dePMeEaiCy1xBztW9yeLSt0kTsJq
# leJjhPDUzz6psSPyacY41cIbN+lhYbpPMyl6VOddsX596cXsLtV0hAAGDfjIG6RD
# zndL9Lst+CpgLX+jM9XBhOFrhEdnjzKcNwuo2POpYKRVlDMH3kfucQzQ+ueH4J5w
# kWJtKOT1xitfO1A6dR42vew2VbQlCYgrKwVfmCSwXPiqcUc/m7I9iMOOYSuNo7zC
# AwIDAQAB
# -----END PUBLIC KEY-----"""
    
    vendor.request_certificate(client, ca_public_key_pem)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
       print("Arrêt du script...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()