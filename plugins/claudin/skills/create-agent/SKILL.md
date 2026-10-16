---
name: create-agent
description: Cria um subagente num projeto, checando antes se subagente é o recurso certo, com tools mínimas e description que faz o Claude delegar.
disable-model-invocation: true
argument-hint: "<o que o agente deve fazer>"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
---

Crie um subagente para: $ARGUMENTS

Se não houver descrição acima, pergunte o que o agente deve fazer. O destino é
`.claude/agents/` do projeto atual, salvo se o usuário indicar outro.

## 1. É subagente mesmo?

Leia `${CLAUDE_PLUGIN_ROOT}/knowledge/guides/choosing-features.md`. Subagente serve para
**isolar contexto**: começa do zero, não vê a conversa, não pergunta nada ao usuário e
devolve um resumo. Se a tarefa precisa conversar, ou se o resultado detalhado precisa
voltar inteiro, proponha o recurso certo (skill, rule, hook) e pare aqui, a menos que o
usuário insista.

## 2. Decida as peças

Descubra o que puder no repositório antes de perguntar. Pergunte só o que é decisão:

- **`tools`:** a lista mínima que o trabalho exige. Sem o campo, o agente herda todas as
  tools. `tools` aceita nomes exatos e `mcp__servidor`; para restringir comandos de Bash,
  use `permissions` no settings, não `Bash(...)` em `tools`. `Agent` em `tools` deixa o
  agente criar subagentes, até 3 níveis abaixo da conversa por padrão
  (`sub-agents.md`)
- **`model`:** `haiku` se a saída é mecânica; omita o campo se exige julgamento
- **`description`:** diga **quando** delegar, não só o que o agente é. Vaga, o Claude não
  delega
- **Corpo:** papel, passos, critério de conclusão, formato de saída fixo. Lembre que o
  agente não tem a conversa: tudo que ele precisa vem do prompt de quem chama ou do corpo

Campos opcionais, só se houver motivo: `maxTurns`, `skills` (pré-carrega o conteúdo
inteiro), `memory` (`user`, `project`, `local`), `isolation: worktree`, `background`,
`effort`, `color`, `autoCompactWindow` (inteiro puro de 100000 a 1000000, v2.1.296+),
`omitClaudeMd`.

**`permissionMode` não garante restrição:** se a conversa principal está em
`bypassPermissions`, `acceptEdits` ou auto, o subagente roda nesse modo e o campo é
ignorado (`sub-agents.md` § Permission modes). Desde a v2.1.283 auto é o modo inicial no
terminal e no VS Code. Restrição que vale sempre vem de `tools` e `permissions`.

## 3. Proponha e confirme

Use `${CLAUDE_SKILL_DIR}/templates/agent.md` como base. Mostre o arquivo completo e
espere a confirmação. Só então escreva `.claude/agents/<nome>.md`. `name` em minúsculas e
hífens, sem `:`.

## 4. Valide

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <raiz-do-projeto>
```

Corrija o que o validador apontar no arquivo novo. Pronto quando o arquivo existe e o
validador não acusa nada nele.
