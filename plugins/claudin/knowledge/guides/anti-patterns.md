# Anti-padrões em projetos Claude Code

Catálogo que o `audit`, o `fix` e o `create-*` consultam. Cada linha cita o snapshot em
`knowledge/snapshots/` que a sustenta. O que o validador já detecta sozinho aparece com o ID
da regra; o resto exige leitura e julgamento.

## Estrutura

| Anti-padrão | Correto | Por quê | Fonte |
|---|---|---|---|
| `agents/` ou `skills/` na raiz do projeto | `.claude/agents/`, `.claude/skills/` | Fora de `.claude/` não são descobertos | `claude-directory.md` |
| Skill como arquivo solto (`skills/x.md`) | `skills/x/SKILL.md` | A descoberta procura `SKILL.md` dentro de uma pasta; pasta própria também permite arquivos de apoio | `skills.md` (SKILL-001) |
| Pasta de skill chamada `synced`, em qualquer caixa | Renomear | Nome reservado para skills sincronizadas da claude.ai; a skill é ignorada sem erro | `skills.md` § Reserved name |
| Nome de skill com `<`, `>`, espaço invisível ou duplicado | Renomear | O Claude Code recusa o nome e a skill não carrega (fora de plugin) | `skills.md` (SKILL-004) |
| `commands/` em projeto novo | `skills/` | Commands seguem funcionando e não precisam migrar; skills têm pasta de apoio e mais campos | `skills.md` |

## Permissões e segurança

| Anti-padrão | Correto | Por quê | Fonte |
|---|---|---|---|
| `Write(path)`, `NotebookEdit(path)`, `Glob(path)`, `Grep(path)` em permissões | `Edit(path)` ou `Read(path)` | Aceitas mas nunca consultadas, desde a v2.1.210 (`Tool(*)` e o nome sozinho valem para todo uso). Como ask, `Read(docs/**)` pergunta quando Grep ou Glob miram o caminho, mas não quando a busca parte de uma pasta acima | `permissions.md` (PERM-001) |
| `Bash(command:rm *)` | `Bash(rm *)` | Regra sobre o campo principal é ignorada | `permissions.md` (PERM-002) |
| `deny: Bash(rm -rf *)` tratado como proteção | Sandbox para isolamento real; deny como atrito | Padrões de Bash com argumentos são frágeis e contornáveis. O sandbox roda em macOS, Linux e WSL2; no Windows nativo os comandos rodam sem sandbox | `permissions.md` (PERM-003), `sandboxing.md` |
| `deny: Read(path)` esperando bloquear toda escrita | Somar `Edit(path)` ao deny | Deny de `Read` bloqueia Edit (v2.1.208+) e Write (v2.1.228+) no mesmo caminho, mas não NotebookEdit | `permissions.md` |
| Apontar `Edit(path)` ao lado de `Read(path)` no deny como redundante | Manter os dois; não é achado | Sem o `Edit`, o NotebookEdit altera o arquivo, e a doc recomenda o deny de `Edit` para caminho que nenhuma tool pode mudar | `permissions.md` |
| `.claudeignore` para esconder arquivos | `Read(.env)`, `Read(secrets/**)` em deny | O Claude Code não lê `.claudeignore` | `permissions.md` |
| `settings.json` sem `permissions` | `allow` e `deny` explícitos | Desde a v2.1.283 o modo inicial no terminal e no VS Code é auto: um classificador decide. `claude -p` e o Agent SDK começam em Manual desde a v2.1.302. Em qualquer modo, só deny explícito garante bloqueio | `permission-modes.md` |
| `autoMode` em settings do projeto | `~/.claude/settings.json` ou managed | O escopo de `autoMode` é usuário ou managed | `settings-reference.md` |
| Deny ou hook `PreToolUse` como garantia absoluta | Managed settings ou sandbox para o que é crítico | Um mod com `tool.check` responde depois das regras e dos hooks e pode trocar a decisão | `permissions.md` § mods |
| `deny: Read(./.env)` esperando cobrir o monorepo | `Read(.env)` | Com `./` a regra casa só na raiz; nome sem prefixo casa em qualquer profundidade do projeto | `permissions.md` (PERM-004) |
| `settings.local.json` commitado | No `.gitignore` | É override pessoal | `settings.md` |
| Settings com comentário ou vírgula sobrando | JSON estrito | O arquivo vira Settings Error e é ignorado | `settings.md` (SET-001) |

## Instruções (CLAUDE.md e rules)

| Anti-padrão | Correto | Por quê | Fonte |
|---|---|---|---|
| CLAUDE.md longo com instrução que só vale para uma área | Rule em `.claude/rules/` com `paths:` | Rule com `paths:` só carrega quando o Claude lê ou edita arquivo correspondente; CLAUDE.md carrega sempre | `memory.md` |
| CLAUDE.md sem comandos de build, teste e execução | Seção de comandos, ou ponteiro explícito para onde eles estão: `@README.md` (import, carrega junto) ou uma linha que nomeia o arquivo e a seção ("comandos em `README.md#Comandos`"). Com ponteiro para um arquivo que tem os comandos, não é achado: copiar duplica e as duas cópias divergem | É o que o Claude mais precisa para trabalhar sozinho | `best-practices.md`; import: `memory.md` |
| Rule com frontmatter que não faz parse | Corrigir o YAML; conferir com `claude --debug` | O frontmatter é ignorado e a rule carrega em **toda** sessão, sem erro visível | `memory.md` (FM-001) |
| Campo além de `paths` em rule | Só `paths` | Os outros são ignorados | `claude-directory.md` (RULE-001) |
| Instrução que o modelo já segue sozinho | Apagar | Custa contexto e não muda nada (ver `writing-for-agents.md`, no-op) | — |

## Skills

| Anti-padrão | Correto | Por quê | Fonte |
|---|---|---|---|
| Skill sem `description` | Description com o caso de uso principal primeiro | Sem ela, o Claude usa a primeira linha do corpo para decidir quando chamar | `skills.md` (SKILL-002) |
| `description` + `when_to_use` acima de 1.536 caracteres | Encurtar | O excesso é cortado na listagem | `skills.md` (SKILL-003) |
| Skill com efeito colateral (deploy, commit, envio) sem `disable-model-invocation: true` | Adicionar | O Claude pode disparar sozinho. Bônus: a description sai do contexto | `skills.md` |
| Skill que é só conhecimento de fundo aparecendo no menu `/` | `user-invocable: false` | Não é uma ação que o usuário tome | `skills.md` |
| Muitas skills automáticas que nunca são usadas | Desligar; medir com `/skill-doctor` (v2.1.252+) | Cada uma ocupa contexto em todo turno | `skills.md` § Find unused skills |

## Agentes

| Anti-padrão | Correto | Por quê | Fonte |
|---|---|---|---|
| Agente sem `tools:` | Lista mínima | Sem o campo, herda todas as tools | `sub-agents.md` |
| `Bash(git diff *)` em `tools` | `Bash` em tools + `permissions` para restringir comandos | `tools` aceita nome exato, `mcp__servidor` e `Agent(tipo)`; restrição por comando é papel das permissões | `sub-agents.md` (AGENT-006) |
| `disallowedTools: Bash(git push *)` esperando bloquear só o push | `permissions.deny` | Especificador em `disallowedTools` remove a tool inteira | `sub-agents.md` (AGENT-005) |
| `model:` fixo em todo agente | Fixar só onde o trabalho é mecânico; omitir para herdar | O frontmatter ganha do modelo da conversa: fixar `sonnet` rebaixa o agente numa sessão Opus. O critério é quanto julgamento a saída exige, não se o agente só lê | `sub-agents.md` § Choose a model |
| Campo em snake_case (`max_turns`) | camelCase exato (`maxTurns`) | Campo desconhecido é ignorado sem erro | `sub-agents.md` (AGENT-003) |
| `autoCompactWindow: 200k` | `200000` | `200k` vira 200, fica fora da faixa e é ignorado (v2.1.296+). Armadilha: a variável `CLAUDE_CODE_AUTO_COMPACT_WINDOW` aceita `200k` desde a v2.1.304, o frontmatter não | `sub-agents.md` (AGENT-004), `env-vars.md` |
| Agente de plugin dependendo de `hooks`, `mcpServers` ou `permissionMode` | Copiar o agente para `.claude/agents/` | Esses campos são ignorados em agente de plugin | `sub-agents.md` (AGENT-007) |
| `CLAUDE.md` de subpasta ou rule com `paths:` acima de 40.000 caracteres | Dividir em rules menores | Arquivo que carrega sob demanda acima do limite só entra pelo começo (janela de 200K; maior com 1M), desde a v2.1.309 | `memory.md` (INSTR-001) |
| Fluxo que precisa do resultado de um subagente no mesmo turno | Skill com `context: fork` e `background: false`, ou fazer o trabalho no thread principal | Nas sessões interativas o subagente chamado da conversa roda em segundo plano e o Claude não espera, desde a v2.1.302 (salvo com fork mode desligado) | `sub-agents.md` |
| Descrições de agentes somando mais de 15.000 tokens | Encurtar as descriptions, detalhe no corpo | Aviso no startup e roteamento pior | `sub-agents.md` |
