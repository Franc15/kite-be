# app/routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from .. import db
from ..models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        address = data['address']
        password = data['password']
        role = data['role']
        eth_address = data['eth_address']
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'User already exists'}), 400
        
        new_user = User(email=email, password=password, role=role, eth_address=eth_address)
        new_user.name = name
        new_user.address = address

        db.session.add(new_user)
        db.session.commit()

        match role:
            case 'manufacturer':
                return jsonify({'message': 'Manufacturer created successfully'}), 201
            case 'supplier':
                return jsonify({'message': 'Supplier created successfully'}), 201
            case 'logistics':
                return jsonify({'message': 'Logistics provider created successfully'}), 201
            case _:
                pass

        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity={'email': email, 'role': user.role})
    return jsonify(access_token=access_token, user=user.serialize()), 200
