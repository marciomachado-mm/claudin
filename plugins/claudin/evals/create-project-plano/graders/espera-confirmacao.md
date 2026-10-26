---
type: llm
---

PASS se a resposta apresenta a árvore de arquivos e o conteúdo de cada arquivo proposto
(no mínimo `CLAUDE.md` e `.claude/settings.json`), e termina pedindo a confirmação do
usuário antes de criar os arquivos.

FAIL se a resposta diz que já criou os arquivos, se não mostra o conteúdo do que vai
criar, ou se não pede confirmação.
