#!/usr/bin/env bash
set -euo pipefail
# Cenário sem nenhum problema real: mede se o audit inventa erro onde não há.
mkdir -p .claude/skills/release src/notas tests
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# notas-cli

CLI em Python para organizar notas em Markdown.

## Comandos

- `uv run pytest`: testes
- `uv run notas --help`: ajuda da CLI

## Convenções

- Type hints em toda função pública
CLAUDIN_EOF
cat > 'pyproject.toml' <<'CLAUDIN_EOF'
[project]
name = "notas-cli"
version = "1.3.0"
requires-python = ">=3.11"

[project.scripts]
notas = "notas.cli:main"

[dependency-groups]
dev = ["pytest>=8"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/notas"]
CLAUDIN_EOF
cat > 'src/notas/cli.py' <<'CLAUDIN_EOF'
def main() -> None:
    print("notas")
CLAUDIN_EOF
cat > '.gitignore' <<'CLAUDIN_EOF'
.venv/
dist/
CLAUDE.local.md
.claude/settings.local.json
.env
.env.*
CLAUDIN_EOF
cat > '.claude/settings.json' <<'CLAUDIN_EOF'
{
  "permissions": {
    "allow": ["Bash(uv run pytest *)", "Bash(uv run notas *)"],
    "deny": ["Read(.env)", "Read(.env.*)", "Edit(.env)", "Edit(.env.*)"]
  }
}
CLAUDIN_EOF
cat > '.claude/skills/release/SKILL.md' <<'CLAUDIN_EOF'
---
description: Publica uma versão nova da CLI no PyPI.
disable-model-invocation: true
argument-hint: "<versão semver, ex: 1.4.0>"
---

Publique a versão $ARGUMENTS.

1. `uv run pytest`. Se falhar, pare.
2. Atualize `version` no `pyproject.toml` e acrescente a seção da versão no `CHANGELOG.md`.
3. `uv build`.
4. Mostre o diff e os arquivos em `dist/` e espere confirmação.
5. `git add pyproject.toml CHANGELOG.md`, `git commit -m "release v$ARGUMENTS"` e `git tag -a v$ARGUMENTS -m "v$ARGUMENTS"`.
6. `git push --follow-tags` e `uv publish`.

Pronto quando a tag existe no remoto e o pacote está no PyPI.
CLAUDIN_EOF
cat > 'CHANGELOG.md' <<'CLAUDIN_EOF'
# Changelog

## 1.3.0

- Busca por tag
CLAUDIN_EOF
cat > 'src/notas/__init__.py' <<'CLAUDIN_EOF'
CLAUDIN_EOF
cat > 'tests/test_cli.py' <<'CLAUDIN_EOF'
from notas.cli import main


def test_main(capsys) -> None:
    main()
    assert capsys.readouterr().out == "notas\n"
CLAUDIN_EOF
