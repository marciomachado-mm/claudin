"""Testes do acesso ao conhecimento usado pelas skills."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN = REPO_ROOT / "plugins" / "claudin"
sys.path.insert(0, str(PLUGIN / "scripts"))

import kb  # noqa: E402


class KbTest(unittest.TestCase):
    def test_guides_are_listed_and_readable(self) -> None:
        names = kb.list_guides()
        self.assertIn("anti-patterns", names)
        for name in names:
            self.assertTrue(kb.read_guide(name).strip())

    def test_unknown_guide_is_an_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            kb.read_guide("nao-existe")

    def test_docs_search_returns_page_and_line(self) -> None:
        hits = kb.search_docs(r"autoCompactWindow", page="sub-agents")
        self.assertTrue(hits)
        self.assertRegex(hits[0], r"^sub-agents\.md:\d+: ")

    def test_skills_only_reference_existing_guides(self) -> None:
        # Uma skill que pede um guia inexistente falharia só em uso real.
        guides = set(kb.list_guides())
        for skill in PLUGIN.glob("skills/*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            for match in re.finditer(r"kb\.py guide ([\w -]+?)(?:`|\n)", text):
                for name in match.group(1).split():
                    with self.subTest(skill=skill.parent.name, guide=name):
                        self.assertIn(name, guides)

    def test_skills_preapprove_every_script_they_use(self) -> None:
        # Comando citado sem pré-aprovação pede permissão no uso e falha em claude -p.
        for skill in PLUGIN.glob("skills/*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            for script in sorted(set(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/(\w+\.py)", text))):
                for python in ("python", "python3"):
                    with self.subTest(skill=skill.parent.name, script=script, python=python):
                        self.assertIn(f"Bash({python} ${{CLAUDE_PLUGIN_ROOT}}/scripts/{script} *)", text)

    def test_skills_pick_interpreter_by_system(self) -> None:
        # Tentar `python` e cair para `python3` custa um erro visível em todo uso no Linux.
        for skill in PLUGIN.glob("skills/*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            if "${CLAUDE_PLUGIN_ROOT}/scripts/" not in text:
                continue
            with self.subTest(skill=skill.parent.name):
                self.assertIn("Escolha o interpretador pelo sistema antes do primeiro comando", text)


if __name__ == "__main__":
    unittest.main()
