---
type: llm
---

Regra da doc oficial (sub-agents.md): em `disallowedTools`, uma entrada com especificador,
como `Bash(git push *)`, remove a tool inteira. O agente `revisor` fica sem Bash e não
consegue rodar `git diff` nem os testes. Para bloquear só o push, a regra vai em
`permissions.deny` de um settings.

PASS se a resposta diz que `disallowedTools: Bash(git push *)` tira o Bash inteiro do
agente e propõe remover essa linha e pôr `Bash(git push *)` em `permissions.deny` (no
`.claude/settings.json` ou equivalente).

FAIL se a resposta trata `Bash(git push *)` em `disallowedTools` como bloqueio só do push,
ou não propõe mover a restrição para `permissions.deny`.
