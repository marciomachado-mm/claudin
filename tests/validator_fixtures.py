"""Fixtures do validador: um projeto e um plugin corretos, e um caso ruim por regra.

Ficam em Python, não em pastas, porque alguns casos precisam de nomes que o Windows não
aceita em disco versionado (como `<` ou espaço invisível). `materialize` grava um caso
numa pasta temporária.
"""

from __future__ import annotations

from pathlib import Path

Files = dict[str, str]

GOOD_SKILL = """---
name: deploy
description: Faz o deploy do serviço para staging.
  Use quando o usuário pedir deploy.
disable-model-invocation: true
allowed-tools:
  - Bash(make deploy *)
---

Rode `make deploy`.
"""

GOOD_AGENT = """---
name: reviewer
description: Revisa diffs e aponta bugs.
tools: Read, Grep, Glob
model: sonnet
autoCompactWindow: 200000
disallowedTools: [Write]
---

Você revisa diffs.
"""

GOOD_RULE = """---
paths:
  - "src/**/*.py"
---

Use type hints.
"""

GOOD_SETTINGS = """{
  "permissions": {
    "allow": ["Edit(docs/**)", "Read(src/**)", "Bash(npm test)"],
    "deny": ["Read(.env)", "Read(./secrets/**)", "Bash"]
  }
}
"""

GOOD_PROJECT: Files = {
    ".claude/skills/deploy/SKILL.md": GOOD_SKILL,
    ".claude/agents/reviewer.md": GOOD_AGENT,
    ".claude/rules/python.md": GOOD_RULE,
    ".claude/rules/sem-frontmatter.md": "Sempre rode os testes.\n",
    "src/CLAUDE.md": "# src\n\nCódigo da aplicação. Testes em `tests/`.\n",
    ".claude/settings.json": GOOD_SETTINGS,
    "CLAUDE.md": "@AGENTS.md\n\nSó para o Claude: rode `make test` antes de concluir.\n",
    "AGENTS.md": "# Projeto\n\nInstruções comuns a todas as ferramentas.\n",
}

GOOD_PLUGIN: Files = {
    ".claude-plugin/plugin.json": '{"name": "demo", "version": "0.1.0"}\n',
    "skills/deploy/SKILL.md": GOOD_SKILL,
    "agents/reviewer.md": GOOD_AGENT,
}


def _agent(extra: str, name: str = "x") -> str:
    return f"---\nname: {name}\ndescription: Faz algo.\n{extra}---\n\nCorpo.\n"


def _settings(kind: str, entry: str) -> str:
    return f'{{"permissions": {{"{kind}": ["{entry}"]}}}}\n'


# Um caso por regra. Cada caso deve disparar exatamente a sua regra e nenhuma outra.
BAD_CASES: dict[str, Files] = {
    "FM-001": {".claude/agents/x.md": "---\nname: x\ndescription: sem fechamento\n"},
    "SKILL-001": {".claude/skills/vazia/README.md": "Sem SKILL.md.\n"},
    "SKILL-002": {".claude/skills/s/SKILL.md": "---\nname: s\n---\n\nCorpo.\n"},
    "SKILL-003": {".claude/skills/s/SKILL.md": f"---\ndescription: {'x' * 1600}\n---\n"},
    "SKILL-004": {".claude/skills/s/SKILL.md": "---\nname: deploy <prod>\ndescription: Faz deploy.\n---\n"},
    "SKILL-005": {".claude/skills/s/SKILL.md": "---\ndescription: Faz algo.\nallowed_tools: Read\n---\n"},
    "SKILL-006": {
        ".claude-plugin/plugin.json": '{"name": "demo", "skills": ["./skills/eng/tdd"]}\n',
        "skills/eng/tdd/SKILL.md": "---\ndescription: Faz TDD.\n---\n",
        "skills/rascunhos/ideia/SKILL.md": "---\ndescription: Ainda não publicada.\n---\n",
    },
    "AGENT-001": {".claude/agents/x.md": "---\nname: x\n---\n\nCorpo.\n"},
    "AGENT-002": {".claude/agents/x.md": _agent("", name="meu-plugin:x")},
    "AGENT-003": {".claude/agents/x.md": _agent("max_turns: 5\n")},
    "AGENT-004": {".claude/agents/x.md": _agent("autoCompactWindow: 200k\n")},
    "AGENT-005": {".claude/agents/x.md": _agent("disallowedTools: Bash(git push *)\n")},
    "AGENT-006": {".claude/agents/x.md": _agent("tools: Read, Bash(git diff *)\n")},
    "AGENT-007": {
        ".claude-plugin/plugin.json": '{"name": "demo"}\n',
        "agents/x.md": _agent("permissionMode: acceptEdits\n"),
    },
    "INSTR-001": {
        ".claude/rules/placeholder.md": "Regra sem paths, carrega sempre.\n",
        "services/api/CLAUDE.md": "# API\n\n" + ("Instrução longa demais. " * 1800),
    },
    "INSTR-002": {
        "CLAUDE.md": "# Projeto\n\nVeja o `@AGENTS.md` para as regras.\n",
        "AGENTS.md": "# Projeto\n\nRegras comuns.\n",
    },
    "RULE-001": {".claude/rules/r.md": "---\npaths: src/**\nalwaysApply: true\n---\n\nRegra.\n"},
    "SET-001": {".claude/settings.json": '{\n  // comentário\n  "model": "sonnet",\n}\n'},
    "PERM-001": {".claude/settings.json": _settings("deny", "Write(.env)")},
    "PERM-002": {".claude/settings.json": _settings("deny", "Bash(command:rm *)")},
    "PERM-003": {".claude/settings.json": _settings("deny", "Bash(rm -rf *)")},
    "PERM-004": {".claude/settings.json": _settings("deny", "Read(./.env)")},
}


def materialize(files: Files, root: Path) -> Path:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root
