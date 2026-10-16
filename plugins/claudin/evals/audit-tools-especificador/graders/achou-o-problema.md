---
type: llm
---

PASS se a resposta aponta que `Bash(git diff *)` no campo `tools` do agente `reviewer` não
é a forma de restringir comandos (tools aceita nomes de tool; restrição de comando fica em
`permissions` do settings) e recomenda trocar por `Bash` com regra em permissions, ou tirar
o Bash do agente.

FAIL se a resposta não menciona o campo `tools` do `reviewer`, ou se trata
`Bash(git diff *)` em `tools` como correto.
