"""Valida um projeto com `.claude/` ou um plugin contra as regras do claudin.

Uso:
    python validate.py <caminho>          # relatório em português
    python validate.py <caminho> --json   # achados em JSON
    python validate.py --rules            # lista as regras e as fontes

Sai com código 1 se houver achado de severidade 'error'. Não dá nota: o que importa é a
lista de achados, e uma nota alta já escondeu problema antes.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validator import RULES, Target, run  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LABELS = {"error": "ERRO", "warn": "AVISO", "info": "INFO"}


def print_rules() -> None:
    for r in RULES:
        since = f" (v{r.since}+)" if r.since else ""
        print(f"{r.id:<10} {LABELS[r.severity]:<6} {r.title}{since}  [{r.source}]")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador do claudin")
    parser.add_argument("path", nargs="?", help="raiz do projeto ou do plugin")
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    parser.add_argument("--rules", action="store_true", help="lista as regras")
    args = parser.parse_args()

    if args.rules:
        print_rules()
        return 0
    if not args.path:
        parser.error("informe o caminho")

    target = Target(Path(args.path).resolve())
    if not target.exists():
        print(f"Nada para validar em {target.root}: sem CLAUDE.md, AGENTS.md, .claude/ nem .claude-plugin/plugin.json")
        return 2

    findings = run(target)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
    else:
        kind = "plugin" if target.is_plugin else "projeto"
        print(f"Validando {kind}: {target.root}\n")
        sources = {r.id: r.source for r in RULES}
        for f in findings:
            print(f"[{LABELS[f.severity]}] {f.rule_id} {f.path}\n        {f.message}  ({sources[f.rule_id]})")
        counts = {s: sum(f.severity == s for f in findings) for s in LABELS}
        print(f"\n{len(RULES)} regras, {counts['error']} erro(s), {counts['warn']} aviso(s), {counts['info']} info.")
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
