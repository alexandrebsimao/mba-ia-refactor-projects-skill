from flask import jsonify
from src.models.relatorio_model import RelatorioModel

class HealthController:
    @staticmethod
    def health_check():
        counts = RelatorioModel.get_database_counts()
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": "1.0.0",
            "ambiente": "producao"
        }), 200
