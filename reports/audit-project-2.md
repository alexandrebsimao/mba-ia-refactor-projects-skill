================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] God Class Architecture (AppManager)
File: src/AppManager.js:4-139
Description: A classe `AppManager` acumula inicialização e conexão com o banco SQLite (:memory:), criação de esquemas DDL, inserção de seeds, mapeamento de rotas HTTP, validação de requisições, orquestração de checkout, gravação de logs e cálculo de relatórios financeiros.
Impact: Violação integral do Princípio da Responsabilidade Única (SRP); alto acoplamento tornando testes unitários e manutenção quase inviáveis.
Recommendation: Decompor o projeto nas camadas MVC: `models/`, `controllers/`, `routes/`, `config/` e `database/`.

### [CRITICAL] Hardcoded Production Secrets
File: src/utils.js:1-7
Description: Credenciais de produção expostas diretamente no código-fonte (`dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: "no-reply@fullcycle.com.br"`).
Impact: Risco crítico de segurança e vazamento de chaves de gateway de pagamento ao vivo e credenciais de banco em repositórios.
Recommendation: Isolar todas as configurações em variáveis de ambiente via `dotenv`, criando um módulo de configuração seguro (`src/config/index.js`).

### [CRITICAL] Sensitive Credit Card Data Logged in Plaintext
File: src/AppManager.js:45
Description: O número completo do cartão de crédito é impresso sem qualquer máscara no console: `console.log('Processando cartão ${cc} na chave ${config.paymentGatewayKey}')`.
Impact: Violação direta das normas de conformidade PCI-DSS e privacidade; dados de pagamento expostos em logs do servidor.
Recommendation: Mascarar os dados do cartão de crédito registrando apenas os últimos 4 dígitos ou remover o log do número do cartão.

### [HIGH] Insecure / Broken Cryptography (badCrypto)
File: src/utils.js:17-23, src/AppManager.js:68
Description: Função de hash de senhas caseira que itera 10.000 vezes concatenando pedaços de strings em Base64 e truncando em 10 caracteres.
Impact: Criptografia fraca e vulnerável a quebra imediata por força bruta ou dicionário; senhas de usuários ficam desprotegidas.
Recommendation: Substituir por algoritmos criptográficos robustos padrão da plataforma Node.js (`crypto.pbkdf2Sync` ou `crypto.scryptSync`) com salt seguro.

### [HIGH] Mutable Shared Global State & Memory Leak Risks
File: src/utils.js:9-15, src/AppManager.js:59
Description: Variáveis globais mutáveis no módulo (`let globalCache = {}; let totalRevenue = 0;`) manipuladas a cada requisição sem limite de armazenamento ou controle de expiração.
Impact: Vazamento de memória contínuo em processos de longa duração; risco de condições de corrida e inconsistência de dados entre requisições simultâneas.
Recommendation: Substituir por um serviço de cache estruturado ou remover o estado global mutável não controlado.

### [HIGH] Callback Hell / "Pyramid of Doom"
File: src/AppManager.js:37-76, 83-127
Description: Aninhamento profundo de callbacks assíncronos (5 a 6 níveis de indentação) com repetição manual de tratamento de erros a cada etapa do fluxo de checkout e relatórios.
Impact: Código ilegível, complexidade ciclomática elevada e alta probabilidade de exceções não capturadas ("unhandled errors").
Recommendation: Promisificar as operações do banco de dados SQLite e adotar `async/await` com blocos `try/catch` lineares.

### [MEDIUM] N+1 and Multi-level Nested Query Problem
File: src/AppManager.js:83-127
Description: No endpoint `/api/admin/financial-report`, para cada curso busca-se matrículas, para cada matrícula busca-se o usuário e para cada matrícula busca-se o pagamento em callbacks aninhados.
Impact: Explosão de consultas ao banco de dados ($1 + C + C \times E \times 2$), gerando latência inaceitável à medida que a base de dados cresce.
Recommendation: Otimizar o relatório utilizando uma consulta consolidada com `LEFT JOIN` entre as tabelas `courses`, `enrollments`, `users` e `payments`.

### [MEDIUM] Data Integrity Violation / Orphaned Records on Delete
File: src/AppManager.js:131-137
Description: Ao deletar um usuário (`DELETE FROM users WHERE id = ?`), os registros dependentes em `enrollments` e `payments` são mantidos intactos no banco.
Impact: Corrupção da integridade referencial do banco de dados, deixando registros órfãos que poluem relatórios futuros.
Recommendation: Executar deleção em cascata dentro de uma transação garantindo a limpeza das tabelas filhas.

### [LOW] Cryptic Variable Naming
File: src/AppManager.js:29-33, 89-93
Description: Uso de nomes de variáveis crípticos com uma ou duas letras (`u`, `e`, `p`, `cid`, `cc`, `c`, `enr`).
Impact: Reduz severamente a legibilidade e a manutenibilidade do código.
Recommendation: Adotar nomenclatura expressiva e semântica (`userName`, `email`, `password`, `courseId`, `creditCard`).

### [LOW] Hardcoded Payment Simulation Logic
File: src/AppManager.js:46
Description: Regra de aprovação de pagamento fixada diretamente na rota através de verificação de prefixo de string (`cc.startsWith("4") ? "PAID" : "DENIED"`).
Impact: Regra de negócio acoplada diretamente à camada de transporte sem abstração de serviço de pagamento.
Recommendation: Encapsular a regra de gateway em um serviço dedicado (`paymentService`).

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
