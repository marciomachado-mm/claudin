#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# api

API interna em Go.

## Comandos

- `go test ./...`
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  // comandos que o time roda sem pedir
  "permissions": {
    "allow": ["Bash(go test ./...)", "Bash(go build ./...)",],
    "deny": ["Read(.env)", "Edit(.env)"]
  }
}
CLAUDIN_EOF
cat > 'go.mod' <<'CLAUDIN_EOF'
module exemplo.com/api

go 1.23
CLAUDIN_EOF
