---
name: refactor-arch
description: Analisa, audita e refatora automaticamente qualquer projeto backend legado para o padrão MVC, independente da linguagem e framework.
---

# Skill: Refatoração Arquitetural Automatizada (refactor-arch)

Esta Skill atua como um Arquiteto de Software Especialista encarregado de modernizar codebases legadas através de um processo automatizado em 3 fases sequenciais:

1. **Fase 1 — Análise do Projeto**: Mapear a tecnologia, dependências, domínio e arquitetura atual.
2. **Fase 2 — Auditoria Arquitetural**: Mapear code smells e vulnerabilidades contra o catálogo de anti-patterns, emitir relatório padronizado e pausar para confirmação do usuário.
3. **Fase 3 — Refatoração e Validação**: Reestruturar o projeto no padrão MVC, eliminar os problemas encontrados e validar a inicialização e endpoints da aplicação.

---

## Arquivos de Referência Obrigatórios

Antes de iniciar cada fase, consulte os arquivos de referência localizados no diretório `references/`:

- **[references/project-analysis.md](references/project-analysis.md)**: Heurísticas para detecção de linguagem, framework, banco de dados e arquitetura.
- **[references/anti-patterns-catalog.md](references/anti-patterns-catalog.md)**: Catálogo com severidades padronizadas (CRITICAL, HIGH, MEDIUM, LOW) e detecção de APIs deprecated.
- **[references/audit-report-template.md](references/audit-report-template.md)**: Template de saída e regras de formatação do relatório de auditoria.
- **[references/architecture-guidelines.md](references/architecture-guidelines.md)**: Diretrizes e responsabilidades das camadas do padrão MVC.
- **[references/refactoring-playbook.md](references/refactoring-playbook.md)**: Padrões de transformação e exemplos de código Antes/Depois.

---

## Fase 1 — Análise do Projeto (Project Analysis)

### Procedimento:
1. Inspecione os manifestos do projeto (`requirements.txt`, `package.json`, etc.) para identificar a linguagem e frameworks utilizados.
2. Mapeie a arquitetura atual e as entidades de banco de dados (`loja.db`, `tasks.db`, queries `CREATE TABLE`, models ORM).
3. Identifique o domínio da aplicação (ex: E-commerce API, LMS com Checkout, Task Manager API).
4. Conte os arquivos fonte analisados e estime as linhas de código.
5. Emita o sumário padronizado no terminal:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Linguagem detectada>
Framework:     <Framework e versão>
Dependencies:  <Principais dependências>
Domain:        <Domínio detectado>
Architecture:  <Classificação da arquitetura atual>
Source files:  <Quantidade de arquivos analisados>
DB tables:     <Tabelas ou modelos detectados>
================================
```

---

## Fase 2 — Auditoria Arquitetural (Architecture Audit)

### Procedimento:
1. Leia e analise todos os arquivos de código-fonte do projeto.
2. Cruze o código contra o catálogo em `references/anti-patterns-catalog.md`, verificando:
   - **CRITICAL**: SQL Injection, queries arbitrárias, credenciais hardcoded, senhas expostas, God Classes.
   - **HIGH**: Regras de negócio em rotas/controllers, criptografia insegura, estado global mutável, callback hell.
   - **MEDIUM**: Queries N+1, falta de tratamento centralizado de erros, entidades órfãs.
   - **LOW**: APIs obsoletas/deprecated (`datetime.utcnow()`, `Model.query.get()`), números mágicos, nomes crípticos.
3. Classifique cada finding identificando o arquivo exato e linha ou intervalo de linhas.
4. Ordene os findings rigorosamente da maior severidade para a menor (`CRITICAL` -> `HIGH` -> `MEDIUM` -> `LOW`).
5. Gere o relatório formatado conforme `references/audit-report-template.md`.
6. Salve uma cópia do relatório gerado na pasta de relatórios `reports/audit-project-<N>.md`.
7. **Ponto de Parada Obrigatório**:
   Exiba a pergunta de confirmação e aguarde a resposta do usuário antes de prosseguir:
   ```
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```

---

## Fase 3 — Refatoração e Validação (Refactoring & Validation)

### Procedimento:
Após a confirmação (`y`), execute a refatoração completa aplicando as diretrizes de `references/architecture-guidelines.md` e o playbook de `references/refactoring-playbook.md`:

1. **Reestruturação em Camadas MVC**:
   - `config/`: Centralizar configurações lendo de variáveis de ambiente (`.env`).
   - `database/`: Isolar conexão com banco e gerenciamento de transações.
   - `models/`: Implementar modelos com queries parametrizadas ou ORM limpo.
   - `controllers/`: Implementar controllers desacoplados de HTTP puro, contendo as regras de negócio.
   - `routes/` (ou `views/`): Implementar rotas limpas mantendo 100% dos contratos e endpoints originais.
   - `middlewares/`: Criar manipulador global de erros e middlewares necessários.
   - `app.py` / `app.js`: Composition root simplificado.
2. **Correção de Todos os Anti-Patterns**:
   - Eliminar SQL Injection e queries arbitrárias.
   - Hash seguro de senhas com salting.
   - Eliminar N+1 queries com JOINs ou batching.
   - Substituir APIs deprecated por versões modernas suportadas.
3. **Validação da Aplicação**:
   - Inicializar o servidor da aplicação em background.
   - Testar a resposta de cada endpoint original (rotas GET, POST, PUT, DELETE, health check, relatórios).
   - Validar que a aplicação inicia sem erros e que zero anti-patterns permanecem.
4. Imprimir o sumário final da refatoração:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios criada>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```
