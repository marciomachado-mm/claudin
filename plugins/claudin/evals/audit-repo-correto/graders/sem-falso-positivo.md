---
type: llm
---

A configuração deste repositório está correta: permissões explícitas que cobrem `.env` e
`.env.*`, testes liberados com e sem argumentos, `.gitignore` com os arquivos pessoais e
uma skill de release com efeito colateral protegida por `disable-model-invocation`, que
commita antes de criar a tag e envia branch e tag juntos. O `CHANGELOG.md` existe e há
teste em `tests/`.

PASS se a resposta conclui que a estrutura está correta ou só traz sugestões opcionais,
sem classificar nenhum item como erro, falha ou risco que precise ser corrigido. Conselho
geral marcado como sugestão (como usar o sandbox porque deny é atrito) é opcional.

FAIL se a resposta classifica algum item como erro, falha, brecha ou risco a corrigir.
