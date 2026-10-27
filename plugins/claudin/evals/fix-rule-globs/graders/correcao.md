---
type: llm
---

Regra da doc oficial (memory.md e claude-directory.md): o único campo de frontmatter de
uma rule é `paths`. Uma rule sem `paths` carrega em toda sessão, para qualquer arquivo;
`globs` e `description` são ignorados.

PASS se a resposta diz que `globs` e `description` não são campos de rule, que por isso a
rule de API carrega sempre, e propõe trocar `globs` por `paths` com o mesmo padrão
(`src/api/**/*.ts`), removendo ou deixando de lado o `description`.

FAIL se a resposta trata `globs` como campo válido, não propõe `paths`, ou propõe um
padrão que não cobre os arquivos `.ts` de `src/api`.
