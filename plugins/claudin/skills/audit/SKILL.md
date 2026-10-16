---
name: audit
description: Audita a estrutura Claude Code de um repositório (CLAUDE.md, .claude/, skills, agentes, rules, permissões) e o custo de contexto fixo, com achados priorizados e a fonte de cada um. Use para auditar, revisar ou analisar a configuração de Claude Code de um projeto.
argument-hint: "<caminho-do-repo>"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
---

Audite a estrutura Claude Code do repositório em: $ARGUMENTS

## 1. Resolva o alvo

Auditar o repositório errado gera um relatório que parece válido, então o alvo precisa ser
explícito:

- **Nada acima:** pergunte ao usuário qual caminho auditar, oferecendo o diretório atual
  como uma das opções. Só siga com a resposta
- **Caminho inexistente ou que não é pasta:** diga isso e pare
- **Sem `CLAUDE.md`, `AGENTS.md` e `.claude/`:** não há estrutura para auditar. Diga qual
  sinal de projeto encontrou (`package.json`, `pyproject.toml`, `go.mod`...) e pare
- **Plugin** (tem `.claude-plugin/plugin.json`): audite como plugin

## 2. Rode o validador

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <caminho> --json
```

Ele cobre o que é mecânico, cada achado com o ID da regra. Código de saída 1 só significa
que há achado de severidade `error`; a saída continua válida. Código 2 significa que não há
`.claude/` nem plugin: siga com a leitura crítica do `CLAUDE.md`/`AGENTS.md`, sem achados
do validador.

## 3. Delegue a leitura crítica

Chame a tool Agent com `subagent_type` igual a `claudin:auditor`. No prompt, passe:

- o caminho absoluto do alvo e se é projeto ou plugin
- a saída JSON do validador, completa
- os guias: `${CLAUDE_PLUGIN_ROOT}/knowledge/guides/anti-patterns.md` e
  `${CLAUDE_PLUGIN_ROOT}/knowledge/guides/writing-for-agents.md`
- a pasta de snapshots para verificar afirmações:
  `${CLAUDE_PLUGIN_ROOT}/knowledge/snapshots/`

## 4. Apresente o relatório

Abra com o **caminho auditado**. Depois:

1. Resumo de 2 a 4 frases: o estado geral e o problema mais importante
2. Achados por severidade (erro → aviso → sugestão), em tabela: arquivo, problema,
   correção, fonte (regra do validador ou snapshot)
3. Custo de contexto fixo estimado e os maiores cortes possíveis
4. O que vale rodar em complemento, no terminal do projeto: `/doctor prompt-audit`
   (instruções desatualizadas ou contraditórias, v2.1.283+, `memory.md`) e `/skill-doctor`
   (custo e uso real de cada skill, v2.1.252+, `skills.md`)
5. Se houver o que corrigir: "para aplicar, rode `/claudin:fix <caminho>`"

Não dê nota. O relatório é a lista de achados.
