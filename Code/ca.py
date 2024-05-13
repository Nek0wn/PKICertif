from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

# Génération de la paire de clés RSA pour la CA
def generate_ca_key_pair():
    key = RSA.generate(2048)
    return key

# Génération du certificat auto-signé pour un vendeur
def generate_certificate(private_key):
    # Création du certificat
    cert = {
        "public_key": private_key.publickey().export_key().decode(),
        "signature": "",
        # D'autres informations de certificat peuvent être ajoutées ici
    }

    # Signature du certificat
    signer = PKCS1_v1_5.new(private_key)
    digest = SHA256.new(str(cert).encode())
    cert["signature"] = signer.sign(digest).hex()

    return cert

# Vérification de la validité d'un certificat
def verify_certificate(cert, ca_key):
    # Récupération de la clé publique de la CA
    ca_pub_key = RSA.import_key(ca_key)

    # Vérification de la signature
    signature = bytes.fromhex(cert["signature"])
    digest = SHA256.new(str(cert).encode())
    verifier = PKCS1_v1_5.new(ca_pub_key)
    if verifier.verify(digest, signature):
        return True
    else:
        return False

# Insertion d'un certificat révoqué
def revoke_certificate(cert):
    # Implémente la logique d'insertion d'un certificat révoqué
    pass
