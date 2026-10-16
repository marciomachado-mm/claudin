"""Regras do validador. Toda regra cita o snapshot e o trecho que a sustentam.

Listas de campos aceitos (SKILL_FIELDS, AGENT_FIELDS, RULE_FIELDS) espelham a tabela
"Frontmatter fields by file" de `claude-directory.md`; um teste compara as duas, então
um campo novo na doc quebra o teste em vez de virar falso positivo em silêncio.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator
from pathlib import Path

from .core import MarkdownFile, Target, rule

SKILL_FIELDS = frozenset({
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools", "disallowed-tools",
    "model", "effort", "context", "agent", "background", "hooks", "paths", "shell",
    "metadata", "license", "compatibility",
})
AGENT_FIELDS = frozenset({
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "autoCompactWindow", "skills", "mcpServers", "hooks", "memory",
    "background", "effort", "isolation", "color", "initialPrompt", "omitClaudeMd",
    "experimental",
})
RULE_FIELDS = frozenset({"paths"})

PLUGIN_IGNORED_AGENT_FIELDS = ("hooks", "mcpServers", "permissionMode")
FILE_PATH_TOOLS = {"Write": "Edit", "NotebookEdit": "Edit", "MultiEdit": "Edit", "Glob": "Read"}
CONTENT_FIELDS = {
    "Bash": "command", "PowerShell": "command", "Read": "file_path", "Edit": "file_path",
    "Write": "file_path", "Grep": "path", "Glob": "path", "NotebookEdit": "notebook_path",
    "WebFetch": "url",
}
RULE_RE = re.compile(r"^(?P<tool>[A-Za-z_][\w]*)\((?P<spec>.*)\)$")
SKILL_DESCRIPTION_LIMIT = 1536
AGENT_NAME_LIMIT = 256
AUTO_COMPACT_RANGE = (100_000, 1_000_000)


def _parsed(files: list[MarkdownFile]) -> Iterator[MarkdownFile]:
    return (f for f in files if f.error is None and f.fm.present)


def _bad_name_chars(name: str) -> list[str]:
    """Motivos pelos quais o Claude Code recusa um nome de skill ou comando."""
    reasons: list[str] = []
    if "<" in name or ">" in name:
        reasons.append("contém < ou >")
    if name != name.strip() or "  " in name:
        reasons.append("espaço no início, no fim ou duplicado")
    for ch in name:
        category = unicodedata.category(ch)
        if ch == "​" or category == "Cf":
            reasons.append(f"caractere invisível ou de direção U+{ord(ch):04X}")
        elif category == "Cc":
            reasons.append(f"caractere de controle U+{ord(ch):04X}")
        elif category in ("Co", "Cn"):
            reasons.append(f"caractere de uso privado ou não atribuído U+{ord(ch):04X}")
        elif category == "Zs" and ch != " ":
            reasons.append(f"espaço especial U+{ord(ch):04X}")
    return sorted(set(reasons))


# --- Frontmatter -------------------------------------------------------------------


@rule(
    "FM-001", severity="error",
    title="Frontmatter faz parse",
    source="claude-directory.md",
    evidence="read their configuration from YAML",
)
def frontmatter_parses(t: Target) -> Iterator[tuple[Path, str]]:
    for f in [*t.skills, *t.agents, *t.rules]:
        if f.error:
            yield f.path, f"frontmatter inválido: {f.error}"


# --- Skills ------------------------------------------------------------------------


@rule(
    "SKILL-001", severity="error",
    title="Pasta de skill tem SKILL.md",
    source="skills.md",
    evidence="Create a `SKILL.md` file with instructions",
)
def skill_has_file(t: Target) -> Iterator[tuple[Path, str]]:
    for d in t.skill_dirs:
        if not (d / "SKILL.md").is_file():
            yield d, "pasta de skill sem SKILL.md: a skill não é descoberta"


@rule(
    "SKILL-002", severity="warn",
    title="Skill tem description",
    source="skills.md",
    evidence="If omitted, uses the first non-empty line of the markdown content",
)
def skill_has_description(t: Target) -> Iterator[tuple[Path, str]]:
    for f in t.skills:
        if f.error is None and not f.fm.text("description"):
            yield f.path, "sem description: o Claude usa a primeira linha do corpo para decidir quando chamar a skill"


@rule(
    "SKILL-003", severity="warn",
    title="description + when_to_use cabem na listagem",
    source="skills.md",
    evidence="is truncated at 1,536 characters in the skill listing",
)
def skill_description_length(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.skills):
        size = len(f.fm.text("description") or "") + len(f.fm.text("when_to_use") or "")
        if size > SKILL_DESCRIPTION_LIMIT:
            yield f.path, f"description + when_to_use com {size} caracteres: o que passar de {SKILL_DESCRIPTION_LIMIT} é cortado"


@rule(
    "SKILL-004", severity="error",
    title="Nome de skill sem caracteres recusados",
    source="skills.md",
    evidence="Claude Code refuses a command name or a frontmatter `name` that contains characters such as these",
)
def skill_name_chars(t: Target) -> Iterator[tuple[Path, str]]:
    if not t.is_plugin:  # em plugin, a pasta tem os caracteres trocados por hífen
        for d in t.skill_dirs:
            if reasons := _bad_name_chars(d.name):
                yield d, f"nome da pasta recusado ({'; '.join(reasons)}): a skill não carrega"
    for f in _parsed(t.skills):
        name = f.fm.text("name")
        if name and (reasons := _bad_name_chars(name)):
            yield f.path, f"name recusado ({'; '.join(reasons)}): não aparece no menu / nem invoca"


@rule(
    "SKILL-005", severity="warn",
    title="Skill só usa campos de frontmatter conhecidos",
    source="claude-directory.md",
    evidence="`name`, `description`, `when_to_use`, `argument-hint`",
)
def skill_unknown_fields(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.skills):
        if unknown := sorted(set(f.fm.fields) - SKILL_FIELDS):
            yield f.path, f"campo(s) desconhecido(s): {', '.join(unknown)}"


# --- Agentes -----------------------------------------------------------------------


@rule(
    "AGENT-001", severity="error",
    title="Agente tem name e description",
    source="sub-agents.md",
    evidence="| `description` | Yes | When Claude should delegate to this subagent |",
)
def agent_required(t: Target) -> Iterator[tuple[Path, str]]:
    for f in t.agents:
        if f.error:
            continue
        missing = [k for k in ("name", "description") if not f.fm.text(k)]
        if missing:
            yield f.path, f"campo(s) obrigatório(s) ausente(s): {', '.join(missing)}"


@rule(
    "AGENT-002", severity="error",
    title="Nome de agente válido",
    source="sub-agents.md",
    evidence="Unique identifier of at most 256 characters",
)
def agent_name(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.agents):
        name = f.fm.text("name") or ""
        if ":" in name:
            yield f.path, f"name '{name}' tem ':', reservado para identificadores de plugin"
        if len(name) > AGENT_NAME_LIMIT:
            yield f.path, f"name com {len(name)} caracteres (máximo {AGENT_NAME_LIMIT})"


@rule(
    "AGENT-003", severity="warn",
    title="Agente só usa campos de frontmatter conhecidos",
    source="sub-agents.md",
    evidence="Claude Code ignores a field it doesn't recognize without reporting an error",
)
def agent_unknown_fields(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.agents):
        if unknown := sorted(set(f.fm.fields) - AGENT_FIELDS):
            yield f.path, f"campo(s) ignorado(s) em silêncio: {', '.join(unknown)} (camelCase exato)"


@rule(
    "AGENT-004", severity="error",
    title="autoCompactWindow é inteiro na faixa aceita",
    source="sub-agents.md",
    evidence="a token count from `100000` to `1000000`",
    since="2.1.296",
)
def agent_auto_compact(t: Target) -> Iterator[tuple[Path, str]]:
    low, high = AUTO_COMPACT_RANGE
    for f in _parsed(t.agents):
        value = f.fm.text("autoCompactWindow")
        if value is None:
            continue
        if not value.isdigit() or not low <= int(value) <= high:
            yield f.path, f"autoCompactWindow '{value}' é ignorado: use inteiro puro entre {low} e {high} (200k vira 200)"


@rule(
    "AGENT-005", severity="warn",
    title="disallowedTools com especificador remove a tool inteira",
    source="sub-agents.md",
    evidence="still removes the whole tool from the subagent",
)
def agent_disallowed_specifier(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.agents):
        for entry in f.fm.items("disallowedTools"):
            if "(" in entry and not entry.startswith("mcp__"):
                yield f.path, f"'{entry}' tira a tool inteira do agente; para bloquear só o comando, use permissions.deny"


@rule(
    "AGENT-006", severity="warn",
    title="tools sem especificador de comando",
    source="sub-agents.md",
    evidence="Both fields accept MCP server-level patterns in addition to exact tool names",
)
def agent_tools_specifier(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.agents):
        for entry in f.fm.items("tools"):
            if "(" in entry and not entry.startswith(("Agent(", "mcp__")):
                yield f.path, f"'{entry}' não é nome de tool: tools aceita nomes exatos, mcp__servidor e Agent(tipo); restrição por comando vai em permissions"


@rule(
    "AGENT-007", severity="warn",
    title="Agente de plugin não depende de campos ignorados",
    source="sub-agents.md",
    evidence="plugin subagents don't support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields",
)
def agent_plugin_ignored(t: Target) -> Iterator[tuple[Path, str]]:
    if not t.is_plugin:
        return
    for f in _parsed(t.agents):
        if used := [k for k in PLUGIN_IGNORED_AGENT_FIELDS if k in f.fm.fields]:
            yield f.path, f"{', '.join(used)} é ignorado em agente de plugin"


# --- Rules -------------------------------------------------------------------------


@rule(
    "RULE-001", severity="warn",
    title="Rule só usa o campo paths",
    source="claude-directory.md",
    evidence="`rules/*.md` | `paths`",
)
def rule_fields(t: Target) -> Iterator[tuple[Path, str]]:
    for f in _parsed(t.rules):
        if unknown := sorted(set(f.fm.fields) - RULE_FIELDS):
            yield f.path, f"campo(s) sem efeito em rule: {', '.join(unknown)}"


# --- Settings e permissões ---------------------------------------------------------


@rule(
    "SET-001", severity="error",
    title="settings é JSON estrito",
    source="settings.md",
    evidence="Settings files are strict JSON",
)
def settings_json(t: Target) -> Iterator[tuple[Path, str]]:
    for path in t.settings_files:
        if path not in t.settings:
            yield path, "JSON inválido (comentário ou vírgula sobrando?): o Claude Code ignora o arquivo"


@rule(
    "PERM-001", severity="error",
    title="Regra de caminho usa Edit ou Read",
    source="permissions.md",
    evidence="Claude Code checks file permissions against `Edit(path)` and `Read(path)` rules only",
    since="2.1.210",
)
def perm_file_tools(t: Target) -> Iterator[tuple[Path, str]]:
    for path, kind, entry in t.permission_rules():
        m = RULE_RE.match(entry)
        if m and m.group("tool") in FILE_PATH_TOOLS and m.group("spec").strip():
            use = FILE_PATH_TOOLS[m.group("tool")]
            yield path, f"{kind}: '{entry}' nunca é consultada; use {use}({m.group('spec')})"


@rule(
    "PERM-002", severity="error",
    title="Regra não casa o campo principal da tool",
    source="permissions.md",
    evidence="You can't match a tool's primary content field this way",
)
def perm_content_field(t: Target) -> Iterator[tuple[Path, str]]:
    for path, kind, entry in t.permission_rules():
        m = RULE_RE.match(entry)
        if not m:
            continue
        field_name = CONTENT_FIELDS.get(m.group("tool"))
        if field_name and m.group("spec").startswith(f"{field_name}:"):
            yield path, f"{kind}: '{entry}' é ignorada (campo principal '{field_name}' não se casa assim)"


@rule(
    "PERM-003", severity="info",
    title="deny de Bash por argumento é frágil",
    source="permissions.md",
    evidence="Bash permission patterns that try to constrain command arguments are fragile",
)
def perm_bash_args(t: Target) -> Iterator[tuple[Path, str]]:
    for path, kind, entry in t.permission_rules():
        m = RULE_RE.match(entry)
        spec = m.group("spec").strip() if m else ""
        # Uma regra 'command:' já é ignorada pelo Claude Code e reportada pelo PERM-002.
        if kind == "deny" and m and m.group("tool") == "Bash" and " " in spec and not spec.startswith("command:"):
            yield path, f"deny '{entry}' é contornável por variações do comando; para isolamento real, use o sandbox (macOS, Linux ou WSL2)"
