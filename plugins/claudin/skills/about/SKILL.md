---
name: about
description: Mostra a versão do claudin instalada e o que ele oferece hoje.
disable-model-invocation: true
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Rode este comando sozinho, com o caminho escrito com barras `/`:
Use `python` no Windows; no Linux ou macOS, se `python` não existir, use `python3` no lugar, com o resto do comando igual.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py about
```

Mostre a saída em português: nome e versão, e cada comando com a sua descrição. Diga que o
claudin está em construção e que o roadmap fica em https://github.com/marciomachado-mm/claudin.
