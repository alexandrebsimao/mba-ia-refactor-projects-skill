# Playbook de Refatoração (Padrões de Transformação Antes / Depois)

Este playbook fornece **11 padrões concretos de transformação** com exemplos de código **Antes** e **Depois** aplicáveis à **Fase 3** da Skill `refactor-arch` em múltiplas stacks (Python, Node.js e conceitos portáveis para outras linguagens).

---

## Padrão 1: Eliminação de SQL Injection com Queries Parametrizadas

### Antes (Vulnerável — Concatenação de Strings)
```python
cursor.execute("SELECT * FROM items WHERE id = " + str(item_id))
cursor.execute("UPDATE items SET name = '" + name + "' WHERE id = " + str(item_id))
```

### Depois (Seguro — Placeholders Parametrizados)
```python
cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
cursor.execute("UPDATE items SET name = ? WHERE id = ?", (name, item_id))
```

---

## Padrão 2: Extração de Credenciais Hardcoded para Módulo de Configuração

### Antes (Inseguro — Segredos Fixos no Código)
```javascript
const config = {
    secretKey: "hardcoded-prod-secret",
    gatewayApiKey: "pk_live_example_key",
    port: 3000
};
```

### Depois (Seguro — Variáveis de Ambiente Nativas sem Dependências Extras)
```javascript
// src/config/index.js
// Lê diretamente de process.env (ou usa dotenv apenas se já estiver no package.json)
const config = {
    secretKey: process.env.SECRET_KEY || "dev-fallback-secret-change-me",
    gatewayApiKey: process.env.GATEWAY_API_KEY || "pk_test_fallback",
    port: parseInt(process.env.PORT, 10) || 3000
};

module.exports = config;
```

---

## Padrão 3: Decomposição de God Class / God Module em Camadas MVC

### Antes (Monolito acoplando DB, Regras e Rotas)
```javascript
class MonolithManager {
    initDb() { /* DDL + seeds */ }
    registerRoutes(app) {
        app.post('/orders', (req, res) => {
            // Validação, query SQL, regra de negócio e resposta no mesmo método
        });
    }
}
```

### Depois (MVC Modular — Model, Controller e Route)
```javascript
// models/orderModel.js
const db = require('../database/connection');
exports.create = (userId, total) =>
    db.run("INSERT INTO orders (user_id, total) VALUES (?, ?)", [userId, total]);

// controllers/orderController.js
const orderModel = require('../models/orderModel');
exports.createOrder = async (req, res, next) => {
    try {
        const { userId, total } = req.body;
        if (!userId || total <= 0) return res.status(400).json({ error: "Invalid payload" });
        const result = await orderModel.create(userId, total);
        return res.status(201).json({ id: result.lastID });
    } catch (err) {
        next(err);
    }
};

// routes/orderRoutes.js
const router = require('express').Router();
const orderController = require('../controllers/orderController');
router.post('/orders', orderController.createOrder);
module.exports = router;
```

---

## Padrão 4: Extração de "Fat Routes" para Camada Controller

### Antes (Rota Inchada com Transação e Regras de Negócio)
```python
@bp.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data or len(data.get('title', '')) < 3:
        return jsonify({'error': 'Invalid title'}), 400
    item = Item(title=data['title'].strip())
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201
```

### Depois (Rota Enxuta + Controller Dedicado)
```python
# controllers/item_controller.py
class ItemController:
    @staticmethod
    def create_item():
        data = request.get_json()
        title = (data or {}).get('title', '').strip()
        if len(title) < 3:
            return jsonify({'error': 'Invalid title'}), 400
        item = Item(title=title)
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201

# routes/item_routes.py
item_bp = Blueprint('items', __name__)
item_bp.route('/items', methods=['POST'])(ItemController.create_item)
```

---

## Padrão 5: Callback Hell para Async/Await com Promises

### Antes (Pyramid of Doom)
```javascript
db.get("SELECT * FROM items WHERE id = ?", [id], (err, item) => {
    if (err) return res.status(500).send("DB Error");
    db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
        if (err) return res.status(500).send("DB Error");
        db.run("INSERT INTO orders (user_id, item_id) VALUES (?, ?)", [user.id, item.id], function(err) {
            if (err) return res.status(500).send("Insert Error");
            return res.status(200).json({ orderId: this.lastID });
        });
    });
});
```

### Depois (Wrapper de Promises + Fluxo Linear Async/Await)
```javascript
try {
    const item = await db.get("SELECT * FROM items WHERE id = ?", [id]);
    if (!item) return res.status(404).json({ error: "Item not found" });

    const user = await db.get("SELECT * FROM users WHERE email = ?", [email]);
    const order = await db.run("INSERT INTO orders (user_id, item_id) VALUES (?, ?)", [user.id, item.id]);
    return res.status(200).json({ orderId: order.lastID });
} catch (err) {
    next(err);
}
```

---

## Padrão 6: Eliminação de N+1 Queries (SQL JOIN e ORM Eager Loading)

### Antes (Query Executada Dentro de Loop)
```python
# SQL puro (N+1)
orders = cursor.execute("SELECT * FROM orders").fetchall()
for order in orders:
    items = cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()

# ORM (N+1 por lazy loading)
records = Record.query.all()
for r in records:
    owner = User.query.get(r.user_id)
    count = len(r.children)  # dispara SELECT por iteração se lazy='select'
```

### Depois (SQL JOIN e ORM Eager Loading)
```python
# SQL puro (1 consulta consolidada com JOIN)
rows = cursor.execute("""
    SELECT o.id AS order_id, o.total, i.product_id, i.quantity
    FROM orders o
    LEFT JOIN order_items i ON i.order_id = o.id
""").fetchall()

# ORM SQLAlchemy (Eager Loading via joinedload / selectinload)
from sqlalchemy.orm import joinedload, selectinload
records = Record.query.options(joinedload(Record.owner), selectinload(Record.children)).all()
```

---

## Padrão 7: Substituição de Criptografia Fraca e Remoção de Vazamento de Senhas

### Antes (MD5 / Plaintext e Senha Exposta em Serialização)
```python
def set_password(self, raw):
    self.password = hashlib.md5(raw.encode()).hexdigest()

def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password}
```

### Depois (Hash Forte com Salt e Serialização Sanitizada)
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, raw):
    self.password = generate_password_hash(raw)

def check_password(self, raw):
    return check_password_hash(self.password, raw)

def to_dict(self):
    return {"id": self.id, "email": self.email}  # nunca incluir password
```

---

## Padrão 8: Atualização de APIs Deprecated (Multi-Stack)

### Python 3.12+ e SQLAlchemy 2.0+
```python
# ANTES (Deprecated)
from datetime import datetime
now = datetime.utcnow()
entity = Entity.query.get(entity_id)

# DEPOIS (Moderno)
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
entity = db.session.get(Entity, entity_id)
```

### Node.js / Express
```javascript
// ANTES (Deprecated)
const buf = new Buffer(rawString);
const parsed = url.parse(req.url);
res.send(400, "Bad Request");

// DEPOIS (Moderno)
const buf = Buffer.from(rawString);
const parsed = new URL(req.url, "http://localhost");
res.status(400).send("Bad Request");
```

---

## Padrão 9: Tratamento Centralizado de Erros (Fim de Bare Excepts)

### Antes (Bare Excepts e Blocos Duplicados)
```python
try:
    return jsonify(service.fetch()), 200
except:
    return jsonify({"error": "Internal error"}), 500
```

### Depois (Middleware / Error Handler Global)
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(Exception)
    def handle_exception(err):
        app.logger.error(f"Unhandled error: {err}")
        return jsonify({"error": "Internal server error"}), 500
```

---

## Padrão 10: Integridade Referencial Transacional (Prevenção de Registros Órfãos)

### Antes (Deleção Parcial Deixando Órfãos)
```javascript
await db.run("DELETE FROM users WHERE id = ?", [userId]);
```

### Depois (Deleção em Cascata Dentro de Transação)
```javascript
await db.run("BEGIN TRANSACTION");
try {
    await db.run("DELETE FROM child_payments WHERE parent_id IN (SELECT id FROM parent_records WHERE user_id = ?)", [userId]);
    await db.run("DELETE FROM parent_records WHERE user_id = ?", [userId]);
    await db.run("DELETE FROM users WHERE id = ?", [userId]);
    await db.run("COMMIT");
} catch (err) {
    await db.run("ROLLBACK");
    throw err;
}
```

---

## Padrão 11: Extração de Lógica de Negócio Procedural da Camada de Dados (Model → Service + Controller)

### Antes (Model Misturando SQL e Regras de Negócio)
```python
# models/report_model.py (ANTI-PATTERN: SQL + regra de desconto no mesmo método)
class ReportModel:
    DISCOUNT_TIERS = [(10000.0, 0.10), (5000.0, 0.05), (1000.0, 0.02)]

    @staticmethod
    def get_sales_report():
        row = db.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders").fetchone()
        total_orders, gross_revenue = row[0], float(row[1])
        discount = 0.0
        for threshold, rate in ReportModel.DISCOUNT_TIERS:
            if gross_revenue > threshold:
                discount = gross_revenue * rate
                break
        return {"gross": gross_revenue, "discount": discount, "net": gross_revenue - discount}
```

### Depois (Model Somente Dados + Service com Regra de Negócio + Controller Orquestrador)
```python
# models/report_model.py (Apenas persistência / SQL agregado)
class ReportModel:
    @staticmethod
    def get_sales_metrics():
        row = db.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM orders").fetchone()
        return {"total_orders": row[0] or 0, "gross_revenue": float(row[1] or 0.0)}

# services/report_service.py (Regra de negócio pura e testável em isolamento)
class ReportService:
    DISCOUNT_TIERS = [(10000.0, 0.10), (5000.0, 0.05), (1000.0, 0.02)]

    @staticmethod
    def calculate_discount(gross_revenue):
        for threshold, rate in ReportService.DISCOUNT_TIERS:
            if gross_revenue > threshold:
                return gross_revenue * rate
        return 0.0

    @staticmethod
    def generate_sales_report():
        metrics = ReportModel.get_sales_metrics()
        gross = metrics["gross_revenue"]
        discount = ReportService.calculate_discount(gross)
        return {
            "total_orders": metrics["total_orders"],
            "gross": round(gross, 2),
            "discount": round(discount, 2),
            "net": round(gross - discount, 2),
        }

# controllers/report_controller.py (Orquestração HTTP)
class ReportController:
    @staticmethod
    def sales_report():
        report = ReportService.generate_sales_report()
        return jsonify({"data": report, "success": True}), 200
```
