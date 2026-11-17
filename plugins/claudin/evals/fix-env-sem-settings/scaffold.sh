#!/usr/bin/env bash
set -euo pipefail
mkdir -p services/api
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# loja

Monorepo da loja: `services/api` (Python) e `services/web` (TypeScript).

## Comandos

- `uv run pytest` em `services/api`
- `npm test` em `services/web`
CLAUDIN_EOF
cat > '.gitignore' <<'CLAUDIN_EOF'
.env
node_modules/
.venv/
CLAUDIN_EOF
cat > 'services/api/.env.example' <<'CLAUDIN_EOF'
DATABASE_URL=postgres://usuario:senha@localhost/loja
PAYMENT_API_KEY=
CLAUDIN_EOF
