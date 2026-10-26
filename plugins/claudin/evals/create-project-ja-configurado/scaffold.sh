#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude
cat > 'package.json' <<'CLAUDIN_EOF'
{
  "name": "painel",
  "private": true,
  "scripts": {
    "dev": "vite",
    "test": "vitest run"
  }
}
CLAUDIN_EOF
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# painel

Painel interno em Vite + React.

## Comandos

- `npm run dev`
- `npm test`
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(npm test)"],
    "deny": ["Read(.env)", "Edit(.env)"]
  }
}
CLAUDIN_EOF
