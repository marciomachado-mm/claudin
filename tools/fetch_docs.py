"""Baixa snapshots das docs oficiais do Claude Code para o conhecimento do plugin.

Uso:
    python tools/fetch_docs.py              # páginas CORE + as que já estão em disco
    python tools/fetch_docs.py --page mcp   # baixa (ou atualiza) uma página avulsa

Só a biblioteca padrão. Um snapshot sem mudança de corpo não é reescrito, então um run
sem novidade deixa o working tree limpo. A data da verificação vai para o arquivo de
estado, uma vez por run.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS_DIR = REPO_ROOT / "plugins" / "claudin" / "knowledge" / "snapshots"
STATE_FILE = REPO_ROOT / "tools" / "snapshots-state.json"
BASE_URL = "https://code.claude.com/docs/en/"

# Páginas sempre mantidas. Toda regra do validador cita uma delas.
CORE: tuple[str, ...] = (
    "best-practices",
    "changelog",
    "claude-directory",
    "cli-reference",
    "env-vars",
    "features-overview",
    "hooks",
    "hooks-guide",
    "memory",
    "permission-modes",
    "permissions",
    "plugin-evals",
    "plugin-marketplaces",
    "plugins",
    "plugins-reference",
    "sandboxing",
    "settings",
    "settings-reference",
    "skills",
    "sub-agents",
    "tools-reference",
)

HEADER_RE = re.compile(r"^<!-- source: (?P<url>\S+) \| updated: (?P<updated>\S+) -->\n")
VERSION_LABEL_RE = re.compile(r'<Update label="(\d+\.\d+\.\d+)"')

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def split_snapshot(text: str) -> tuple[str | None, str]:
    """Separa o header (URL de origem) do corpo de um snapshot."""
    match = HEADER_RE.match(text)
    if not match:
        return None, text
    return match.group("url"), text[match.end():]


def render_snapshot(url: str, body: str, updated: datetime) -> str:
    return f"<!-- source: {url} | updated: {updated.isoformat()} -->\n{body}"


def fetch(url: str, timeout: float = 30.0) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "claudin-fetch-docs"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def changelog_versions(text: str) -> list[str]:
    return VERSION_LABEL_RE.findall(text)


def load_state() -> dict[str, str]:
    if not STATE_FILE.is_file():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict[str, str]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pages_to_fetch(only: str | None) -> dict[str, str]:
    """Página -> URL. Snapshot fora do CORE já em disco é atualizado pela URL do header."""
    if only:
        return {only: f"{BASE_URL}{only}.md"}
    pages = {name: f"{BASE_URL}{name}.md" for name in CORE}
    for path in sorted(SNAPSHOTS_DIR.glob("*.md")):
        if path.stem not in pages:
            url, _ = split_snapshot(path.read_text(encoding="utf-8"))
            if url:
                pages[path.stem] = url
    return pages


def update_page(name: str, url: str, now: datetime) -> str:
    """Retorna 'updated', 'unchanged' ou 'error: <motivo>'."""
    try:
        body = fetch(url)
    except (urllib.error.URLError, TimeoutError, UnicodeDecodeError) as exc:
        return f"error: {exc}"
    path = SNAPSHOTS_DIR / f"{name}.md"
    if path.is_file():
        _, old_body = split_snapshot(path.read_text(encoding="utf-8"))
        if old_body == body:
            return "unchanged"
    path.write_text(render_snapshot(url, body, now), encoding="utf-8", newline="\n")
    return "updated"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--page", help="baixa só esta página (nome sem .md)")
    args = parser.parse_args()

    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    changelog = SNAPSHOTS_DIR / "changelog.md"
    before = set(changelog_versions(changelog.read_text(encoding="utf-8"))) if changelog.is_file() else set()

    now = datetime.now(timezone.utc)
    pages = pages_to_fetch(args.page)
    print(f"Atualizando {len(pages)} página(s)...\n")
    errors = 0
    updated = 0
    for name, url in pages.items():
        result = update_page(name, url, now)
        label = {"updated": "[OK] atualizado", "unchanged": "[SEM MUDANÇA]"}.get(result, f"[ERRO] {result}")
        print(f"{label:<20} {name}")
        errors += result.startswith("error")
        updated += result == "updated"

    if errors == len(pages):
        print("\nNenhuma página baixada. Verifique a rede; o estado não foi alterado.")
        return 1

    state = load_state()
    state["last_checked"] = now.isoformat()
    save_state(state)

    if changelog.is_file():
        new_versions = [v for v in changelog_versions(changelog.read_text(encoding="utf-8")) if v not in before]
        if new_versions and before:
            print(f"\nVersões novas no changelog: {', '.join(new_versions)}")

    print(f"\n{updated} página(s) atualizada(s), {errors} erro(s).")
    if updated:
        print("Próximo passo: python tools/check_drift.py")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
