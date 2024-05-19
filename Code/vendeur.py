import json
import mqtt

class Vendor:
    def __init__(self):
        self.certificate = None

    # Demander un certificat à la CA
    def request_certificate(self, client):
        mqtt.publish_message(client, "vehicle/ca/request_cert", "vendor_1")
        print("-----Demande de certificat . . .")


    # Recevoir le certificat de la CA
    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/ca/response_cert":
            self.certificate = json.loads(message.payload.decode())
            print("-----Certificat reçu:", self.certificate)

        # Recevoir la demande de verification de la part du client (pour lui envoyer son certif)    
        elif message.topic == "vehicle/client/verify_cert":
            print("-----Client demande le certif du Vendeur. . .")
            self.send_certificate(client)


    # Envoyer le certificat au client
    def send_certificate(self, client):
        mqtt.publish_message(client, "vehicle/client/cert_from_vendor", json.dumps(self.certificate))
        print("-----Envoi du certif Vendeur au Client . . .")


# Initialisation du vendeur
def main():
    vendor = Vendor()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/response_cert")
    client.subscribe("vehicle/client/verify_cert")
    client.on_message = vendor.on_message

    client.loop_start()
    try:
        vendor.request_certificate(client)
        while True:
            pass
    except KeyboardInterrupt:
        print("Arrêt du script...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
