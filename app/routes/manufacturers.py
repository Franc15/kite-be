# app/routes/manufacturers.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import User, Asset, MeterReading
from ..services.upload_service import upload_image
import pandas as pd
from app import ml_model
# from ..web3_utils import web3_utils

bp = Blueprint('manufacturers', __name__, url_prefix='/manufacturers')


@bp.route('/get_all', methods=['GET'])
@jwt_required()
def get_all():
    identity = get_jwt_identity()
    current_user = User.query.filter_by(email=identity['email']).first()
    
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    manufacturers = User.query.filter_by(role='manufacturer').all()
    return jsonify([manufacturer.serialize() for manufacturer in manufacturers]), 200

@bp.route('/create_asset', methods=['POST'])
@jwt_required()
def create_asset():
    user_session = get_jwt_identity()
    
    try:
        data = request.get_json()
        name = data['name']
        description = data['description']
        location = data['location']
        type = data['type']
        status = data['status']
        serial_number = data['serial']
        user = User.query.filter_by(email=user_session['email']).first()

        asset = Asset(name=name, owner_id=user.id)
        asset.description = description
        asset.location = location
        asset.type = type
        asset.status = status
        asset.serial_number = serial_number

        db.session.add(asset)
        db.session.commit()

        return jsonify({'status': 'Asset created'})
    except Exception as e:
        return jsonify({'status': 'An error occurred', 'error': str(e)}), 500
    
@bp.route('/get_all_assets', methods=['GET'])
@jwt_required()
def get_all_assets():
    user_session = get_jwt_identity()

    user = User.query.filter_by(email=user_session['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    assets = Asset.query.filter_by(owner_id=user.id).all()
    return jsonify([asset.serialize() for asset in assets]), 200

@bp.route('/assets/<int:asset_id>/predict', methods=['POST'])
def predict(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first()
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404
    

    data = request.get_json()
    # Assuming data is sent as a list of dictionaries
    df = pd.DataFrame([data])
    # Ensure the order of columns matches the training data
    df = df[['Type_L', 'Type_M', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']]
    prediction = ml_model.predict(df)

    # save meter reading
    meter_reading = MeterReading(asset_id=asset.id, type_l=data['Type_L'], type_m=data['Type_M'], air_temperature=data['Air temperature [K]'], process_temperature=data['Process temperature [K]'], rorational_speed=data['Rotational speed [rpm]'], torque=data['Torque [Nm]'], tool_wear=data['Tool wear [min]'])
    # convert to int
    meter_reading.prediction = int(prediction[0])
    db.session.add(meter_reading)
    db.session.commit()

    return jsonify({'prediction': prediction[0]}), 200

@bp.route('/assets/<int:asset_id>/meter_readings', methods=['GET'])
def get_meter_readings(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first()
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404

    meter_readings = MeterReading.query.filter_by(asset_id=asset.id).all()
    return jsonify([meter_reading.serialize() for meter_reading in meter_readings]), 200





    
   