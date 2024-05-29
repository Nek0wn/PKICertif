import time
import paho.mqtt.client as mqtt
import json


mqtt_broker_ip = "194.57.103.203"
mqtt_broker_port = 1883

def on_message(client, userdata, message):
    print(f"Reçu sur {message.topic}: {message.payload.decode()}")

def simulate_scenario_1(client):
    print("Démarrage du Scénario 1")
    ca_public_key = "-----BEGIN PUBLIC KEY-----\n...CA public key...\n-----END PUBLIC KEY-----"
    
    # Le vendeur demande un certificat
    client.publish("vehicle/ca/request_cert", json.dumps({"vendor": "vendor_1", "symmetric_key": ca_public_key}))
    time.sleep(5)  # Attendre pour laisser le temps de réponse

    # Le vendeur envoie sa clé publique à la CA
    client.publish("vehicle/ca/vendor_public_key", json.dumps({"vendor": "vendor_1", "public_key": ca_public_key}))
    time.sleep(5)  # Attendre pour laisser le temps de réponse

    # Le client vérifie le certificat du vendeur
    client.publish("vehicle/client/verify_cert", "vendor_1")
    time.sleep(5)  # Attendre pour laisser le temps de vérification

    # Le client fait un achat
    client.publish("vehicle/client/make_purchase", "vendor_1")
    time.sleep(5)  # Attendre pour laisser le temps de réalisation d'achat

def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker_ip, mqtt_broker_port)

    client.loop_start()

    simulate_scenario_1(client)
    time.sleep(10)  # Attendre un peu avant le scénario suivant

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
