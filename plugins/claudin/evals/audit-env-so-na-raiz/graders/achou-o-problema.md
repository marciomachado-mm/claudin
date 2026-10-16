---
type: llm
---

PASS se a resposta aponta que `Read(./.env)` (com `./`) só protege o `.env` da raiz, e que
os `.env` dentro de `packages/` continuam legíveis, recomendando a forma sem prefixo
(`Read(.env)` ou `Read(**/.env)`) ou regra equivalente que cubra os pacotes.

FAIL se a resposta considera o deny atual suficiente para o monorepo, ou não fala da
proteção dos arquivos `.env`.
