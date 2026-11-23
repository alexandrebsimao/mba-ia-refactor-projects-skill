from src.database.connection import get_db_connection


class RelatorioModel:
    @staticmethod
    def get_vendas_metrics():
        """Retorna métricas brutas agregadas da tabela de pedidos em uma única consulta SQL."""
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_pedidos,
                COALESCE(SUM(total), 0.0) AS faturamento_bruto,
                COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pedidos_pendentes,
                COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS pedidos_aprovados,
                COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS pedidos_cancelados
            FROM pedidos
        """)
        row = cursor.fetchone()

        return {
            "total_pedidos": int(row["total_pedidos"] or 0),
            "faturamento_bruto": float(row["faturamento_bruto"] or 0.0),
            "pedidos_pendentes": int(row["pedidos_pendentes"] or 0),
            "pedidos_aprovados": int(row["pedidos_aprovados"] or 0),
            "pedidos_cancelados": int(row["pedidos_cancelados"] or 0),
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
            "pedidos": pedidos,
        }
