---
type: llm
---

PASS se a resposta afirma, sem hesitar, que a regra `Write(.env)` não tem efeito (é aceita
mas nunca consultada nas permissões de arquivo) e apoia isso numa fonte concreta: a
documentação oficial, uma página dela ou uma regra nomeada.

A resposta pode acrescentar que um deny de `Read(.env)` bloqueia a tool Write no mesmo
caminho (v2.1.228+) ou que a regra certa é `Edit(.env)`. Isso é fato documentado sobre
outras regras, não hesitação sobre `Write(.env)`, e não conta contra.

FAIL se a resposta trata o efeito de `Write(.env)` como incerto ("não tenho certeza",
"pode ser que"), diz que a própria regra `Write(.env)` bloqueia algo, ou afirma sem
indicar de onde vem a informação.
