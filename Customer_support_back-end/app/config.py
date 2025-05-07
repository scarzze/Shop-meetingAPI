class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://support_service_user:lInOw7ByXdFPAN2w8DBSokS4nlH45shN@dpg-d0crhmemcj7s73asmdb0-a.oregon-postgres.render.com/support_service' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    JWT_SECRET_KEY = 'jwt_secret_key'
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email'
    MAIL_PASSWORD = 'your_password'

