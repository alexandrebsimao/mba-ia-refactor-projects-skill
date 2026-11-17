from flask import Flask
from flask_cors import CORS
from src.config.settings import config
from src.database.connection import init_db, close_db_connection
from src.middlewares.error_handler import register_error_handlers
from src.routes.produto_routes import produto_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.pedido_routes import pedido_bp
from src.routes.relatorio_routes import relatorio_bp
from src.routes.health_routes import health_bp
from src.routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    CORS(app)

    # Inicializa banco
    init_db()

    # Registra teardown de conexão de banco
    app.teardown_appcontext(close_db_connection)

    # Registra error handlers centrais
    register_error_handlers(app)

    # Registra Blueprints das rotas
    app.register_blueprint(health_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(admin_bp)

    return app
