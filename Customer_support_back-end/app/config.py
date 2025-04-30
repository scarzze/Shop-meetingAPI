class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://BL4CK:Oversea838@localhost/customer_support' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    JWT_SECRET_KEY = 'jwt_secret_key'
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email'
    MAIL_PASSWORD = 'your_password'

