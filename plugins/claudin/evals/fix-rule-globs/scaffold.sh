#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude/rules src/api src/web
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# portal

Portal em TypeScript: API em `src/api`, front em `src/web`.

## Comandos

- `npm test`
CLAUDIN_EOF
cat > '.claude/rules/api.md' <<'CLAUDIN_EOF'
---
description: Convenções da API
globs: src/api/**/*.ts
---

- Toda rota valida a entrada com zod antes de tocar no banco
- Erros saem no formato `{ "erro": string, "codigo": string }`
CLAUDIN_EOF
cat > 'src/api/rotas.ts' <<'CLAUDIN_EOF'
export const rotas = [];
CLAUDIN_EOF
cat > 'package.json' <<'CLAUDIN_EOF'
{
  "name": "portal",
  "private": true,
  "scripts": { "test": "vitest run" }
}
CLAUDIN_EOF
