import requests

from sys import argv
from json import dumps
from hashlib import sha256


def find_proof(block_string: str):
    proof = 0
    while not valid_proof(block_string, proof):
        proof += 1
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
    return hashed[0] == "0" and hashed[1] == "0" and hashed[2] == "0"


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(argv) > 1:
        node = argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    my_id = f.read()
    print("ID is", my_id)
    f.close()

    coins_mined = 0

    while True:
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        new_proof = find_proof(dumps(data))
        r = requests.post(url=node + "/mine",
                          json={"proof": new_proof, "miner": my_id})
        data = r.json()

        if (data != "Invalid Proof"):
            coins_mined += 1
            print(data)
