---
description: "Pasta que já tem CLAUDE.md e .claude/: o create-project não sobrescreve e oferece audit e fix"
tags: [create-project]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---

/claudin:create-project .
