"""Testes do detector de defasagem, num repositório git temporário."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_drift  # noqa: E402

HEADER = "<!-- source: https://code.claude.com/docs/en/sub-agents.md | updated: 2026-10-01T00:00:00+00:00 -->\n"
CHANGELOG = """<!-- source: x | updated: y -->
<Update label="2.1.301" description="October 15, 2026">
  **Added**

  * Added the `%` motion to vim mode
  * Added `rows` to a mod's `Input`

  **Fixed**

  * Fixed something
</Update>

<Update label="2.1.299" description="October 13, 2026">
  **Added**

  * Added an old thing
</Update>
"""


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


class DriftRepo:
    """Repo mínimo com snapshots, estado alinhado e manifesto."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.snapshots = root / check_drift.SNAPSHOTS_REL
        self.snapshots.mkdir(parents=True)
        (root / "tools").mkdir()
        git(root, "init", "-q", "-b", "main")
        git(root, "config", "user.email", "t@example.com")
        git(root, "config", "user.name", "t")
        git(root, "config", "core.autocrlf", "false")

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def commit_and_align(self, version: str) -> None:
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "snapshots")
        self.write(check_drift.STATE_REL, json.dumps({"aligned_version": "0.0.0"}))
        self.assertOk(check_drift.set_aligned(self.root, version))

    @staticmethod
    def assertOk(code: int) -> None:
        if code != 0:
            raise AssertionError(f"set_aligned retornou {code}")


class FindClaimsTest(unittest.TestCase):
    def test_prose_forms(self) -> None:
        lines = [
            "Requires Claude Code v2.1.296 or later.",
            "Before v2.1.288, the command was other.",
            "As of v2.1.193, it applies differently.",
            "{/* min-version: 2.1.210 */}",
            "Requires Claude Desktop v2.26454.0 or later.",
            "Nothing dated here.",
        ]
        found = [c.version for c in check_drift.find_claims("x", lines)]
        self.assertEqual(found, ["2.1.296", "2.1.288", "2.1.193", "2.1.210"])


class DriftReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = DriftRepo(Path(self._tmp.name))
        self.repo.write(f"{check_drift.SNAPSHOTS_REL}/sub-agents.md", HEADER + "| `maxTurns` | No | Limit |\n")
        self.repo.write(f"{check_drift.SNAPSHOTS_REL}/changelog.md", CHANGELOG)
        self.repo.write(check_drift.MAP_REL, json.dumps({
            "coverage_globs": ["skills/*.md"],
            "artifacts": {"skills/agent.md": ["sub-agents"]},
        }))
        self.repo.write("skills/agent.md", "x\n")
        self.repo.commit_and_align("2.1.299")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def add_to_snapshot(self, line: str) -> None:
        path = self.repo.snapshots / "sub-agents.md"
        path.write_text(path.read_text(encoding="utf-8") + line + "\n", encoding="utf-8", newline="\n")

    def test_late_documented_feature_is_reported(self) -> None:
        # O caso real: campo datado abaixo do marco, mas documentado depois dele.
        self.add_to_snapshot("| `autoCompactWindow` | No | Requires Claude Code v2.1.296 or later |")
        report = check_drift.build_report(self.repo.root)
        self.assertEqual([c.version for c in report.late_claims], ["2.1.296"])
        self.assertEqual(report.new_claims, [])
        self.assertEqual(report.impacted, {"skills/agent.md": ["sub-agents"]})

    def test_claim_above_marker_is_new(self) -> None:
        self.add_to_snapshot("Requires Claude Code v2.1.300 or later.")
        report = check_drift.build_report(self.repo.root)
        self.assertEqual([c.version for c in report.new_claims], ["2.1.300"])
        self.assertEqual(report.late_claims, [])

    def test_header_only_change_is_not_a_change(self) -> None:
        path = self.repo.snapshots / "sub-agents.md"
        path.write_text(path.read_text(encoding="utf-8").replace("2026-10-01", "2026-10-16"), encoding="utf-8", newline="\n")
        report = check_drift.build_report(self.repo.root)
        self.assertEqual(report.changed_snapshots, {})
        self.assertEqual(report.impacted, {})

    def test_changelog_added_items_above_marker(self) -> None:
        report = check_drift.build_report(self.repo.root)
        self.assertEqual(list(report.releases), ["2.1.301"])
        self.assertEqual(len(report.releases["2.1.301"]), 2)

    def test_set_aligned_refuses_uncommitted_snapshots(self) -> None:
        self.add_to_snapshot("nova linha")
        self.assertEqual(check_drift.set_aligned(self.repo.root, "2.1.301"), 1)

    def test_coverage_flags_undeclared_artifact(self) -> None:
        self.repo.write("skills/novo.md", "x\n")
        self.assertEqual(check_drift.coverage_problems(self.repo.root),
                         ["não declarado no knowledge-map: skills/novo.md"])


class RealRepoCoverageTest(unittest.TestCase):
    def test_this_repo_coverage_is_complete(self) -> None:
        self.assertEqual(check_drift.coverage_problems(REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
