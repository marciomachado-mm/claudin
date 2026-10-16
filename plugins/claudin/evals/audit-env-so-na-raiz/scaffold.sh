#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude packages/api packages/web
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# loja

Monorepo: `packages/api` (Node) e `packages/web` (React).

## Comandos

- `npm test -ws`: testes de todos os pacotes
CLAUDIN_EOF
cat > 'packages/api/.env.example' <<'CLAUDIN_EOF'
DATABASE_URL=
CLAUDIN_EOF
cat > 'packages/api/package.json' <<'CLAUDIN_EOF'
{"name": "api", "scripts": {"test": "node --test"}}
CLAUDIN_EOF
cat > 'packages/web/package.json' <<'CLAUDIN_EOF'
{"name": "web", "scripts": {"test": "vitest"}}
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(npm test -ws)"],
    "deny": ["Read(./.env)", "Edit(./.env)"]
  }
}
CLAUDIN_EOF
