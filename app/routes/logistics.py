from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import User, Product
from ..services.upload_service import upload_image
# from ..web3_utils import web3_utils

bp = Blueprint('logistics', __name__, url_prefix='/logistics')

@bp.route('/get_all', methods=['GET'])
@jwt_required()
def get_all():
    identity = get_jwt_identity()
    current_user = User.query.filter_by(email=identity['email']).first()
    
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    logistics = User.query.filter_by(role='logistics').all()
    return jsonify([logistic.serialize() for logistic in logistics]), 200