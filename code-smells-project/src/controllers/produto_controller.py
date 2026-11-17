from flask import request, jsonify
from src.models.produto_model import ProdutoModel

class ProdutoController:
    CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

    @staticmethod
    def listar_produtos():
        produtos = ProdutoModel.get_all()
        return jsonify({"dados": produtos, "sucesso": True}), 200

    @staticmethod
    def buscar_produto(produto_id):
        produto = ProdutoModel.get_by_id(produto_id)
        if produto:
            return jsonify({"dados": produto, "sucesso": True}), 200
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404

    @staticmethod
    def criar_produto():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        for campo in ["nome", "preco", "estoque"]:
            if campo not in dados:
                return jsonify({"erro": f"{campo.capitalize()} é obrigatório"}), 400

        nome = str(dados["nome"]).strip()
        descricao = dados.get("descricao", "")
        preco = float(dados["preco"])
        estoque = int(dados["estoque"])
        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return jsonify({"erro": "Preço não pode ser negativo"}), 400
        if estoque < 0:
            return jsonify({"erro": "Estoque não pode ser negativo"}), 400
        if len(nome) < 2:
            return jsonify({"erro": "Nome muito curto"}), 400
        if len(nome) > 200:
            return jsonify({"erro": "Nome muito longo"}), 400
        if categoria not in ProdutoController.CATEGORIAS_VALIDAS:
            return jsonify({"erro": f"Categoria inválida. Válidas: {ProdutoController.CATEGORIAS_VALIDAS}"}), 400

        novo_id = ProdutoModel.create(nome, descricao, preco, estoque, categoria)
        return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    @staticmethod
    def atualizar_produto(produto_id):
        produto_existente = ProdutoModel.get_by_id(produto_id)
        if not produto_existente:
            return jsonify({"erro": "Produto não encontrado"}), 404

        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        for campo in ["nome", "preco", "estoque"]:
            if campo not in dados:
                return jsonify({"erro": f"{campo.capitalize()} é obrigatório"}), 400

        nome = str(dados["nome"]).strip()
        descricao = dados.get("descricao", "")
        preco = float(dados["preco"])
        estoque = int(dados["estoque"])
        categoria = dados.get("categoria", "geral")

        if preco < 0:
            return jsonify({"erro": "Preço não pode ser negativo"}), 400
        if estoque < 0:
            return jsonify({"erro": "Estoque não pode ser negativo"}), 400

        ProdutoModel.update(produto_id, nome, descricao, preco, estoque, categoria)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    @staticmethod
    def deletar_produto(produto_id):
        produto_existente = ProdutoModel.get_by_id(produto_id)
        if not produto_existente:
            return jsonify({"erro": "Produto não encontrado"}), 404

        ProdutoModel.delete(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

    @staticmethod
    def buscar_produtos():
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)

        if preco_min is not None:
            preco_min = float(preco_min)
        if preco_max is not None:
            preco_max = float(preco_max)

        resultados = ProdutoModel.search(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
