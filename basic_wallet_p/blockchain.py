from typing import List

from json import dumps
from hashlib import sha256
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


def flatten(l): return [item for sublist in l for item in sublist]


class Transaction():
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __iter__(self):
        yield "amount", self.amount
        yield "receiver", self.receiver
        yield "sender", self.sender

    def __str__(self):
        return dumps(dict(self))


class Block():
    def __init__(self, index: int, timestamp: float, proof: int, previous_hash: str, transations: List[Transaction], miner: str):
        self.index = index
        self.timestamp = timestamp
        self.proof = proof
        self.previous_hash = previous_hash
        self.transactions = transations
        self.miner = miner

    def __iter__(self):
        yield "index", self.index
        yield "miner", self.miner
        yield "previous_hash", self.previous_hash
        yield "proof", self.proof
        yield "timestamp", self.timestamp
        yield "transations", [dict(transaction) for transaction in self.transactions]

    def __str__(self):
        return dumps(dict(self))

    def hash(self):
        """
        Creates a SHA-256 hash of a Block
        """

        return sha256(str(self).encode('utf-8')).hexdigest()


class Blockchain(object):
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []
        self.new_block(proof="100")

    def new_block(self, proof: int, previous_hash: str = None, miner: str = None):
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
        if proof is None:
            raise Exception("Proof of work is required to create a new block!")

        block = Block(index=len(self), timestamp=time(),
                      proof=proof, previous_hash=previous_hash, transations=[*self.current_transactions], miner=miner)

        self.current_transactions = []
        self.chain.append(block)
        return block

    def __len__(self):
        return len(self.chain)

    @property
    def last_block(self):
        return self.chain[-1]

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
        return hashed[0:6] == "000000"


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transation():
    sender = request.json['sender']
    receiver = request.json['receiver']
    amount = request.json['amount']
    transaction = Transaction(sender, receiver, amount)
    blockchain.current_transactions.append(transaction)
    return jsonify(dict(transaction)), 200


@app.route('/mine', methods=['POST'])
def mine():
    proof = request.json['proof']
    miner = request.json['miner']
    last_block = blockchain.last_block
    valid = Blockchain.valid_proof(str(last_block), proof)

    if valid:
        previous_hash = blockchain.last_block.hash()
        reward = Transaction(
            f"node {len(blockchain)}", miner, 1)
        blockchain.current_transactions.append(reward)
        block = blockchain.new_block(proof, previous_hash, miner)
        return jsonify(dict(block)), 200
    else:
        return jsonify("Invalid Proof"), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    chain = [dict(block) for block in blockchain.chain]
    return jsonify(chain), 200


@app.route('/<miner>/transactions', methods=['GET'])
def transactions(miner):
    transactions = [[dict(transaction) for transaction in block.transactions if transaction.receiver == miner or transaction.sender == miner]
                    for block in blockchain.chain]
    return jsonify(flatten(transactions)), 200


@app.route('/<miner>/balance', methods=['GET'])
def balance(miner):
    transactions = [[dict(transaction) for transaction in block.transactions if transaction.receiver == miner or transaction.sender == miner]
                    for block in blockchain.chain]

    balance = 0
    for transaction in flatten(transactions):
        if transaction['sender'] == miner:
            balance -= transaction['amount']

        if transaction['receiver'] == miner:
            balance += transaction['amount']

        print(transaction)

    return jsonify(balance), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    block = dict(blockchain.last_block)
    return jsonify(block), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
