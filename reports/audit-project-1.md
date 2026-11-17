================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] SQL Injection Vulnerabilities
File: models.py:28, 48-50, 58-61, 68, 92, 109-111, 127-129, 140, 149, 155, 158-160, 164, 174, 188, 192, 220, 224, 280, 291-297
Description: Concatenação direta de strings e interpolação de variáveis do usuário em comandos SQL brutos em múltiplos métodos de acesso a dados (produtos, usuários, pedidos, login e busca).
Impact: Permite que invasores executem SQL malicioso, extraiam dados confidenciais, contornem autenticação (ex: `' OR '1'='1`) e alterem ou apaguem registros da base de dados.
Recommendation: Substituir todas as concatenações por consultas SQL parametrizadas com placeholders `?` e tuplas de argumentos.

### [CRITICAL] Arbitrary SQL Execution Endpoint & Backdoor
File: app.py:59-78
Description: O endpoint `/admin/query` aceita instruções SQL brutas enviadas no corpo da requisição JSON (`{"sql": "..."}`) e as executa diretamente na conexão do banco de dados SQLite.
Impact: Controle total do banco de dados acessível via requisições HTTP; qualquer cliente pode executar DROP TABLE, extrair todos os dados ou corromper o estado do sistema.
Recommendation: Remover completamente o endpoint de execução arbitrária de queries. Operações administrativas devem ser expostas através de rotas restritas e seguras.

### [CRITICAL] Hardcoded Credentials & Secret Exposure
File: app.py:7, controllers.py:289
Description: A chave de sessão `SECRET_KEY` está hardcoded no código (`"minha-chave-super-secreta-123"`). Além disso, o endpoint `/health` expõe publicamente a `secret_key`, o caminho do banco de dados e o modo debug na resposta JSON.
Impact: Falsificação de tokens/sessões de usuários, comprometimento da integridade da aplicação e vazamento de informações internas de infraestrutura.
Recommendation: Extrair a `SECRET_KEY` para variáveis de ambiente via módulo de configuração (`config/settings.py`) e sanitizar o payload do endpoint `/health`.

### [CRITICAL] Sensitive Data Exposure (Plaintext Passwords)
File: models.py:79-87, 95-103, controllers.py:128-144
Description: Senhas de usuários são salvas em texto puro no banco e expostas explicitamente no retorno das listagens `/usuarios` e `/usuarios/<id>`.
Impact: Violação severa de privacidade e conformidade de segurança (LGPD); vazamento imediato de credenciais de todos os usuários.
Recommendation: Implementar hashing seguro de senhas com salting (Werkzeug security) e remover o campo de senha das respostas de serialização do usuário.

### [CRITICAL] God Module / Violation of Single Responsibility Principle
File: models.py:1-314
Description: Arquivo único concentrando queries SQL, validações de entrada, mutação de inventário, regras de faturamento e relatórios para 4 domínios diferentes (Produtos, Usuários, Pedidos e Relatórios).
Impact: Impossível realizar testes unitários isolados; alto risco de efeitos colaterais onde a alteração em um domínio quebra os demais; violação grave do SRP.
Recommendation: Decompor o arquivo em modelos de domínio dedicados (`produto_model.py`, `usuario_model.py`, `pedido_model.py`, `relatorio_model.py`) dentro de um diretório `models/`.

### [HIGH] Direct Database Access in Controllers
File: controllers.py:264-290
Description: A função `health_check` no controller importa `get_db()`, cria cursores e executa queries SQL diretamente (`SELECT COUNT(*)...`), violando a separação de camadas.
Impact: Acoplamento indevido entre a camada de transporte/controle e a persistência de banco de dados.
Recommendation: Mover verificações de integridade e contagens de banco para os respectivos modelos ou para um serviço de infraestrutura de banco de dados.

### [HIGH] Procedural Business Logic in Data Layer
File: models.py:133-170, 256-273
Description: Regras de negócio como cálculo de desconto progressivo por faturamento, validação de estoque suficiente para pedidos e decremento de inventário estão acopladas diretamente nas funções de persistência.
Impact: Mistura regras de negócio com detalhes de infraestrutura SQL, dificultando a evolução de regras e a reutilização do código.
Recommendation: Migrar a lógica de negócio e orquestração de pedidos e relatórios para a camada de Controllers e serviços de aplicação.

### [MEDIUM] N+1 Query Problem in Order Retrieval
File: models.py:171-201, 203-234
Description: Nos métodos `get_pedidos_usuario` e `get_todos_pedidos`, para cada pedido recuperado é realizada uma nova consulta para itens de pedido, e para cada item outra consulta para obter o nome do produto.
Impact: Explosão do número de queries enviadas ao banco ($1 + N + N \times M$), gerando lentidão extrema conforme a quantidade de pedidos cresce.
Recommendation: Consolidar as consultas utilizando comandos SQL com `JOIN` entre as tabelas `pedidos`, `itens_pedido` e `produtos`.

### [MEDIUM] Lack of Centralized Error Handling & Inconsistent Responses
File: controllers.py:5-263
Description: Repetição de blocos `try...except Exception as e:` em todas as funções de controle, utilizando `print()` simples e retornando respostas de erro de forma inconsistente.
Impact: Falta de padronização nas respostas da API, engolimento de detalhes de diagnóstico e impossibilidade de monitoramento padronizado de erros.
Recommendation: Implementar um middleware centralizado de tratamento de erros (`middlewares/error_handler.py`) registrando handlers para exceções e erros HTTP.

### [LOW] Magic Numbers in Business Calculations
File: models.py:257-263
Description: Valores mágicos de faixas de faturamento (`10000`, `5000`, `1000`) e alíquotas de desconto (`0.1`, `0.05`, `0.02`) fixados diretamente dentro da condicional de cálculo.
Impact: Dificulta a parametrização e legibilidade do código de faturamento.
Recommendation: Extrair esses valores para constantes bem documentadas no módulo de configuração ou modelo de relatório.

### [LOW] Global SQLite Connection without Request Lifecycle Scoping
File: database.py:4, 8-12
Description: Conexão SQLite compartilhada globalmente com flag `check_same_thread=False` sem fechamento ao final do contexto de requisição.
Impact: Risco de concorrência e travamentos sob servidores WSGI multi-thread em produção.
Recommendation: Gerenciar a conexão utilizando o contexto de aplicação do Flask (`g.db`) com teardown automático ao final da requisição.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
