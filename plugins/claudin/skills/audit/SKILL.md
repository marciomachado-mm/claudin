---
name: audit
description: Audita a estrutura Claude Code de um repositório (CLAUDE.md, .claude/, skills, agentes, rules, permissões) e o custo de contexto fixo, com achados priorizados e a fonte de cada um. Use para auditar, revisar ou analisar a configuração de Claude Code de um projeto.
argument-hint: "<caminho-do-repo>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Audite a estrutura Claude Code do repositório em: $ARGUMENTS

Os comandos do claudin abaixo são pré-aprovados só na forma exata: rode cada um
**sozinho** (sem `cd`, `&&`, `;` ou `echo`) e escreva o caminho com barras `/`.

## 1. Resolva o alvo

Auditar o repositório errado gera um relatório que parece válido, então o alvo precisa ser
explícito:

- **Nada acima:** pergunte ao usuário qual caminho auditar, oferecendo o diretório atual
  como uma das opções. Só siga com a resposta
- **Caminho inexistente ou que não é pasta:** diga isso e pare
- **Sem `CLAUDE.md`, `AGENTS.md` e `.claude/`:** não há estrutura para auditar. Diga qual
  sinal de projeto encontrou (`package.json`, `pyproject.toml`, `go.mod`...) e pare
- **Plugin** (tem `.claude-plugin/plugin.json`): audite como plugin

## 2. Validador e guias

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <caminho> --json
```

Código 1 só significa que há achado `error`; a saída vale. Código 2 significa que não há
`.claude/` nem plugin: siga só com a leitura crítica do `CLAUDE.md`/`AGENTS.md`.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide anti-patterns writing-for-agents
```

## 3. Delegue a leitura crítica

Chame a tool Agent com `subagent_type` igual a `claudin:auditor`. O auditor não consegue
ler a pasta do plugin, então o prompt leva tudo:

- o caminho absoluto do alvo e se é projeto ou plugin
- a saída JSON do validador, completa
- o texto integral dos dois guias, como veio do comando acima

## 4. Confira o que ficou sem fonte

Para cada item que o auditor marcou como "não verificado", busque na doc oficial:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py docs "<termo ou regex>"
```

Para ler o contexto de um resultado, use
`python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py section <página> <linha>`, não o Read: a pasta
do plugin fica fora do projeto. Achou e confirma: cite `página.md:linha` como fonte. Achou e contradiz: corrija o achado.
Não achou: mantenha em "não verificado".

## 5. Apresente o relatório

Abra com o **caminho auditado**. Depois:

1. Resumo de 2 a 4 frases: o estado geral e o problema mais importante
2. Achados por severidade (erro → aviso → sugestão), em tabela: arquivo, problema,
   correção, fonte (regra do validador, guia ou `página.md:linha`)
3. Custo de contexto fixo estimado e os maiores cortes possíveis
4. O que segue sem verificação, se houver
5. Complementos para rodar no terminal do projeto: `/doctor prompt-audit` (instruções
   desatualizadas ou contraditórias, v2.1.283+) e `/skill-doctor` (custo e uso real de
   cada skill, v2.1.252+)
6. Se houver o que corrigir: "para aplicar, rode `/claudin:fix <caminho>`"

Não dê nota. O relatório é a lista de achados.
