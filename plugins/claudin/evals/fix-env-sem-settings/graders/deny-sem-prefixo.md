---
type: llm
---

Regra da doc oficial (permissions.md): em regras de permissão, um nome de arquivo sem
prefixo, como `Read(.env)`, casa em qualquer profundidade dentro do projeto; com `./`, como
`Read(./.env)`, casa só na raiz. Neste repo o `.env` fica em `services/api/`.

PASS se o plano propõe criar `.claude/settings.json` com um `deny` que cobre o `.env` em
qualquer pasta: `Read(.env)`, de preferência com o `Edit`
correspondente.

FAIL se o plano propõe `Read(./.env)` ou `Edit(./.env)`, se propõe só caminhos da raiz, ou
se não propõe nenhum `deny` para o `.env`.
