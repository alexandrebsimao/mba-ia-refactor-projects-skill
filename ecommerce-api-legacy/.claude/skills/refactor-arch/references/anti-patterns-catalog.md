# Catálogo de Anti-Patterns e Code Smells

Este catálogo guia a **Fase 2 (Architecture Audit)** da Skill `refactor-arch`. Cada item define **sinais concretos e acionáveis de detecção**, severidade padronizada (MVC + SOLID), impacto e recomendação.

---

## 1. Escala de Severidades

- **CRITICAL**: Falhas graves de arquitetura ou segurança que impedem o funcionamento seguro, expõem dados sensíveis (credenciais hardcoded, SQL Injection, execução arbitrária de SQL, vazamento de senhas/cartões) ou violam completamente a separação de responsabilidades (ex: God Class/Module concentrando banco, regras de negócio e roteamento).
- **HIGH**: Fortes violações do padrão MVC ou princípios SOLID que dificultam severamente manutenção e testes (lógicas de negócio pesadas em rotas/controllers, forte acoplamento sem injeção/desacoplamento, criptografia fraca/caseira, estado global mutável, Callback Hell).
- **MEDIUM**: Problemas de padronização, duplicação de código, integridade ou performance moderada (Queries N+1, ausência de tratamento centralizado de erros / bare `except:`, validações ausentes nas rotas, domínios misturados em arquivos errados, uso de APIs deprecated).
- **LOW**: Melhorias de legibilidade e higiene de código (nomenclatura críptica, magic numbers / magic strings, `print`/`console.log` de debug e imports não utilizados).

---

## 2. Catálogo de Anti-Patterns

### 1. [CRITICAL] SQL Injection & Execução Arbitrária de SQL
- **Sinais de Detecção**:
  - Concatenação (`+`), formatação (`%`, `.format()`) ou interpolação (`f"..."`, `` `${...}` ``) de variáveis externas diretamente dentro de strings SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
  - Endpoints HTTP que recebem uma instrução SQL enviada pelo cliente e a executam diretamente no banco (`cursor.execute(payload["sql"])` ou equivalente).
- **Impacto**: Extração integral do banco de dados, bypass de autenticação, alteração ou destruição de tabelas por invasores.
- **Recomendação**: Utilizar exclusivamente consultas parametrizadas com placeholders (`?`, `%s`, `$1`) ou métodos seguros de ORM/Query Builder. Remover endpoints de execução arbitrária de SQL.

### 2. [CRITICAL] Hardcoded Credentials & Secret Exposure
- **Sinais de Detecção**:
  - Strings literais atribuídas a chaves secretas, senhas de banco, tokens de API, chaves de gateway de pagamento ou credenciais SMTP (`SECRET_KEY = "..."`, `dbPass = "..."`, `apiKey = "pk_live_..."`).
  - Endpoints (ex: `/health`, `/status`, `/config`) que retornam chaves secretas, flags internas de debug ou caminhos internos do servidor na resposta JSON.
- **Impacto**: Comprometimento imediato de sessões, gateways externos e infraestrutura caso o repositório seja acessado ou vazado.
- **Recomendação**: Mover todas as credenciais e parâmetros de ambiente para variáveis de ambiente lidas por um módulo `config/` com fallbacks seguros apenas para desenvolvimento. Sanitizar respostas de diagnóstico.

### 3. [CRITICAL] Sensitive Data Exposure (Senhas / Dados de Pagamento)
- **Sinais de Detecção**:
  - Campos de senha (em texto claro ou hash) incluídos em métodos de serialização (`to_dict()`, `SELECT *`) e retornados em respostas HTTP de leitura de usuários.
  - Logs (`print`, `console.log`, `logger`) imprimindo números completos de cartão de crédito, CVV, senhas ou tokens em texto plano.
- **Impacto**: Violação grave de privacidade e conformidade (LGPD, GDPR, PCI-DSS) e exposição direta de credenciais de clientes.
- **Recomendação**: Omitir explicitamente campos sensíveis de qualquer serialização/query pública e mascarar dados de pagamento em logs (exibir no máximo os 4 últimos dígitos ou omitir por completo).

### 4. [CRITICAL] God Class / God Module (Violação Extrema do SRP)
- **Sinais de Detecção**:
  - Um único arquivo ou classe (>150–200 linhas ou acumulando ≥3 domínios distintos) responsável simultaneamente por: conexão de banco, DDL/seeds, registro de rotas HTTP, validação de payloads, regras de negócio, cálculos e formatação de respostas.
- **Impacto**: Acoplamento extremo; impossibilidade de testar domínios em isolamento; qualquer alteração introduz alto risco de regressão em outras áreas.
- **Recomendação**: Decompor por domínio e responsabilidade nas camadas MVC: `models/`, `controllers/`, `routes/` (ou `views/`), `config/`, `database/` e `middlewares/`.

### 5. [HIGH] Fat Routes / Business Logic in Transport Layer
- **Sinais de Detecção**:
  - Funções de rota HTTP contendo extensas validações manuais, regras de domínio, cálculos repetidos, queries diretas ao banco ou controle transacional (`commit`/`rollback`), sem delegar a uma camada de Controllers/Services.
  - Controllers acessando diretamente cursores ou executando SQL bruto em vez de invocar Models.
- **Impacto**: Forte acoplamento ao framework web; duplicação de regras entre rotas; impossibilidade de testar lógica de negócio sem subir o servidor HTTP.
- **Recomendação**: Extrair orquestração e regras de negócio para `controllers/` e encapsular queries em `models/`, mantendo `routes/` restrito ao mapeamento HTTP.

### 6. [HIGH] Insecure / Weak Cryptography & Plaintext Passwords
- **Sinais de Detecção**:
  - Senhas salvas e comparadas em texto plano (`senha == input`).
  - Algoritmos criptográficos quebrados ou sem salt para senhas (`MD5`, `SHA1`, `Base64` ou funções de hash caseiras com loops/substrings).
- **Impacto**: Quebra trivial de senhas via força bruta ou rainbow tables em caso de comprometimento da base de dados.
- **Recomendação**: Utilizar algoritmos modernos de derivação de chave com salt automático (`bcrypt`, `argon2`, `scrypt` ou `PBKDF2` nativo via `werkzeug.security` / `crypto.pbkdf2Sync` / `crypto.scryptSync`).

### 7. [HIGH] Mutable Shared Global State & Tight Coupling
- **Sinais de Detecção**:
  - Variáveis globais mutáveis no escopo de módulo usadas como cache sem limite de tamanho/TTL, acumuladores financeiros ou estado de sessão compartilhado entre requisições.
  - Instanciação hardcoded de conexões globais sem escopo de requisição (ex: conexão SQLite única com `check_same_thread=False` sem gerenciamento de ciclo de vida) ou acoplamento rígido sem injeção/composição modular.
- **Impacto**: Condições de corrida (race conditions), vazamento progressivo de memória (memory leak), dados inconsistentes entre requisições/workers e baixa testabilidade.
- **Recomendação**: Encapsular estado em serviços com limite/ciclo de vida controlado, usar conexões com escopo de requisição (`g` / pool) e compor dependências no entry point.

### 8. [HIGH] Callback Hell ("Pyramid of Doom")
- **Sinais de Detecção**:
  - Aninhamento de 3 ou mais callbacks assíncronos encadeados (`(err, res) => { db.get(..., (err, res2) => { ... }) }`), com checagem repetitiva de erro em cada nível e uso de `const self = this`.
- **Impacto**: Complexidade ciclomática elevada, difícil leitura, risco de respostas HTTP duplicadas ou pendentes em caso de erro intermediário.
- **Recomendação**: Promisificar operações assíncronas e reescrever fluxos de forma linear usando `async/await` com `try/catch` encaminhando falhas ao error handler central.

### 9. [MEDIUM] N+1 Query Problem
- **Sinais de Detecção**:
  - Execução de query SQL ou consulta ORM (`cursor.execute(...)`, `db.get(...)`, `Model.query.get(...)`, `Model.query.filter_by(...)`) dentro de um laço (`for`, `forEach`, `map`) sobre registros previamente buscados.
  - Acesso a relacionamentos `lazy` em ORM dentro de loops de serialização sem carregamento antecipado.
- **Impacto**: Multiplicação exponencial ou linear de idas ao banco ($1 + N$ ou $1 + N + N \times M$), degradando severamente a latência sob carga.
- **Recomendação**: Consolidar consultas usando `SQL JOIN`, consultas agregadas (`GROUP BY`) ou eager loading no ORM (`joinedload` / `selectinload` / `include`).

### 10. [MEDIUM] Missing Centralized Error Handling & Bare Exceptions
- **Sinais de Detecção**:
  - Blocos `except:` genéricos (bare except) ou `catch (err) {}` que silenciam erros sem logging ou retornam respostas genéricas/inconsistentes.
  - Repetição do mesmo padrão `try/except` ou `if (err) return res.status(500)...` em todos os endpoints sem um handler global.
- **Impacto**: Erros de runtime mascarados, respostas HTTP sem padrão consistente e diagnóstico extremamente difícil em produção.
- **Recomendação**: Criar middleware/handler global de erros (`middlewares/error_handler`) e capturar apenas exceções específicas quando houver recuperação real.

### 11. [MEDIUM] Uso de APIs Deprecated (Obsoletas)
- **Sinais de Detecção (Multi-Stack)**:
  - **Python 3.12+**: `datetime.utcnow()`, `datetime.utcfromtimestamp()` → substituir por `datetime.now(timezone.utc)` / `datetime.fromtimestamp(ts, tz=timezone.utc)`.
  - **SQLAlchemy 2.0+ / Flask-SQLAlchemy 3.x**: `Model.query.get(id)` → substituir por `db.session.get(Model, id)`; `Query.count()` / APIs legadas 1.x quando obsoletas.
  - **Python Packaging / Stdlib**: `pkg_resources`, `distutils`, `imp`, `cgi`, `asyncio.get_event_loop()` em coroutines.
  - **Node.js / Express**: `new Buffer(...)` → `Buffer.from(...)` / `Buffer.alloc(...)`; `url.parse()` → `new URL()`; `fs.exists()` → `fs.existsSync()` / `fs.promises.access()`; `req.param()` → `req.params`/`req.query`/`req.body`; `res.send(status, body)` → `res.status(status).send(body)`; `app.del()` → `app.delete()`.
  - **Dependências / Frameworks**: Métodos marcados como deprecated na versão do framework detectada na Fase 1.
- **Impacto**: Emissão de warnings contínuos, falhas de segurança não corrigidas e quebra de compatibilidade em atualizações da linguagem ou framework.
- **Recomendação**: Substituir cada API obsoleta pelo equivalente moderno recomendado pela documentação oficial da stack.

### 12. [MEDIUM] Misplaced Domain Responsibilities, Missing Validation & Orphaned Records
- **Sinais de Detecção**:
  - Endpoints de um domínio colocados em arquivo de rotas/controller de outro domínio não relacionado.
  - Rotas `POST`/`PUT` que aceitam payloads sem validar campos obrigatórios, tipos ou faixas de valores, ou validação duplicada manualmente em múltiplos lugares.
  - Operações `DELETE` em entidades pai sem remover registros dependentes (ou sem `ON DELETE CASCADE` / transação), gerando registros órfãos.
- **Impacto**: Baixa coesão, inconsistência de dados no banco e comportamento imprevisível com entradas malformadas.
- **Recomendação**: Separar módulos por domínio, centralizar validações de entrada e garantir integridade referencial em transações.

### 13. [LOW] Magic Numbers & Magic Strings
- **Sinais de Detecção**:
  - Limiares numéricos, alíquotas, limites de tamanho, prefixos de validação ou status fixados literalmente dentro de condicionais (`if value > 10000: rate = 0.1`, `startsWith("4")`) sem constantes nomeadas.
- **Impacto**: Dificulta compreensão das regras de negócio e aumenta o risco de inconsistência quando um valor muda.
- **Recomendação**: Extrair valores de negócio para constantes descritivas ou configuração.

### 14. [LOW] Poor Naming, Debug Prints & Unused Code
- **Sinais de Detecção**:
  - Variáveis com nomes crípticos de 1–2 letras em lógica de negócio (ex: `u`, `e`, `p`, `cid`, `cc` fora de índices triviais de loop).
  - Uso de `print(...)` / `console.log(...)` espalhados em vez de logging estruturado.
  - Imports não utilizados ou variáveis locais declaradas e nunca lidas.
- **Impacto**: Reduz legibilidade, polui stdout e dificulta manutenção.
- **Recomendação**: Adotar nomes semânticos, remover imports/variáveis mortas e padronizar logging.
