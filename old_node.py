from blockchain import Blockchain
from wallet import Wallet
from utility_tools.verification import Verification
from uuid import uuid4


class Node:

    def __init__(self):
        # self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        """Returns the input of the user (a new transaction amount) as a float."""
        transaction_recipient = input(
            "Enter the recipient of the transaction: ")
        transaction_amount = float(
            input("Enter the recipient of the amount: "))

        # tuple example
        return (transaction_recipient, transaction_amount)

    def get_user_choice(self):
        _user_choice = input("Your choice: ")
        return _user_choice

    def output_blockchain_blocks(self):
        for block in self.blockchain.chain:
            print("Outputting block")
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print("Choose the options")
            print("1: Add a new transaction value")
            print("2: Mine a new block")
            print("3: Output the blockchain blocks")
            print("4: Check transaction validity")
            print("5: Create a wallet")
            print("6: Load Wallet")
            print("h: Manipulate the hack")
            print("q: Exit")

            user_choice = self.get_user_choice()

            if user_choice == "1":
                transaction_data = self.get_transaction_value()
                recipient, amount = transaction_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print("Transaction added!")
                else:
                    print("Transaction failed!")
                print(self.blockchain.open_transactions)
            elif user_choice == 2:
                if not self.blockchain.mine_block():
                    print('Mining failed. A wallet is required!')
            elif user_choice == "3":
                self.output_blockchain_blocks()
            elif user_choice == "4":
                if Verification.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance):
                    print("All Transactions are valid")
                else:
                    print("There are invalid transactions")
            elif user_choice == "5":
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == "6":
                self.wallet.load_wallet_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == "q":
                print("Exiting...")
                waiting_for_input = False
            else:
                print("Input was invalid!, try again following the options")
            if not Verification.verify_chain(self.blockchain.chain, self.blockchain.get_balance):
                print("Invalid blockchain!")
                self.output_blockchain_blocks()
                break
            print('Balance of {}: {:6.2f}'.format(
                self.wallet.public_key, self.blockchain.get_balance()))
            print("User left!")


if __name__ == "__main__":
    node = Node()
    node.listen_for_input()
