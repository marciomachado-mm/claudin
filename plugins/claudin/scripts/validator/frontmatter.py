"""Parser mínimo de frontmatter YAML, só com a biblioteca padrão.

Não é um parser YAML completo: cobre o que os arquivos do `.claude/` usam no topo do
frontmatter. Chaves de topo viram strings ou listas; blocos aninhados (como `hooks` ou
`mcpServers`) ficam como texto bruto, porque o validador só olha os nomes das chaves.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

KEY_RE = re.compile(r"^(?P<key>[A-Za-z_][\w-]*):(?:\s+(?P<value>.*))?$")


class FrontmatterError(ValueError):
    """Frontmatter presente mas malformado."""


@dataclass
class Frontmatter:
    fields: dict[str, str | list[str]] = field(default_factory=dict)
    raw: dict[str, str] = field(default_factory=dict)
    present: bool = False

    def text(self, key: str) -> str | None:
        value = self.fields.get(key)
        if isinstance(value, list):
            return ", ".join(value)
        return value

    def items(self, key: str) -> list[str]:
        """Valor como lista: aceita lista YAML, `[a, b]` ou string separada por vírgula."""
        value = self.fields.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        inner = value.strip()
        if inner.startswith("[") and inner.endswith("]"):
            inner = inner[1:-1]
        return [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse(text: str) -> tuple[Frontmatter, str]:
    """Retorna (frontmatter, corpo). Sem `---` na primeira linha, não há frontmatter."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return Frontmatter(), text
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise FrontmatterError("frontmatter sem a linha '---' de fechamento") from None

    fm = Frontmatter(present=True)
    current: str | None = None
    block: list[str] = []

    def flush() -> None:
        if current is None:
            return
        fm.raw[current] = "\n".join(block)
        items = [ln.strip()[2:].strip() for ln in block if ln.strip().startswith("- ")]
        if items and len(items) == len([ln for ln in block if ln.strip()]):
            fm.fields[current] = [_unquote(item) for item in items]
        elif block and fm.fields[current] in ("", ">", "|", ">-", "|-"):
            fm.fields[current] = " ".join(ln.strip() for ln in block if ln.strip())
        elif block:
            # Continuação de escalar em várias linhas (ex: description recuada)
            # ou bloco aninhado: guarda o texto achatado.
            head = fm.fields[current]
            rest = " ".join(ln.strip() for ln in block if ln.strip())
            fm.fields[current] = f"{head} {rest}".strip()

    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            if current is not None and line.strip():
                block.append(line)
            continue
        if line[0] in " \t":
            if current is None:
                raise FrontmatterError(f"linha {number}: recuo sem chave antes")
            block.append(line)
            continue
        match = KEY_RE.match(line)
        if not match:
            raise FrontmatterError(f"linha {number}: esperado 'chave: valor', veio {line!r}")
        flush()
        current = match.group("key")
        if current in fm.fields:
            raise FrontmatterError(f"linha {number}: chave '{current}' repetida")
        fm.fields[current] = _unquote(match.group("value") or "")
        block = []
    flush()
    body = "\n".join(lines[end + 1:])
    return fm, body
