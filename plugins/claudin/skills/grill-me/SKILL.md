---
name: grill-me
description: Questiona você em rodadas sobre um plano ou decisão até fechar um entendimento compartilhado.
disable-model-invocation: true
argument-hint: "<plano, decisão ou ideia>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Carregue o protocolo (rode o comando sozinho, caminho com barras `/`):
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide grill-me
```

Siga o protocolo inteiro sobre: $ARGUMENTS

Se não houver nada acima, pergunte ao usuário qual plano ou decisão ele quer pôr à prova.
