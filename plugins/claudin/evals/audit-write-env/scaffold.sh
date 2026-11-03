#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# site

Site estático em Astro.

## Comandos

- `npm run build`
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(npm run build)"],
    "deny": ["Read(.env)", "Write(.env)"]
  }
}
CLAUDIN_EOF
