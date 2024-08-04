from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..web3_utils import web3_utils

bp = Blueprint('shipment', __name__, url_prefix='/shipment')

@bp.route('/create_shipment', methods=['POST'])
def create_shipment():
    web3 = web3_utils.get_web3()
    contract = web3_utils.get_contract()

    data = request.get_json()
    description = data['description']
    address = data['address']

    tx_hash = contract.functions.createShipment(description).transact({'from': address})
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({'status': 'Shipment created'})

@bp.route('/transfer_shipment', methods=['POST'])
def transfer_shipment():
    web3 = web3_utils.get_web3()
    contract = web3_utils.get_contract()

    data = request.get_json()
    shipment_id = data['shipment_id']
    to_address = data['to_address']
    from_address = data['from_address']
    status_str = data['status']

    status_map = {
        'Created': 0,
        'InTransit': 1,
        'Delivered': 2
    }
    status = status_map.get(status_str, 0) 

    tx_hash = contract.functions.transferShipment(shipment_id, to_address, status).transact({'from': from_address})
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return jsonify({'status': 'Shipment transferred'})

@bp.route('/get_shipment_history/<int:shipment_id>', methods=['GET'])
def get_shipment_history(shipment_id):
    contract = web3_utils.get_contract()

    history = contract.functions.getShipmentHistory(shipment_id).call()
    detailed_history = []
    for record in history:
        detailed_history.append({
            'from': record[0],
            'to': record[1],
            'status': record[2],
            'timestamp': record[3]
        })
    return jsonify({'history': detailed_history})

@bp.route('/get_shipment_status/<int:shipment_id>', methods=['GET'])
def get_shipment_status(shipment_id):
    contract = web3_utils.get_contract()

    status = contract.functions.getShipmentStatus(shipment_id).call()
    return jsonify({'status': status})
