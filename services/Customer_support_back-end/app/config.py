import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email'
    MAIL_PASSWORD = 'your_password'

