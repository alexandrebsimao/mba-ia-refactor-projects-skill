# Guia de Análise de Projeto (Heurísticas de Detecção)

Este guia define as heurísticas agnósticas de tecnologia para a **Fase 1 (Project Analysis)** da Skill `refactor-arch`. O objetivo é mapear automaticamente linguagem, framework, dependências, persistência, domínio e arquitetura de qualquer codebase antes da auditoria.

---

## 1. Heurísticas de Detecção de Linguagem e Framework

Inspecione arquivos de manifesto, configuração e extensões de código-fonte (ignorando diretórios de terceiros como `node_modules/`, `.venv/`, `vendor/`, `target/`, `.git/` e `.claude/`):

| Arquivo de Manifesto / Build | Padrões / Dependências | Linguagem | Framework |
|---|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | `flask` / `Flask` | Python | Flask |
| `requirements.txt`, `pyproject.toml`, `Pipfile` | `fastapi` | Python | FastAPI |
| `requirements.txt`, `pyproject.toml`, `Pipfile` | `django` | Python | Django |
| `package.json` | `"express"` | JavaScript / TypeScript (Node.js) | Express |
| `package.json` | `"fastify"` | JavaScript / TypeScript (Node.js) | Fastify |
| `package.json` | `"@nestjs/core"` | TypeScript (Node.js) | NestJS |
| `package.json` | `"koa"` | JavaScript / TypeScript (Node.js) | Koa |
| `go.mod` | `github.com/gin-gonic/gin`, `labstack/echo`, `gofiber/fiber` | Go | Gin / Echo / Fiber |
| `pom.xml`, `build.gradle` | `spring-boot-starter-web` | Java / Kotlin | Spring Boot |
| `Gemfile` | `rails`, `sinatra` | Ruby | Rails / Sinatra |
| `composer.json` | `laravel/framework` | PHP | Laravel |
| `*.csproj` | `Microsoft.AspNetCore` | C# | ASP.NET Core |

> **Dica**: Sempre capture a versão exata declarada no manifesto (ex: `Flask 3.1.1`, `Express 4.18.2`) e liste as principais dependências diretas.

---

## 2. Heurísticas de Detecção de Banco de Dados e Persistência

1. **Drivers Nativos / SQL Direto**:
   - **SQLite**: `sqlite3` (Python/Node), arquivos `*.db`/`*.sqlite`, conexão `:memory:`.
   - **PostgreSQL / MySQL**: `psycopg2`, `asyncpg`, `pg`, `mysql2`, `pymysql`, `database/sql`.
   - **NoSQL**: `pymongo`, `mongodb`, `redis`, `ioredis`.
2. **ORMs e Query Builders**:
   - **Python**: `SQLAlchemy`, `Flask-SQLAlchemy`, `Django ORM`, `Peewee`, `Tortoise ORM`.
   - **Node.js**: `Sequelize`, `TypeORM`, `Prisma`, `Knex`, `Mongoose`, `Drizzle`.
   - **Java / Go / Ruby**: `Hibernate/JPA`, `GORM`, `ActiveRecord`.
3. **Extração de Tabelas / Entidades**:
   - Busque comandos DDL (`CREATE TABLE [IF NOT EXISTS] <nome>`), declarações `__tablename__`, schemas/models ORM ou coleções NoSQL.

---

## 3. Heurísticas de Classificação da Arquitetura Atual

Analise a árvore de diretórios e o acoplamento interno dos arquivos para classificar a arquitetura em uma das categorias abaixo:

1. **Monolito Desestruturado / Procedural**:
   - Poucos arquivos planos na raiz ou em `src/`, sem separação clara de camadas.
   - Rotas HTTP, regras de negócio, SQL bruto e configuração convivem nos mesmos arquivos.
2. **God Class / Monolito Orientado a Classe Única**:
   - Uma classe centralizadora instancia o banco, cria tabelas, popula dados iniciais, registra rotas e concentra toda a lógica de negócio e serialização.
3. **Arquitetura Parcialmente Organizada ("Fat Routes" / Camadas Incompletas)**:
   - Já existem diretórios parciais (ex: `models/`, `routes/`, `services/`, `utils/`), porém faltam camadas essenciais do MVC (como `controllers/`, `config/`, `middlewares/`), há rotas sobrecarregadas com regras de negócio e persistência direta, ou domínios misturados em arquivos incorretos.
4. **Arquitetura em Camadas com Acoplamento / Débito Técnico**:
   - Camadas existem nominalmente, mas há violações de fronteira (ex: controllers executando SQL diretamente, models acessando objetos HTTP, estado global compartilhado).

---

## 4. Heurísticas de Mapeamento de Domínio e Contratos de API

Para garantir refatoração segura sem quebra de contrato:

1. **Varredura de Endpoints**:
   - **Flask**: `@app.route`, `app.add_url_rule`, `@<bp>.route`.
   - **FastAPI**: `@app.get/post/put/delete`, `@router.*`.
   - **Express / Koa**: `app.get/post/put/patch/delete`, `router.*`.
   - **Spring / NestJS / Gin**: `@GetMapping`, `@Get`, `r.GET`, etc.
2. **Inferência do Domínio**:
   - Analise os substantivos presentes nas rotas, nomes de tabelas/modelos e payloads JSON para descrever o domínio de negócio de forma clara e objetiva.
3. **Inventário de Contratos HTTP**:
   - Registre todos os endpoints ativos (método + path), parâmetros de rota/query, campos de entrada e formato de resposta esperada (chaves JSON, texto puro e códigos de status HTTP).
   - **Regra de Preservação**: A Fase 3 deve manter compatibilidade com todos os endpoints funcionais legítimos (exceto backdoors críticos como execução arbitrária de SQL).

---

## 5. Formato Obrigatório de Saída da Fase 1

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Linguagem detectada>
Framework:     <Framework e versão>
Dependencies:  <Principais dependências>
Domain:        <Domínio da aplicação e principais recursos>
Architecture:  <Classificação da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas ou coleções encontradas>
================================
```
