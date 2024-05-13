import ca
import mqtt

# Fonction pour envoyer le certificat du vendeur
def send_certificate(ca_cert):
    # Génère la paire de clés RSA pour le vendeur
    vendeur_key = ca.generate_ca_key_pair()

    # Génère le certificat du vendeur
    vendeur_cert = ca.generate_certificate(vendeur_key)

    # Initialise le client MQTT
    client = mqtt.initialize_mqtt_client()

    # Envoie le certificat du vendeur sur le topic MQTT approprié
    mqtt.publish_message(client, mqtt.base_topic + "/vendeur/certificat", vendeur_cert)

    # Se désabonne du topic MQTT après avoir envoyé le certificat
    client.unsubscribe(mqtt.base_topic + "/vendeur/certificat")
