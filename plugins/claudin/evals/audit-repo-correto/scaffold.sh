#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude .claude/skills/release
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# notas-cli

CLI em Python para organizar notas em Markdown.

## Comandos

- `uv run pytest`: testes
- `uv run notas --help`: ajuda da CLI

## Convenções

- Type hints em toda função pública
CLAUDIN_EOF
cat > '.gitignore' <<'CLAUDIN_EOF'
.venv/
CLAUDE.local.md
.claude/settings.local.json
.env
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(uv run pytest)", "Bash(uv run notas *)"],
    "deny": ["Read(.env)", "Edit(.env)"]
  }
}
CLAUDIN_EOF
cat > '.claude/skills/release/SKILL.md' <<'CLAUDIN_EOF'
---
description: Publica uma versão nova da CLI (tag, changelog e build). Use quando o usuário pedir release.
disable-model-invocation: true
---

1. Rode os testes.
2. Atualize o CHANGELOG.
3. Crie a tag e confirme antes de publicar.
CLAUDIN_EOF
