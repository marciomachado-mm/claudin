#!/usr/bin/env bash
set -euo pipefail
mkdir -p .claude/skills/release
cat > 'CLAUDE.md' <<'CLAUDIN_EOF'
# cli

Ferramenta de linha de comando em Rust.

## Comandos

- `cargo test`
CLAUDIN_EOF
cat > '.claude/skills/release/SKILL.md' <<'CLAUDIN_EOF'
---
name: release
description: Prepara uma release do cli. Use quando o usuário pedir para lançar uma versão.
disable-model-invocation: true
allowed_tools:
  - Bash(cargo test)
  - Bash(git tag *)
---

1. Rode `cargo test`
2. Atualize a versão no `Cargo.toml` e o `CHANGELOG.md`
3. Crie a tag `v<versão>`
CLAUDIN_EOF
cat > 'Cargo.toml' <<'CLAUDIN_EOF'
[package]
name = "cli"
version = "0.1.0"
edition = "2021"
CLAUDIN_EOF
