from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': getattr(e, 'description', 'Dados inválidos')}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': getattr(e, 'description', 'Recurso não encontrado')}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Erro interno do servidor'}), 500

    @app.errorhandler(Exception)
    def handle_unhandled(e):
        app.logger.error(f"Erro inesperado: {str(e)}")
        return jsonify({'error': str(e)}), 500
