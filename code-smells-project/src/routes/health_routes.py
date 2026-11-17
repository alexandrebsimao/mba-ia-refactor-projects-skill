from flask import Blueprint, jsonify
from src.controllers.health_controller import HealthController

health_bp = Blueprint("health", __name__)

health_bp.add_url_rule("/health", "health_check", HealthController.health_check, methods=["GET"])

@health_bp.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health"
        }
    })
