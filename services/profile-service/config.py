import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://BL4CK:Oversea838@localhost/customer_support'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_super_secret_jwt_key'
    PRODUCT_SERVICE_URL = 'http://localhost:5001'
