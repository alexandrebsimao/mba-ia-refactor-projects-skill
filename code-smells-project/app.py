import os
import sys

# Garante que o diretório atual está no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app import create_app
from src.config.settings import config

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR REFACTORADO INICIADO (PADRÃO MVC)")
    print(f"Rodando em http://{config.HOST}:{config.PORT}")
    print("=" * 50)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
