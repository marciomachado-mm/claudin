---
name: fix
description: Corrige a estrutura Claude Code de um repositório a partir de uma auditoria, com sua aprovação antes de editar e validação depois.
disable-model-invocation: true
argument-hint: "<caminho-do-repo>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Corrija a estrutura Claude Code do repositório em: $ARGUMENTS

Esta skill edita arquivos de outro projeto. Cada passo abaixo existe para que nada mude sem
você ter visto e aprovado.

## 1. Alvo

Sem caminho acima, use o alvo que o usuário já deu na conversa (um caminho, o nome do
repo, ou "este repo", que é o diretório atual; ou o caminho da auditoria feita aqui) e diga
qual caminho resolveu. Sem alvo nenhum, pergunte qual repositório corrigir; o diretório
atual só vale se o usuário o escolher. Caminho inexistente: diga e pare.

## 2. Achados

Se houve uma auditoria desse caminho nesta conversa, use os achados dela. Se não, chame a
tool Skill com `claudin:audit` e o caminho, e use o relatório.

## 3. Plano, antes de qualquer edição

Monte uma tabela com cada correção proposta:

| # | Arquivo | Problema | Correção | Fonte | Evidência |
|---|---|---|---|---|---|

Antes de propor, carregue o catálogo para usar a correção recomendada (rode o comando
sozinho, caminho com barras `/`):
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide anti-patterns
```

Se a auditoria trouxe evidência de uso, preencha a coluna Evidência com a contagem (ex.:
"9 bloqueios em 30 dias", "0 usos") e ordene por ela dentro de cada severidade: o que mais
atrapalhou o uso real vem primeiro. Sem evidência, deixe a coluna vazia.

Correção que exige decisão de desenho (ex: dividir o CLAUDE.md em
rules, trocar o modelo de um agente) entra marcada como **decisão**, com a sua
recomendação.

Pergunte ao usuário o que aplicar: tudo, só os erros, ou números específicos. Espere a
resposta. Só aplique o que foi aprovado.

## 4. Aplique

Se o alvo é um repositório git, anote antes o `git status --short` para separar as suas
mudanças das que já existiam. Leia cada arquivo antes de editá-lo e aplique só as
correções aprovadas. Arquivo novo (como um `.gitignore` que falta) só com aprovação
explícita na tabela.

## 5. Verifique

1. Rode de novo o validador:
   `python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <caminho>`
2. Mostre o diff do que mudou (`git diff` no alvo, se for git; senão, um resumo por arquivo)
3. Reporte em três listas: corrigido e confirmado pelo validador; corrigido mas não
   verificável por ele (julgamento); pendente, com o motivo

Pronto quando toda correção aprovada aparece em uma das três listas.
