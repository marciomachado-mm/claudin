---
description: "Monorepo sem settings.json e com o .env numa subpasta: o deny proposto precisa ser Read(.env), sem ./, para cobrir services/api/.env"
tags: [fix, settings, permissions]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/claudin:fix .
