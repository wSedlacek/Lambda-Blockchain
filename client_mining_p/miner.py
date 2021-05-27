import requests

from hashlib import sha256
from json import dumps
from sys import argv
from time import perf_counter
from typing import List


def find_proof(block_string: str, starting: int):
    proof = starting
    perf_counter()
    while not valid_proof(block_string, proof):
        proof += 1
    print(f'Took: {int(perf_counter())}s')

    return proof


def valid_proof(block_string: str, proof: int):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 3
    leading zeroes?  Return true if the proof is valid

    :param block_string: <string> The stringified block to use to
    check in combination with `proof`

    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.

    :return: True if the resulting hash is a valid proof, False otherwise
    """
    work = f'{block_string} {proof}'.encode('utf-8')
    hashed = sha256(work).hexdigest()
    return hashed[0:6] == "000000"


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(argv) > 1:
        node = argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    my_id = f.read()
    print("ID:", my_id)
    f.close()

    coins_mined = 0

    while True:

        try:
            request = requests.get(url=node + "/last_block")

            try:
                data = request.json()
            except ValueError:
                print("Error:  Non-json response")
                print("Response returned:")
                print(request)
                break

            print("================")
            print("Mining...")
            proof = find_proof(dumps(data), 0)

            try:
                request = requests.post(
                    url=node + "/mine", json={"proof": proof, "miner": my_id})
                data = request.json()

                if (data != "Invalid Proof"):
                    coins_mined += 1
                print(f"You now have {coins_mined} coins!")

            except requests.exceptions.ConnectionError:
                print("Could not post coin...")
        except requests.exceptions.ConnectionError:
            print("Could not fetch last coin...")
        except KeyboardInterrupt:
            print("Stoping...")
            break
