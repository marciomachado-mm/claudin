---
name: audit
description: Audita a estrutura Claude Code de um repositório (CLAUDE.md, .claude/, skills, agentes, rules, permissões) e o custo de contexto fixo, com achados priorizados e a fonte de cada um. Use para auditar, revisar ou analisar a configuração de Claude Code de um projeto.
argument-hint: "<caminho-do-repo>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py *)
---

Audite a estrutura Claude Code do repositório em: $ARGUMENTS

Os comandos do claudin abaixo são pré-aprovados só na forma exata: rode cada um
**sozinho** (sem `cd`, `&&`, `;` ou `echo`) e escreva o caminho com barras `/`.
Use `python` no Windows; no Linux ou macOS, se `python` não existir, use `python3` no lugar, com o resto do comando igual.

## 1. Resolva o alvo

Auditar o repositório errado gera um relatório que parece válido, então o alvo precisa ser
explícito:

- **Nada acima, mas o usuário já nomeou o alvo na conversa** ("audite este repo", "o
  market_data", um caminho): use esse alvo e diga qual caminho resolveu. "Este repo" e
  "aqui" são o diretório atual
- **Nada acima nem na conversa:** pergunte ao usuário qual caminho auditar, oferecendo o
  diretório atual como uma das opções. Só siga com a resposta
- **Caminho inexistente ou que não é pasta:** diga isso e pare
- **Sem `CLAUDE.md`, `AGENTS.md` e `.claude/`:** não há estrutura para auditar. Diga qual
  sinal de projeto encontrou (`package.json`, `pyproject.toml`, `go.mod`...) e pare
- **Plugin** (tem `.claude-plugin/plugin.json`): audite como plugin

## 2. Validador e guias

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <caminho> --json
```

Código 1 só significa que há achado `error`; a saída vale. Código 2 significa que não há
estrutura Claude Code nenhuma no caminho.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide anti-patterns writing-for-agents
```

## 3. Evidência de uso (opcional)

Pergunte ao usuário se quer incluir o histórico de sessões deste projeto: o script lê as
transcrições locais e devolve só contagens (erros por causa, bloqueios de hook, uso de
skills, sessões pesadas). O padrão é não. Se não der para perguntar, pule este passo.

Com o sim:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py <caminho> --json
```

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide usage-evidence
```

Siga as regras de privacidade do guia. Código 2 significa que não há histórico para esse
projeto nesta máquina: diga isso e siga sem ele.

## 4. Leitura crítica

Feita aqui mesmo, sem subagente: nas sessões interativas o subagente roda em segundo plano
e o resultado chegaria fora deste fluxo (`sub-agents.md`, v2.1.302).

1. Mapeie o alvo: `CLAUDE.md` e `AGENTS.md` (raiz e subpastas), `CLAUDE.local.md`,
   `.claude/` (skills, agents, rules, commands, hooks, settings), `.mcp.json`, `.gitignore`.
   Em plugin: `skills/`, `agents/`, `hooks/`, `.mcp.json`. Leia cada arquivo do mapa
2. Os achados do validador já vêm explicados: não os repita, só use a severidade deles
3. Procure o que o validador não decide, com o catálogo de anti-padrões na mão:
   - skill com efeito colateral sem `disable-model-invocation: true`
   - description vaga, que não diz quando usar
   - agente sem `tools:` ou com tools além do que o corpo usa
   - `model:` fixo onde o trabalho exige julgamento
   - CLAUDE.md sem comandos, longo, ou repetindo o que o ambiente já diz
   - rule sem `paths:` que só vale para uma área
   - `settings.local.json` fora do `.gitignore`; settings sem `permissions`
   - instrução que contradiz outra, ou que o modelo já segue sozinho
4. Estime o contexto fixo por sessão (cerca de 4 caracteres por token): CLAUDE.md ou
   AGENTS.md carregado, rules sem `paths:`, descriptions de skills chamáveis pelo Claude,
   descriptions de agentes, servidores em `.mcp.json`. É estimativa: não inclui o prompt do
   sistema nem skills sincronizadas da claude.ai

5. Com evidência de uso: cruze cada sinal com a estrutura, pela tabela do guia
   `usage-evidence`. Achado que vem do histórico cita a contagem como fonte
   (ex.: "9 bloqueios em 30 dias")

Pronto quando cada arquivo do mapa foi lido e cada item da lista acima foi checado.

## 5. Confira na doc antes de afirmar

Todo comportamento do Claude Code que você for afirmar e que não esteja nos guias, busque
na doc oficial antes. Não afirme de memória:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py docs "<termo ou regex>"
```

Para ler o contexto de um resultado, use
`python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py section <página> <linha>`, não o Read: a pasta
do plugin fica fora do projeto. Achou e confirma: cite `página.md:linha` como fonte. Achou
e contradiz: corrija o achado. Não achou: o item vai para "não verificado".

## 6. Apresente o relatório

Abra com o **caminho auditado**. Depois:

1. Resumo de 2 a 4 frases: o estado geral e o problema mais importante
2. Achados por severidade (erro → aviso → sugestão), em tabela: arquivo, problema,
   correção, fonte (regra do validador, guia ou `página.md:linha`)
3. Custo de contexto fixo estimado e os maiores cortes possíveis
4. Com evidência de uso: a seção "Evidência de uso", com a janela, as contagens que
   sustentam achados e as ressalvas do guia
5. O que segue sem verificação, se houver
6. Complementos para rodar no terminal do projeto: `/doctor prompt-audit` (instruções
   desatualizadas ou contraditórias, v2.1.283+) e `/skill-doctor` (custo e uso real de
   cada skill, v2.1.252+)
7. Se houver o que corrigir: "para aplicar, rode `/claudin:fix <caminho>`"

Não dê nota. O relatório é a lista de achados.
