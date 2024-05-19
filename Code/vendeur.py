import ca
import mqtt

# Demander un certificat à la CA
def request_certificate():
    client = mqtt.initialize_mqtt_client()
    mqtt.publish_message(client, "vehicle/ca/request_cert", "Requesting Cert")

# Recevoir le certificat de la CA
def on_message(client, userdata, message):
    if message.topic == "vehicle/ca/response_cert":
        print("Certificat reçu:", message.payload.decode())
        # Traiter et stocker le certificat du vendeur ici

# Initialisation du vendeur
def main():
    client = mqtt.initialize_mqtt_client()
    client.subscribe("vehicle/ca/response_cert")
    client.on_message = on_message
    request_certificate()
    client.loop_forever()

if __name__ == "__main__":
    main()
