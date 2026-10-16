"""Motor do validador: alvo, registro de regras e achados.

Cada regra declara de onde vem: o snapshot da doc oficial (`source`), um trecho literal
dele que sustenta a regra (`evidence`) e a versão do Claude Code a partir da qual vale
(`since`, quando a doc data). O teste de rastreabilidade confere que o trecho continua
no snapshot; se a doc mudar, a regra é revisada em vez de seguir ensinando o antigo.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from . import frontmatter

SEVERITIES = ("error", "warn", "info")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    message: str


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    title: str
    source: str
    evidence: str
    since: str | None
    check: Callable[["Target"], Iterable[tuple[Path, str]]]


RULES: list[Rule] = []


def rule(
    id: str, *, severity: str, title: str, source: str, evidence: str, since: str | None = None
) -> Callable[[Callable[["Target"], Iterable[tuple[Path, str]]]], Callable[["Target"], Iterable[tuple[Path, str]]]]:
    """Registra uma regra. `check` produz pares (arquivo, mensagem)."""
    if severity not in SEVERITIES:
        raise ValueError(f"severidade inválida: {severity}")

    def register(check: Callable[["Target"], Iterable[tuple[Path, str]]]) -> Callable[["Target"], Iterable[tuple[Path, str]]]:
        if any(r.id == id for r in RULES):
            raise ValueError(f"regra duplicada: {id}")
        RULES.append(Rule(id, severity, title, source, evidence, since, check))
        return check

    return register


@dataclass
class MarkdownFile:
    path: Path
    fm: frontmatter.Frontmatter = field(default_factory=frontmatter.Frontmatter)
    error: str | None = None


def load_markdown(path: Path) -> MarkdownFile:
    try:
        fm, _ = frontmatter.parse(path.read_text(encoding="utf-8"))
    except frontmatter.FrontmatterError as exc:
        return MarkdownFile(path, error=str(exc))
    except UnicodeDecodeError:
        return MarkdownFile(path, error="arquivo não está em UTF-8")
    return MarkdownFile(path, fm)


@dataclass
class Target:
    """Um projeto com `.claude/` ou um plugin com `.claude-plugin/plugin.json`."""

    root: Path

    @cached_property
    def is_plugin(self) -> bool:
        return (self.root / ".claude-plugin" / "plugin.json").is_file()

    @cached_property
    def base(self) -> Path:
        return self.root if self.is_plugin else self.root / ".claude"

    def exists(self) -> bool:
        return self.is_plugin or self.base.is_dir()

    @cached_property
    def skill_dirs(self) -> list[Path]:
        skills = self.base / "skills"
        return sorted(p for p in skills.iterdir() if p.is_dir()) if skills.is_dir() else []

    @cached_property
    def skills(self) -> list[MarkdownFile]:
        return [load_markdown(d / "SKILL.md") for d in self.skill_dirs if (d / "SKILL.md").is_file()]

    @cached_property
    def agents(self) -> list[MarkdownFile]:
        agents = self.base / "agents"
        return [load_markdown(p) for p in sorted(agents.glob("*.md"))] if agents.is_dir() else []

    @cached_property
    def rules(self) -> list[MarkdownFile]:
        rules = self.base / "rules"
        return [load_markdown(p) for p in sorted(rules.rglob("*.md"))] if rules.is_dir() else []

    @cached_property
    def settings_files(self) -> list[Path]:
        if self.is_plugin:
            return []
        names = ("settings.json", "settings.local.json")
        return [self.base / n for n in names if (self.base / n).is_file()]

    @cached_property
    def settings(self) -> dict[Path, dict[str, object]]:
        """Settings que fazem parse. Os inválidos são reportados por uma regra própria."""
        parsed: dict[Path, dict[str, object]] = {}
        for path in self.settings_files:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(data, dict):
                parsed[path] = data
        return parsed

    def permission_rules(self) -> Iterator[tuple[Path, str, str]]:
        """(arquivo, lista, regra) para allow/ask/deny de cada settings."""
        for path, data in self.settings.items():
            perms = data.get("permissions")
            if not isinstance(perms, dict):
                continue
            for kind in ("allow", "ask", "deny"):
                entries = perms.get(kind)
                if isinstance(entries, list):
                    for entry in entries:
                        if isinstance(entry, str):
                            yield path, kind, entry

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()


def run(target: Target, rules: Iterable[Rule] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for r in rules if rules is not None else RULES:
        for path, message in r.check(target):
            findings.append(Finding(r.id, r.severity, target.rel(path), message))
    order = {s: i for i, s in enumerate(SEVERITIES)}
    return sorted(findings, key=lambda f: (order[f.severity], f.rule_id, f.path))
