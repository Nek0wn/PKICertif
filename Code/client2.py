import json
import mqtt

class Client:
    def __init__(self):
        self.ca_certificate = None  # Part du principe que le client lui-même est certifié

    def verify_certificate(self, cert):
        print("Vérification du certificat:", cert)
        return True  # Suppose que la vérification est réussie

    def check_revocation(self, client, vendor_id):
        mqtt.publish_message(client, "vehicle/ca/check_revocation", vendor_id)
        print("-----Demande à la CA si le Certif vendeur est révoqué . . .")

    def on_message(self, client, userdata, message):
        if message.topic == "vehicle/client/cert_from_vendor":
            vendor_cert = json.loads(message.payload.decode())
            if self.verify_certificate(vendor_cert):
                print("-----Certificat du vendeur vérifié.")
                self.make_purchase(client)
            else:
                print("-----Certificat du vendeur non vérifié.")
        elif message.topic == "vehicle/ca/revocation_status":
            revocation_status = message.payload.decode()
            if revocation_status == "Not Revoked":
                print("-----Certificat non révoqué, achat possible.")
            else:
                print("-----Certificat révoqué, achat annulé.")

    def request_certificate_verification(self, client, vendor_id):
        mqtt.publish_message(client, "vehicle/client/verify_cert", vendor_id)
        print("-----Demande de vérification de certificat envoyée au vendeur . . .")

    def make_purchase(self, client):
        print("-----Achat effectué avec le vendeur . . .")
        mqtt.publish_message(client, "vehicle/client/make_purchase", "vendor_1")

# Initialisation du client
def main():
    client = Client()
    mqtt_client = mqtt.initialize_mqtt_client()
    mqtt_client.subscribe("vehicle/client/cert_from_vendor")
    mqtt_client.subscribe("vehicle/ca/revocation_status")
    mqtt_client.on_message = client.on_message

    vendor_id = "vendor_1"
    client.request_certificate_verification(mqtt_client, vendor_id)
    client.check_revocation(mqtt_client, vendor_id)

    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("Arrêt du script...")
    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()
