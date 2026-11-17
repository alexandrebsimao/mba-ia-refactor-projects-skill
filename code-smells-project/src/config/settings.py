import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-dev-secret-key-32chars")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "loja.db")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

config = Config()
