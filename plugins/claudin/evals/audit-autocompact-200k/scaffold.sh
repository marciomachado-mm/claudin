#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude .claude/agents
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# logs-tools

Utilitários para analisar logs de produção.

## Comandos

- `make test`
CLAUDIN_EOF
cat > '.claude/agents/log-reader.md' <<'CLAUDIN_EOF'
---
name: log-reader
description: Lê arquivos de log longos e resume os erros. Use quando o usuário pedir análise de logs.
tools: Read, Grep, Glob
autoCompactWindow: 200k
---

Leia os logs indicados e devolva os erros agrupados por tipo.
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(make test)"],
    "deny": ["Read(.env)"]
  }
}
CLAUDIN_EOF
