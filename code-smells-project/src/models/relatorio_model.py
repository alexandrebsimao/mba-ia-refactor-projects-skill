from src.database.connection import get_db_connection

class RelatorioModel:
    DISCOUNT_TIERS = [
        (10000.0, 0.10),
        (5000.0, 0.05),
        (1000.0, 0.02)
    ]

    @staticmethod
    def get_vendas_data():
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento_val = cursor.fetchone()[0]
        faturamento = float(faturamento_val) if faturamento_val is not None else 0.0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0] or 0

        desconto = 0.0
        for threshold, rate in RelatorioModel.DISCOUNT_TIERS:
            if faturamento > threshold:
                desconto = faturamento * rate
                break

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0.0
        }

    @staticmethod
    def get_database_counts():
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0] or 0
        return {
            "produtos": produtos,
            "usuarios": usuarios,
            "pedidos": pedidos
        }
