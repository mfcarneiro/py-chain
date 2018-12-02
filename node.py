from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_node_view():
    return send_from_directory('front-end', 'node_interface.html')


@app.route('/node_network', methods=['GET'])
def get_node_network_view():
    return send_from_directory('front-end', 'node_network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()

    if wallet.save_wallet_keys():
        initialize_blockchian()
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }

        return jsonify(response, 201)
    else:
        response = {
            'message': 'Something went wrong! Failed saving the keys'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_wallet_keys():
        initialize_blockchian()
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Something went wrong! Failed loading the keys'
        }
        return jsonify(response), 500


@app.rounte('/transactions', methods=['GET'])
def get_open_transactions():
    open_transactions = blockchain.get_open_transactions()
    dict_transactions = [
        transactions.__dict__ for transactions in open_transactions]
    return jsonify(dict_transactions), 201


@app.route('/broadcast-transactions', methods=['POST'])
def broadcast_transactions():
    broadcast_values = request.get_json()
    if not broadcast_values:
        response = {
            'message': 'No Broadcast data was found!'
        }
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in broadcast_values for key in required):
        response = {
            'message': 'Some information is missing!'
        }
        return jsonify(response), 400
    is_success = blockchain.add_transaction(
        broadcast_values['sender'],
        broadcast_values['recipient'],
        broadcast_values['amount'],
        broadcast_values['signature'],
        is_receiving=True)
    if is_success:
        response = {
            'message': 'A broadcast transaction was added sucessfully!',
            'transaction': {
                'sender': broadcast_values['sender'],
                'receiver': broadcast_values['recipient'],
                'amount': broadcast_values['amount'],
                'signature': broadcast_values['signature']
            },
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'a broadcast transaction failed!'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    broadcast_values = request.get_json()
    if not broadcast_values:
        response = {
            'message': 'No Broadcast data was found!'
        }
        return jsonify(response), 400
    if 'block' not in broadcast_values:
        response = {
            'message': 'Some information is missing!'
        }
        return jsonify(response), 400
    block = broadcast_block['block']
    if block['index'] is blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {
                'message': 'Block has been added!'
            }
            return jsonify(response), 201
        else:
            response = {
                'messsage': 'Block is invalid!'
            }
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'Blockchain seems to be differ from local blockchain!'
        }
        blockchain.resonve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            'message': 'Blockchain seems to be shorter, block not added!'
        }
        return jsonify(response), 409


@app.route('/trasnaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {
            'message': 'No wallet setup!'
        }
        return jsonify(response), 400

    user_values = request.get_json()

    if not user_values:
        response = {
            'message': 'No data found!'
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']

    if not all(field in user_values for field in required_fields):
        response = {
            'message': 'Required data is missing!'
        }
        return jsonify(response), 400

    recipeint = user_values['recipient']
    amount = user_values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipeint, amount)
    is_success = blockchain.add_transaction(
        recipeint, wallet.public_key, amount)

    if is_success:
        response = {
            'message': 'A transaction was added sucessfully!',
            'transaction': {
                'sender': wallet.public_key,
                'receiver': recipeint,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed!'
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced_chain = blockchain.resolve_conflicts()
    if replaced_chain:
        response = {
            'message': 'The Blockchain chain was replaced successfully'
        }
    else:
        response = {
            'message': 'Local chain remains unreplaced'
        }
    return jsonify(response), 200


@app.route('/mining', methods=['POST'])
def mining():
    if blockchain.resolve_conflicts:
        response = {
            'message': 'Resolve conficlts first, block not added!'
        }
        return jsonify(response), 409

    block = blockchain.mine_block()

    if block is not None:
        dict_block = blockchain.__dict__.copy()
        dict_block['trasactions'] = [
            transactions.__dict__
            for transactions in dict_block['transactions']]
        response = {
            'message': 'Block added successfully!',
            'block': dict_block,
            'funds':  get_balance()
        }
    else:
        response = {
            'message': 'The block added has failed',
            'wallet_setup': wallet.public_key is not None
        }
        return jsonify(response), 500


def get_balance():

    if balance is not None:
        balance = blockchain.get_balance()
        response = {
            'message': 'Fetched balance successfully!',
            'funds': balance
        }
    else:
        reponse = {
            'message': 'Loading balance failed!',
            'wallet_setup': wallet.public_key is not None
        }
        return jsonify(reponse), 500


@app.route('/', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]

    for dict_block in dict_chain:
        dict_block['transaction'] = [
            transactions.__dict__
            for transactions in dict_block['transactions']]

    return jsonify(chain_snapshot), 200


def initialize_blockchian():
    global blockchain
    blockchain = Blockchain(wallet.public_key, port)
    return blockchain


@app.route('/node', methos=['POST'])
def add_node():
    node_values = request.get_json()

    if not node_values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400

    if 'node' not in node_values:
        response = {
            'message': 'No node data found!'
        }
        return jsonify(response), 400

    node = node_values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully!',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url is '' or node_url is None:
        response = {
            'message': 'No node Found!'
        }
        return jsonify(response), 400
    blockchain.remove_peer_nodes(node_url)
    response = {
        'message': 'Node removed!',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    all_nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': all_nodes
    }
    return jsonify(response), 200


if __name__ is '__main__':
    """Argument parser are a tooll that allows us to parse arguments passing along
    with your python filename command
    """
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000)
    arguments = parser.parse_args()
    port = arguments.port
    wallet = Wallet()
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
