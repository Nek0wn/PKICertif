import json
import mqtt

class Vendor:
    def __init__(self):
        self.certificate = None

    # Demander un certificat à la CA
    def request_certificate(self, client):
        mqtt.publish_message(client, "vehicle/ca/request_cert", "vendor_1")

    # Recevoir le certificat de la CA
    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/ca/response_cert":
            self.certificate = json.loads(message.payload.decode())
            print("Certificat reçu:", self.certificate)
        elif message.topic == "vehicle/client/verify_cert":
            self.send_certificate(client)

    # Envoyer le certificat au client
    def send_certificate(self, client):
        mqtt.publish_message(client, "vehicle/client/cert_from_vendor", json.dumps(self.certificate))

# Initialisation du vendeur
def main():
    vendor = Vendor()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/response_cert")
    client.subscribe("vehicle/client/verify_cert")
    client.on_message = vendor.on_message

    client.loop_start()
    vendor.request_certificate(client)
    client.loop_forever()

if __name__ == "__main__":
    main()
