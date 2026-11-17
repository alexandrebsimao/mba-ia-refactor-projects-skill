from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": getattr(e, "description", "Requisição inválida"), "sucesso": False}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": getattr(e, "description", "Recurso não encontrado"), "sucesso": False}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error(f"Exceção não tratada: {str(e)}")
        return jsonify({"erro": str(e), "sucesso": False}), 500
