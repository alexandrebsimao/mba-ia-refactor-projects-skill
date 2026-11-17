# Template de Relatório de Auditoria Arquitetural

Este documento define o formato padronizado obrigatório para a saída da **Fase 2 (Architecture Audit)** da Skill `refactor-arch`.

---

## Template Padrão

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <Linguagem> + <Framework>
Files:   <N> analyzed | ~<M> lines of code

## Summary
CRITICAL: <Qtd> | HIGH: <Qtd> | MEDIUM: <Qtd> | LOW: <Qtd>

## Findings

### [<SEVERIDADE>] <Nome do Anti-Pattern>
File: <caminho/relativo/do/arquivo>:<linha_ou_intervalo>
Description: <Descrição técnica clara e contextualizada do problema encontrado no código>
Impact: <Impacto concreto em arquitetura, segurança, performance ou manutenibilidade>
Recommendation: <Ação corretiva específica a ser executada na Fase 3>

[... Repetir para todos os findings encontrados ...]

================================
Total: <Total de achados> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras Obrigatórias do Relatório

1. **Ordenação Estrita**: Liste todos os achados em ordem decrescente de severidade: `CRITICAL` → `HIGH` → `MEDIUM` → `LOW`.
2. **Rastreabilidade Exata**: Todo finding deve indicar o caminho relativo real e o número de linha ou intervalo exato (ex: `src/service.js:42-89`, `app.py:8`).
3. **Consistência de Contadores**: Os números em `## Summary` devem corresponder exatamente à contagem real dos findings listados e somar o valor informado em `Total: <N> findings`.
4. **Cobertura de APIs Deprecated**: Sempre que o projeto utilizar APIs obsoletas da linguagem ou framework detectado, inclua um finding específico indicando a API obsoleta e o substituto moderno.
5. **Confirmação Obrigatória**: O relatório deve terminar com a pergunta `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e aguardar a resposta explícita do usuário antes de qualquer edição de arquivo.
