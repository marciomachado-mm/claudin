"""Acesso ao conhecimento do claudin pelas skills, sem ler arquivos fora do projeto.

Uso:
    python kb.py guide <nome> [<nome> ...]   # imprime guias de knowledge/guides/
    python kb.py guides                      # lista os guias
    python kb.py docs <regex> [--page <p>]   # busca nos snapshots das docs oficiais
    python kb.py section <pagina> <linha>    # lê o trecho em volta de um resultado

Existe porque as skills rodam no projeto do usuário, e ler a pasta do plugin com Read pede
permissão (ou é negado em `claude -p`). Um único comando pré-aprovado no `allowed-tools`
de cada skill cobre guias e busca.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

KNOWLEDGE = Path(__file__).resolve().parents[1] / "knowledge"
GUIDES = KNOWLEDGE / "guides"
SNAPSHOTS = KNOWLEDGE / "snapshots"
MAX_HITS = 25
MAX_LINE = 400

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def list_guides() -> list[str]:
    return sorted(p.stem for p in GUIDES.glob("*.md"))


def read_guide(name: str) -> str:
    path = GUIDES / f"{Path(name).stem}.md"
    if not path.is_file():
        raise FileNotFoundError(f"guia '{name}' não existe. Disponíveis: {', '.join(list_guides())}")
    return path.read_text(encoding="utf-8")


def search_docs(pattern: str, page: str | None = None) -> list[str]:
    """Linhas dos snapshots que casam o regex (sem diferenciar caixa), como pagina.md:linha."""
    regex = re.compile(pattern, re.IGNORECASE)
    paths = [SNAPSHOTS / f"{page}.md"] if page else sorted(SNAPSHOTS.glob("*.md"))
    hits: list[str] = []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"snapshot '{path.stem}' não existe")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if regex.search(line):
                text = line.strip()
                text = text if len(text) <= MAX_LINE else text[:MAX_LINE - 3] + "..."
                hits.append(f"{path.name}:{number}: {text}")
                if len(hits) >= MAX_HITS:
                    return hits
    return hits


def read_section(page: str, line: int, count: int = 30) -> str:
    """Trecho de um snapshot a partir de uma linha, para ler o contexto de um resultado de docs."""
    path = SNAPSHOTS / f"{Path(page).stem}.md"
    if not path.is_file():
        raise FileNotFoundError(f"snapshot '{page}' não existe")
    lines = path.read_text(encoding="utf-8").splitlines()
    start = max(line, 1)
    chunk = lines[start - 1:start - 1 + count]
    return "\n".join(f"{path.name}:{start + i}: {text}" for i, text in enumerate(chunk))


def about() -> str:
    """Nome, versão e skills do plugin instalado."""
    import json

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validator import frontmatter

    root = KNOWLEDGE.parent
    manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    lines = [f"{manifest['name']} {manifest.get('version', '?')}", ""]
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        fm, _ = frontmatter.parse(skill.read_text(encoding="utf-8"))
        lines.append(f"/{manifest['name']}:{skill.parent.name}: {fm.text('description') or ''}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Conhecimento do claudin")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("about")
    guide = sub.add_parser("guide")
    guide.add_argument("names", nargs="+")
    sub.add_parser("guides")
    docs = sub.add_parser("docs")
    docs.add_argument("pattern")
    docs.add_argument("--page")
    section = sub.add_parser("section")
    section.add_argument("page")
    section.add_argument("line", type=int)
    section.add_argument("--lines", type=int, default=30)
    args = parser.parse_args()

    try:
        if args.command == "about":
            print(about())
        elif args.command == "guides":
            print("\n".join(list_guides()))
        elif args.command == "guide":
            print("\n\n---\n\n".join(read_guide(n) for n in args.names))
        elif args.command == "section":
            print(read_section(args.page, args.line, args.lines))
        else:
            hits = search_docs(args.pattern, args.page)
            print("\n".join(hits) if hits else "Nenhuma linha encontrada nos snapshots.")
            if len(hits) >= MAX_HITS:
                print(f"(parou em {MAX_HITS} resultados: refine o padrão ou use --page)")
    except (FileNotFoundError, re.error) as exc:
        print(f"Erro: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
