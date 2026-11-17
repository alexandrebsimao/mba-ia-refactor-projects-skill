from src.database.connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioModel:
    @staticmethod
    def get_all():
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(usuario_id):
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(nome, email, senha, tipo="cliente"):
        db = get_db_connection()
        cursor = db.cursor()
        senha_hash = generate_password_hash(senha)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def authenticate(email, senha):
        user = UsuarioModel.get_by_email(email)
        if not user:
            return None

        stored_password = user["senha"]
        is_valid = False
        # Suporta tanto hash moderno quanto legado caso exista
        if stored_password.startswith(("scrypt:", "pbkdf2:")):
            is_valid = check_password_hash(stored_password, senha)
        else:
            is_valid = (stored_password == senha)

        if is_valid:
            return {
                "id": user["id"],
                "nome": user["nome"],
                "email": user["email"],
                "tipo": user["tipo"]
            }
        return None
