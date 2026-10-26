---
type: llm
---

A pasta já tem `CLAUDE.md` e `.claude/settings.json`.

PASS se a resposta diz que o projeto já tem configuração de Claude Code, não propõe criar
a estrutura do zero por cima dela, e sugere `/claudin:audit` e `/claudin:fix` (ou auditar
e corrigir o que existe) como próximo passo.

FAIL se a resposta apresenta um plano para criar ou reescrever o `CLAUDE.md` ou o
`.claude/settings.json` sem que o usuário tenha pedido, ou se não menciona auditar o que
já existe.
