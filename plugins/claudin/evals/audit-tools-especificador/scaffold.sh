#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude .claude/agents
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# api-pagamentos

Serviço de pagamentos em Python.

## Comandos

- `pytest`: roda os testes
CLAUDIN_EOF
cat > '.claude/agents/reviewer.md' <<'CLAUDIN_EOF'
---
name: reviewer
description: Revisa diffs de PR. Use quando o usuário pedir revisão de um branch.
tools: Read, Grep, Bash(git diff *)
---

Você revisa o diff do branch atual com `git diff main` e aponta bugs.
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(pytest)"],
    "deny": ["Read(.env)"]
  }
}
CLAUDIN_EOF
