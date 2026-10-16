# Protocolo grill-me

Questione o usuário em rodadas até chegar a um entendimento compartilhado de um plano ou
decisão. Organize as decisões como uma **árvore**: cada decisão se ramifica nas que
dependem dela.

Adaptado por Marcio Machado da skill `grill-me` de
[mattpocock/skills](https://github.com/mattpocock/skills)
(`skills/productivity/grill-me`), licença MIT, Copyright (c) Matt Pocock.

## Rodadas e fronteira

A **fronteira** é o conjunto de decisões cujos pré-requisitos já foram resolvidos: as
perguntas que dá para fazer agora sem presumir respostas que ainda não chegaram.

Em cada rodada:

1. Faça todas as perguntas da fronteira de uma vez, numeradas, cada uma com a sua resposta
   recomendada
2. No thread principal, use a tool `AskUserQuestion` para elas. Pergunta aberta entra com
   uma opção de escape que aceita texto livre. Pergunta escrita só no corpo do chat costuma
   ficar sem resposta
3. Espere as respostas, recalcule a fronteira e faça a próxima rodada

Pergunta que depende de outra ainda aberta na mesma rodada pertence à rodada seguinte.

Rodando como subagente, `AskUserQuestion` não existe (`sub-agents.md`, lista de tools
removidas). Use este formato em texto e devolva ao thread principal:

```
**Q1 — <título>**: <pergunta e alternativas>
→ <sua recomendação>
```

## Fato é seu, decisão é do usuário

Fato do ambiente você descobre, não pergunta:

| Não pergunte | Descubra |
|---|---|
| "você já tem `.claude/`?" | Glob no repo |
| "qual stack?" | `package.json`, `pyproject.toml`, `go.mod` |
| "rule aceita `paths:`?" | `knowledge/snapshots/memory.md` |
| "skill ou agente para isso?" | `knowledge/snapshots/features-overview.md` |

Enquanto uma investigação roda, só as perguntas que dependem dela esperam; faça as outras.
Anote cada fato e onde o verificou.

Decisão é do usuário: o que ele quer, que trade-off aceita, o que fica fora. Apresente e
espere.

## Conclusão

Termina quando a fronteira está vazia: todos os ramos percorridos e nada presumido.

## Fechamento

O fechamento é um turno de entrega, **sem tools**: uma pergunta no fechamento transforma
qualquer resposta em aprovação do plano inteiro antes de o usuário lê-lo. Formato:

```
## Entendimento compartilhado

**Síntese**: 2 a 4 frases sobre o desenho e o que o sustenta.

**Decisões**
| # | O que ficou acordado | Por quê |

**Descartado**
| Alternativa | Por que não |

**Fatos apurados**
| Fato | Onde foi verificado |

**Fora de escopo**: item a item.

**Próximo passo**: o que será feito, por quem, depois da confirmação.
```

Só execute depois da confirmação. Contestação reabre a fronteira: volte às rodadas.
