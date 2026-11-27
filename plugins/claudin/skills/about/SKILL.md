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

O comando também consulta o `plugin.json` da `main` no GitHub para saber se há versão nova.
Sem rede, ele só diz que não conseguiu conferir; isso não é erro.

Mostre a saída em português: nome e versão, e cada comando com a sua descrição. Depois,
a situação da versão, como o comando disse:

- **Versão nova:** dê os dois comandos para o usuário digitar, um de cada vez. Você não
  consegue rodar comandos `/plugin`; quem digita é ele
- **Pasta local:** explique que a atualização automática não traz versão nova nesse caso e
  dê as duas saídas que o comando listou
- **Não conferiu:** diga em uma frase, sem insistir

Diga que o claudin está em construção e que instalação, novidades e como reportar um
problema ficam em https://github.com/marciomachado-mm/claudin.
