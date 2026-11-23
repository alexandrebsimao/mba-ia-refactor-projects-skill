---
name: refactor-arch
description: Analisa, audita e refatora automaticamente qualquer projeto backend legado para o padrão MVC (Model-View-Controller), independente da linguagem ou framework.
---

# Skill: Refatoração Arquitetural Automatizada (`refactor-arch`)

Atue como um Arquiteto de Software Especialista responsável por analisar, auditar e refatorar qualquer codebase backend para o padrão **MVC (Model-View-Controller)**, de forma agnóstica de tecnologia, preservando integralmente os contratos da aplicação.

Execute rigorosamente as **3 fases sequenciais** abaixo. **Nunca pule fases** e **nunca modifique arquivos antes da confirmação explícita do usuário ao final da Fase 2**.

---

## Arquivos de Referência

Consulte os documentos em `references/` antes de executar cada fase:

- **[references/project-analysis.md](references/project-analysis.md)** — Heurísticas para detecção de linguagem, framework, banco de dados, domínio e arquitetura atual (Fase 1).
- **[references/anti-patterns-catalog.md](references/anti-patterns-catalog.md)** — Catálogo de anti-patterns, sinais de detecção, severidades (CRITICAL, HIGH, MEDIUM, LOW) e APIs deprecated (Fase 2).
- **[references/audit-report-template.md](references/audit-report-template.md)** — Template obrigatório do relatório de auditoria (Fase 2).
- **[references/architecture-guidelines.md](references/architecture-guidelines.md)** — Regras e responsabilidades das camadas do padrão MVC alvo e adaptação por maturidade do projeto (Fase 3).
- **[references/refactoring-playbook.md](references/refactoring-playbook.md)** — Padrões concretos de transformação com exemplos Antes/Depois multi-stack (Fase 3).

---

## Fase 1 — Análise do Projeto (Somente Leitura)

Consulte `references/project-analysis.md` e execute:

1. Liste a árvore de arquivos do projeto ignorando diretórios de dependências, caches, ambientes virtuais e controle de versão (`node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `.git/`, `.claude/`).
2. Inspecione manifestos e arquivos de configuração (`requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, `Gemfile`, etc.) para detectar **linguagem**, **framework (com versão)** e **dependências principais**.
3. Leia os arquivos-fonte para identificar:
   - **Domínio da aplicação** (a partir dos endpoints, entidades e regras de negócio).
   - **Arquitetura atual** (monolito procedural, God Class única, arquitetura parcialmente em camadas, etc.).
   - **Banco de dados e tabelas/modelos** (SQL DDL, ORM models, drivers).
   - **Contratos de API existentes** (rotas, métodos HTTP, payloads e formatos de resposta que devem ser preservados).
4. Conte exatamente quantos arquivos-fonte foram analisados e o total aproximado de linhas de código.
5. Imprima o sumário no formato exato abaixo:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Linguagem detectada>
Framework:     <Framework e versão>
Dependencies:  <Principais dependências>
Domain:        <Descrição concisa do domínio da aplicação>
Architecture:  <Descrição da arquitetura atual encontrada>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/coleções/modelos detectados>
================================
```

---

## Fase 2 — Auditoria Arquitetural (Somente Leitura)

Consulte `references/anti-patterns-catalog.md` e `references/audit-report-template.md` e execute:

1. Analise linha a linha todos os arquivos-fonte mapeados na Fase 1, sem modificar nenhum arquivo.
2. Cruze o código contra o catálogo de anti-patterns, verificando obrigatoriamente:
   - **CRITICAL**: SQL Injection / execução arbitrária de SQL, credenciais hardcoded, exposição de segredos ou dados sensíveis em respostas/logs, God Class / God Module.
   - **HIGH**: Regras de negócio pesadas em rotas/controllers ("Fat Routes"), acoplamento direto ao banco em controllers, ausência de injeção/desacoplamento, criptografia fraca/caseira ou senhas em texto plano, estado global mutável, Callback Hell.
   - **MEDIUM**: Queries N+1, ausência de tratamento centralizado de erros / bare `except:`, validações ausentes ou duplicação excessiva de código, violação de integridade referencial (registros órfãos), uso de APIs deprecated.
   - **LOW**: Magic numbers / magic strings, nomenclatura críptica, `print`/`console.log` de debug e imports não utilizados.
3. Para cada achado, registre o **caminho relativo exato do arquivo e os números de linha precisos** (`arquivo:linha` ou `arquivo:inicio-fim`).
4. Ordene todos os findings estritamente da maior para a menor severidade: **CRITICAL → HIGH → MEDIUM → LOW**.
5. Imprima o relatório completo seguindo fielmente `references/audit-report-template.md`.
6. **PARADA OBRIGATÓRIA PARA CONFIRMAÇÃO**:
   - **NUNCA** edite, crie ou remova arquivos durante as Fases 1 e 2.
   - Encerre o turno exibindo exatamente a pergunta abaixo e aguarde a resposta do usuário:
     ```text
     Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
     ```
   - Se o usuário responder `n` (ou recusar), finalize a execução sem alterar nenhum arquivo.

---

## Fase 3 — Refatoração para MVC e Validação

Somente após confirmação explícita (`y`) do usuário, consulte `references/architecture-guidelines.md` e `references/refactoring-playbook.md` e execute:

1. **Rastreabilidade 1-para-1 com a Fase 2 (Aplicação Integral das Recomendações)**:
   - Percorra **cada finding** do relatório da Fase 2 e aplique sua recomendação **por inteiro**, sem implementações parciais.
   - Se uma recomendação determinar a migração de regras de negócio da camada de dados para controllers e/ou services (ex: cálculos de pedidos **e** cálculos de relatórios/descontos), migre **todos os domínios citados** — nunca deixe cálculos de domínio dentro de um Model apenas movendo o arquivo para `models/`.
2. **Adapte a Estratégia ao Contexto do Projeto**:
   - **Monolito desestruturado ou God Class**: crie a estrutura MVC completa (`config/`, `database/`, `models/`, `services/` quando houver regras/cálculos de domínio, `controllers/`, `routes/` ou `views/`, `middlewares/`, entry point limpo) e remova os arquivos monolíticos obsoletos.
   - **Projeto parcialmente organizado**: preserve o que já funciona bem, crie as camadas ausentes (ex: `controllers/`, `services/`, `config/`, `middlewares/`), extraia regras de negócio de rotas inchadas, corrija módulos com domínios misturados e elimine todos os anti-patterns sem quebrar a organização existente.
3. **Aplique as Camadas MVC e Elimine os Findings**:
   - **Config**: extraia todas as credenciais e parâmetros de ambiente para um módulo de configuração lendo variáveis de ambiente com fallbacks seguros (sem introduzir dependências não instaladas).
   - **Models**: isole **exclusivamente** persistência, queries SQL/ORM parametrizadas, JOINs/eager loading (eliminando N+1), hashing seguro de senhas e serialização sanitizada — **nunca** inclua regras de negócio procedurais (como faixas de desconto, cálculos financeiros, ticket médio ou orquestração) no mesmo método que executa consultas SQL.
   - **Services (`services/`)**: extraia regras de negócio, cálculos de domínio reutilizáveis (ex: descontos progressivos, agregações de relatórios, pagamentos, criptografia, cache) para módulos dedicados em `services/`, consumindo dados brutos dos Models.
   - **Controllers**: concentre o fluxo de aplicação e orquestração chamando Services e Models, **sem SQL bruto**, sem acesso direto a drivers de banco e sem atuar como mero passthrough para um Model que ainda carrega lógica de negócio.
   - **Views / Routes**: mantenha rotas enxutas, preservando **100% dos endpoints, métodos HTTP e contratos originais**.
   - **Middlewares / Error Handlers**: implemente tratamento centralizado de erros e remova bare `except:` / blocos repetitivos.
   - **APIs Deprecated**: substitua todas as chamadas obsoletas detectadas pelo equivalente moderno da stack.
   - **Entry Point**: mantenha um composition root limpo que inicializa banco, registra middlewares e conecta rotas.
4. **Verificação Pós-Refatoração (Zero Anti-Patterns)**:
   - Faça uma conferência item a item de **todos os findings da Fase 2** contra o código refatorado, verificando explicitamente se cada recomendação foi cumprida integralmente (incluindo `models/`, `services/`, `controllers/`, `routes/`, `utils/` e `seed`).
   - Confirme que nenhum Model mistura consultas SQL com cálculos de regra de negócio.
5. **Validação Funcional Obrigatória**:
   - Verifique que a aplicação inicia sem erros de sintaxe, importação ou runtime.
   - Exercite os endpoints originais (via test client nativo do framework ou subindo o servidor em background, executando requisições HTTP e encerrando o processo ao final).
   - Se qualquer erro ocorrer, corrija e valide novamente antes de concluir.
6. **Emita o Sumário Final**:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore real dos diretórios e arquivos criados/refatorados>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```
