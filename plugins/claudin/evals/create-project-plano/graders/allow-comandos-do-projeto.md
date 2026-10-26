---
type: llm
---

O projeto roda os testes com `make test` (que chama `uv run pytest`) e o lint com
`make lint` (que chama `uv run ruff check src tests`).

PASS se o `allow` do `.claude/settings.json` proposto traz comandos que o projeto de fato
usa (`make test`, `make lint`, `uv run pytest`, `uv run ruff ...` ou equivalentes) e não
libera Bash de forma ampla.

FAIL se o `allow` libera Bash inteiro ou um programa sem restrição de argumento (por
exemplo `Bash`, `Bash(*)`, `Bash(uv *)`, `Bash(make *)`, `Bash(python *)`), se inventa
comandos que o projeto não tem (como `npm test`), ou se não há `allow`.
