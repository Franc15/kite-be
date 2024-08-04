from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app import db

bcrypt = Bcrypt()

# User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # manufacturer, supplier, logistics_provider
    name = db.Column(db.String(100), nullable=True)  # New field added
    address = db.Column(db.String(100), nullable=True)
    eth_address = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assets = db.relationship('Asset', back_populates='owner', cascade='all, delete-orphan')
    products = db.relationship('Product', back_populates='manufacturer', cascade='all, delete-orphan')
    orders = db.relationship('Order', foreign_keys='Order.user_id', back_populates='user', cascade='all, delete-orphan')
    current_orders = db.relationship('Order', foreign_keys='Order.current_owner_id', back_populates='current_owner', cascade='all, delete-orphan')

    def __init__(self, email, password, role, eth_address, name=None):
        self.email = email
        self.set_password(password)
        self.role = role
        self.name = name
        self.eth_address = eth_address

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'address': self.address,
            'eth_address': self.eth_address
        }

# Product model
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(150), nullable=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manufacturer = db.relationship('User', back_populates='products')

    orders = db.relationship('Order', back_populates='product', cascade='all, delete-orphan')

    def __init__(self, sku, manufacturer_id):
        self.sku = sku
        self.manufacturer_id = manufacturer_id

    def serialize(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'description': self.description,
            'quantity': self.quantity,
            'image': self.image,
            'manufacturer_id': self.manufacturer_id
        }

# Order model
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product = db.relationship('Product', back_populates='orders')
    quantity = db.Column(db.Integer, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    current_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='orders')
    current_owner = db.relationship('User', foreign_keys=[current_owner_id], back_populates='current_orders')
    history = db.relationship('OrderHistory', back_populates='order', cascade='all, delete-orphan')

    def __init__(self, product_id, quantity, origin, user_id):
        self.product_id = product_id
        self.quantity = quantity
        self.origin = origin
        self.current_owner_id = user_id
        self.user_id = user_id

    def serialize(self):
        return {
            'id': self.id,
            'product': self.product.serialize(),
            'quantity': self.quantity,
            'origin': self.origin,
            'status': self.status,
            'current_owner': self.current_owner.serialize(),
            'user': self.user.serialize(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='assets')

    meter_readings = db.relationship('MeterReading', back_populates='asset', cascade='all, delete-orphan')

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'serial_number': self.serial_number,
            'status': self.status,
            'type': self.type,
            'description': self.description,
            'location': self.location,
            'owner_id': self.owner_id
        }

class MeterReading(db.Model):
    __tablename__ = 'meter_readings'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    asset = db.relationship('Asset', back_populates='meter_readings')
    type_l = db.Column(db.String(50), nullable=False)
    type_m = db.Column(db.String(50), nullable=False)
    air_temperature = db.Column(db.Float, nullable=False)
    process_temperature = db.Column(db.Float, nullable=False)
    rorational_speed = db.Column(db.Float, nullable=False)
    torque = db.Column(db.Float, nullable=False)
    tool_wear = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, asset_id, type_l, type_m, air_temperature, process_temperature, rorational_speed, torque, tool_wear):
        self.asset_id = asset_id
        self.type_l = type_l
        self.type_m = type_m
        self.air_temperature = air_temperature
        self.process_temperature = process_temperature
        self.rorational_speed = rorational_speed
        self.torque = torque
        self.tool_wear = tool_wear

    def serialize(self):
        return {
            'id': self.id,
            'asset': self.asset.serialize(),
            'type_l': self.type_l,
            'type_m': self.type_m,
            'air_temperature': self.air_temperature,
            'process_temperature': self.process_temperature,
            'rorational_speed': self.rorational_speed,
            'torque': self.torque,
            'tool_wear': self.tool_wear,
            'prediction': self.prediction,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
class OrderHistory(db.Model):
    __tablename__ = 'order_history'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    order = db.relationship('Order', back_populates='history')
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, order_id, description):
        self.order_id = order_id
        self.description = description

    def serialize(self):
        return {
            'id': self.id,
            'order': self.order.serialize(),
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }