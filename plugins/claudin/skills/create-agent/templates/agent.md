---
name: nome-do-agente
description: O que faz e QUANDO o Claude deve delegar. Ex: "Revisa diffs buscando problemas de segurança. Use quando o usuário pedir revisão de segurança de um branch."
tools: Read, Glob, Grep
---

Você é <papel> em <domínio>. Quem te chama passa <o que você recebe no prompt>.

## Passos

1. <Primeiro passo concreto, normalmente mapear ou ler>
2. <Segundo passo>
3. <...>

Pronto quando <condição verificável, ex: "cada arquivo alterado no diff foi lido">.

## Saída

<Formato fixo. É o que volta para quem chamou, então seja explícito.>
