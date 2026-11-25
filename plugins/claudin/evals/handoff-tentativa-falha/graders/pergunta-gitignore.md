---
type: llm
---

O `HANDOFF.md` não está no `.gitignore` do projeto.

PASS se a resposta mostra o caminho do arquivo, avisa que ele não está no `.gitignore` e
pergunta se o usuário quer versioná-lo ou ignorá-lo, e dá um prompt para colar numa sessão
nova.

FAIL se a resposta não faz a pergunta sobre o `.gitignore`, se diz que já editou o
`.gitignore`, ou se não dá o prompt para a sessão nova.
