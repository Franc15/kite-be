# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from web3 import Web3
import json
from flask_migrate import Migrate
from .web3_utils import web3_utils
import joblib
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
w3 = None
contract = None
ml_model = None

def create_app():
    global ml_model
    app = Flask(__name__)

    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Define the absolute path to the model file
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'my_model.pkl')

    # Load the predictive model
    ml_model = joblib.load(model_path)

    try:
        # Initialize Web3 and contract using Web3Utils
        contract = web3_utils.get_contract()
        print(f"Contract successfully set up at address: {web3_utils.contract_address}")

    except Exception as e:
        print(f"Error setting up Web3 or contract: {e}")
        contract = None

    # from .routes import auth, manufacturers, suppliers, logistics, tracking, blockchain
    from .routes import auth, manufacturers, shipment, orders, products, logistics, suppliers
    app.register_blueprint(auth.bp)
    app.register_blueprint(manufacturers.bp)
    app.register_blueprint(shipment.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(suppliers.bp)
    app.register_blueprint(logistics.bp)
    # app.register_blueprint(tracking.bp)
    # app.register_blueprint(blockchain.bp)

    return app

