#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude/agents
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# loja

Loja virtual em Django.

## Comandos

- `python manage.py test`
CLAUDIN_EOF
cat > '.claude/agents/revisor.md' <<'CLAUDIN_EOF'
---
name: revisor
description: Revisa o diff atual antes do commit e aponta bugs e testes faltando. Use antes de commitar.
tools: Read, Grep, Glob, Bash
disallowedTools: Bash(git push *)
---

Rode `git diff` e `python manage.py test`, leia o que mudou e liste os problemas por
severidade. Não faça push.
CLAUDIN_EOF
cat > 'manage.py' <<'CLAUDIN_EOF'
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loja.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
CLAUDIN_EOF
