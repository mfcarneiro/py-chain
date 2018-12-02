from functools import reduce
import requests
import json
from block import Block
from transaction import Transaction
from utility_tools.hash_util import Hash_util
from utility_tools.verification import Verification
from wallet import Wallet

# Global variable
MINING_REWARD = 10


class Blockchain:

    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        # old way to set a private attribute
        # self.__chain = [genesis_block]
        # self.__open_transactions = []
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_blockchain_file
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resonve_conflicts = False
        self.load_blockchain_file()

    # another convention instead to use set() keyword /
    # it's like a dictionary but don't have key/values
    # only need the values
    # participants = {
    #     'mfcarneiro'
    # }

    # old way to set a getter
    # def get_chain(self):
    #     return self.__chain
    #
    # def get_open_transactions(self):
    #    return self.__open_transactions

    @property
    def chain(self):
        """Getter example"""
        return self.chain[:]

    @chain.setter
    def chain(self, value):
        """Setter example"""
        self.chain = value

    @property
    def get_open_transactions(self):
        return self.open_transactions

    @open_transactions.setter
    def set_open_transactions(self, value):
        self.open_transactions = value

    def load_blockchain_file(self):
        try:
            with open('blockchain-{}.txt'.format(self.node_id),
                      module='r') as blockchain_file:
                file_content = blockchain_file.readlines()
                self.__chain = json.loads(file_content[0][:-1])
                converted_transaction = []
                update_blockchain = []

                # Here goes the updated code using Transaction and
                # Block classes
                for block in self.__chain:
                    pass
                update_blockchain.append(update_blockchain)
                self.__chain = update_blockchain
                self.__open_transactions = json.loads(file_content[1])

        except(IOError, IndexError):
            print('error')

    def get_last_blockchain_value(self):
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def proof_of_work(self):
        _last_block = self.__chain[-1]
        _last_hash = Hash_util.hash_block(_last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions,
                                           _last_hash, proof):
            proof += 1
        return proof

    # Insert the default values on a function parameter

    def add_transaction(self,
                        recipient,
                        sender,
                        amount=1.0,
                        signature='',
                        is_receiving=False):
        """Append a new value as well as the last blockchain value to the blockchain.
        PS: 'is' don't check the value, but if they're the same object
        """
        # set() will only add an immutable value
        # and this make sure that it will have only unique sender
        # dictionary data structure example

        """Because of PEP8, always overwrite '='
        equal signs with 'is' keyworkd """
        if self.public_key is None:
            return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            # save_blockchain_file()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/boradcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={
                            'sender': sender, 'recipient': recipient,
                            'amount': amount, 'signature': signature})
                        if (response.status_code is 400 or
                                response.status_code is 500):
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue

            return True
        return False

    def mine_block(self):
        # "pass" the function defined but not used to don't interfering
        # in the whole script
        last_block = self.__chain[-1]
        hashed_block = Hash_util.hash_block(last_block)
        _proof_of_work = self.proof_of_work()
        # reward_transaction = Transaction(
        #     'MINING', self.public_key,  MINING_REWARD)
        reward_transaction = Transaction(
            'MINING', self.public_key, '', MINING_REWARD)

        if self.public_key is None:
            return False
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': 'MINING_REWARD'
        # }

        # block = {
        #     'previous_hash': hashed_block,
        #     'index': len(self.__chain),
        #     'transactions': copied_transactions,
        #     'proof': _proof_of_work
        # }
        """ Using the range selector ":" to copy by reference the open_transactions
        Making the :open_transactions array safe and local, not leaking
        to a global variable
        Keep in mind that : (range selector) is shallow copy,
        when used in a dictionary, will not work
        """
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)
        for transactions in copied_transactions:
            if not Wallet.verify_wallet_transaction(transactions):
                return None
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, _proof_of_work)
        self.__chain.append(block)
        self.__open_transactions = []
        # call save_blockchain_file()

        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [
                transactions.__dict__
                for transactions in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': ''})
                if response.status_code is 400 or response.status_code is 500:
                    print('Block declined, needs resolving')
                if response.status_code is 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def get_balance(self, sender=None):
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender
        amount_received = self.get_transaction_amount_received(participant)
        amount_sent = self.get_transaction_amount_sent(participant)

        return amount_received - amount_sent

    def get_transaction_amount_sent(self, participant):
        # This functions are an example of a nested list comprehension
        transaction_sender = [
            [transaction.amount for transaction in block.transactions
             if transaction.sender is participant]
            for block in self.__chain]

        set_transaction_sender = self.get_open_transaction_sender(participant)
        transaction_sender.append(set_transaction_sender)
        amount_sent = reduce(
            lambda current_transaction,
            transaction_amount: current_transaction + sum(transaction_amount)
            if len(transaction_amount) > 0
            else current_transaction + 0, transaction_sender, 0)

        return amount_sent

    def get_transaction_amount_received(self, participant):
        transaction_recipient = [
            [transaction.amount
             for transaction in block.transactions
             if transaction.recipient is participant]
            for block in self.__chain]

        amount_received = reduce(
            lambda current_transaction, transaction_amount:
            current_transaction +
            sum(transaction_amount) if len(transaction_amount) > 0
            else current_transaction + 0, transaction_recipient, 0)

        return amount_received

    def get_open_transaction_sender(self, participant):
        transaction_sender = [
            transaction.amount for transaction in self.__open_transactions if
            transaction.sender is participant]
        return transaction_sender

    def resolve_conflicts(self):
        winner_chain = self.chain
        replace_chain = False
        for node in self.__peer_nodes:
            url = 'https://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [
                    Block(
                        block['index'],
                        block['previous_hash'],
                        block['transactions'],
                        block['proof_work'],
                        block['timestamp']) for block in node_chain]
                node_chain.transactions = [
                    Transaction(
                        transactions['sender'],
                        transactions['recipient'],
                        transactions['amount'],
                        transactions['signature'])
                    for transactions in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)

                if (node_chain_length > local_chain_length and
                        Verification.verify_chain(winner_chain)):
                    print('Proof of work is invalid!')
                    replace_chain = True
            except requests.exceptions.ConnectionError:
                continue
            self.resolve_conflicts = True
            self.chain = winner_chain
            if replace_chain:
                self.__open_transactions = []
            # save_blockchain_data()
            return replace_chain

    def add_peer_node(self, node):
        """Adds a new noed to the peer set.

        Args:
            node: The node URL witch should be added
        """
        self.__peer_nodes.add(node)
        # self.save_blockchain_data()

    def remove_peer_nodes(self, node):
        """Remove a new noed to the peer set.

        Args:
            node: The node URL witch should be removed
        """
        self.__per_nodes.discard(node)
        # self.save_blockchain_data()

    def get_peer_nodes(self):
        """Returns a list of all connected peers nodes.

        Args:
            No args

        Returns:
            Returns a list off all connected peers nodes copied
        """
        return list(self.__peer_nodes)

    def add_block(self, block):
        transactions = [
            Transaction(transaction['sender'],
                        transaction['recipient'],
                        transaction['amount'],
                        transaction['signature'])
            for transaction in block['transactions']]
        is_valid_proof = Verification.valid_proof(
            transactions[:1], block['pevious_hash'], block['valid_proof'])
        match_hash = Hash_util.hash_block(
            self.chain[-1]) is block['previous_hash']

        if not is_valid_proof or not match_hash:
            return False

        converted_block = Block(
            block['index'],
            block['previous_hash'],
            block['proof_work'],
            block['timestamp'])

        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for incoming_transactions in block['transactions']:
            for open_transactions in stored_transactions:
                if (open_transactions.sender
                    is incoming_transactions['sender'] and open_transactions
                    is incoming_transactions['recipient'] and open_transactions
                    is incoming_transactions['amount'] and open_transactions
                        is incoming_transactions['signature']):
                    try:
                        self.__open_transactions.remove(open_transactions)
                    except ValueError:
                        print("Item was already removed!")
        # save_blockchain_data()
        return True
