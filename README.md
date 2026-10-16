# claudin

**claud(e) + (plug)in**: meu toolkit pessoal de Claude Code. O nome também é o Claudinho.

Um plugin que audita, cria e corrige estruturas `.claude/` em qualquer projeto, acompanha as
docs oficiais do Claude Code e só mantém o que comprovadamente funciona melhor que o Claude
Code puro.

> Em construção. Hoje: `/claudin:audit`, `/claudin:fix`, `/claudin:design`,
> `/claudin:create-project`, `/claudin:create-agent`, `/claudin:create-skill`,
> `/claudin:create-hook`, `/claudin:grill-me` e `/claudin:about`. Ainda sem avaliação
> comparativa com o Claude Code puro.

## Instalar

No Claude Code:

```
/plugin marketplace add marciomachado-mm/claudin
/plugin install claudin@claudin
```

Depois, em qualquer projeto: `/claudin:about`.

## Como o repo se organiza

| Pasta | O que é |
|---|---|
| `plugins/claudin/` | O plugin: o que é instalado |
| `.claude-plugin/marketplace.json` | Faz deste repo um marketplace com um plugin |
| `tests/` | Testes do repo e do validador |

## Créditos

O protocolo de `/claudin:grill-me` e o vocabulário de
`knowledge/guides/writing-for-agents.md` são adaptados de
[mattpocock/skills](https://github.com/mattpocock/skills), licença MIT,
Copyright (c) Matt Pocock.

## Desenvolvimento

Carregar o plugin direto da pasta, só para uma sessão:

```bash
claude --plugin-dir ./plugins/claudin
```

Validar e testar:

```bash
claude plugin validate .
python -m unittest discover -s tests -v
```
