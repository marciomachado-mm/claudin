---
name: create-hook
description: Cria um hook num projeto, escolhendo evento, matcher e handler e gerando o settings.json e o script com a semântica de saída certa para o evento.
disable-model-invocation: true
argument-hint: "<o que automatizar>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Crie um hook para: $ARGUMENTS

Se não houver descrição acima, pergunte o que deve acontecer e em que momento. O destino
é o `.claude/settings.json` do projeto atual, salvo se o usuário indicar outro escopo.

Hook é a peça com mais armadilhas silenciosas: o efeito do código de saída e o formato do
JSON de decisão **mudam por evento**. Todo detalhe abaixo se confere na doc oficial antes de escrever.

Os comandos do claudin são pré-aprovados só na forma exata: rode cada um **sozinho**
(sem `cd`, `&&` ou `;`) e escreva o caminho com barras `/`.
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py docs "<termo>" --page hooks
```

mostra as linhas de `hooks.md` sobre o termo (ex: o nome do evento ou `onFailure`).

## 1. É hook mesmo?

Hook é para o que precisa acontecer **sempre** num evento, sem depender de o Claude
lembrar. Se é preferência que o Claude pode seguir na maior parte das vezes, é instrução
(CLAUDE.md ou rule). Na dúvida:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide choosing-features
```


## 2. Evento e filtro

Mapeie a necessidade para o evento e busque a seção dele com `kb.py docs`:

| Necessidade | Evento |
|---|---|
| Bloquear ou validar antes de uma tool rodar | `PreToolUse` |
| Reagir depois de uma tool (lint, formatar) | `PostToolUse` |
| Validar ou enriquecer o prompt | `UserPromptSubmit` |
| Carregar contexto no início | `SessionStart` (só handlers `command` e `mcp_tool`) |
| Agir quando o Claude termina o turno | `Stop` |
| Reagir a arquivo alterado no disco, por qualquer um | `FileChanged` |

Defina o `matcher` (qual tool ou arquivo) e, em eventos de tool, o `if` com sintaxe de
regra de permissão (ex: `"Bash(rm *)"`), que restringe ainda mais quando o handler roda.

## 3. Handler

`command` (script, recebe o JSON do evento no stdin), `http`, `mcp_tool`, `prompt` ou
`agent`. Os padrões de `timeout` diferem por tipo e por evento (`hooks.md`, tabela de
campos).

## 4. Semântica que mais gera erro

Confira cada item na seção do evento escolhido:

- **Código de saída:** `0` é sucesso. `2` é o erro que bloqueia, e o que exatamente ele faz
  depende do evento (tabela "Exit code 2 behavior per event"). Qualquer outro código, ou
  falha ao iniciar, ou JSON inválido, é erro **não bloqueante**: a ação segue
- **Hook de proteção falha aberto por padrão.** Se ele quebrar, tudo passa. Em hook que
  protege algo, use `"onFailure": "block"` (v2.1.295+)
- **JSON de decisão** tem formato próprio por evento (ex: `permissionDecision` no
  `PreToolUse`). Para devolver decisão em JSON, saia com 0. Logs vão para stderr, nunca
  misturados ao JSON no stdout
- **Um mod instalado com `tool.check` pode aprovar o que o `PreToolUse` bloqueou**, seja
  qual for o arquivo do hook, a menos que a máquina tenha managed settings ou
  `managed-mcp.json`, ou que a sessão use login Team ou Enterprise (API key e
  `CLAUDE_CODE_OAUTH_TOKEN` não contam) (`permissions.md` § mods, `hooks-guide.md`). Para
  algo crítico, diga isso ao usuário
- **Prompt bloqueado não some do disco:** um `UserPromptSubmit` que bloqueia impede o
  prompt de chegar ao Claude, mas o texto continua no transcript. Hook que barra segredo
  não o mantém fora do disco (`hooks.md` § What a blocked prompt leaves behind)
- **Tool MCP:** decida confiança pelo `mcp_server.source` da entrada, não pelo nome do
  servidor, que quem configura escolhe à vontade

## 5. Proponha e confirme

Mostre o trecho do `settings.json` (formato: evento → lista de `{matcher, hooks: [...]}`)
e o script completo. Espere a confirmação. Só então escreva. Script em
`.claude/hooks/`, chamado por caminho relativo à raiz do projeto.

Script que precisa de interpretador vai na forma exec: o interpretador em `command` e o
caminho em `args` (`"args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/<script>"]`), que é o que
a doc pede quando há placeholder de caminho (`hooks.md`, Exec form and shell form). O nome
do interpretador muda por sistema (`python` no Windows, `python3` no Linux e no macOS) e o
`settings.json` vale para toda máquina que abrir o projeto: na proposta, diga qual nome
escolheu, para qual sistema, e que outro sistema precisa trocar. Com
`"onFailure": "block"`, um nome errado bloqueia a ação em vez de deixá-la passar.

## 6. Valide

1. `python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <raiz-do-projeto>` para o JSON do
   settings
2. Se for `command`, rode o script uma vez com um JSON de exemplo no stdin e confira a
   saída e o código de saída
3. Diga ao usuário como observar o hook disparando (ex: `claude --debug`)

No relatório, atribua cada verificação a quem a fez: o validador confere o JSON do
settings, não o hook (a última linha da saída dele diz o que cobre); o script, o matcher e
a decisão só o teste do passo 2 conferiu.

Pronto quando o settings é JSON válido, o script responde certo ao exemplo e o usuário
sabe como verificar na sessão.
