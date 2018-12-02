from time import time
from utility_tools.printable import Printable


class Block(Printable):

    def __init__(self, index, previous_hash, transactions, proof_work, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof_work = proof_work
        self.timestamp = time() if timestamp is None else timestamp

    def __repr__(self):
        return 'Index: {}, Previous Hash: {}, Proof: {}, Transactions: {}'.format(self.index, self.previous_hash, self.proof_work, self.transactions)
