# Guia de Análise de Projeto (Heurísticas de Detecção)

Este guia define as heurísticas para a **Fase 1 (Project Analysis)** da Skill `refactor-arch`. O objetivo é mapear automaticamente a tecnologia, ecossistema, domínio de negócio e arquitetura de qualquer codebase antes de iniciar a auditoria e a refatoração.

---

## 1. Heurísticas de Detecção de Linguagem e Framework

A detecção deve inspecionar arquivos de manifesto, dependências e extensões de código na raiz do projeto:

| Arquivo de Manifesto | Padrões de Conteúdo / Dependências | Linguagem Detectada | Framework Detectado |
|---|---|---|---|
| `requirements.txt` / `pyproject.toml` / `Pipfile` | `flask` / `Flask` | Python | Flask |
| `requirements.txt` / `pyproject.toml` / `Pipfile` | `fastapi` | Python | FastAPI |
| `requirements.txt` / `pyproject.toml` / `Pipfile` | `django` | Python | Django |
| `package.json` | `"express"` em `dependencies` | JavaScript / Node.js | Express |
| `package.json` | `"@nestjs/core"` em `dependencies` | TypeScript / Node.js | NestJS |
| `package.json` | `"koa"` em `dependencies` | JavaScript / Node.js | Koa |
| `go.mod` | `github.com/gin-gonic/gin` | Go | Gin |
| `pom.xml` / `build.gradle` | `spring-boot` | Java | Spring Boot |
| `Gemfile` | `rails` / `sinatra` | Ruby | Rails / Sinatra |

---

## 2. Heurísticas de Detecção de Banco de Dados e Persistência

1. **SQLite (Arquivo / Memória)**:
   - Python: `import sqlite3`, `sqlite3.connect('loja.db')`, `sqlite:///:memory:`, arquivos `*.db`, `*.sqlite`.
   - Node.js: `require('sqlite3')`, `new sqlite3.Database(':memory:')` ou caminho para arquivo SQLite.
2. **PostgreSQL / MySQL / SQLite com ORM**:
   - Python: `flask_sqlalchemy`, `SQLAlchemy`, `peewee`, `tortoise-orm`.
   - Node.js: `sequelize`, `typeorm`, `prisma`, `knex`, `mongoose`.
3. **Mapeamento de Tabelas / Entidades**:
   - Procurar instruções `CREATE TABLE` em SQL puro ou classes herdando de `db.Model` / `BaseEntity`.
   - Listar todas as entidades/tabelas encontradas (ex: `produtos`, `usuarios`, `pedidos`, `itens_pedido`, `courses`, `enrollments`, `tasks`).

---

## 3. Heurísticas de Mapeamento de Arquitetura Atual

A arquitetura deve ser classificada com base na disposição dos arquivos e no acoplamento das responsabilidades:

1. **Monolito Desestruturado / Procedural em Raiz**:
   - Todo o código reside na raiz sem pastas de camadas (`models/`, `controllers/`, `views/`, `src/`).
   - Arquivos genéricos como `app.py`, `models.py`, `controllers.py`, `database.py` contendo SQL puro, regras de negócio e rotas misturadas.
2. **Frankenstein Monolithic Class**:
   - Uma ou poucas classes gigantes (ex: `AppManager.js`, `Server.js`) instanciam conexão com banco, definem tabelas, criam rotas HTTP e executam queries diretamente em callbacks aninhados.
3. **Arquitetura Parcialmente Organizada ("Fat Routes" / Falta de Controllers)**:
   - Pastas como `models/`, `routes/`, `services/` já existem, mas as rotas (`routes/*.py` ou `routes/*.js`) contêm toda a lógica de negócio, orquestração de transações e tratamento de erros, deixando as rotas inchadas e sem camada controladora explícita.

---

## 4. Heurísticas de Mapeamento de Domínio e Contratos de API

Para garantir que a refatoração mantenha 100% de retrocompatibilidade:

1. **Varredura de Rotas e Endpoints**:
   - Flask: `app.route(...)`, `app.add_url_rule(...)`, `Blueprint.route(...)`.
   - Express: `app.get(...)`, `app.post(...)`, `app.put(...)`, `app.delete(...)`, `router.get(...)`.
2. **Mapeamento do Domínio**:
   - Analisar substantivos nas rotas e tabelas:
     - E-commerce / Vendas: `/produtos`, `/pedidos`, `/usuarios`, `/checkout`, `/carrinho`.
     - LMS / Cursos: `/courses`, `/enrollments`, `/checkout`, `/students`.
     - Gerenciador de Tarefas: `/tasks`, `/categories`, `/users`, `/reports`.
3. **Contratos e Respostas HTTP**:
   - Mapear formato das respostas (ex: `{ dados: [...], sucesso: true }` vs `{ msg: "Sucesso" }` vs status codes 200, 201, 400, 404, 500).
   - **Regra de Ouro**: A refatoração MVC NÃO pode alterar nomes de endpoints, métodos HTTP, nem as chaves JSON esperadas pelos clientes.

---

## 5. Formato de Saída Obrigatório da Fase 1

O sumário no terminal/log deve seguir rigorosamente a seguinte estrutura:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Linguagem detectada>
Framework:     <Framework e versão>
Dependencies:  <Principais dependências>
Domain:        <Domínio detectado da aplicação>
Architecture:  <Classificação da arquitetura atual>
Source files:  <Quantidade de arquivos analisados>
DB tables:     <Tabelas ou modelos detectados>
================================
```
