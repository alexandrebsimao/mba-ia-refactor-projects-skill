from flask import jsonify
from src.database.connection import reset_db

class AdminController:
    @staticmethod
    def reset_database():
        reset_db()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
