from flask import request, jsonify
from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel

class PedidoController:
    STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

    @staticmethod
    def criar_pedido():
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])

        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens or len(itens) == 0:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

        total = 0.0
        itens_processados = []

        for item in itens:
            pid = item.get("produto_id")
            qtd = item.get("quantidade", 0)

            produto = ProdutoModel.get_by_id(pid)
            if not produto:
                return jsonify({"erro": f"Produto {pid} não encontrado", "sucesso": False}), 400
            if produto["estoque"] < qtd:
                return jsonify({"erro": f"Estoque insuficiente para {produto['nome']}", "sucesso": False}), 400

            preco_unitario = float(produto["preco"])
            total += preco_unitario * qtd
            itens_processados.append({
                "produto_id": pid,
                "quantidade": qtd,
                "preco_unitario": preco_unitario
            })

        pedido_id = PedidoModel.create(usuario_id, itens_processados, total)

        # Decrementa o estoque
        for item in itens_processados:
            ProdutoModel.decrement_stock(item["produto_id"], item["quantidade"])

        return jsonify({
            "dados": {"pedido_id": pedido_id, "total": round(total, 2)},
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso"
        }), 201

    @staticmethod
    def listar_pedidos_usuario(usuario_id):
        pedidos = PedidoModel.get_by_usuario(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    @staticmethod
    def listar_todos_pedidos():
        pedidos = PedidoModel.get_all()
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    @staticmethod
    def atualizar_status_pedido(pedido_id):
        dados = request.get_json()
        novo_status = dados.get("status", "") if dados else ""

        if novo_status not in PedidoController.STATUS_VALIDOS:
            return jsonify({"erro": "Status inválido"}), 400

        PedidoModel.update_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
