================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   11 analyzed | ~1150 lines of code

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Credentials & Sensitive SMTP Secrets
File: app.py:13, services/notification_service.py:9-10
Description: `SECRET_KEY = 'super-secret-key-123'` fixada em código puro em `app.py`. Credenciais completas de email (`self.email_user = 'taskmanager@gmail.com'` e `self.email_password = 'senha123'`) em texto claro no serviço de notificação.
Impact: Risco crítico de segurança; possibilidade de assinatura indevida de cookies/sessões e sequestro da conta SMTP utilizada pelo serviço.
Recommendation: Mover todas as credenciais sensíveis para variáveis de ambiente (`.env`) gerenciadas por um módulo de configuração central (`config/settings.py`).

### [CRITICAL] Weak Cryptography (MD5) & Password Hash Leakage
File: models/user.py:21, 27-32
Description: O hash de senhas de usuários utiliza o algoritmo MD5 sem salting (`hashlib.md5(pwd.encode()).hexdigest()`), que é vulnerável a colisões e tabelas arco-íris. Além disso, o método `to_dict()` inclui `'password': self.password`, vazando o hash de senha nas rotas GET `/users` e `/users/<id>`.
Impact: Quebra trivial de senhas em caso de vazamento da base; violação de privacidade com exposição do hash em endpoints públicos de leitura de usuários.
Recommendation: Adotar `werkzeug.security.generate_password_hash` com algoritmo PBKDF2/SHA256 e salting automático, removendo a chave `password` do dicionário serializado.

### [HIGH] Missing Controller Layer ("Fat Routes" Anti-Pattern)
File: routes/task_routes.py:11-299, routes/user_routes.py:10-211, routes/report_routes.py:12-223
Description: As rotas concentram regras de negócio extensas, validações manuais de campos, cálculos de atraso (`overdue`) repetidos e controle transacional (`db.session.commit()` / `rollback()`), sem uma camada controladora intermediária.
Impact: Forte acoplamento ao framework web (Flask), impedindo a testabilidade das regras de negócio de forma isolada e gerando alta duplicação de código.
Recommendation: Criar a camada `controllers/` (`task_controller.py`, `user_controller.py`, `category_controller.py`, `report_controller.py`) transferindo a orquestração e lógica de negócio.

### [HIGH] Misplaced Domain Responsibilities (Categories inside Report Routes)
File: routes/report_routes.py:157-223
Description: O CRUD completo de categorias (`/categories`, `POST`, `PUT`, `DELETE`) está implementado dentro do arquivo `report_routes.py`, violando a coesão de domínio.
Impact: Confusão na navegação da base de código e violação do princípio de responsabilidade única dos módulos.
Recommendation: Mover as rotas de categoria para um arquivo próprio (`routes/category_routes.py` e `controllers/category_controller.py`).

### [MEDIUM] Deprecated APIs (datetime.utcnow & Model.query.get)
File: models/user.py:14, models/task.py:15-16, routes/task_routes.py:31, 67, 117, 122, 158, routes/user_routes.py:29, 94, 136, seed.py:66-74
Description: Uso de `datetime.utcnow()`, expressamente depreciado a partir do Python 3.12 (gerando avisos e agendado para remoção futura). Uso de `Model.query.get(id)`, depreciado no ecossistema SQLAlchemy 2.0+ / Flask-SQLAlchemy 3.x.
Impact: Quebra de compatibilidade em novas versões do Python e do SQLAlchemy, além de poluição nos logs de execução.
Recommendation: Substituir `datetime.utcnow()` por `datetime.now(timezone.utc)` e `Model.query.get(id)` pelo moderno `db.session.get(Model, id)`.

### [MEDIUM] N+1 Query Problem in Task and Report Endpoints
File: routes/task_routes.py:41-58, routes/report_routes.py:53-68
Description: Na rota de listagem de tasks (`get_tasks`), para cada tarefa itera-se executando queries individuais para carregar o nome do usuário e da categoria. No relatório consolidado (`summary_report`), itera-se por todos os usuários executando `Task.query.filter_by` para cada um.
Impact: Degradação de desempenho proporcional ao volume de registros, gerando dezenas de idas desnecessárias ao banco de dados.
Recommendation: Utilizar carregamento adiantado (`joinedload`) nas relações do SQLAlchemy ou consultas agregadas com `func.count()`.

### [MEDIUM] Bare Except Clauses Swallowing Exceptions
File: routes/task_routes.py:62, 137, 204, 236, routes/user_routes.py:130, 149, routes/report_routes.py:186, 208, 221
Description: Uso sistemático de cláusulas `except:` genéricas sem especificação do tipo de erro nem captura de stack trace, retornando apenas status 500 silencioso.
Impact: Mascaramento de erros de sintaxe, falhas de schema ou interrupções de conexão, tornando o diagnóstico em produção praticamente inviável.
Recommendation: Tratar exceções específicas com log estruturado e implementar um handler global de exceções.

### [LOW] Volatile In-Memory State in Services
File: services/notification_service.py:6, 31-36, 43-48
Description: A lista `self.notifications = []` mantém o histórico de notificações em memória no processo da aplicação.
Impact: Perda de dados a cada reinício do servidor ou inconsistência entre diferentes workers de um servidor de aplicação WSGI.
Recommendation: Persistir as notificações em banco de dados ou utilizar um serviço de mensageria / logging persistente.

### [LOW] Fake JWT Authentication Token
File: routes/user_routes.py:210
Description: O endpoint de login devolve um token forjado estático (`'fake-jwt-token-' + str(user.id)`) sem assinatura criptográfica real nem tempo de expiração.
Impact: Mecanismo de autenticação incompleto que induz a uma falsa sensação de segurança.
Recommendation: Adotar uma biblioteca padrão como `PyJWT` para geração de tokens com assinatura segura ou documentar formalmente o placeholder.

================================
Total: 9 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
