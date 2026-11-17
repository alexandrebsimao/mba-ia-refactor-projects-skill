from flask import jsonify
from src.models.relatorio_model import RelatorioModel

class RelatorioController:
    @staticmethod
    def relatorio_vendas():
        relatorio = RelatorioModel.get_vendas_data()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
