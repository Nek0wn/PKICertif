from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
import mqtt

# Fonction pour la vérification du certificat du vendeur
def verify_seller_certificate(seller_cert, ca_cert):
    # Vérification de la validité du certificat du vendeur
    if ca.verify_certificate(seller_cert, ca_cert):
        print("Le certificat du vendeur est valide.")
        return True
    else:
        print("Le certificat du vendeur est invalide.")
        return False

# Fonction pour la vérification de la révocation du certificat du vendeur
def check_seller_revocation(seller_cert):
    # Vérification de la révocation du certificat du vendeur
    if ca.check_revoked(seller_cert):
        print("Le certificat du vendeur est révoqué.")
        return True
    else:
        print("Le certificat du vendeur n'est pas révoqué.")
        return False

# Fonction pour simuler le scénario 1
def simulate_scenario_1():
    # Connecte le client au vendeur
    # client.connect_to_seller()

    # Reçoit le certificat du vendeur
    # seller_cert = client.receive_certificate()

    # Vérifie la validité du certificat du vendeur
    # verify_seller_certificate(seller_cert)

    # Effectue l'achat
    print("Client fait un achat.")

# Fonction pour simuler le scénario 2
def simulate_scenario_2():
    # Connecte le client au vendeur
    # client.connect_to_seller()

    # Reçoit le certificat du vendeur
    # seller_cert = client.receive_certificate()

    # Vérifie la validité du certificat du vendeur
    # verify_seller_certificate(seller_cert)

    # Vérifie la révocation du certificat du vendeur
    # check_seller_revocation(seller_cert)

    # Effectue l'achat
    print("Client fait un achat.")

# Fonction pour simuler le scénario 3
def simulate_scenario_3():
    # Connecte le client au vendeur
    # client.connect_to_seller()

    # Reçoit le certificat du vendeur
    # seller_cert = client.receive_certificate()

    # Vérifie la validité du certificat du vendeur
    # verify_seller_certificate(seller_cert)

    # Vérifie la révocation du certificat du vendeur
    # check_seller_revocation(seller_cert)

    # Si le certificat du vendeur est révoqué, n'effectue pas l'achat
    # if not check_seller_revocation(seller_cert):
    #     print("Client fait un achat.")
    # else:
    #     print("Client ne fait pas d'achat car le certificat du vendeur est révoqué.")
    pass
