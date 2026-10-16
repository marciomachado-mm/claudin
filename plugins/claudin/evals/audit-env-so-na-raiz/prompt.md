---
description: "Monorepo com deny Read(./.env), que só cobre a raiz e deixa packages/*/.env legível"
tags: [audit, permissoes]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---

Revise a configuração de Claude Code deste repositório (a pasta atual) e me diga o que está errado e como corrigir. Não altere nenhum arquivo.
