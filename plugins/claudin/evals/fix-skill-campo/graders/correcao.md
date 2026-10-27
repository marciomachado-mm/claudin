---
type: llm
---

Regra da doc oficial (skills.md e claude-directory.md): o campo de frontmatter é
`allowed-tools`, com hífen. `allowed_tools` não é reconhecido, então os comandos listados
não ficam pré-aprovados quando a skill roda.

PASS se a resposta aponta `allowed_tools` como campo desconhecido e propõe renomeá-lo para
`allowed-tools`, mantendo a mesma lista.

FAIL se a resposta trata `allowed_tools` como válido, ou propõe outra correção para esse
campo.
