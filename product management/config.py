import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://shopuser:Access@localhost:5432/shopdb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
