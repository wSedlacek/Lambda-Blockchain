from typing import List

from json import dumps
from hashlib import sha256
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Block():
    def __init__(self, index: int, timestamp: float, proof: int, previous_hash: str, transations: List[int]):
        self.index = index
        self.timestamp = timestamp
        self.proof = proof
        self.previous_hash = previous_hash
        self.transactions = transations

    def __iter__(self):
        yield "index", self.index
        yield "timestamp", self.timestamp
        yield "proof", self.proof
        yield "previous_hash", self.previous_hash
        yield "transations", self.transactions

    def __str__(self):
        return dumps(dict(self))

    def hash(self):
        """
        Creates a SHA-256 hash of a Block
        """

        return sha256(str(self).encode('utf-8')).hexdigest()


class Blockchain(object):
    def __init__(self):
        self.chain: List(Block) = []
        self.current_transactions: List[float] = []
        self.new_block(previous_hash=1, proof="100")

    def new_block(self, proof: int, previous_hash: str = None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        if not proof:
            raise Exception("Proof of work is required to create a new block!")

        block = Block(index=len(self.chain), timestamp=time(),
                      proof=proof, previous_hash=previous_hash, transations=[*self.current_transactions])

        self.current_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def proof_of_work(block: Block):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof

        :return: A valid proof for the provided block
        """

        proof = 0
        while not Blockchain.valid_proof(str(block), proof):
            proof += 1

        return proof

    @staticmethod
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


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    proof = Blockchain.proof_of_work(blockchain.last_block)
    previous_hash = str(blockchain.last_block.hash())
    block = blockchain.new_block(proof=proof, previous_hash=previous_hash)
    return jsonify(dict(block)), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    chain = [dict(block) for block in blockchain.chain]
    return jsonify(chain), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
