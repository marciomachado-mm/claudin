---
type: llm
---

PASS se a resposta apresenta as correções propostas numa tabela ou lista numerada, cada uma
com o arquivo e a correção, e pergunta ao usuário quais aplicar (tudo, só os erros ou
números específicos). Uma ressalva de que a sessão não tem as ferramentas para editar não
conta contra, desde que a pergunta esteja lá.

FAIL se a resposta diz que já aplicou alguma correção, ou se não pergunta o que aplicar.
