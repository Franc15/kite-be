# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:franc123@localhost/supplychain_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'supersecretjwtkey'
    WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI') or 'http://127.0.0.1:7545'
    JWT_ACCESS_TOKEN_EXPIRES = False

    CONTRACT_ADDRESS = '0x7433C3f6b7672EDA710991b842d64f0a5e85A2ea'
