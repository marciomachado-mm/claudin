"""Detecta o que mudou nas docs desde o último alinhamento e o que revisar no claudin.

Uso:
    python tools/check_drift.py                     # relatório em Markdown
    python tools/check_drift.py --output drift.md   # grava o relatório (corpo do PR da Action)
    python tools/check_drift.py --coverage-only     # todo artefato está no knowledge-map?
    python tools/check_drift.py --set-aligned 2.1.301

Três sinais, porque nenhum basta sozinho:

1. Afirmações datadas com versão acima do marco (`aligned_version`).
2. Afirmações datadas que entraram nas linhas adicionadas desde o commit do alinhamento
   (`aligned_commit`), qualquer que seja a versão. Pega recurso documentado com atraso:
   o `autoCompactWindow`, datado de v2.1.296, apareceu depois de um marco 2.1.299.
3. Itens "Added" das releases novas do changelog, matéria-prima do radar.

Os artefatos a revisar vêm de `tools/knowledge-map.json` e, para o validador, das
fontes declaradas em cada regra.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS_REL = "plugins/claudin/knowledge/snapshots"
STATE_REL = "tools/snapshots-state.json"
MAP_REL = "tools/knowledge-map.json"
VALIDATOR_REL = "plugins/claudin/scripts/validator/checks.py"

# Formas de datação em prosa que as docs usam. A versão citada é a fronteira da mudança.
# Versões do Claude Code têm o número do meio curto (2.1.x); as do Claude Desktop, não
# (v2.26454.0), e não devem entrar.
VERSION = r"(\d+\.\d{1,3}\.\d+)\b"
CLAIM_PATTERNS = (
    re.compile(rf"Claude Code v{VERSION}"),
    re.compile(rf"\b(?:Before|before|As of|as of|From|from|Since|since|Starting in|starting in|Until|until) v{VERSION}"),
    re.compile(rf"\bv{VERSION} or later"),
    re.compile(rf"min-version:\s*{VERSION}"),  # marcador antigo, abandonado ~v2.1.250
)
# O changelog já mudou de formato uma vez sem aviso: de blocos <Update label="X"> para
# títulos **X**. Os dois são lidos; changelog sem release reconhecida vira alerta no
# relatório, para o detector não silenciar como aconteceu com o min-version.
UPDATE_RE = re.compile(r'<Update label="(\d+\.\d+\.\d+)"[^>]*>(.*?)</Update>', re.S)
RELEASE_HEADING_RE = re.compile(r"^\*\*(\d+\.\d+\.\d+)\*\*\s*$", re.M)
LINK_RE = re.compile(r"\]\([^)]*\)")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in version.split("."))


@dataclass(frozen=True)
class Claim:
    snapshot: str
    version: str
    line: str


def find_claims(snapshot: str, lines: list[str]) -> list[Claim]:
    claims: list[Claim] = []
    for line in lines:
        versions = {m.group(1) for p in CLAIM_PATTERNS for m in p.finditer(line)}
        for version in sorted(versions, key=version_key):
            claims.append(Claim(snapshot, version, line.strip()))
    return claims


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True, encoding="utf-8").stdout


def added_lines(repo: Path, commit: str, rel_path: str) -> list[str]:
    """Linhas adicionadas em rel_path desde commit, incluindo o que não foi commitado."""
    diff = git(repo, "diff", "--unified=0", commit, "--", rel_path)
    lines = [ln[1:] for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
    if not git(repo, "ls-files", "--", rel_path).strip() and (repo / rel_path).is_file():
        lines = (repo / rel_path).read_text(encoding="utf-8").splitlines()  # arquivo novo, não rastreado
    return lines


def changelog_releases(text: str) -> list[tuple[str, str]]:
    """(versão, corpo) de cada release, em qualquer um dos dois formatos conhecidos."""
    releases = UPDATE_RE.findall(text)
    if releases:
        return releases
    parts = RELEASE_HEADING_RE.split(text)
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def changelog_added(text: str, aligned: str) -> dict[str, list[str]]:
    """Release -> itens da seção Added, só para releases acima do marco."""
    result: dict[str, list[str]] = {}
    for version, body in changelog_releases(text):
        if version_key(version) <= version_key(aligned):
            continue
        section = re.search(r"\*\*Added\*\*(.*?)(?:\*\*[A-Z]\w+\*\*|<Expandable|$)", body, re.S)
        items = re.findall(r"^\s*\*\s+(.+)$", section.group(1), re.M) if section else []
        result[version] = items
    return result


def old_text(repo: Path, commit: str, rel_path: str) -> str:
    try:
        return git(repo, "show", f"{commit}:{rel_path}")
    except subprocess.CalledProcessError:
        return ""  # snapshot que não existia no alinhamento


def late_claims(name: str, old: str, new: str, aligned: str) -> list[Claim]:
    """Afirmações datadas até o marco que surgiram depois do alinhamento.

    Comparar linhas do diff não serve: quando a doc é reformatada (links, componentes),
    toda linha muda e centenas de afirmações antigas parecem novas. Uma afirmação é nova
    quando a sua versão passou a aparecer mais vezes na página. Entre as linhas dessa
    versão, mostra as que não existiam antes (ignorando a forma dos links).
    """
    def norm(line: str) -> str:
        return LINK_RE.sub("]", line).strip()

    old_claims = find_claims(name, old.splitlines())
    new_claims = find_claims(name, new.splitlines())
    old_count = Counter(c.version for c in old_claims)
    new_count = Counter(c.version for c in new_claims)
    old_lines = {norm(c.line) for c in old_claims}
    result: list[Claim] = []
    for version, count in new_count.items():
        grew = count - old_count.get(version, 0)
        if grew <= 0 or version_key(version) > version_key(aligned):
            continue
        candidates = [c for c in new_claims if c.version == version]
        fresh = [c for c in candidates if norm(c.line) not in old_lines]
        result.extend((fresh or candidates)[:grew])
    return result


@dataclass
class DriftReport:
    aligned_version: str
    aligned_commit: str | None
    new_claims: list[Claim] = field(default_factory=list)
    late_claims: list[Claim] = field(default_factory=list)
    changed_snapshots: dict[str, int] = field(default_factory=dict)
    releases: dict[str, list[str]] = field(default_factory=dict)
    changelog_unreadable: bool = False
    impacted: dict[str, list[str]] = field(default_factory=dict)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def artifact_sources(repo: Path) -> dict[str, list[str]]:
    """Artefato -> snapshots de que depende (manifesto + fontes das regras do validador)."""
    mapping = {k: list(v) for k, v in load_json(repo / MAP_REL).get("artifacts", {}).items()}
    checks = repo / VALIDATOR_REL
    if checks.is_file():
        sources = re.findall(r'source="([\w-]+)\.md"', checks.read_text(encoding="utf-8"))
        mapping[VALIDATOR_REL] = sorted(set(sources))
    return mapping


def build_report(repo: Path) -> DriftReport:
    state = load_json(repo / STATE_REL)
    aligned = state.get("aligned_version", "0.0.0")
    commit = state.get("aligned_commit")
    report = DriftReport(aligned, commit)
    snapshots = sorted((repo / SNAPSHOTS_REL).glob("*.md"))

    for path in snapshots:
        name = path.stem
        text = path.read_text(encoding="utf-8")
        if name == "changelog":
            report.releases = changelog_added(text, aligned)
            report.changelog_unreadable = not changelog_releases(text)
            continue
        for claim in find_claims(name, text.splitlines()):
            if version_key(claim.version) > version_key(aligned):
                report.new_claims.append(claim)
        if commit:
            rel = f"{SNAPSHOTS_REL}/{path.name}"
            added = added_lines(repo, commit, rel)
            # Linha 1 é o header com a data de atualização: não é conteúdo.
            content = [ln for ln in added if not ln.startswith("<!-- source:")]
            if content:
                report.changed_snapshots[name] = len(content)
            report.late_claims.extend(late_claims(name, old_text(repo, commit, rel), text, aligned))

    touched = {c.snapshot for c in report.new_claims + report.late_claims} | set(report.changed_snapshots)
    for artifact, sources in artifact_sources(repo).items():
        hit = sorted(touched & set(sources))
        if hit:
            report.impacted[artifact] = hit
    return report


def render(report: DriftReport) -> str:
    out = [f"# Relatório de defasagem desde a v{report.aligned_version}", ""]
    if not report.aligned_commit:
        out += ["> Sem `aligned_commit` no estado: o sinal por diff (recurso documentado com atraso) "
                "fica desligado até o primeiro `--set-aligned`.", ""]

    def claims_section(title: str, claims: list[Claim], explain: str) -> None:
        out.extend([f"## {title}", "", explain, ""])
        if not claims:
            out.extend(["Nenhuma.", ""])
            return
        for c in sorted(claims, key=lambda c: (c.snapshot, version_key(c.version))):
            text = c.line if len(c.line) <= 220 else c.line[:217] + "..."
            out.append(f"- `{c.snapshot}` v{c.version}: {text}")
        out.append("")

    claims_section("1. Afirmações novas", report.new_claims,
                   "Datadas com versão acima do marco.")
    claims_section("2. Documentadas com atraso", report.late_claims,
                   "Datadas com versão até o marco, mas que entraram nas docs depois do último alinhamento.")

    out.extend(["## 3. Artefatos a revisar", ""])
    if report.impacted:
        out.extend(f"- `{a}` ← {', '.join(f'`{s}`' for s in s_)}" for a, s_ in sorted(report.impacted.items()))
    else:
        out.append("Nenhum artefato declara depender dos snapshots que mudaram.")
    if report.changed_snapshots:
        changed = ", ".join(f"`{k}` (+{v})" for k, v in sorted(report.changed_snapshots.items()))
        out.extend(["", f"Snapshots com linhas novas desde o alinhamento: {changed}"])
    out.append("")

    out.extend(["## 4. Novidades do changelog (para o radar)", ""])
    if report.changelog_unreadable:
        out.append("**ALERTA: nenhuma release reconhecida no changelog. O formato mudou de novo; "
                   "ajuste `changelog_releases` antes de confiar nesta seção.**")
    elif not report.releases:
        out.append("Nenhuma release acima do marco.")
    for version, items in sorted(report.releases.items(), key=lambda kv: version_key(kv[0]), reverse=True):
        out.append(f"### v{version}")
        out.extend(f"- {item}" for item in items) if items else out.append("- (sem itens Added)")
        out.append("")
    newest = max(report.releases, key=version_key) if report.releases else report.aligned_version
    out.extend(["", "Depois de revisar, registre o alinhamento (com os snapshots já commitados):", "",
                f"    python tools/check_drift.py --set-aligned {newest}"])
    return "\n".join(out) + "\n"


def coverage_problems(repo: Path) -> list[str]:
    data = load_json(repo / MAP_REL)
    declared = set(data.get("artifacts", {}))
    files = {
        p.relative_to(repo).as_posix()
        for pattern in data.get("coverage_globs", [])
        for p in repo.glob(pattern) if p.is_file()
    }
    snapshots = {p.stem for p in (repo / SNAPSHOTS_REL).glob("*.md")}
    problems = [f"não declarado no knowledge-map: {f}" for f in sorted(files - declared)]
    problems += [f"declarado mas não existe: {a}" for a in sorted(declared) if not (repo / a).is_file()]
    for artifact, sources in data.get("artifacts", {}).items():
        problems += [f"{artifact}: snapshot inexistente '{s}'" for s in sources if s not in snapshots]
    globs = data.get("coverage_globs", [])
    problems += [f"declarado fora dos coverage_globs: {a}" for a in sorted(declared)
                 if not any(fnmatch.fnmatch(a, g) for g in globs)]
    return problems


def set_aligned(repo: Path, version: str) -> int:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        print(f"Versão inválida: {version}")
        return 2
    if git(repo, "status", "--porcelain", "--", SNAPSHOTS_REL).strip():
        print("Há snapshots não commitados. Commite-os antes: o alinhamento aponta para o HEAD.")
        return 1
    path = repo / STATE_REL
    state = load_json(path)
    state["aligned_version"] = version
    state["aligned_commit"] = git(repo, "rev-parse", "HEAD").strip()
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Alinhado até a v{version} no commit {state['aligned_commit'][:7]}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Detecta defasagem entre docs e claudin")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, help="grava o relatório neste arquivo")
    parser.add_argument("--coverage-only", action="store_true")
    parser.add_argument("--set-aligned", metavar="VERSAO")
    args = parser.parse_args()

    if args.set_aligned:
        return set_aligned(args.repo, args.set_aligned)

    problems = coverage_problems(args.repo)
    if args.coverage_only:
        print("\n".join(problems) if problems else "Cobertura OK: todo artefato está no knowledge-map.")
        return 1 if problems else 0

    text = render(build_report(args.repo))
    if problems:
        text += "\n## Cobertura do manifesto\n\n" + "\n".join(f"- {p}" for p in problems) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Relatório gravado em {args.output}")
    else:
        print(text)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
