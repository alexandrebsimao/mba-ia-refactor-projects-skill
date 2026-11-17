import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key-taskmanager-32chars')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')

    # SMTP Configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', 'taskmanager@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'dev_email_password_fallback')

config = Config()
