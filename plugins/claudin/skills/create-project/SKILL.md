---
name: create-project
description: Cria a estrutura Claude Code de um projeto (CLAUDE.md, .claude/, settings, .gitignore e as skills, agentes e hooks combinados), a partir de um desenho aprovado ou de poucas perguntas.
disable-model-invocation: true
argument-hint: "<caminho-do-projeto>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Crie a estrutura Claude Code do projeto em: $ARGUMENTS

Sem caminho acima, pergunte onde criar. Se a pasta já tem `.claude/` ou `CLAUDE.md`, não
sobrescreva: ofereça `/claudin:audit` e `/claudin:fix` e pare, a menos que o usuário
peça para completar o que falta.

## 1. Entrada

- **Houve um `/claudin:design` nesta conversa:** use o entendimento compartilhado como
  especificação
- **Não houve:** descubra a stack, os comandos de build e teste e a estrutura de pastas
  lendo o projeto. Pergunte só o que é decisão: quem usa o projeto (só o usuário ou um
  time), que fluxos viram skills, o que precisa de hook. Se o desenho tiver mais de duas
  ou três peças em aberto, sugira rodar `/claudin:design` antes

## 2. Monte o plano

Os comandos do claudin são pré-aprovados só na forma exata: rode cada um **sozinho**
(sem `cd`, `&&` ou `;`) e escreva o caminho com barras `/`.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide anti-patterns
```

A base:

| Arquivo | Conteúdo |
|---|---|
| `CLAUDE.md` | O que o projeto é, em uma frase; comandos reais de build, teste e execução; arquitetura em poucas linhas; convenções que o código não deixa óbvias. Curto: o que vale só para uma área vira rule |
| `.claude/settings.json` | `permissions` explícitas: `allow` só com os comandos que o projeto usa (ex: `Bash(npm test)`); `deny` com `Read(.env)`, `Read(.env.*)` e `Edit(.env)`: sem `./`, o nome casa em qualquer profundidade do projeto, enquanto `./.env` cobre só a raiz (`permissions.md`). Se o usuário quer isolamento real de comandos, aponte o sandbox (`sandboxing.md`) em vez de denys de Bash; ele roda em macOS, Linux e WSL2, não no Windows nativo |
| `.gitignore` | `CLAUDE.local.md` e `.claude/settings.local.json`, além do que a stack pede |
| `.claude/rules/*.md` | Só para convenção de uma área, com `paths:` |
| skills, agentes, hooks | Os combinados, cada um seguindo o mesmo processo de `/claudin:create-skill`, `/claudin:create-agent` e `/claudin:create-hook` |

Apresente a árvore completa e o conteúdo de cada arquivo. Espere a confirmação. Só então
escreva.

## 3. Valide

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <caminho>
```

Corrija o que for apontado. Termine com a árvore final e como verificar dentro de uma
sessão nova no projeto: `/context` para ver o que carrega e `/skills` para as skills.

Pronto quando todos os arquivos do plano existem e o validador não acusa erro.
