# main.py
import subprocess
import time
import paho.mqtt.client as mqtt

# Fonction pour lancer un processus en arrière-plan
def launch_process(script_name):
    return subprocess.Popen(["python", script_name])

# Fonction de rappel pour la réception de messages MQTT
def on_message(client, userdata, message):
    print(f"Message reçu sur le topic {message.topic}: {message.payload.decode()}")

# Initialise le client MQTT
def initialize_mqtt_client():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("194.57.103.203", 1883, 60)
    client.loop_start()
    return client

# Publie un message sur un topic MQTT
def publish_message(client, topic, message):
    client.publish(topic, message)

# Simulation des scénarios
def run_scenario(scenario):
    mqtt_client = initialize_mqtt_client()
    
    if scenario == 1:
        # 1er scénario : Client fait un achat après vérification du certificat vendeur
        print("Lancement du scénario 1")
        vendor = launch_process("vendor.py")
        client1 = launch_process("client.py")
        time.sleep(5)
        
    elif scenario == 2:
        # 2ème scénario : Client fait un achat après vérification du certificat vendeur et demande s’il est révoqué
        print("Lancement du scénario 2")
        vendor = launch_process("vendor.py")
        client1 = launch_process("client.py")
        time.sleep(5)
        # Demander la vérification de la révocation (implémentation à ajouter)
        # publish_message(mqtt_client, "vehicle/ca/check_revocation", "vendor_1")
        
    elif scenario == 3:
        # 3ème scénario : Client fait un achat après vérification du certificat vendeur, demande s’il est révoqué et découvre qu’il est révoqué
        print("Lancement du scénario 3")
        vendor = launch_process("vendor.py")
        client1 = launch_process("client.py")
        time.sleep(5)
        # Ajouter le vendeur à la liste des révocations (implémentation à ajouter)
        # publish_message(mqtt_client, "vehicle/ca/revoke_cert", "vendor_1")
        # Demander la vérification de la révocation (implémentation à ajouter)
        # publish_message(mqtt_client, "vehicle/ca/check_revocation", "vendor_1")
        
    time.sleep(10)
    mqtt_client.loop_stop()

# Main
if __name__ == "__main__":
    print("Choisissez un scénario à lancer :")
    print("1 - Client fait un achat après vérification du certificat vendeur")
    print("2 - Client fait un achat après vérification du certificat vendeur et demande s’il est révoqué")
    print("3 - Client fait un achat après vérification du certificat vendeur, demande s’il est révoqué et découvre qu’il est révoqué")
    
    scenario = int(input("Entrez le numéro du scénario : "))
    run_scenario(scenario)
