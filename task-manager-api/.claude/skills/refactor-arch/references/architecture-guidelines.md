# Diretrizes de Arquitetura Alvo (Padrão MVC)

Este guia estabelece os princípios e as diretrizes estruturais para a **Fase 3 (Refatoração Arquitetural)** da Skill `refactor-arch`. O objetivo é transformar qualquer codebase legada ou parcialmente organizada em uma estrutura limpa e manutenível baseada em **MVC (Model-View-Controller)**.

---

## 1. Princípios Fundamentais

1. **Separação de Responsabilidades (SRP)**:
   - Cada camada e cada arquivo deve ter apenas um motivo para mudar.
2. **Preservação Contratual de APIs**:
   - Rotas, métodos HTTP, query params, schemas de payload e códigos de status originais devem permanecer estritamente compatíveis.
3. **Isolamento de Configuração**:
   - Nenhuma credencial ou configuração de ambiente pode permanecer hardcoded no código.
4. **Testabilidade e Modularidade**:
   - A lógica de negócio e as consultas ao banco não devem depender diretamente de objetos de requisição HTTP (`request`).

---

## 2. Camadas da Arquitetura MVC Alvo

```
src/ (ou estrutura modular do projeto)
├── config/
│   └── settings.py / config.js      # Variáveis de ambiente e configurações
├── database/
│   └── connection.py / db.js        # Conexão de banco e pool/instância
├── models/
│   └── <dominio>_model.py / .js     # Abstração de dados, schemas e queries
├── controllers/
│   └── <dominio>_controller.py / .js# Orquestração do fluxo e regras de aplicação
├── routes/ (ou views/)
│   └── <dominio>_routes.py / .js    # Roteamento HTTP e mapping de endpoints
├── middlewares/
│   └── error_handler.py / .js       # Tratamento centralizado de erros
└── app.py / app.js                  # Composition Root / Entry point
```

### Camada 1: Config (`config/`)
- **Responsabilidade**: Carregar e validar variáveis de ambiente (`.env`), fornecendo valores padrão seguros para desenvolvimento e levantando erros para secrets de produção ausentes.
- **Regras**:
  - Nunca commitar secrets no repositório.
  - Prover objetos tipados ou dicts imutáveis (`Config`, `settings`).

### Camada 2: Models (`models/`)
- **Responsabilidade**: Abstração da camada de dados e persistência.
- **Regras**:
  - Representa as entidades do domínio (ex: `Produto`, `Usuario`, `Pedido`, `Task`, `Category`, `Course`, `Enrollment`).
  - Responsável por executar queries de forma segura e parametrizada (ou via ORM/Query Builder).
  - **Proibição**: Models NUNCA devem acessar o objeto `request`, importar bibliotecas de rotas HTTP ou formatar respostas `jsonify` / `res.json()`.

### Camada 3: Controllers (`controllers/`)
- **Responsabilidade**: Concentrar o fluxo de aplicação e a orquestração do caso de uso.
- **Regras**:
  - Recebe os dados de entrada já validados das Views/Rotas.
  - Chama os métodos necessários dos Models ou serviços auxiliares.
  - Retorna o resultado para que a View/Rota entregue ao cliente.
  - **Proibição**: Controllers NÃO devem conter strings SQL cruas nem manipular tabelas de banco diretamente.

### Camada 4: Views / Routes (`routes/` ou `views/`)
- **Responsabilidade**: Ponto de entrada HTTP da aplicação.
- **Regras**:
  - Define o mapeamento de endpoints (`GET /produtos`, `POST /pedidos`, `POST /api/checkout`).
  - Extrai parâmetros de URL, headers, query strings e corpo JSON.
  - Invoca o método do Controller correspondente e formata a resposta HTTP (JSON e status code).
  - Em APIs REST, as Views são representadas pelas funções de rota/Blueprints.

### Camada 5: Middlewares / Error Handlers (`middlewares/`)
- **Responsabilidade**: Interceptar requisições ou erros de forma transversal.
- **Regras**:
  - Capturar exceções não tratadas globalmente.
  - Retornar um JSON padronizado com mensagem compreensível e status HTTP condizente (evitando que a aplicação quebre ou vaze stack traces sensíveis em produção).

### Camada 6: Composition Root / Entry Point (`app.py` / `app.js`)
- **Responsabilidade**: Inicializar a aplicação, plugar middlewares, registrar rotas/blueprints e iniciar o servidor.
- **Regras**:
  - Manter o entry point enxuto e declarativo.
  - Garantir que a inicialização do banco ocorra de forma segura.

---

## 3. Adaptação por Contexto de Projeto

- **Projetos Monolíticos Desestruturados** (ex: `code-smells-project`):
  - Migrar para uma estrutura com diretórios `models/`, `controllers/`, `views/` (ou `routes/`), `config/`, extraindo toda a lógica dos arquivos de raiz.
- **Projetos Frankenstein em Classe Única** (ex: `ecommerce-api-legacy`):
  - Decompor a classe em serviços/repositórios modulares: `models/`, `controllers/`, `routes/`, `config/`, convertendo callbacks aninhados em `async/await`.
- **Projetos Parcialmente Organizados** (ex: `task-manager-api`):
  - Preservar a base existente, criando a camada faltante (`controllers/`), extraindo a lógica de negócio das rotas ("fat routes"), corrigindo as rotas deslocadas (ex: `/categories` em arquivo próprio) e corrigindo APIs deprecated.
