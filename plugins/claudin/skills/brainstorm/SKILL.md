---
name: brainstorm
description: Pensa junto com você sobre uma ideia ou um problema, numa conversa leve, para encontrar caminhos e desenvolver a ideia, sem rodadas de perguntas e sem precisar virar projeto.
disable-model-invocation: true
argument-hint: "<ideia ou problema>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Carregue o protocolo (rode o comando sozinho, caminho com barras `/`):
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide brainstorm
```

Siga o protocolo sobre: $ARGUMENTS

Se não houver nada acima, pergunte ao usuário, numa frase, sobre o que ele quer pensar.
