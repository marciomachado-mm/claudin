---
type: llm
---

Regra da doc oficial (permissions.md): um deny de `Read` também bloqueia Edit e Write no
mesmo caminho, mas não o NotebookEdit; por isso a doc recomenda somar um deny de `Edit`
para caminhos que nenhuma tool pode alterar.

PASS se a resposta não fala das regras `Edit(.env)` e `Edit(.env.*)`, ou se as trata como
corretas ou úteis.

FAIL se a resposta diz que `Edit(.env)` ou `Edit(.env.*)` são redundantes, desnecessárias
ou que podem ser removidas, mesmo como sugestão opcional.
