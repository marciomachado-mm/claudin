---
description: "Agente com disallowedTools: Bash(git push *), que remove o Bash inteiro; a correção é permissions.deny"
tags: [fix, agentes]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/claudin:fix .
