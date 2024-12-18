import os
import sys

# Get the directory containing this script and add it to the sys.path
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

from utils_simulation import createHospitals, set_hospitals, get_hospitals, print_line

# utilizzando brownie importo il contratto FederatedLearning.sol per utilizzarlo
# (il contratto deve essere nella directoru 'contracts')
# importo l'oggetto 'accounts' da brownie. Rappresenta la lista dei contratti partecipanti alla blockchain.
# quando usi una blockchain locale come GANACHE, brownie carica gli account forniti dal nodo ganache
from brownie import FederatedLearning, accounts
import deploy_FL


# with this CLI argument choose to retrieve or to create the hospitals information
isCreated = True
if "main" in sys.argv:
    isCreated = False


def main():
    """
    1)  Hospitals creation
    """
    hospitals = None
    if isCreated:
        hospitals = get_hospitals()
    else:
        hospitals = createHospitals()
    print("[1]\tHospitals have been created")
    print_line("*")

    # KYC = Know Your Customer process - identity verification
    """
    2)  KYC Process and Off-Chain Hospitals Registration
        - This must be done before the blockchain
    """
    print("[2]\tKYC Process and Off-Chain Hospitals Registration completed")
    print_line("*")

    """
    3)  Blockchain implementation
    """
    deploy_FL.deploy_federated_learning()
    print("[3]\tFederatedLearning contract has been deployed - Blockchain implemented")
    print_line("*")

    # for each fake hospital assign an account from the mock blockchain
    """
    4)  Assign Blockchain addresses to Hospitals
    """
    # only with Ganache fl-local network
    for idx, hospital_name in enumerate(hospitals, start=1):
        hospitals[hospital_name].address = accounts[idx].address
        print(
            "Hospital name:",
            hospital_name,
            "\tGanache address:",
            hospitals[hospital_name].address,
            "\tGanache idx:",
            idx,
        )
    print("[4]\tAssigned Ganache addresses to the hospitals")
    print_line("*")

    """
    5)  Opening the Blockchain and adding the Collaborators
    """
    federated_learning = FederatedLearning[-1]
    manager = deploy_FL.get_account()
    print("Manager address:", manager)

    open_tx = federated_learning.open({"from": manager})
    open_tx.wait(1)
    print(open_tx.events)

    for hospital_name in hospitals:
        hospital_address = hospitals[hospital_name].address
        add_tx = federated_learning.add_collaborator(
            hospital_address, {"from": manager}
        )
        add_tx.wait(1)
        print(add_tx.events)
    print("[5]\tBlockchain opened and collaborators authorized to ues it")
    print_line("*")

    if not isCreated:
        # print all information of each Hospital object in the dictionary
        for key, hospital in hospitals.items():
            print(f"Key: {key}")
            hospital_info = vars(hospital)
            for attr, value in hospital_info.items():
                print(f"{attr}: {value}")
            print()

        # set the Hospital file
        set_hospitals(hospitals)


if __name__ == "__main__":
    main()
