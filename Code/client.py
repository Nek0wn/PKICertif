import json
import mqtt

class Client:
    def __init__(self):
        self.ca_certificate = None  # Assume preloaded with CA certificate

    # Vérifier le certificat du vendeur
    def verify_certificate(self, cert):
        # Logique de vérification du certificat du vendeur
        print("Vérification du certificat:", cert)
        return True  # Suppose la vérification est réussie

    # Demander à la CA si le certificat du vendeur est révoqué
    def check_revocation(self, client, vendor_id):
        mqtt.publish_message(client, "vehicle/ca/check_revocation", vendor_id)

    # Recevoir les réponses de la CA
    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/client/cert_from_vendor":
            vendor_cert = json.loads(message.payload.decode())
            if self.verify_certificate(vendor_cert):
                self.check_revocation(client, vendor_cert["subject"])
        elif message.topic == "vehicle/ca/revocation_status":
            print("Statut de révocation reçu:", message.payload.decode())
        elif message.topic == "vehicle/client/make_purchase":
            print("Client fait un achat.")

# Initialisation du client
def main():
    client_instance = Client()
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/client/cert_from_vendor")
    client.subscribe("vehicle/ca/revocation_status")
    client.subscribe("vehicle/client/make_purchase")
    client.on_message = client_instance.on_message

    client.loop_start()
    client.loop_forever()

if __name__ == "__main__":
    main()
