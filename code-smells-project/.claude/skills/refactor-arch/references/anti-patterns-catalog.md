# Catálogo de Anti-Patterns e Code Smells

Este catálogo serve como base de conhecimento para a **Fase 2 (Architecture Audit)** da Skill `refactor-arch`. Ele define a escala de severidade padronizada baseada em MVC e SOLID, os sinais concretos de detecção e as recomendações de mitigação.

---

## 1. Escala de Severidades

- **CRITICAL**: Falhas graves de arquitetura ou segurança que impedem o funcionamento seguro e correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection, execução arbitrária de queries) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, regras de negócio e roteamento no mesmo arquivo).
- **HIGH**: Fortes violações do padrão MVC ou princípios SOLID que dificultam severamente a manutenção e testes (ex: regras de negócio pesadas em controllers/rotas, forte acoplamento sem injeção de dependência, criptografia insegura/caseira, ou estado global mutável em toda a aplicação).
- **MEDIUM**: Problemas de padronização, duplicação de código, gargalos de performance moderada (ex: Queries N+1 no banco de dados, ausência de tratamento centralizado de erros, entidades órfãs/falta de integridade referencial, APIs deprecated com risco moderado).
- **LOW**: Melhorias de legibilidade, nomenclatura de variáveis ruim ou críptica, "magic numbers" / "magic strings" soltos pelo código, print/console.log espalhados para debug.

---

## 2. Catálogo de Anti-Patterns

### 1. [CRITICAL] SQL Injection & Execução Arbitrária de SQL
- **Sinais de Detecção**:
  - Concatenação direta de strings ou interpolação com variáveis em comandos SQL (ex: `"SELECT * FROM produtos WHERE id = " + str(id)` ou `"UPDATE usuarios SET nome = '" + nome + "'"`).
  - Endpoints que recebem queries SQL abertas do cliente HTTP e as executam diretamente (ex: `cursor.execute(request.json['sql'])`).
- **Impacto**: Exposição catastrófica de dados, possibilidade de extração, corrupção ou destruição total do banco de dados através de injeção maliciosa.
- **Recomendação**: Utilizar queries parametrizadas com placeholders (`?` ou `%s`) ou abstrações seguras via ORM/Query Builder. Remover endpoints de execução arbitrária de SQL.

### 2. [CRITICAL] Hardcoded Credentials & Sensitive Data Exposure
- **Sinais de Detecção**:
  - Chaves de segurança, senhas, chaves de gateway de pagamento ou credenciais de banco declaradas em texto puro nos arquivos de código (ex: `SECRET_KEY = "minha-chave-super-secreta-123"`, `paymentGatewayKey: "pk_live_..."`).
  - Endpoints públicos (ex: `/health` ou `/usuarios`) que expõem senhas de usuários ou secrets da aplicação no corpo da resposta JSON.
  - Logs que imprimem números completos de cartão de crédito ou tokens de autenticação no console (`console.log('Processando cartão ${cc}...')`).
- **Impacto**: Comprometimento imediato da segurança dos usuários e da infraestrutura da aplicação. Violação de conformidades como LGPD e PCI-DSS.
- **Recomendação**: Isolar todas as configurações sensíveis em variáveis de ambiente (`.env` / `os.environ` / `process.env`) consumidas por um módulo central `config`. Sanitizar payloads de resposta para omitir campos sensíveis (`senha`, `hash`, `tokens`).

### 3. [CRITICAL] God Class / God Module (Violação do SRP)
- **Sinais de Detecção**:
  - Arquivo ou classe única acumulando múltiplas responsabilidades não relacionadas: gerenciamento de conexão de banco, criação de DDL/tabelas, seed de dados, roteamento HTTP, regras de validação, cálculos financeiros e chamadas de serviços (ex: `models.py` com mais de 300 linhas manipulando 4 domínios diferentes ou `AppManager.js`).
- **Impacto**: Altíssimo acoplamento; qualquer modificação introduz efeitos colaterais em toda a aplicação; testes unitários em isolamento são impossíveis.
- **Recomendação**: Desmembrar a God Class/Module em camadas bem definidas seguindo MVC: Models independentes por domínio, Controllers com funções focadas e Views/Rotas dedicadas.

### 4. [HIGH] Fat Routes / Business Logic in Controllers
- **Sinais de Detecção**:
  - Arquivos de rotas (`routes/*.py` ou `routes/*.js`) contendo dezenas de linhas de regras de validação procedural, cálculos matemáticos, queries diretas de banco de dados e orquestração de transações (`db.session.commit()`).
  - Inexistência de uma camada Controller ou serviço intermediário entre o framework web e a persistência.
- **Impacto**: Violação do Princípio da Responsabilidade Única (SRP); impede o reaproveitamento de regras de negócio em outros canais (ex: CLI, mensageria, jobs em lote); impossibilita testes de negócio sem instanciar servidor HTTP.
- **Recomendação**: Extrair as regras de negócio e validações para Controllers e Models de domínio, mantendo as rotas (Views) estritamente responsáveis pelo parsing de requests e respostas HTTP.

### 5. [HIGH] Insecure / Broken Cryptography & Plaintext Passwords
- **Sinais de Detecção**:
  - Senhas armazenadas em texto plano sem qualquer hash.
  - Algoritmos criptográficos obsoletos/quebrados (ex: `hashlib.md5(pwd.encode()).hexdigest()` sem salt).
  - Funções de criptografia caseiras baseadas em laços de concatenação de substrings em base64 (`badCrypto`).
- **Impacto**: Facilidade de ataque por força bruta, tabelas arco-íris (rainbow tables) e decodificação trivial em caso de vazamento da base de dados.
- **Recomendação**: Adotar algoritmos padrão da indústria para hash de senhas com salting embutido (ex: `werkzeug.security.generate_password_hash` / `bcrypt` / `argon2` ou `crypto.pbkdf2` / `scrypt`).

### 6. [HIGH] Mutable Shared Global State & Memory Leaks
- **Sinais de Detecção**:
  - Variáveis globais mutáveis no nível do módulo (ex: `let globalCache = {}; let totalRevenue = 0;` ou conexões globais sem controle de thread/concorrência).
- **Impacto**: Condições de corrida (race conditions) em ambientes multi-thread ou assíncronos, poluição cruzada entre requisições de clientes diferentes e vazamento progressivo de memória RAM.
- **Recomendação**: Encapsular estado em serviços com ciclo de vida definido, utilizar bancos de cache dedicados (ou estruturas thread-safe com eviction) e evitar variáveis globais expostas.

### 7. [HIGH] Callback Hell / "Pyramid of Doom"
- **Sinais de Detecção**:
  - Aninhamento excessivo de callbacks assíncronos (4 ou mais níveis de profundidade com `(err, result) => { ... }`) com tratamento repetitivo de erros em cada nó.
- **Impacto**: Dificuldade extrema de leitura, facilidade para cometer erros de fluxo e "unhandled rejections", alta complexidade ciclomática.
- **Recomendação**: Migrar para Promises ou `async/await`, encapsulando queries com utilitários assíncronos e tratando erros de forma linear com `try/catch`.

### 8. [MEDIUM] N+1 Query Problem
- **Sinais de Detecção**:
  - Execução de queries dentro de loops de iteração de coleções (ex: iterar uma lista de pedidos e fazer um `SELECT` para buscar os itens de cada pedido, ou iterar tarefas e buscar individualmente o usuário e a categoria com `query.get()`).
  - Múltiplas queries síncronas aninhadas em endpoints de listagem ou relatórios.
- **Impacto**: Degradação severa de performance proporcional ao volume de dados (ex: com 1.000 itens, 1.001 queries ao invés de 1).
- **Recomendação**: Utilizar `JOIN`s em SQL puro, queries em batch (`WHERE id IN (...)`) ou técnicas de Eager Loading no ORM (ex: `options(joinedload(...))` no SQLAlchemy).

### 9. [MEDIUM] Falta de Tratamento Centralizado de Erros (Bare Excepts & Swallowed Exceptions)
- **Sinais de Detecção**:
  - Blocos `except:` genéricos sem especificação de exceção e sem log detalhado, retornando apenas status 500 genérico.
  - Repetição do padrão `try/except` idêntico em todas as funções de controle.
- **Impacto**: Dificuldade de diagnóstico em produção; erros ocultos (bugs silenciosos) que mascaram problemas de banco de dados ou lógica.
- **Recomendação**: Implementar um middleware ou manipulador global de erros (`@app.errorhandler(Exception)` no Flask ou middleware `(err, req, res, next)` no Express) com logs estruturados.

### 10. [MEDIUM / LOW] Uso de APIs Deprecated (Obsoletas)
- **Sinais de Detecção**:
  - **Python 3.12+**: Uso de `datetime.utcnow()` (deprecated desde o Python 3.12, gerando `DeprecationWarning`).
  - **SQLAlchemy 2.0+ / Flask-SQLAlchemy 3.x**: Uso de `Model.query.get(id)` (legado 1.x; no 2.0 deve-se usar `db.session.get(Model, id)`).
  - **Express / Node.js**: Métodos ou pacotes deprecated no `package.json` ou chamadas obsoletas.
- **Impacto**: Risco de quebra de compatibilidade em upgrades futuros da linguagem/framework; poluição de logs com warnings.
- **Recomendação**: Substituir `datetime.utcnow()` por `datetime.now(timezone.utc)` e `Model.query.get(id)` por `db.session.get(Model, id)`.

### 11. [LOW] Magic Numbers, Magic Strings & Nomenclatura Críptica
- **Sinais de Detecção**:
  - Números e strings com significado de negócio embutidos diretamente no código sem constantes nomeadas (ex: descontos `10000`, `0.1`, `5000`, `0.05`).
  - Variáveis com nomes crípticos de 1 ou 2 letras (ex: `u`, `e`, `p`, `cid`, `cc`, `enr`).
- **Impacto**: Dificulta a compreensão do código e onboarding de novos desenvolvedores; risco de alterar o valor em um lugar e esquecer em outros.
- **Recomendação**: Definir constantes explicativas e utilizar nomes de variáveis semânticos e descritivos.
