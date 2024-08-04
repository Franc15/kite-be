from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from .. import db
from ..web3_utils import web3_utils
from app.models import User, Order, OrderHistory

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    user_session = get_jwt_identity()

    # Initialize web3 and contract
    web3 = web3_utils.get_web3()
    contract = web3_utils.get_contract()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        data = request.get_json()
        product_id = data['product']
        quantity = data['quantity']
        origin = data['manufacturer']
        user_id = user.id

        origin_entity = User.query.filter_by(id=origin).first()
        if not origin_entity:
            return jsonify({'message': 'Origin not found'}), 404

        order = Order(product_id=product_id, quantity=quantity, origin=origin_entity.name, user_id=user_id)
        db.session.add(order)
        db.session.commit()

        # Interact with the blockchain
        tx_hash = contract.functions.createOrder(order.id).transact({'from': user.eth_address})
        web3.eth.wait_for_transaction_receipt(tx_hash)

        # Log the order creation
        description = f'Order created by {user.name}'
        order_history = OrderHistory(order_id=order.id, description=description)
        db.session.add(order_history)
        db.session.commit()

        return jsonify({'status': 'Order created'}), 201
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 500
    
@bp.route('/get_all_made', methods=['GET'])
@jwt_required()
def get_all_orders():
    user_session = get_jwt_identity()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    orders = Order.query.filter_by(user_id=user.id).all()
    return jsonify([order.serialize() for order in orders]), 200

@bp.route('/get_all_received', methods=['GET'])
@jwt_required()
def get_all_received_orders():
    user_session = get_jwt_identity()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    orders = Order.query.filter(or_(Order.current_owner_id == user.id, Order.origin == user.name)).all()
    return jsonify([order.serialize() for order in orders]), 200

@bp.route('/<int:order_id>/update_status', methods=['PUT'])
@jwt_required()
def update_status(order_id):
    user_session = get_jwt_identity()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Initialize web3 and contract
    web3 = web3_utils.get_web3()
    contract = web3_utils.get_contract()

    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    data = request.get_json()
    status = data['status']
    
    # Update the order status in the database
    order.status = status
    if status == 'Accepted':
        order.current_owner_id = user.id
        order.product.quantity -= order.quantity
    db.session.commit()

    # Update the order status on the blockchain
    try:
        # log the order status update
        description = f'Order status updated to {status} by {user.name}'
        order_history = OrderHistory(order_id=order.id, description=description)
        db.session.add(order_history)
        db.session.commit()

        # Assuming `updateOrderStatus` is a function in your smart contract that accepts order ID and status
        tx_hash = contract.functions.transferOwnership(order_id, user.eth_address, status).transact({'from': user.eth_address})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return jsonify({'status': 'Order updated successfully on the blockchain'}), 200
        else:
            return jsonify({'status': 'Failed to update order on the blockchain'}), 500
    except Exception as e:
        # Rollback database changes if blockchain update fails
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@bp.route('/<int:order_id>/update_owner_status', methods=['PUT'])
@jwt_required()
def update_owner_status(order_id):
    user_session = get_jwt_identity()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Initialize web3 and contract
    web3 = web3_utils.get_web3()
    contract = web3_utils.get_contract()

    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    data = request.get_json()
    current_owner_id = data['current_owner_id']
    status = data['status']
    
    # Check if the current user is authorized to update the order
    if order.current_owner_id != user.id:
        return jsonify({'message': 'Unauthorized action'}), 403

    next_owner = User.query.filter_by(id=current_owner_id).first()
    if not next_owner:
        return jsonify({'message': 'Next owner not found'}), 404
    
    # Update the order status in the database
    order.status = status
    order.current_owner_id = current_owner_id
    db.session.commit()

    # Update the order status on the blockchain
    try:
        # log the order status and owner update
        description = f'Order status updated to {status} and transferred to {next_owner.name} by {user.name}'
        order_history = OrderHistory(order_id=order.id, description=description)
        db.session.add(order_history)
        db.session.commit()

        tx_hash = contract.functions.transferOwnership(order_id, next_owner.eth_address, status).transact({'from': user.eth_address})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            return jsonify({'status': 'Order updated successfully on the blockchain'}), 200
        else:
            return jsonify({'status': 'Failed to update order on the blockchain'}), 500
    except Exception as e:
        # Rollback database changes if blockchain update fails
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
    

@bp.route('/<int:order_id>/history', methods=['GET'])
def get_order_history(order_id):
    # Initialize web3 and contract
    web3 = web3_utils.get_web3()
    contract = web3_utils.get_contract()

    try:
        # Fetch raw history from the blockchain
        raw_history = contract.functions.getOrderHistory(order_id).call()
        
        # Initialize a list to store formatted history
        formatted_history = []

        # Fetch names for addresses
        address_to_name = {address: address for address in {entry[0] for entry in raw_history}}
        for address in address_to_name:
            try:
                name = contract.functions.getName(address).call()
                address_to_name[address] = name if name else address
            except:
                address_to_name[address] = address

        # Format the history with names
        for entry in raw_history:
            owner, status, timestamp = entry
            owner_name = address_to_name.get(owner, owner)
            formatted_history.append({
                'owner': owner_name,
                'status': status,
                'timestamp': timestamp
            })

        # get order history from the database
        order_history = OrderHistory.query.filter_by(order_id=order_id).all()

        return jsonify({'history': [entry.serialize() for entry in order_history]}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

