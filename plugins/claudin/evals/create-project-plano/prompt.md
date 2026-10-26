---
description: "Projeto Python sem Claude Code: o plano traz deny de .env sem ./, allow só com os comandos do Makefile, e espera confirmação antes de escrever"
tags: [create-project, permissoes]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/claudin:create-project .
