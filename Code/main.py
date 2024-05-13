import ca
import client
import vendeur

def main():
    # Génère la paire de clés RSA pour la CA
    ca_key = ca.generate_ca_key_pair()

    # Génère le certificat de la CA
    ca_cert = ca.generate_certificate(ca_key)

    # Simulation des scénarios
    print("Simulation du scénario 1:")
    client.simulate_scenario_1(ca_cert)

    print("\nSimulation du scénario 2:")
    client.simulate_scenario_2(ca_cert)

    print("\nSimulation du scénario 3:")
    client.simulate_scenario_3(ca_cert)

if __name__ == "__main__":
    main()
