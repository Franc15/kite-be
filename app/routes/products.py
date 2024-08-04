from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..web3_utils import web3_utils
from app.services.upload_service import upload_image
from app.models import User, Product

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_product():
    user_session = get_jwt_identity()
    
    # web3 = web3_utils.get_web3()
    # contract = web3_utils.get_contract()

    try:
        data = request.form
        sku = data['sku']
        description = data['description']
        quantity = data['quantity']
        image_file = request.files.get('image')
        user = User.query.filter_by(email=user_session['email']).first()

        image = ""
        if image_file:
            image = upload_image(image_file)

        product = Product(sku=sku, manufacturer_id=user.id)
        product.image = image
        product.description = description
        product.quantity = quantity

        db.session.add(product)
        db.session.commit()

        if image is None:
            image = ""

        # tx_hash = contract.functions.addProduct(name, image, owner, description).transact({'from': user.eth_address})
        # web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({'status': 'Product created'})
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 500

@bp.route('/get_all', methods=['GET'])
@jwt_required()
def get_all_products():
    user_session = get_jwt_identity()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    owner = user.name

    # contract = web3_utils.get_contract()
    # products = contract.functions.getProductsByOwner(owner).call()

    # products = [{'id': product[0], 'name': product[1], 'owner': product[2], 'image': product[3], 'description': product[4]} for product in products]

    products = Product.query.filter_by(manufacturer_id=user.id).all()
    products = [product.serialize() for product in products]

    return jsonify({'products': products})

@bp.route('/get_by_manufacturer/<int:manufacturer_id>', methods=['GET'])
@jwt_required()
def get_by_manufacturer(manufacturer_id):
    identity = get_jwt_identity()
    current_user = User.query.filter_by(email=identity['email']).first()
    
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    manufacturer = User.query.filter_by(id=manufacturer_id, role='manufacturer').first()
    if not manufacturer:
        return jsonify({'message': 'Manufacturer not found'}), 404
    
    products = Product.query.filter_by(manufacturer_id=manufacturer_id).all()
    return jsonify([product.serialize() for product in products]), 200