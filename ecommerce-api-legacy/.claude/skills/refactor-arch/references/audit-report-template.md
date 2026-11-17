# Template de Relatório de Auditoria Arquitetural

Este documento define o formato padronizado que o relatório da **Fase 2 (Architecture Audit)** deve seguir. A Skill deve gerar a saída no terminal e persistir o arquivo em `reports/audit-project-{1,2,3}.md`.

---

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
File: <caminho/do/arquivo>:<linha_inicio>-<linha_fim>
Description: <Descrição clara e contextualizada do problema encontrado>
Impact: <Impacto arquitetural, de segurança, manutenibilidade ou performance>
Recommendation: <Ação corretiva recomendada para a Fase 3>

[... Repetir para cada finding identificado, ordenado por severidade: CRITICAL -> HIGH -> MEDIUM -> LOW ...]

================================
Total: <Total de achados> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras de Formatação dos Findings:
1. **Ordenação Obrigatória**: Os achados devem estar estritamente ordenados da maior para a menor severidade (`CRITICAL` -> `HIGH` -> `MEDIUM` -> `LOW`).
2. **Localização Exata**: O campo `File` deve conter o caminho relativo do arquivo acompanhado da linha exata ou intervalo de linhas (ex: `models.py:1-350` ou `app.py:8`).
3. **Mínimo de Findings**: O relatório deve conter no mínimo 5 findings documentados, contendo pelo menos 1 de severidade `CRITICAL` ou `HIGH`.
4. **Pausa para Confirmação**: A skill deve obrigatoriamente pausar a execução ao final do relatório e solicitar a aprovação explícita do usuário (`[y/n]`) antes de iniciar qualquer modificação no código.
