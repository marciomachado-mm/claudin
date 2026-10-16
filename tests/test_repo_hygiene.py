"""Garante que o laboratório privado nunca entra no repositório público."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


class LabIsPrivateTest(unittest.TestCase):
    def test_gitignore_lists_lab(self) -> None:
        lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("lab/", [line.strip() for line in lines])

    def test_no_lab_file_is_tracked(self) -> None:
        # O .gitignore evita o acidente comum; este teste pega o `git add -f`.
        tracked = _git("ls-files", "--", "lab").strip()
        self.assertEqual(tracked, "", f"arquivos do lab no índice:\n{tracked}")


if __name__ == "__main__":
    unittest.main()
