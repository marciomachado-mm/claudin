---
name: update-docs
description: Alinha o claudin às docs oficiais do Claude Code - corrige o que ficou errado e transforma novidades em oportunidades no lab.
disable-model-invocation: true
---

Alinhe o claudin às docs oficiais. Duas perguntas guiam tudo: **o que ficou errado?** e
**o que ficou possível?** A segunda é o que faltava no claude_expert.

## 1. Snapshots

Se existe a branch `docs/semanal` com PR aberto (Action semanal), faça checkout dela. Senão:

```bash
python tools/fetch_docs.py
```

Se nenhuma página baixar, pare: as fases seguintes rodariam sobre dados velhos.

## 2. Detector e testes

```bash
python tools/check_drift.py
python -m unittest discover -s tests
```

Teste de rastreabilidade falhando significa que o trecho que sustenta uma regra do
validador mudou na doc: essa regra entra na revisão.

Se o relatório acusa release nova mas nenhuma afirmação datada, desconfie do detector
antes de concluir que nada mudou: confira se a forma de datação da doc mudou.

## 3. O que ficou errado

Para cada afirmação nova, documentada com atraso, regra com teste falhando e artefato
listado em "Artefatos a revisar": leia o artefato e o trecho do snapshot e classifique.

- **Contradição:** o claudin afirma algo que a doc agora desmente → correção
- **Lacuna:** a doc descreve algo que um artefato existente deveria cobrir → correção
- **Irrelevante** para o escopo do claudin → descarte, dizendo por quê

## 4. O que ficou possível

Para cada item da seção "Novidades do changelog" e cada afirmação nova, responda:

1. Que problema isso resolve?
2. Alguma skill, guia ou regra do claudin poderia usar isso, ou ficou desnecessária por
   causa disso?
3. Existe uma skill, agente, hook ou regra do validador **nova** que isso permite?

O que passar na pergunta 2 ou 3 vira uma linha em `lab/inbox.md`, com origem `official`:

```
- AAAA-MM-DD · official:v<versão> · <novidade> → <ideia para o claudin>
```

Ideias não são aplicadas aqui; o `evolve` faz a triagem.

## 5. Proponha e aplique

Apresente as correções: arquivo e linha, o que está escrito, o que passa a valer, a fonte
(`plugins/claudin/knowledge/snapshots/<página>.md`) e a versão. Espere a aprovação. Depois:

1. Aplique o aprovado. Afirmação corrigida leva a versão junto ("desde a v2.1.x")
2. `python -m unittest discover -s tests` e
   `python plugins/claudin/scripts/validate.py plugins/claudin`
3. Commit dos snapshots e das correções
4. `python tools/check_drift.py --set-aligned <versão mais nova>` e commit do estado
5. Se houve mudança no plugin, suba a versão em `plugin.json`

Pronto quando todo item do relatório foi corrigido, descartado com motivo ou anotado no
inbox, e o alinhamento foi registrado.
