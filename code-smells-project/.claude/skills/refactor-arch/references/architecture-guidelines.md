# Diretrizes de Arquitetura Alvo (Padrão MVC)

Este guia estabelece as regras estruturais e responsabilidades das camadas para a **Fase 3 (Refatoração Arquitetural)** da Skill `refactor-arch`, aplicáveis a qualquer stack backend (Python, Node.js, Go, Java, Ruby, C#, PHP).

---

## 1. Princípios Fundamentais

1. **Separação de Responsabilidades (SRP)**: cada módulo e cada camada tem uma única responsabilidade bem delimitada.
2. **Fluxo Unidirecional de Dependências**:
   `Views/Routes → Controllers → (Services) → Models → Database`
3. **Preservação Contratual**: URLs, métodos HTTP, parâmetros, formatos de resposta e códigos de status dos endpoints legítimos devem permanecer compatíveis após a refatoração.
4. **Configuração Externalizada**: nenhuma credencial, chave secreta ou configuração específica de ambiente deve ficar hardcoded no código-fonte.
5. **Respeito às Dependências Instaladas**: evite introduzir pacotes externos não declarados no manifesto do projeto, preferindo bibliotecas padrão da linguagem ou dependências já presentes.

---

## 2. Estrutura de Diretórios MVC Alvo

```text
<raiz ou src>/
├── config/                  # Carregamento de variáveis de ambiente e constantes
├── database/                # Conexão, inicialização de schema, ciclo de vida/pool
├── models/                  # Entidades de domínio, ORM e queries parametrizadas
├── controllers/             # Orquestração de casos de uso e regras de negócio
├── routes/ (ou views/)      # Mapeamento HTTP (endpoints, blueprints, routers)
├── services/ (opcional)     # Integrações externas, criptografia, cache, notificações
├── middlewares/             # Tratamento centralizado de erros e middlewares HTTP
└── app.<ext>                # Composition Root / Entry Point
```

---

## 3. Responsabilidades e Limites de Cada Camada

### Config (`config/`)
- **Faz**: lê variáveis de ambiente (`os.getenv`, `process.env`, etc.) com fallbacks seguros para desenvolvimento e expõe um objeto de configuração imutável.
- **Não faz**: nunca armazena segredos de produção literais nem executa lógica de negócio.

### Database (`database/`)
- **Faz**: gerencia conexão, inicialização de tabelas/seeds (quando aplicável), encerramento por ciclo de requisição (teardown) ou wrapper assíncrono (Promises).
- **Não faz**: não contém regras de negócio de domínio nem roteamento HTTP.

### Models (`models/`)
- **Faz**: abstrai persistência de cada entidade de domínio (1 arquivo por domínio), executa queries parametrizadas ou operações ORM otimizadas (JOINs / eager loading), aplica hash seguro de senhas e serializa dados **omitindo campos sensíveis**.
- **Não faz**: **nunca** importa objetos HTTP (`request`, `res`, `jsonify`), nunca decide status codes HTTP e nunca concentra múltiplos domínios no mesmo arquivo.

### Controllers (`controllers/`)
- **Faz**: concentra o fluxo da aplicação, valida entradas de negócio, coordena chamadas a um ou mais Models/Services e devolve o resultado estruturado para a camada de rota/view.
- **Não faz**: **nunca** escreve SQL bruto, nunca acessa diretamente drivers/cursores de banco de dados e nunca duplica lógica que pertence a um Model ou Service.

### Views / Routes (`routes/` ou `views/`)
- **Faz**: mapeia URLs e métodos HTTP para os métodos de Controller correspondentes (ex: Flask Blueprints, Express Routers), separando um arquivo de rotas por domínio sem duplicar registros de URL.
- **Não faz**: não contém regras de negócio, queries ao banco, transações (`commit`/`rollback`) nem lógica de cálculo.

### Middlewares / Error Handlers (`middlewares/`)
- **Faz**: captura exceções e erros HTTP de forma centralizada, registra logs apropriados e devolve respostas JSON padronizadas sem vazar stack traces ou segredos.
- **Não faz**: não silencia erros sem registro (evitar bare `except:` / `catch` vazio).

### Composition Root / Entry Point (`app.<ext>`)
- **Faz**: instancia o app do framework, carrega configuração, inicializa o banco, registra middlewares de erro, monta os routers/blueprints e inicia o servidor quando executado diretamente.
- **Não faz**: não define queries SQL, regras de negócio nem handlers longos inline.

---

## 4. Adaptação ao Nível de Maturidade do Projeto

A Fase 3 deve se adaptar ao ponto de partida detectado na Fase 1:

1. **Monolito Plano / Procedural**: criar a árvore MVC completa (ex: dentro de `src/`), decompor arquivos monolíticos por domínio, remover arquivos legados obsoletos da raiz e manter um entry point claro.
2. **Monolito em God Class Única**: extrair cada responsabilidade da classe (conexão/DDL, modelos por entidade, serviços auxiliares, controllers assíncronos e routers) para módulos MVC independentes, removendo a God Class.
3. **Projeto Parcialmente Organizado**: respeitar a estrutura base existente (`models/`, `routes/`, `services/`, `utils/`), introduzir as camadas faltantes (`config/`, `controllers/`, `middlewares/`), migrar regras de negócio das rotas inchadas para os controllers, separar domínios misturados em arquivos próprios e higienizar todos os arquivos auxiliares (como `utils/` e `seed`).
