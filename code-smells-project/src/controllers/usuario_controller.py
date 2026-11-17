from flask import request, jsonify
from src.models.usuario_model import UsuarioModel

class UsuarioController:
    @staticmethod
    def listar_usuarios():
        usuarios = UsuarioModel.get_all()
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    @staticmethod
    def buscar_usuario(usuario_id):
        usuario = UsuarioModel.get_by_id(usuario_id)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True}), 200
        return jsonify({"erro": "Usuário não encontrado"}), 404

    @staticmethod
    def criar_usuario():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        nome = str(dados.get("nome", "")).strip()
        email = str(dados.get("email", "")).strip()
        senha = str(dados.get("senha", "")).strip()
        tipo = dados.get("tipo", "cliente")

        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

        novo_id = UsuarioModel.create(nome, email, senha, tipo)
        return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201

    @staticmethod
    def login():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        email = str(dados.get("email", "")).strip()
        senha = str(dados.get("senha", "")).strip()

        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        usuario = UsuarioModel.authenticate(email, senha)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
