import time
import paho.mqtt.client as mqtt
import json

mqtt_broker_ip = "194.57.103.203"
mqtt_broker_port = 1883

def on_message(client, userdata, message):
    print(f"Reçu sur {message.topic}: {message.payload.decode()}")


def simulate_scenario_3(client):
    print("Démarrage du Scénario 3")
    # Le vendeur demande à la CA de certifier son certificat
    client.publish("vehicle/ca/request_cert", json.dumps({"vendor": "vendor_3"}))
    time.sleep(5)  # Attendre pour laisser le temps de réponse

    # Le client vérifie le certificat du vendeur
    client.publish("vehicle/client/verify_cert", "vendor_3")
    time.sleep(5)  # Attendre pour laisser le temps de vérification

    # Révocation automatique du certificat de vendor_3 par la CA
    client.publish("vehicle/ca/revoke_cert", "vendor_3")
    print("Certificat de vendor_3 ajouté à la liste des certificats révoqués.")

    # Le client demande à la CA si le certificat est révoqué
    client.publish("vehicle/ca/check_revocation", "vendor_3")
    time.sleep(5)  # Attendre pour laisser le temps de vérification de révocation

    # Pas d'achat car le certificat est révoqué
    print("Le certificat de vendor_3 est révoqué, achat annulé.")


def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker_ip, mqtt_broker_port)

    client.loop_start()

    simulate_scenario_3(client)

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
