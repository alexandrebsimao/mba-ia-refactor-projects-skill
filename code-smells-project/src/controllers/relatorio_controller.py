from flask import jsonify
from src.services.relatorio_service import RelatorioService


class RelatorioController:
    @staticmethod
    def relatorio_vendas():
        relatorio = RelatorioService.gerar_relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
