# Qual recurso usar

Guia que o `design` e os `create-*` consultam antes de propor qualquer peça. Destila
`features-overview.md` (§ Match features to your goal, § Context cost by feature); na
dúvida, a doc ganha.

## Pela necessidade

| Necessidade | Recurso | Custo de contexto |
|---|---|---|
| Convenção que vale em toda conversa ("use pnpm") | `CLAUDE.md` | todo turno |
| Convenção que só vale numa área do repo | rule com `paths:` | só quando o Claude lê ou edita arquivo correspondente |
| Fluxo que se repete e alguém dispara (`/deploy`) | skill | description em todo turno; zero com `disable-model-invocation: true` |
| Conhecimento que o Claude deve achar sozinho quando relevante | skill chamável pelo Claude | description em todo turno |
| Trabalho volumoso cujo detalhe não precisa voltar (varrer arquivos, pesquisar) | subagente | isolado da sessão principal |
| Algo que precisa acontecer **sempre** num evento (lint após editar, bloquear comando) | hook | zero, salvo se o hook devolver contexto |
| Dado ou ação de sistema externo (banco, Slack, navegador) | MCP | nomes das tools; schema completo sob demanda |
| Tom, formato ou papel da sessão inteira | output style | todo turno |
| Reusar o mesmo conjunto em vários repos ou distribuir | plugin | soma do que ele contém |

## Distinções que mais confundem

- **Skill ou rule?** Se alguém vai *querer chamar*, é skill. Se o Claude deve *já saber*, é
  rule (ou CLAUDE.md)
- **Skill ou subagente?** Skill roda no contexto principal e vê a conversa. Subagente
  começa do zero, não vê a conversa, não pode perguntar nada ao usuário
  (`AskUserQuestion` é removida, `sub-agents.md`) e devolve só um resumo. Use subagente
  para isolar contexto, não para conversar. Nas sessões interativas (terminal, VS Code,
  app desktop), o subagente chamado da conversa roda em segundo plano e o resultado chega
  depois, desde a v2.1.302. Se o fluxo precisa do resultado no mesmo turno, use uma skill
  com `context: fork` e `background: false` (`sub-agents.md`)
- **Instrução ou hook?** Instrução é seguida na maior parte das vezes; hook roda sempre.
  O que não pode falhar vira hook
- **Pergunta rápida sobre a conversa:** `/btw`, não subagente (`sub-agents.md`)

## Modelo de subagente

O critério é **quanto julgamento a saída exige**, não se o agente só lê:

- `haiku`: trabalho mecânico (buscar, extrair, converter)
- campo omitido (herda a sessão): trabalho com julgamento (priorizar, atribuir severidade,
  calibrar tom). Fixar `sonnet` rebaixa o agente numa sessão em Opus, porque o frontmatter
  ganha do modelo da conversa (`sub-agents.md` § Choose a model)
