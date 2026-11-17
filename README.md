# Desafio MBA IA: Criação de Skills — Refatoração Arquitetural Automatizada

Este repositório contém a solução completa do desafio de **Criação de Skills — Refatoração Arquitetural Automatizada** do módulo de *Desenvolvimento de Software e Aplicações com IA*.

O objetivo foi projetar e implementar a Skill `refactor-arch`, uma especialização agnóstica de tecnologia capaz de **analisar**, **auditar** e **refatorar** codebases backend legadas para o padrão arquitetural **MVC (Model-View-Controller)**, eliminando vulnerabilidades de segurança, anti-patterns e code smells, mantendo 100% de compatibilidade funcional.

---

## Estrutura do Repositório

```
mba-ia-refactor-projects-skill/
├── README.md                              # Documentação completa do projeto
├── reports/                               # Relatórios padronizados de auditoria (Fase 2)
│   ├── audit-project-1.md                 # Relatório de auditoria do Projeto 1
│   ├── audit-project-2.md                 # Relatório de auditoria do Projeto 2
│   └── audit-project-3.md                 # Relatório de auditoria do Projeto 3
│
├── code-smells-project/                   # Projeto 1: Python / Flask (E-commerce API)
│   ├── .claude/skills/refactor-arch/      # Definição e referências da Skill
│   ├── src/                               # Código refatorado no padrão MVC
│   │   ├── config/settings.py
│   │   ├── database/connection.py
│   │   ├── models/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── middlewares/error_handler.py
│   │   └── app.py (factory)
│   ├── app.py (entry point)
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2: Node.js / Express (LMS Checkout API)
│   ├── .claude/skills/refactor-arch/      # Definição e referências da Skill
│   ├── src/                               # Código refatorado no padrão MVC
│   │   ├── config/index.js
│   │   ├── database/connection.js
│   │   ├── models/
│   │   ├── services/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── middlewares/errorHandler.js
│   │   └── app.js (entry point)
│   ├── api.http
│   └── package.json
│
└── task-manager-api/                      # Projeto 3: Python / Flask (Task Manager API)
    ├── .claude/skills/refactor-arch/      # Definição e referências da Skill
    ├── config/settings.py
    ├── database.py
    ├── seed.py
    ├── models/
    ├── controllers/
    ├── routes/
    ├── middlewares/error_handler.py
    ├── services/
    ├── utils/
    ├── app.py (entry point)
    └── requirements.txt
```

---

## A) Seção "Análise Manual"

Antes de automatizar a auditoria e a refatoração, foi realizada a leitura e a análise manual detalhada dos 3 projetos fornecidos. A escala de severidade adotada seguiu rigorosamente os padrões de MVC e SOLID do curso:

### Projeto 1 — `code-smells-project` (Python / Flask — E-commerce API)

| # | Problema Identificado | Arquivo e Linhas | Severidade | Justificativa de Relevância |
|---|---|---|---|---|
| 1 | **SQL Injection Generalizado** | `models.py:28, 48, 58, 109, 140, 188, 280, 291-297` | **CRITICAL** | Concatenação direta de strings em comandos SQL brutos em múltiplos métodos (`get_produto_por_id`, `login_usuario`, `buscar_produtos`, etc.). Permite extração de dados e bypass de autenticação trivial (`' OR '1'='1`). |
| 2 | **Endpoint de Execução Arbitrária de SQL (Backdoor)** | `app.py:59-78` (`/admin/query`) | **CRITICAL** | A API aceita strings SQL abertas enviadas pelo cliente HTTP e as executa diretamente no banco de dados SQLite, permitindo que qualquer um apague tabelas ou assuma o controle do banco. |
| 3 | **Credenciais Hardcoded & Exposição de Segredos** | `app.py:7`, `controllers.py:289` | **CRITICAL** | `SECRET_KEY = "minha-chave-super-secreta-123"` fixada no código. Além disso, o endpoint `/health` vaza abertamente a chave secreta e o caminho do banco de dados na resposta JSON. |
| 4 | **God Module / Violação Total de SRP** | `models.py:1-314` | **CRITICAL** | Arquivo monolítico com mais de 300 linhas misturando conexão de banco, regras de faturamento, validações de payload, queries SQL e relatórios de 4 domínios não correlatos. |
| 5 | **Senhas em Texto Claro Expostas em Endpoints** | `models.py:79-87`, `controllers.py:128-144` | **HIGH** | Senhas são gravadas sem hash e retornadas explicitamente no JSON de `/usuarios` e `/usuarios/<id>`, violando requisitos de segurança e conformidade (LGPD). |
| 6 | **Acesso Direto ao Banco na Camada de Controle** | `controllers.py:264-290` | **HIGH** | A função `health_check` manipula cursores e consultas SQL diretamente no controller, violando a separação de responsabilidades da camada MVC. |
| 7 | **Problema de Consulta N+1 nos Pedidos** | `models.py:171-201, 203-234` | **MEDIUM** | Em `get_pedidos_usuario` e `get_todos_pedidos`, para cada pedido itera-se fazendo uma nova query para itens, e para cada item outra query para o nome do produto ($1 + N + N \times M$ queries). |
| 8 | **Falta de Tratamento Centralizado de Erros** | `controllers.py:5-263` | **MEDIUM** | Blocos `try...except Exception as e:` repetidos em todas as funções, logando com `print()` e retornando formatos de erro inconsistentes. |
| 9 | **Magic Numbers em Regras de Desconto** | `models.py:257-263` | **LOW** | Faixas de faturamento (`10000`, `5000`, `1000`) e percentuais de desconto (`0.1`, `0.05`, `0.02`) fixados no meio do código procedural. |
| 10 | **Conexão SQLite Global sem Escopo de Requisição** | `database.py:4, 8-12` | **LOW** | `db_connection` global sem teardown de contexto ou controle de concorrência. |

---

### Projeto 2 — `ecommerce-api-legacy` (Node.js / Express — LMS Checkout API)

| # | Problema Identificado | Arquivo e Linhas | Severidade | Justificativa de Relevância |
|---|---|---|---|---|
| 1 | **God Class (`AppManager`) & Ausência de Camadas** | `src/AppManager.js:4-139` | **CRITICAL** | Uma única classe gerencia banco de dados em memória, esquemas DDL, seeds, registro de rotas Express, regras de checkout, simulação de gateway e cálculo de relatórios financeiros. |
| 2 | **Chaves de Produção e Senhas Hardcoded** | `src/utils.js:1-7` | **CRITICAL** | Chaves privadas ao vivo (`paymentGatewayKey: "pk_live_1234567890abcdef"`), senhas de produção (`dbPass: "senha_super_secreta_prod_123"`) e contas de email embutidas no código. |
| 3 | **Dados de Cartão de Crédito Logados em Texto Claro** | `src/AppManager.js:45` | **CRITICAL** | O número integral do cartão de crédito é impresso no console sem máscara: `console.log('Processando cartão ${cc}...')`, violando normas internacionais PCI-DSS. |
| 4 | **Criptografia Caseira Insegura (`badCrypto`)** | `src/utils.js:17-23` | **HIGH** | Algoritmo caseiro baseado em loop de 10.000 iterações recortando substrings de Base64. É trivialmente vulnerável a ataques de dicionário e quebra imediata. |
| 5 | **Callback Hell ("Pyramid of Doom")** | `src/AppManager.js:37-76, 83-127` | **HIGH** | Callbacks aninhados em 5 a 6 níveis de profundidade com repetição de código de erro e alta propensão a unhandled rejections e travamentos. |
| 6 | **Estado Global Mutável & Risco de Vazamento de Memória** | `src/utils.js:9-15` | **HIGH** | `let globalCache = {}; let totalRevenue = 0;` crescem indefinidamente sem política de despejo (eviction) ou controle de concorrência entre requisições. |
| 7 | **Gargalo N+1 e Múltiplas Queries Aninhadas** | `src/AppManager.js:83-127` | **MEDIUM** | O relatório financeiro busca cursos, depois faz queries para matrículas de cada curso, depois para usuários de cada matrícula e para pagamentos de cada matrícula. |
| 8 | **Violação de Integridade / Registros Órfãos na Deleção** | `src/AppManager.js:131-137` | **MEDIUM** | `DELETE FROM users WHERE id = ?` remove o usuário mas deixa registros órfãos nas tabelas `enrollments` e `payments`, corrompendo a integridade referencial. |
| 9 | **Nomenclatura Críptica de Variáveis** | `src/AppManager.js:29-33` | **LOW** | Parâmetros de rota desestruturados como `u`, `e`, `p`, `cid`, `cc`, prejudicando gravemente a legibilidade e manutenibilidade. |
| 10 | **Regra de Pagamento Simulada Hardcoded** | `src/AppManager.js:46` | **LOW** | Verificação de status fixada por prefixo de string `cc.startsWith("4")` dentro do handler HTTP. |

---

### Projeto 3 — `task-manager-api` (Python / Flask — Task Manager API)

| # | Problema Identificado | Arquivo e Linhas | Severidade | Justificativa de Relevância |
|---|---|---|---|---|
| 1 | **Chaves de Sessão e Credenciais SMTP Hardcoded** | `app.py:13`, `services/notification_service.py:9-10` | **CRITICAL** | `SECRET_KEY = 'super-secret-key-123'` e credenciais reais de email (`taskmanager@gmail.com` / `senha123`) embutidas diretamente no código-fonte. |
| 2 | **Criptografia Fraca (MD5) & Vazamento de Hash** | `models/user.py:21, 27-32` | **CRITICAL** | Uso de MD5 puro sem salt para hash de senhas de usuários. Além disso, `to_dict()` inclui `'password': self.password`, vazando os hashes em requisições GET públicas. |
| 3 | **Ausência de Camada Controller ("Fat Routes")** | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | **HIGH** | As rotas acumulam toda a lógica de negócio, orquestração de transações (`db.session.commit()`), filtros manuais e cálculos de `overdue` duplicados. |
| 4 | **Rotas Deslocadas de Domínio (Categorias em Relatórios)** | `routes/report_routes.py:157-223` | **HIGH** | O CRUD inteiro de categorias (`/categories`, POST, PUT, DELETE) foi colocado dentro de `report_routes.py`, violando a coesão de domínio. |
| 5 | **Uso de APIs Deprecated (Python 3.12+ e SQLAlchemy 2.0+)** | `models/user.py:14`, `routes/task_routes.py:31, 67`, `seed.py:66-74` | **MEDIUM** | Uso de `datetime.utcnow()` (depreciado no Python 3.12+) e `Model.query.get(id)` (depreciado no SQLAlchemy 2.0+ / Flask-SQLAlchemy 3.x). |
| 6 | **Consultas N+1 nas Listagens e Relatórios** | `routes/task_routes.py:41-58`, `routes/report_routes.py:53-68` | **MEDIUM** | `get_tasks` busca individualmente o usuário e categoria de cada task em um loop for; `summary_report` busca individualmente as tasks de cada usuário em loop. |
| 7 | **Bare Excepts Engolindo Erros** | `routes/task_routes.py:62, 137, 204`, `routes/user_routes.py:130, 149` | **MEDIUM** | Uso repetitivo de `except:` genérico sem logging, mascarando erros reais e dificultando o troubleshooting. |
| 8 | **Estado Volátil em Memória no Serviço de Notificação** | `services/notification_service.py:6, 31-36` | **LOW** | Notificações salvas em lista em memória do processo (`self.notifications = []`), perdendo dados após restart da aplicação. |
| 9 | **Token JWT Forjado Estático** | `routes/user_routes.py:210` | **LOW** | Rota `/login` retorna `'token': 'fake-jwt-token-' + str(user.id)` sem assinatura criptográfica nem expiração. |

---

## B) Seção "Construção da Skill"

### 1. Decisões de Design e Estrutura

A Skill `refactor-arch` foi desenhada seguindo a convenção moderna de Agent Skills, separando estritamente as **instruções de orquestração** (`SKILL.md`) do **conhecimento especializado de domínio** armazenado nos arquivos de referência em Markdown:

```
.claude/skills/refactor-arch/
├── SKILL.md                               # Prompt mestre orquestrador em 3 fases
└── references/
    ├── project-analysis.md                # Área 1: Heurísticas de detecção de tecnologia e arquitetura
    ├── anti-patterns-catalog.md           # Área 2: Catálogo de anti-patterns com sinais e severidades
    ├── audit-report-template.md           # Área 3: Template padronizado de saída do relatório
    ├── architecture-guidelines.md         # Área 4: Diretrizes arquiteturais do padrão MVC
    └── refactoring-playbook.md            # Área 5: Padrões de transformação com código antes/depois
```

- **Fase 1 (Project Analysis)**: Detecta manifestos (`requirements.txt`, `package.json`), mapeia linguagem, framework, persistência e domínio de negócio, emitindo o resumo padronizado.
- **Fase 2 (Architecture Audit)**: Analisa detalhadamente os arquivos-fonte, cruza com o catálogo de anti-patterns, localiza arquivos e linhas exatos, calcula o sumário de severidades, gera o relatório e **obrigatoriamente pausa** solicitando a confirmação do usuário (`[y/n]`).
- **Fase 3 (Refactoring & Validation)**: Executa a reestruturação física para a arquitetura MVC (Models, Views/Routes, Controllers, Config, Middlewares), elimina os code smells e inicia a aplicação para validar a integridade dos endpoints.

### 2. Catálogo de Anti-Patterns

O catálogo em `anti-patterns-catalog.md` inclui **11 anti-patterns** catalogados com critérios objetivos de detecção e classificação:
1. `[CRITICAL] SQL Injection & Execução Arbitrária de SQL` (concatenações em queries e endpoints de backdoor).
2. `[CRITICAL] Hardcoded Credentials & Sensitive Data Exposure` (segredos em código e vazamento em responses/logs).
3. `[CRITICAL] God Class / God Module` (arquivos gigantes acumulando responsabilidades divergentes).
4. `[HIGH] Fat Routes / Business Logic in Controllers` (ausência de camada controladora e rotas inchadas).
5. `[HIGH] Insecure / Broken Cryptography & Plaintext Passwords` (senhas sem hash, MD5 e algoritmos caseiros).
6. `[HIGH] Mutable Shared Global State & Memory Leaks` (variáveis de módulo manipuladas concorrentemente).
7. `[HIGH] Callback Hell / Pyramid of Doom` (aninhamento excessivo em JavaScript).
8. `[MEDIUM] N+1 Query Problem` (queries em loop sem JOINs ou eager loading).
9. `[MEDIUM] Falta de Tratamento Centralizado de Erros` (bare excepts e exceptions engolidas).
10. `[MEDIUM / LOW] Uso de APIs Deprecated` (`datetime.utcnow()` no Python 3.12+ e `Model.query.get()` no SQLAlchemy 2.0+).
11. `[LOW] Magic Numbers, Magic Strings & Nomenclatura Críptica` (falta de semântica e clareza).

### 3. Como Garantir a Natureza Agnóstica de Tecnologia

A skill alcança independência de stack ao focar nas **responsabilidades conceituais das camadas MVC**, e não em uma sintaxe específica:
- **Heurísticas flexíveis**: O arquivo `project-analysis.md` estabelece regras de detecção para Python (Flask, FastAPI, Django), Node.js (Express, NestJS), Go, Java e Ruby.
- **Camadas equivalentes**:
  - `Models`: Abstração de persistência (seja SQLite nativo, ORM SQLAlchemy, Sequelize ou Prisma).
  - `Controllers`: Funções puras de aplicação e orquestração de regras de negócio.
  - `Views / Routes`: Adaptação do protocolo HTTP (seja `add_url_rule` / Blueprints no Flask ou `express.Router` no Express).
  - `Config`: Centralização de variáveis de ambiente (`.env` via `os.getenv` ou `process.env`).
  - `Middlewares`: Interceptação global de erros (`@app.errorhandler` ou Express Error Middleware).
- **Playbook poliglota**: O arquivo `refactoring-playbook.md` fornece receitas práticas Antes/Depois tanto em Python quanto em Node.js.

### 4. Desafios Encontrados e Como Foram Resolvidos

1. **Retrocompatibilidade de Contratos HTTP**:
   - *Desafio*: A refatoração arquitetural não podia quebrar clientes legados que esperavam respostas em formatos específicos (ex: strings puras no DELETE de usuários no Projeto 2, ou status codes 404 em determinadas buscas de produtos).
   - *Solução*: Todos os controllers foram implementados respeitando 100% dos schemas de resposta originais e status codes.
2. **Ambiente com Depreciações Recentes**:
   - *Desafio*: O runtime do ambiente possui Python 3.12.4 e SQLAlchemy 3.1.1 / 2.0+, onde `datetime.utcnow()` e `Model.query.get()` geram warnings severos ou falhas.
   - *Solução*: A skill substituiu preventivamente essas chamadas por `datetime.now(timezone.utc)` e `db.session.get(Model, id)`.
3. **Criptografia Retrocompatível**:
   - *Desafio*: Usuários semeados no banco possuíam senhas legadas (ou MD5 no Projeto 3). Trocar abruptamente para PBKDF2 quebraria os logins existentes.
   - *Solução*: Os métodos de autenticação foram implementados com verificação inteligente: validam o hash moderno e, caso a senha esteja no formato legado, realizam a validação correspondente com sucesso.

---

## C) Seção "Resultados"

### 1. Resumo dos Relatórios de Auditoria (Fase 2)

| Projeto | Stack | Arquivos | Linhas | CRITICAL | HIGH | MEDIUM | LOW | Total Findings |
|---|---|---|---|---|---|---|---|---|
| **Projeto 1 (`code-smells-project`)** | Python / Flask | 4 | ~780 | 5 | 2 | 2 | 2 | **11** |
| **Projeto 2 (`ecommerce-api-legacy`)** | Node.js / Express | 3 | ~180 | 3 | 3 | 2 | 2 | **10** |
| **Projeto 3 (`task-manager-api`)** | Python / Flask | 11 | ~1150 | 2 | 2 | 3 | 2 | **9** |

Os relatórios detalhados gerados pela Fase 2 estão disponíveis em:
- [reports/audit-project-1.md](reports/audit-project-1.md)
- [reports/audit-project-2.md](reports/audit-project-2.md)
- [reports/audit-project-3.md](reports/audit-project-3.md)

---

### 2. Comparação Antes / Depois da Estrutura de Cada Projeto

#### Projeto 1 — `code-smells-project`
- **Antes (Monolito Desestruturado na Raiz)**:
  ```
  code-smells-project/
  ├── app.py             # 88 linhas: rotas + backdoor /admin/query + credenciais hardcoded
  ├── controllers.py     # 292 linhas: regras misturadas + acesso direto a banco
  ├── models.py          # 314 linhas: SQL injection + God module de 4 domínios
  ├── database.py        # 86 linhas: SQLite global sem escopo
  └── requirements.txt
  ```
- **Depois (Arquitetura MVC Modular em `src/`)**:
  ```
  code-smells-project/
  ├── app.py                        # Entry point limpo (Composition Root)
  ├── requirements.txt
  └── src/
      ├── config/settings.py        # Configurações isoladas com variáveis de ambiente
      ├── database/connection.py    # Conexão segura com inicialização e lifecycle scoping
      ├── models/
      │   ├── produto_model.py      # Queries 100% parametrizadas para produtos
      │   ├── usuario_model.py      # Hash Werkzeug PBKDF2 + proteção de senhas
      │   ├── pedido_model.py       # Resolução N+1 com JOINs consolidados
      │   └── relatorio_model.py    # Agregações financeiras e métricas de banco
      ├── controllers/
      │   ├── produto_controller.py # Validações de input e orquestração
      │   ├── usuario_controller.py # Fluxo de usuários e login seguro
      │   ├── pedido_controller.py  # Gestão transacional de pedidos e estoque
      │   ├── relatorio_controller.py
      │   ├── health_controller.py  # Health check sanitizado (sem vazar segredos)
      │   └── admin_controller.py   # Reset controlado (sem backdoor SQL)
      ├── routes/
      │   ├── produto_routes.py     # Blueprints HTTP dedicados
      │   ├── usuario_routes.py
      │   ├── pedido_routes.py
      │   ├── relatorio_routes.py
      │   ├── health_routes.py
      │   └── admin_routes.py
      ├── middlewares/
      │   └── error_handler.py      # Tratamento centralizado de exceções
      └── app.py                    # Application Factory pattern
  ```

---

#### Projeto 2 — `ecommerce-api-legacy`
- **Antes (Frankenstein Monolithic Class)**:
  ```
  ecommerce-api-legacy/src/
  ├── app.js               # Bootstrap que delega tudo ao AppManager
  ├── AppManager.js        # 141 linhas: DDL + seeds + routes + payment + callback hell
  └── utils.js             # Segredos hardcoded + crypto caseiro + cache global mutável
  ```
- **Depois (Arquitetura MVC Desacoplada)**:
  ```
  ecommerce-api-legacy/src/
  ├── app.js                     # Entry point enxuto com registro de rotas e middlewares
  ├── config/index.js            # Configuração via process.env com fallbacks seguros
  ├── database/connection.js     # Wrapper com Promises (run/get/all) para SQLite
  ├── models/
  │   ├── userModel.js           # Consultas e deleção em cascata transacional
  │   ├── courseModel.js         # Abstração de cursos ativos
  │   ├── enrollmentModel.js     # Gerenciamento de matrículas
  │   ├── paymentModel.js        # Registro de pagamentos
  │   └── auditLogModel.js       # Log de auditoria desacoplado
  ├── services/
  │   ├── paymentService.js      # Máscara PCI-DSS e simulação de gateway
  │   ├── cryptoService.js       # PBKDF2 com salt via módulo nativo 'crypto'
  │   └── cacheService.js        # Cache em memória estruturado com limite de tamanho
  ├── controllers/
  │   ├── checkoutController.js  # Async/await linear substituindo o callback hell
  │   ├── reportController.js    # Resolução N+1 com JOIN consolidado
  │   └── userController.js      # Deleção com integridade referencial
  ├── routes/
  │   ├── checkoutRoutes.js      # Mapeamento REST
  │   ├── reportRoutes.js
  │   ├── userRoutes.js
  │   └── index.js               # Router agregador
  └── middlewares/
      └── errorHandler.js        # Middleware global de erro do Express
  ```

---

#### Projeto 3 — `task-manager-api`
- **Antes (Parcialmente Organizado / Fat Routes)**:
  ```
  task-manager-api/
  ├── app.py             # Segredos hardcoded
  ├── models/            # MD5 vulnerável + vazamento de senha em to_dict() + datetime.utcnow()
  ├── routes/            # Fat routes sem controllers + bare excepts + N+1 queries
  └── services/          # Credenciais SMTP hardcoded
  ```
- **Depois (Padrão MVC Completo)**:
  ```
  task-manager-api/
  ├── app.py                     # Factory com registro limpo de Blueprints e error handler
  ├── config/settings.py         # Configuração centralizada para banco, app e SMTP
  ├── database.py                # Instância SQLAlchemy
  ├── models/
  │   ├── user.py                # Hash Werkzeug seguro + remoção de senha do to_dict()
  │   ├── task.py                # datetime.now(timezone.utc) + relacionamentos ORM
  │   └── category.py            # Model de categorias
  ├── controllers/
  │   ├── task_controller.py     # Eager loading (joinedload) eliminando N+1 + db.session.get()
  │   ├── user_controller.py     # Operações de usuário desacopladas de HTTP
  │   ├── category_controller.py # Camada dedicada para CRUD de categorias
  │   └── report_controller.py   # Agregações otimizadas
  ├── routes/
  │   ├── task_routes.py         # Rotas enxutas delegando para controllers
  │   ├── user_routes.py
  │   ├── category_routes.py     # Extração de categorias de dentro de report_routes
  │   └── report_routes.py       # Rotas de relatórios + alias retrocompatível
  ├── middlewares/
  │   └── error_handler.py       # Error handlers globais eliminando bare excepts
  └── services/
      └── notification_service.py # Credenciais seguras via config
  ```

---

### 3. Checklist de Validação Preenchido

| Critério de Validação | Projeto 1 | Projeto 2 | Projeto 3 |
|---|:---:|:---:|:---:|
| **Fase 1: Linguagem detectada corretamente** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 1: Framework detectado corretamente** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 1: Domínio da aplicação descrito corretamente** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 1: Número de arquivos analisados condizente** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 2: Relatório segue o template padronizado** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 2: Cada finding possui arquivo e linhas exatas** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 2: Findings ordenados por severidade (CRITICAL → LOW)** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 2: Mínimo de 5 findings identificados** | [x] Sim (11) | [x] Sim (10) | [x] Sim (9) |
| **Fase 2: Contém pelo menos 1 CRITICAL ou HIGH** | [x] Sim (7) | [x] Sim (6) | [x] Sim (4) |
| **Fase 2: Detecção de APIs deprecated incluída** | [x] N/A | [x] N/A | [x] Sim |
| **Fase 2: Pausa e confirmação antes da Fase 3** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Estrutura de diretórios segue padrão MVC** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Configuração extraída para módulo de config** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Models criados para abstrair dados** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Views / Routes separadas para roteamento** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Controllers concentram o fluxo da aplicação** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Error handling centralizado** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Entry point claro** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Aplicação inicia sem erros** | [x] Sim | [x] Sim | [x] Sim |
| **Fase 3: Endpoints originais respondem corretamente** | [x] Sim | [x] Sim | [x] Sim |

---

### 4. Logs de Execução e Validação das Aplicações

#### Validação do Projeto 1 (`code-smells-project`):
```text
✓ GET /health: {'ambiente': 'producao', 'counts': {'pedidos': 0, 'produtos': 10, 'usuarios': 3}, 'database': 'connected', 'status': 'ok', 'versao': '1.0.0'}
✓ GET /: {'endpoints': {'health': '/health', 'login': '/login', 'pedidos': '/pedidos', 'produtos': '/produtos', 'relatorios': '/relatorios/vendas', 'usuarios': '/usuarios'}, 'mensagem': 'Bem-vindo à API da Loja', 'versao': '1.0.0'}
✓ GET /produtos: 10 produtos encontrados
✓ GET /produtos/1: Notebook Gamer
✓ POST /produtos: criado id 11
✓ PUT /produtos: {'mensagem': 'Produto atualizado', 'sucesso': True}
✓ GET /produtos/busca: 2 encontrados
✓ DELETE /produtos: {'mensagem': 'Produto deletado', 'sucesso': True}
✓ GET /usuarios: 3 usuarios (senhas protegidas)
✓ POST /login: Login OK
✓ POST /pedidos: criado id 1
✓ GET /pedidos/usuario/1: 1 pedidos encontrados
✓ GET /relatorios/vendas: {'desconto_aplicavel': 300.0, 'faturamento_bruto': 5999.99, 'faturamento_liquido': 5699.99, 'pedidos_aprovados': 0, 'pedidos_cancelados': 0, 'pedidos_pendentes': 1, 'ticket_medio': 5999.99, 'total_pedidos': 1}

*** TODOS OS TESTES PASSARAM COM SUCESSO NO PROJETO 1! ***
```

#### Validação do Projeto 2 (`ecommerce-api-legacy`):
```text
Test server listening on port 3009
✓ POST /api/checkout (sucesso): { status: 200, data: { msg: 'Sucesso', enrollment_id: 2 } }
✓ POST /api/checkout (recusado): { status: 400, data: 'Pagamento recusado' }
✓ GET /api/admin/financial-report: [
  {
    "course": "Clean Architecture",
    "revenue": 997,
    "students": [
      {
        "student": "Leonan",
        "paid": 997
      }
    ]
  },
  {
    "course": "Docker",
    "revenue": 497,
    "students": [
      {
        "student": "Guilherme",
        "paid": 497
      }
    ]
  }
]
✓ DELETE /api/users/1: {
  status: 200,
  data: 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.'
}

*** TODOS OS TESTES PASSARAM COM SUCESSO NO PROJETO 2! ***
```

#### Validação do Projeto 3 (`task-manager-api`):
```text
✓ GET /health: {'status': 'ok', 'timestamp': '2026-11-17T23:03:37.372650+00:00'}
✓ GET /: {'message': 'Task Manager API', 'version': '1.0'}
✓ GET /tasks: 10 tasks encontradas
✓ GET /tasks/1: Implementar autenticação JWT
✓ POST /tasks: criada task id 11
✓ PUT /tasks: done
✓ GET /tasks/search: 1 task encontrada
✓ GET /tasks/stats: {'cancelled': 1, 'completion_rate': 18.18, 'done': 2, 'in_progress': 2, 'overdue': 2, 'pending': 6, 'total': 11}
✓ DELETE /tasks: {'message': 'Task deletada com sucesso'}
✓ GET /users: 3 usuarios (senhas protegidas)
✓ GET /users/1: João Silva (4 tasks)
✓ POST /login: Login realizado com sucesso
✓ GET /categories: 4 categorias
✓ POST /categories: categoria id 5
✓ DELETE /categories: {'message': 'Categoria deletada'}
✓ GET /reports/summary: {'total_categories': 4, 'total_tasks': 10, 'total_users': 3}
✓ GET /reports/user/1: {'cancelled': 0, 'completion_rate': 0.0, 'done': 0, 'high_priority': 2, 'in_progress': 0, 'overdue': 2, 'pending': 4, 'total_tasks': 4}

*** TODOS OS TESTES PASSARAM COM SUCESSO NO PROJETO 3! ***
```

---

## D) Seção "Como Executar"

### 1. Pré-Requisitos

- **Python**: Versão 3.10 ou superior (testado no Python 3.12).
- **Node.js**: Versão 18 ou superior (testado no Node.js v25).
- **Ferramenta Agêntica**: Claude Code, Antigravity CLI ou Gemini CLI com suporte a Custom Skills.

---

### 2. Comandos para Executar a Skill em Cada Projeto

A Skill está devidamente instalada em `.claude/skills/refactor-arch/` dentro dos 3 projetos.

#### Execução no Projeto 1:
```bash
cd code-smells-project
claude "/refactor-arch"
```

#### Execução no Projeto 2:
```bash
cd ecommerce-api-legacy
claude "/refactor-arch"
```

#### Execução no Projeto 3:
```bash
cd task-manager-api
claude "/refactor-arch"
```

---

### 3. Como Validar que a Refatoração Funcionou

Para executar os servidores de teste manualmente e verificar os endpoints:

#### Validar Projeto 1 (Python / Flask):
```bash
cd code-smells-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
Em outro terminal:
```bash
curl http://localhost:5000/health
curl http://localhost:5000/produtos
curl http://localhost:5000/relatorios/vendas
```

#### Validar Projeto 2 (Node.js / Express):
```bash
cd ecommerce-api-legacy
npm install
npm start
```
Em outro terminal:
```bash
curl http://localhost:3000/api/admin/financial-report
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"123","c_id":2,"card":"4111222233334444"}'
```

#### Validar Projeto 3 (Python / Flask):
```bash
cd task-manager-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 seed.py
python3 app.py
```
Em outro terminal:
```bash
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/reports/summary
```
