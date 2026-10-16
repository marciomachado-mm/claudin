---
name: design
description: Desenha a arquitetura Claude Code de um projeto (CLAUDE.md, rules, skills, agentes, hooks) em rodadas de perguntas, antes de criar qualquer arquivo.
disable-model-invocation: true
argument-hint: "<projeto ou problema>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Desenhe a estrutura Claude Code para: $ARGUMENTS

Nenhum arquivo é criado aqui. O resultado é um entendimento compartilhado que o
`/claudin:create-project` executa depois.

## 1. Prepare

Os comandos do claudin são pré-aprovados só na forma exata: rode cada um **sozinho**
(sem `cd`, `&&` ou `;`) e escreva o caminho com barras `/`.

Carregue os três guias: `grill-me` (o protocolo da conversa), `choosing-features`
(qual recurso para cada necessidade) e `anti-patterns` (o que não propor).
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide grill-me choosing-features anti-patterns
```


Se o projeto já existe no disco, mapeie antes de perguntar: manifestos da stack,
`CLAUDE.md`, `.claude/`, scripts de build e teste. Stack e estrutura são fatos, não
perguntas.

## 2. Questione em rodadas

Siga o protocolo grill-me. Quando o usuário ainda não descreveu nada, a primeira fronteira
sai daqui:

- que trabalho manual de hoje deveria acontecer sozinho
- quem usa: só ele, um time, ou outras pessoas
- que fluxo se repete o bastante para virar comando
- o que precisa acontecer **sempre**, sem depender de lembrar (candidato a hook)
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
