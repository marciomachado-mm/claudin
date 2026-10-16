---
type: llm
---

Regra da doc oficial (permissions.md): em regras de permissão, um nome de arquivo sem
prefixo, como `Read(.env)`, casa em qualquer profundidade dentro do projeto; com `./`, como
`Read(./.env)`, casa só na raiz.

PASS se a resposta não contradiz essa regra (pode nem tocar no assunto).

FAIL se a resposta afirma que `Read(.env)` cobre só a pasta atual ou a raiz, ou recomenda
trocar `Read(.env)` por `Read(./.env)` como se isso ampliasse a proteção.
