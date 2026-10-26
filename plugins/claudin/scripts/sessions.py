"""Agregados do histórico de sessões de um projeto, para usar como evidência no audit.

Uso:
    python sessions.py <caminho-do-projeto> [--days N] [--json] [--no-samples]

Lê as transcrições em ~/.claude/projects/<projeto>/ e devolve só contagens e categorias.
O modelo nunca lê um .jsonl: lê a saída deste script. Nada é gravado e nada usa a rede.

Fatos da doc oficial (claude-directory.md, env-vars.md):
- `projects/<project>/<session>.jsonl` é a transcrição completa da sessão
- `.orphaned-*` e `.superseded-*` são cópias postas de lado: ignoradas
- `<session>/subagents/` guarda as transcrições de subagentes
- `CLAUDE_CODE_SESSION_ID` identifica a sessão atual, que fica de fora

Não documentado (parse defensivo, campo ausente vira nota em `nao_verificado`): o formato
de cada linha e a regra que transforma o caminho do projeto no nome da pasta.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SAMPLE_LEN = 80
COMMAND_RE = re.compile(r"<command-name>/?([^<\s]+)</command-name>")
CONFUSION_RE = re.compile(
    r"\b(n[ãa]o entendi|pera\b|peraí|como assim|t[ôo] confus|"
    r"i don'?t (understand|get it)|what do you mean|wait,? what)", re.IGNORECASE)

# Ordem importa: a primeira família que casa ganha. Texto livre, sem formato documentado.
ERROR_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("bloqueio_de_hook", re.compile(r"\bhook\b", re.IGNORECASE)),
    ("permissao_negada", re.compile(
        r"Permission to use|permission(s)? .*(denied|grant)|denied by|doesn't want to proceed|requested permissions",
        re.IGNORECASE)),
    ("classificador_auto", re.compile(r"auto mode|classifier", re.IGNORECASE)),
    ("sintaxe_shell", re.compile(
        r"syntax error|unexpected EOF|unterminated|here-document|unmatched|bad substitution|unexpected token",
        re.IGNORECASE)),
    ("encoding", re.compile(r"Unicode(De|En)codeError|codec can't|charmap|\bCRLF\b", re.IGNORECASE)),
    ("rede_ssh", re.compile(
        r"\bssh:|Connection (refused|timed out|reset|closed)|Could not resolve|Network is unreachable|Host key",
        re.IGNORECASE)),
    ("uso_de_tool", re.compile(r"<tool_use_error>")),
    ("limite_de_subagentes", re.compile(r"Concurrent subagent limit", re.IGNORECASE)),
    ("comando_falhou", re.compile(r"^Exit code \d+")),
)
# Negação de regra de permissão usa frase padrão do Claude Code. Um bloqueio de hook chega
# com o mesmo toolDenialKind ("permission-rule"), mas com o texto que o hook escreveu.
HARNESS_PERMISSION_RE = re.compile(
    r"Permission to use|permission(s)? .*(denied|grant)|denied by|requested permissions", re.IGNORECASE)
HOOK_PREFIX_RE = re.compile(r"^\w+:\w+ hook error:\s*")
DENIAL_KINDS = {
    "permission-rule": "permissao_negada",
    "user-rejected": "recusado_pelo_usuario",
    "automode-blocked": "classificador_auto",
    "automode-unavailable": "classificador_auto",
}


# --- Máscara -----------------------------------------------------------------------

_HOME = str(Path.home())
_MASKS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"://[^/\s:@]+:[^/\s@]+@"), "://<credencial>@"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<ip>"),
    (re.compile(r"(?i)\b(pass(word)?|senha|secret|token|api[_-]?key)\b\s*[=:]\s*\S+"), r"\1=<oculto>"),
    (re.compile(r"\b[A-Za-z0-9_\-]{24,}\b"), "<token>"),
    (re.compile(r"(?i)[a-z]:[\\/]+users[\\/]+[^\\/\s]+"), "~"),
    (re.compile(r"(?i)/[a-z]/users/[^/\s]+"), "~"),  # caminho do Git Bash: /c/Users/<nome>
    (re.compile(r"/(?:home|Users)/[^/\s]+"), "~"),
)


def mask(text: str) -> str:
    """Primeira linha, sem segredo aparente, no máximo SAMPLE_LEN caracteres."""
    line = text.strip().splitlines()[0] if text.strip() else ""
    line = line.replace(_HOME, "~").replace(_HOME.replace("\\", "/"), "~")
    for pattern, repl in _MASKS:
        line = pattern.sub(repl, line)
    return line if len(line) <= SAMPLE_LEN else line[:SAMPLE_LEN - 1] + "…"


# --- Leitura ------------------------------------------------------------------------


def project_slug(project: Path) -> str:
    """Regra observada (não documentada): todo caractere fora de [A-Za-z0-9] vira '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(project))


def find_project_dir(project: Path, projects_dir: Path) -> Path | None:
    if not projects_dir.is_dir():
        return None
    slug = project_slug(project).lower()
    for candidate in projects_dir.iterdir():
        # A letra do drive aparece em maiúscula ou minúscula conforme quem abriu a sessão.
        if candidate.is_dir() and candidate.name.lower() == slug:
            return candidate
    return None


def tool_result_text(block: dict) -> str:
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(i.get("text", "")) for i in content if isinstance(i, dict))
    return ""


def classify_error(text: str) -> str:
    for name, pattern in ERROR_FAMILIES:
        if pattern.search(text):
            return name
    return "outro"


def classify_denial(kind: str, text: str, from_hook: bool) -> str | None:
    """Família de uma negação marcada no registro, ou None se não houve negação."""
    if from_hook or ERROR_FAMILIES[0][1].search(text):
        return "bloqueio_de_hook" if kind or from_hook else None
    if kind == "permission-rule" and not HARNESS_PERMISSION_RE.search(text):
        return "bloqueio_de_hook"
    return DENIAL_KINDS.get(kind)


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@dataclass
class Session:
    id: str
    title: str = ""
    start: datetime | None = None
    end: datetime | None = None
    prompts: int = 0
    first_prompt: str = ""
    interruptions: int = 0
    compactions: int = 0
    api_errors: int = 0
    confusion: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    tools: Counter = field(default_factory=Counter)
    errors: Counter = field(default_factory=Counter)
    hook_samples: Counter = field(default_factory=Counter)  # (motivo, comando) -> vezes
    skills: Counter = field(default_factory=Counter)
    malformed: int = 0
    seen: Counter = field(default_factory=Counter)  # campos esperados que apareceram

    def touch(self, when: datetime | None) -> None:
        if when is None:
            return
        self.start = when if self.start is None or when < self.start else self.start
        self.end = when if self.end is None or when > self.end else self.end


def _user_text(session: Session, record: dict, text: str) -> None:
    if record.get("isCompactSummary"):
        session.compactions += 1
        return
    if text.startswith("[Request interrupted"):
        session.interruptions += 1
        return
    for name in COMMAND_RE.findall(text):
        session.skills[name.lower()] += 1
    if record.get("isMeta") or text.startswith("<"):
        return  # contexto injetado, não fala do usuário (mas comandos já contados acima)
    session.prompts += 1
    if not session.first_prompt:
        session.first_prompt = text.strip()[:500]
    if CONFUSION_RE.search(text):
        session.confusion += 1


def parse_session(path: Path, session_id: str) -> Session:
    session = Session(session_id)
    usage_ids: set[str] = set()
    commands: dict[str, str] = {}  # tool_use id -> comando, para nomear o que um hook bloqueou
    api_error_ids: set[str] = set()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                session.malformed += 1
                continue
            if not isinstance(record, dict):
                session.malformed += 1
                continue
            kind = record.get("type")
            if kind == "custom-title" and isinstance(record.get("customTitle"), str):
                session.title = record["customTitle"]
            if kind not in ("user", "assistant", "system"):
                continue  # cópias de requisição e metadados: contar aqui dobraria os números
            when = parse_time(record.get("timestamp"))
            if when:
                session.seen["timestamp"] += 1
            session.touch(when)
            if kind == "system":
                if record.get("subtype") == "api_error":
                    api_error_ids.add(str(record.get("uuid", len(api_error_ids))))
                continue
            message = record.get("message")
            if not isinstance(message, dict):
                continue
            session.seen["message"] += 1
            content = message.get("content")
            if kind == "assistant":
                if record.get("isApiErrorMessage"):
                    api_error_ids.add(str(record.get("uuid", len(api_error_ids))))
                usage = message.get("usage")
                msg_id = str(message.get("id", ""))
                if isinstance(usage, dict) and msg_id not in usage_ids:
                    usage_ids.add(msg_id)
                    session.seen["usage"] += 1
                    session.tokens_in += sum(int(usage.get(k) or 0) for k in (
                        "input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                    session.tokens_out += int(usage.get("output_tokens") or 0)
                for block in content if isinstance(content, list) else []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = str(block.get("name", "?"))
                        session.tools[name] += 1
                        tool_input = block.get("input") if isinstance(block.get("input"), dict) else {}
                        if "command" in tool_input:
                            commands[str(block.get("id"))] = str(tool_input["command"])
                        if name == "Skill" and tool_input.get("skill"):
                            session.skills[str(tool_input["skill"]).lower()] += 1
                continue
            # kind == "user"
            if isinstance(content, str):
                _user_text(session, record, content)
                continue
            denial_kind = str(record.get("toolDenialKind", ""))
            decision = record.get("permissionDecision")
            from_hook = isinstance(decision, dict) and decision.get("source") == "hook"
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    _user_text(session, record, str(block.get("text", "")))
                elif block.get("type") == "tool_result" and block.get("is_error"):
                    text = tool_result_text(block)
                    family = classify_denial(denial_kind, text, from_hook) or classify_error(text)
                    session.errors[family] += 1
                    if family == "bloqueio_de_hook":
                        blocked = commands.get(str(block.get("tool_use_id")), "")
                        reason = HOOK_PREFIX_RE.sub("", text.strip())
                        session.hook_samples[(mask(reason), mask(blocked))] += 1
    session.api_errors = len(api_error_ids)
    return session


# --- Agregação ----------------------------------------------------------------------


def defined_skills(project: Path) -> set[str]:
    names = {p.parent.name.lower() for p in (project / ".claude" / "skills").glob("*/SKILL.md")}
    names |= {p.stem.lower() for p in (project / ".claude" / "commands").glob("*.md")}
    return names


def short_name(name: str) -> str:
    return name.rsplit(":", 1)[-1].lstrip("/")


def collect(project: Path, project_dir: Path, days: int | None, current: str | None) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days else None
    sessions: list[Session] = []
    excluded_current = False
    for path in sorted(project_dir.glob("*.jsonl")):
        if ".orphaned-" in path.name:
            continue
        session_id = path.stem
        if current and session_id == current:
            excluded_current = True
            continue
        session = parse_session(path, session_id)
        if cutoff and session.end and session.end < cutoff:
            continue
        sessions.append(session)

    # Duplicatas: mesmo título e mesmo primeiro prompt. Fica a mais completa.
    unique: dict[str, Session] = {}
    for s in sessions:
        key = hashlib.sha1(f"{s.title}\x00{s.first_prompt}".encode()).hexdigest() if s.first_prompt else s.id
        if key not in unique or s.prompts > unique[key].prompts:
            unique[key] = s
    duplicates = len(sessions) - len(unique)
    sessions = list(unique.values())

    sub_errors: Counter = Counter()
    sub_count = 0
    for s in sessions:
        for path in (project_dir / s.id / "subagents").glob("*.jsonl"):
            sub_count += 1
            sub_errors.update(parse_session(path, path.stem).errors)

    def total(attr: str) -> int:
        return sum(getattr(s, attr) for s in sessions)

    tools: Counter = Counter()
    errors: Counter = Counter()
    hooks: Counter = Counter()
    skills: Counter = Counter()
    seen: Counter = Counter()
    for s in sessions:
        tools.update(s.tools)
        errors.update(s.errors)
        hooks.update(s.hook_samples)
        skills.update(s.skills)
        seen.update(s.seen)

    used_short = {short_name(n) for n in skills}
    never_used = sorted(defined_skills(project) - used_short)
    starts = [s.start for s in sessions if s.start]
    ends = [s.end for s in sessions if s.end]
    heavy = sorted(sessions, key=lambda s: s.tokens_in, reverse=True)[:3]

    not_verified: list[str] = []
    if sessions:
        for key, label in (("timestamp", "timestamp"), ("message", "message"), ("usage", "message.usage")):
            if not seen[key]:
                not_verified.append(f"campo {label} não apareceu em nenhuma sessão: os números que dependem dele saem zerados")
    malformed = total("malformed")
    if malformed:
        not_verified.append(f"{malformed} linha(s) que não são JSON válido foram puladas")

    return {
        "projeto": str(project),
        "pasta_de_sessoes": project_dir.name,
        "janela": {
            "de": min(starts).date().isoformat() if starts else None,
            "ate": max(ends).date().isoformat() if ends else None,
            "sessoes": len(sessions),
            "duplicadas_removidas": duplicates,
            "atual_excluida": excluded_current,
            "aviso_retencao": "transcrições mais velhas que cleanupPeriodDays (padrão 30 dias) já foram apagadas",
        },
        "totais": {
            "prompts": total("prompts"),
            "interrupcoes": total("interruptions"),
            "compactacoes": total("compactions"),
            "erros_api": total("api_errors"),
            "tokens": {"entrada": total("tokens_in"), "saida": total("tokens_out")},
        },
        "tools": dict(tools.most_common()),
        "erros_por_causa": dict(errors.most_common()),
        "hooks": hook_groups(hooks),
        "skills": {
            "usadas": dict(skills.most_common()),
            "nunca_usadas": never_used,
        },
        "subagentes": {"transcricoes": sub_count, "erros_por_causa": dict(sub_errors.most_common())},
        "sessoes_pesadas": [
            {
                "id": s.id[:8],
                "data": s.start.date().isoformat() if s.start else None,
                "horas": round((s.end - s.start).total_seconds() / 3600, 1) if s.start and s.end else None,
                "tokens_entrada": s.tokens_in,
                "erros_api": s.api_errors,
            }
            for s in heavy if s.tokens_in
        ],
        "sinais_de_confusao": total("confusion"),
        "nao_verificado": not_verified,
    }


def hook_groups(samples: Counter) -> list[dict]:
    """Bloqueios agrupados pelo motivo, com até 3 comandos de exemplo."""
    groups: dict[str, dict] = {}
    for (reason, command), n in samples.items():
        group = groups.setdefault(reason, {"motivo": reason, "bloqueios": 0, "exemplos": []})
        group["bloqueios"] += n
        if command and command not in group["exemplos"] and len(group["exemplos"]) < 3:
            group["exemplos"].append(command)
    return sorted(groups.values(), key=lambda g: g["bloqueios"], reverse=True)[:10]


def render(report: dict) -> str:
    j, t = report["janela"], report["totais"]
    lines = [
        f"Histórico de {report['projeto']} ({report['pasta_de_sessoes']})",
        f"{j['sessoes']} sessão(ões) de {j['de']} a {j['ate']}; "
        f"{j['duplicadas_removidas']} duplicada(s) removida(s); sessão atual excluída: {j['atual_excluida']}",
        f"Prompts {t['prompts']}, interrupções {t['interrupcoes']}, compactações {t['compactacoes']}, "
        f"erros de API {t['erros_api']}, tokens de entrada {t['tokens']['entrada']:,}",
        "", "Erros por causa: " + (", ".join(f"{k} {v}" for k, v in report["erros_por_causa"].items()) or "nenhum"),
    ]
    if report["hooks"]:
        lines.append("Bloqueios de hook mais frequentes:")
        for h in report["hooks"]:
            lines.append(f"  {h['bloqueios']}x {h['motivo']}")
            lines += [f"      ex.: {c}" for c in h["exemplos"]]
    lines.append("Skills usadas: " + (", ".join(f"{k} {v}" for k, v in report["skills"]["usadas"].items()) or "nenhuma"))
    lines.append("Skills do projeto nunca usadas: " + (", ".join(report["skills"]["nunca_usadas"]) or "nenhuma"))
    for s in report["sessoes_pesadas"]:
        lines.append(f"Sessão pesada {s['id']} ({s['data']}): {s['horas']} h, {s['tokens_entrada']:,} tokens, {s['erros_api']} erro(s) de API")
    lines.append(f"Sinais de confusão: {report['sinais_de_confusao']}")
    lines += [f"Não verificado: {n}" for n in report["nao_verificado"]]
    lines.append(f"Aviso: {j['aviso_retencao']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Agregados do histórico de sessões de um projeto")
    parser.add_argument("path", help="raiz do projeto")
    parser.add_argument("--days", type=int, help="só sessões dos últimos N dias")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-samples", action="store_true", help="sem nenhum trecho literal")
    parser.add_argument("--projects-dir", type=Path, default=Path.home() / ".claude" / "projects",
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    project = Path(args.path).resolve()
    project_dir = find_project_dir(project, args.projects_dir)
    if project_dir is None:
        print(f"Nenhum histórico encontrado para {project} em {args.projects_dir} "
              f"(pasta esperada: {project_slug(project)})")
        return 2
    report = collect(project, project_dir, args.days, os.environ.get("CLAUDE_CODE_SESSION_ID"))
    if args.no_samples:
        report["hooks"] = [{"motivo": "(oculto)", "bloqueios": h["bloqueios"], "exemplos": []}
                           for h in report["hooks"]]
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
