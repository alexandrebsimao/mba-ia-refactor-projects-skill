from src.models.relatorio_model import RelatorioModel


class RelatorioService:
    DISCOUNT_TIERS = [
        (10000.0, 0.10),
        (5000.0, 0.05),
        (1000.0, 0.02),
    ]

    @staticmethod
    def calcular_desconto(faturamento_bruto):
        """Aplica a regra de negócio de desconto progressivo por faixa de faturamento."""
        for threshold, rate in RelatorioService.DISCOUNT_TIERS:
            if faturamento_bruto > threshold:
                return faturamento_bruto * rate
        return 0.0

    @staticmethod
    def calcular_ticket_medio(faturamento_bruto, total_pedidos):
        if total_pedidos <= 0:
            return 0.0
        return faturamento_bruto / total_pedidos

    @staticmethod
    def gerar_relatorio_vendas():
        """Consolida métricas de banco com regras de negócio de desconto e ticket médio."""
        metrics = RelatorioModel.get_vendas_metrics()
        total_pedidos = metrics["total_pedidos"]
        faturamento_bruto = metrics["faturamento_bruto"]

        desconto = RelatorioService.calcular_desconto(faturamento_bruto)
        faturamento_liquido = faturamento_bruto - desconto
        ticket_medio = RelatorioService.calcular_ticket_medio(faturamento_bruto, total_pedidos)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento_bruto, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento_liquido, 2),
            "pedidos_pendentes": metrics["pedidos_pendentes"],
            "pedidos_aprovados": metrics["pedidos_aprovados"],
            "pedidos_cancelados": metrics["pedidos_cancelados"],
            "ticket_medio": round(ticket_medio, 2),
        }
