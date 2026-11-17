# Playbook de Refatoração (Padrões de Transformação com Código Antes/Depois)

Este playbook fornece padrões concretos de transformação para as correções aplicadas na **Fase 3 (Refatoração)** da Skill `refactor-arch`. Cada padrão contém exemplos práticos de código **Antes** e **Depois** em Python e Node.js.

---

## Padrão 1: Eliminação de SQL Injection com Consultas Parametrizadas

### Antes (Python / Flask)
```python
# VULNERÁVEL: Concatenação direta de strings
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("UPDATE usuarios SET nome = '" + nome + "' WHERE id = " + str(id))
```

### Depois (Python / Flask)
```python
# SEGURO: Placeholders com tupla de parâmetros
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (nome, id))
```

---

## Padrão 2: Extração de Credenciais Hardcoded para Módulo de Configuração

### Antes (Node.js)
```javascript
// INSEGURO: Segredos expostos no código
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    port: 3000
};
```

### Depois (Node.js)
```javascript
// SEGURO: Carregamento a partir de variáveis de ambiente com fallback
require('dotenv').config();

const config = {
    dbPass: process.env.DB_PASS || "dev_secret_fallback",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_fallback",
    port: parseInt(process.env.PORT, 10) || 3000
};

module.exports = config;
```

---

## Padrão 3: Decomposição de God Class / God Module para MVC

### Antes (Node.js - Frankenstein Class)
```javascript
class AppManager {
    initDb() { /* DDL e seeds */ }
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            // Lógica de banco, validação, gateway e resposta tudo junto
        });
    }
}
```

### Depois (Node.js - MVC Modular)
```javascript
// models/courseModel.js (Model cuida de dados)
const db = require('../database/connection');
exports.findById = (id) => db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);

// controllers/checkoutController.js (Controller cuida de orquestração)
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');

exports.processCheckout = async (req, res, next) => {
    try {
        const { usr, eml, pwd, c_id, card } = req.body;
        const course = await courseModel.findById(c_id);
        if (!course) return res.status(404).send("Curso não encontrado");
        // Orquestra matrícula e pagamento...
        return res.status(200).json({ msg: "Sucesso", enrollment_id: enrId });
    } catch (err) {
        next(err);
    }
};

// routes/checkoutRoutes.js (Routes / Views cuida do mapeamento HTTP)
const express = require('express');
const router = express.Router();
const checkoutController = require('../controllers/checkoutController');

router.post('/checkout', checkoutController.processCheckout);
module.exports = router;
```

---

## Padrão 4: Transformação de Callback Hell ("Pyramid of Doom") para Async/Await

### Antes (Node.js)
```javascript
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    if (err) return res.status(500).send("Erro DB");
    db.get("SELECT id FROM users WHERE email = ?", [email], (err, user) => {
        if (err) return res.status(500).send("Erro DB");
        db.run("INSERT INTO enrollments...", [user.id, cid], function(err) {
            if (err) return res.status(500).send("Erro Matrícula");
            // Mais callbacks aninhados...
        });
    });
});
```

### Depois (Node.js)
```javascript
// Utilizando Promises / util.promisify ou wrapper assíncrono
try {
    const course = await db.getAsync("SELECT * FROM courses WHERE id = ?", [cid]);
    if (!course) return res.status(404).send("Curso não encontrado");

    let user = await db.getAsync("SELECT id FROM users WHERE email = ?", [email]);
    if (!user) {
        const hash = hashPassword(pwd);
        const result = await db.runAsync("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [u, email, hash]);
        user = { id: result.lastID };
    }

    const enr = await db.runAsync("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [user.id, cid]);
    res.status(200).json({ msg: "Sucesso", enrollment_id: enr.lastID });
} catch (err) {
    next(err);
}
```

---

## Padrão 5: Otimização de N+1 Queries com JOINs e Eager Loading

### Antes (Python / Flask)
```python
# N+1 Queries: 1 query para pedidos + N queries para itens + N*M queries para produtos
pedidos = cursor.execute("SELECT * FROM pedidos").fetchall()
for p in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(p["id"]))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

### Depois (Python / Flask)
```python
# Otimizado com JOIN em uma ou duas queries consolidadas
query = """
    SELECT p.id as pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
           i.id as item_id, i.produto_id, i.quantidade, i.preco_unitario,
           pr.nome as produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    ORDER BY p.id
"""
rows = db.execute(query).fetchall()
# Agrupamento eficiente em memória sem novas idas ao banco
```

---

## Padrão 6: Correção de Criptografia Insegura e Senhas em Plaintext

### Antes (Python / Node.js)
```python
# INSEGURO: MD5 sem salt ou armazenamento em plaintext
import hashlib
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

### Depois (Python / Werkzeug Security)
```python
# SEGURO: PBKDF2 / SHA256 com salting automático padrão do Werkzeug/Flask
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    # Compatibilidade retroativa para senhas legadas em MD5 durante a transição
    if self.password == hashlib.md5(pwd.encode()).hexdigest():
        return True
    return check_password_hash(self.password, pwd)
```

---

## Padrão 7: Substituição de APIs Deprecated (Obsoletas)

### 7.1 Python `datetime.utcnow()` (Deprecated no Python 3.12+)
```python
# ANTES:
from datetime import datetime
created_at = datetime.utcnow()

# DEPOIS:
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

### 7.2 Flask-SQLAlchemy `Model.query.get(id)` (Deprecated no SQLAlchemy 2.0+)
```python
# ANTES:
user = User.query.get(user_id)

# DEPOIS:
user = db.session.get(User, user_id)
```

---

## Padrão 8: Centralização de Tratamento de Erros e Eliminação de Bare Excepts

### Antes (Python / Flask)
```python
# Erros engolidos e blocos duplicados em toda rota
try:
    # lógica...
except:
    return jsonify({'error': 'Erro interno'}), 500
```

### Depois (Python / Flask com Middleware Centralizado)
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Erro inesperado: {str(e)}")
        return jsonify({"erro": str(e), "sucesso": False}), 500
```

---

## Padrão 9: Proteção de Integridade Referencial e Prevenção de Registros Órfãos

### Antes (Node.js)
```javascript
// Deleta usuário sem limpar tabelas dependentes
db.run("DELETE FROM users WHERE id = ?", [id]);
```

### Depois (Node.js)
```javascript
// Deleção em cascata transacional garantindo integridade
await db.runAsync("BEGIN TRANSACTION");
try {
    await db.runAsync("DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [id]);
    await db.runAsync("DELETE FROM enrollments WHERE user_id = ?", [id]);
    await db.runAsync("DELETE FROM users WHERE id = ?", [id]);
    await db.runAsync("COMMIT");
} catch (err) {
    await db.runAsync("ROLLBACK");
    throw err;
}
```
