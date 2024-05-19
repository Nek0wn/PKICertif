import time
import paho.mqtt.client as mqtt
import json

mqtt_broker_ip = "194.57.103.203"
mqtt_broker_port = 1883

def on_message(client, userdata, message):
    print(f"Reçu sur {message.topic}: {message.payload.decode()}")

def simulate_scenario_1(client):
    print("Démarrage du Scénario 1")
    # Le vendeur demande à la CA de certifier son certificat
    client.publish("vehicle/ca/request_cert", json.dumps({"vendor": "vendor_1"}))
    time.sleep(5)  # Attendre pour laisser le temps de réponse
    
    # Le client vérifie le certificat du vendeur
    client.publish("vehicle/client/verify_cert", "vendor_1")
    time.sleep(5)  # Attendre pour laisser le temps de vérification

    # Le client fait un achat
    client.publish("vehicle/client/make_purchase", "vendor_1")
    time.sleep(5)  # Attendre pour laisser le temps de réalisation d'achat

def simulate_scenario_2(client):
    print("Démarrage du Scénario 2")
    # Le vendeur demande à la CA de certifier son certificat
    client.publish("vehicle/ca/request_cert", json.dumps({"vendor": "vendor_2"}))
    time.sleep(5)  # Attendre pour laisser le temps de réponse

    # Le client vérifie le certificat du vendeur
    client.publish("vehicle/client/verify_cert", "vendor_2")
    time.sleep(5)  # Attendre pour laisser le temps de vérification

    # Le client demande à la CA si le certificat est révoqué
    client.publish("vehicle/ca/check_revocation", "vendor_2")
    time.sleep(5)  # Attendre pour laisser le temps de vérification de révocation

    # Supposer que le certificat n'est pas révoqué
    client.publish("vehicle/client/make_purchase", "vendor_2")
    time.sleep(5)  # Attendre pour laisser le temps de réalisation d'achat

def simulate_scenario_3(client):
    print("Démarrage du Scénario 3")
    # Le vendeur demande à la CA de certifier son certificat
    client.publish("vehicle/ca/request_cert", json.dumps({"vendor": "vendor_3"}))
    time.sleep(5)  # Attendre pour laisser le temps de réponse

    # Le client vérifie le certificat du vendeur
    client.publish("vehicle/client/verify_cert", "vendor_3")
    time.sleep(5)  # Attendre pour laisser le temps de vérification

    # Le client demande à la CA si le certificat est révoqué
    client.publish("vehicle/ca/check_revocation", "vendor_3")
    time.sleep(5)  # Attendre pour laisser le temps de vérification de révocation

    # Supposer que le certificat est révoqué
    # Pas d'achat car le certificat est révoqué
    print("Le certificat de vendor_3 est révoqué, achat annulé.")

def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker_ip, mqtt_broker_port)

    client.loop_start()

    simulate_scenario_1(client)
    time.sleep(10)  # Attendre un peu avant le scénario suivant

    simulate_scenario_2(client)
    time.sleep(10)  # Attendre un peu avant le scénario suivant

    simulate_scenario_3(client)

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
