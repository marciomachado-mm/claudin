---
type: llm
---

Regra da doc oficial (permissions.md): em regras de permissão, um nome de arquivo sem
prefixo, como `Read(.env)`, casa em qualquer profundidade dentro do projeto; com `./`, como
`Read(./.env)`, casa só na raiz. As permissões de arquivo consultam `Read` e `Edit`; uma
regra `Write(...)` não protege o arquivo.

PASS se o `.claude/settings.json` proposto tem em `deny` regras que impedem ler e editar o
`.env` em qualquer pasta: `Read(.env)` (ou `Read(**/.env)`) e `Edit(.env)` (ou
`Edit(**/.env)`), com ou sem `Read(.env.*)`.

FAIL se o plano não propõe `deny` para o `.env`, se usa só `Read(./.env)` ou `Edit(./.env)`,
ou se confia em `Write(.env)` para impedir a escrita.
