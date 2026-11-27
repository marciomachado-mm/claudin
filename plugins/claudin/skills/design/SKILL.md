---
name: design
description: Desenha a arquitetura Claude Code de um projeto (CLAUDE.md, rules, skills, agentes, hooks) em rodadas de perguntas, antes de criar qualquer arquivo.
disable-model-invocation: true
argument-hint: "<projeto ou problema>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py *)
---

Desenhe a estrutura Claude Code para: $ARGUMENTS

Nenhum arquivo é criado aqui. O resultado é um entendimento compartilhado que o
`/claudin:create-project` executa depois.

## 1. Prepare

Os comandos do claudin são pré-aprovados só na forma exata: rode cada um **sozinho**
(sem `cd`, `&&` ou `;`) e escreva o caminho com barras `/`.
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.

Carregue os quatro guias: `brainstorm` e `grill-me` (os dois modos da conversa),
`choosing-features` (qual recurso para cada necessidade) e `anti-patterns` (o que não
propor).
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide brainstorm grill-me choosing-features anti-patterns
```


Se o projeto já existe no disco, mapeie antes de perguntar: manifestos da stack,
`CLAUDE.md`, `.claude/`, scripts de build e teste. Stack e estrutura são fatos, não
perguntas.

Se o projeto já existe, pergunte também se quer incluir o histórico de sessões dele (padrão:
não). Com o sim, rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py <caminho> --json` e
`python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide usage-evidence`, siga as regras de
privacidade do guia e use os agregados em "Fatos apurados": eles respondem perguntas sem
precisar fazê-las (ex.: quais skills ninguém usa, onde o trabalho trava).

## 2. Converse, depois feche as decisões

A conversa tem dois modos, e você troca de um para o outro sem anunciar.

**Ideia ainda vaga** (o usuário não sabe bem o que quer automatizar, ou só descreveu o
projeto): comece no modo do guia `brainstorm`. Entenda o problema, devolva-o consolidado e
abra caminhos de estrutura. Siga nele até aparecer uma direção que o usuário quer; aqui,
o fim do brainstorm é passar a fechar as decisões, sem oferecer outra skill.

**Direção clara:** feche as decisões com o protocolo `grill-me`, perguntando **só o que muda
a arquitetura**. O resto, assuma com o padrão mais simples e diga o que assumiu, para o
usuário corrigir se quiser ("assumi que só você usa, então nada de skill compartilhada").

Estes pontos precisam estar resolvidos antes da proposta, por pergunta, por fato do
projeto ou por suposição declarada. Não são um questionário:

- que trabalho manual de hoje deveria acontecer sozinho
- quem usa: só ele, um time, ou outras pessoas
- que fluxo se repete o bastante para virar comando
- o que precisa acontecer **sempre**, sem depender de lembrar (candidato a hook)
- que segredo local o projeto terá (`.env`, token de API, credencial de banco). Este sempre
  vira pergunta quando o projeto fala com API, banco ou serviço. Com segredo, o `deny` de
  `Read` e `Edit` dele é a recomendação padrão, mesmo que o usuário não tenha pedido nada
  "sempre"; se ele recusar, o risco vai para **Descartado**
- que decisão já está tomada e não deve ser revisitada

## 3. Proponha a arquitetura

Com a fronteira vazia, apresente:

1. Um diagrama em texto do fluxo:
   ```
   Usuário
     ├─► /skill-a ──► agente-x ──► resumo
     └─► hook PostToolUse ──► lint
   ```
2. Para cada peça: o que faz, que problema resolve, a alternativa descartada e por quê, e
   o modelo (agente) ou quem chama (skill)
3. O custo de contexto fixo que a estrutura adiciona, peça por peça

Mínimo necessário: cada peça resolve um problema que o usuário confirmou. Nada
especulativo.

## 4. Feche

Entregue o "Entendimento compartilhado" do protocolo, sem tools nesse turno. No **Próximo
passo**, indique `/claudin:create-project` para gerar os arquivos a partir deste desenho.
