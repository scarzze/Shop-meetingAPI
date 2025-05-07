# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://support_service_user:lInOw7ByXdFPAN2w8DBSokS4nlH45shN@dpg-d0crhmemcj7s73asmdb0-a.oregon-postgres.render.com/support_service')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '31a0c532e236e4af9fd9629f827a85458bef6cfc537a127d5e3f01283cd72fd7')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    SUPPORT_EMAIL = 'saluhagi@gmail.com'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
