from src.database.connection import get_db_connection

class PedidoModel:
    @staticmethod
    def create(usuario_id, itens, total):
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total)
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
            )

        db.commit()
        return pedido_id

    @staticmethod
    def update_status(pedido_id, novo_status):
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_by_usuario(usuario_id):
        return PedidoModel._fetch_orders_with_items("WHERE p.usuario_id = ?", (usuario_id,))

    @staticmethod
    def get_all():
        return PedidoModel._fetch_orders_with_items()

    @staticmethod
    def _fetch_orders_with_items(where_clause="", params=()):
        """Resolve o problema N+1 consolidando pedidos e itens com JOIN em uma única consulta."""
        db = get_db_connection()
        cursor = db.cursor()

        query = f"""
            SELECT
                p.id as pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
                i.produto_id, i.quantidade, i.preco_unitario,
                COALESCE(pr.nome, 'Desconhecido') as produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = i.produto_id
            {where_clause}
            ORDER BY p.id DESC
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()

        orders_dict = {}
        for row in rows:
            pid = row["pedido_id"]
            if pid not in orders_dict:
                orders_dict[pid] = {
                    "id": pid,
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": []
                }
            if row["produto_id"] is not None:
                orders_dict[pid]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"]
                })

        return list(orders_dict.values())
