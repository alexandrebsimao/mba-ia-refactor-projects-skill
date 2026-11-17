from flask import jsonify
from src.database.connection import get_db_connection

class AdminController:
    @staticmethod
    def reset_database():
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
