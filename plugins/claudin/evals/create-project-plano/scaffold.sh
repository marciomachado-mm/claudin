#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/cotacoes tests
cat > 'pyproject.toml' <<'CLAUDIN_EOF'
[project]
name = "cotacoes"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx", "pandas"]

[dependency-groups]
dev = ["pytest", "ruff"]
CLAUDIN_EOF
cat > 'Makefile' <<'CLAUDIN_EOF'
test:
	uv run pytest

lint:
	uv run ruff check src tests
CLAUDIN_EOF
cat > 'README.md' <<'CLAUDIN_EOF'
# cotacoes

Baixa cotações diárias de uma API e grava em parquet. O token da API fica no `.env`.
CLAUDIN_EOF
cat > 'src/cotacoes/__init__.py' <<'CLAUDIN_EOF'
CLAUDIN_EOF
cat > 'src/cotacoes/baixar.py' <<'CLAUDIN_EOF'
import os

import httpx
import pandas as pd


def baixar(data: str) -> pd.DataFrame:
    resposta = httpx.get(
        "https://api.exemplo.com/cotacoes",
        params={"data": data},
        headers={"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
    )
    resposta.raise_for_status()
    return pd.DataFrame(resposta.json())
CLAUDIN_EOF
cat > 'tests/test_baixar.py' <<'CLAUDIN_EOF'
def test_importa():
    import cotacoes.baixar  # noqa: F401
CLAUDIN_EOF
cat > '.env' <<'CLAUDIN_EOF'
API_TOKEN=fixture-sem-valor
CLAUDIN_EOF
cat > '.gitignore' <<'CLAUDIN_EOF'
.venv/
__pycache__/
.env
CLAUDIN_EOF
