---
name: about
description: Mostra a versão do claudin instalada e o que ele oferece hoje.
disable-model-invocation: true
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Rode este comando sozinho, com o caminho escrito com barras `/`:
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py about
```

Mostre a saída em português: nome e versão, e cada comando com a sua descrição. Diga que o
claudin está em construção e que instalação, novidades e como reportar um problema ficam em
https://github.com/marciomachado-mm/claudin.
