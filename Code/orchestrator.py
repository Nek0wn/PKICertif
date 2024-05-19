import time
import paho.mqtt.client as mqtt

mqtt_broker_ip = "194.57.103.203"
mqtt_broker_port = 1883

def on_message(client, userdata, message):
    print(f"Reçu sur {message.topic}: {message.payload.decode()}")

def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker_ip, mqtt_broker_port)

    client.loop_start()

    # Scenario 1: Client fait un achat juste après avoir vérifié le certificat vendeur
    print("Démarrage du Scénario 1")
    client.publish("vehicle/ca/request_cert", "vendor_1")
    time.sleep(5)  # Attendre pour laisser le temps de réponse
    client.publish("vehicle/client/verify_cert", "Verify Cert")
    time.sleep(5)  # Attendre pour laisser le temps de vérification
    client.publish("vehicle/client/make_purchase", "Make Purchase")
    time.sleep(5)  # Attendre pour laisser le temps de réalisation d'achat

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
