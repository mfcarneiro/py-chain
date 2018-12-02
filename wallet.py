from Crypto.PublicKey import RSA
from Crypto import Signature
from Crypto.Hash import SHA256
from Crypto import Random
import binascii


class Wallet:
    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key
        self.save_wallet_keys()

    def generate_keys(self):
        private_key = RSA.generate(1024, Random.new().read)
        public_key = private_key
        return (
            binascii
            .hexlify(private_key.exportKey(format='DER'))
            .decode('ascii'),
            binascii
            .hexlify(public_key.exportKey(format='DER'))
            .decode('ascii')
        )

    def save_wallet_keys(self):
        if self.private_key is not None and self.public_key is not None:
            try:
                with open('wallet-{}.txt.'.format(self.node_id),
                          mode='w') as wallet_file:
                    wallet_file.write(self.public_key)
                    wallet_file.write('\n')
                    wallet_file.write(self.private_key)
                    return True
            except():
                print('Loading the wallet has failed..')
                return False

    def load_wallet_keys(self):
        try:
            with open('wallet-{}.txt'.format(self.node_id),
                      mode='r') as wallet_file:
                read_keys = wallet_file.readlines()
                public_key = read_keys[0][:-1]
                private_key = read_keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except(IOError, IndexError):
            print('Saving the walled has failed..')
            return False

    def sign_transaction(self, sender, recipent, amount):
        signer_identity = Signature.PKCS1_v1_5.new(
            RSA.importKey(binascii.unhexlify(self.private_key)))
        sign_hash = SHA256.new(
            (str(sender) + str(recipent) + str(amount)).encode('utf-8'))
        signature = signer_identity.sign(sign_hash)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_wallet_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = Signature.PKCS1_v1_5.new(public_key)
        verify_hash = SHA256.new(
            (str(transaction.sender) +
             str(transaction.recipent) +
             str(transaction.amount)).encode('utf-8'))
        return verifier.verify(verify_hash,
                               binascii.unhexlify(transaction.signature))
