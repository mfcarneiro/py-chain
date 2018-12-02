from utility_tools.hash_util import hash_block, hash_string_256
from wallet import Wallet


class Verification:
    @classmethod
    def verify_chain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block['previous_hash'] != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block['transactions'][:-1],
                                   block['previous_hash'], block['proof']):
                print('Proof of work is invalid')
                return False

        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return (sender_balance >= transaction.amount and
                    Wallet.verify_wallet_transaction(transaction))
        else:
            return Wallet.verify_wallet_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Verify all the open_transactions using the all() function are valid or not

        Args:
            No args

        Returns:
            bool: Verifing all the transactions to be valid
        """
        return all([cls.verify_transaction(transaction, get_balance, False)
                    for transaction in open_transactions])

    @staticmethod
    def valid_proof(transactions, last_hash, proof_number):
        """The function receives the @staticmethod because is not using
        anything of the class
        """
        guess = (str([transactions.to_orderer_dict()
                      for transactions in transactions]
                     ) + str(last_hash) + str(proof_number)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'
