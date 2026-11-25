"""Testes do validador: fixtures por regra e rastreabilidade das regras até a doc."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN = REPO_ROOT / "plugins" / "claudin"
SNAPSHOTS = PLUGIN / "knowledge" / "snapshots"
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validator import RULES, Target, run  # noqa: E402
from validator import checks, frontmatter  # noqa: E402
from validator_fixtures import BAD_CASES, GOOD_PLUGIN, GOOD_PROJECT, materialize  # noqa: E402


def findings_for(files: dict[str, str]) -> list:
    with tempfile.TemporaryDirectory() as tmp:
        return run(Target(materialize(files, Path(tmp))))


class FixtureTest(unittest.TestCase):
    def test_good_project_is_clean(self) -> None:
        self.assertEqual(findings_for(GOOD_PROJECT), [])

    def test_good_plugin_is_clean(self) -> None:
        self.assertEqual(findings_for(GOOD_PLUGIN), [])

    def test_each_bad_case_triggers_only_its_rule(self) -> None:
        for rule_id, files in BAD_CASES.items():
            with self.subTest(rule=rule_id):
                fired = {f.rule_id for f in findings_for(files)}
                self.assertEqual(fired, {rule_id})

    def test_skill_folder_with_invisible_char_is_refused(self) -> None:
        # Fora do BAD_CASES porque o nome da pasta é o próprio caso.
        files = {".claude/skills/de​ploy/SKILL.md": "---\ndescription: Faz deploy.\n---\n"}
        self.assertEqual({f.rule_id for f in findings_for(files)}, {"SKILL-004"})

    def test_agent004_has_no_upper_limit(self) -> None:
        # A doc de 2026-11-23 tirou o teto de 1000000; só o mínimo vale.
        agent = "---\nname: x\ndescription: Faz x.\nautoCompactWindow: 2000000\n---\n\nCorpo.\n"
        self.assertEqual(findings_for({".claude/agents/x.md": agent}), [])

    def test_perm001_star_path_and_grep(self) -> None:
        # A doc só desconsidera caminho diferente de `*`; Grep entrou na lista no snapshot de 2026-11-16.
        def rules(entry: str) -> set[str]:
            settings = '{"permissions": {"deny": ["%s"]}}\n' % entry
            return {f.rule_id for f in findings_for({".claude/settings.json": settings})}
        self.assertEqual(rules("Write(*)"), set())
        self.assertEqual(rules("Grep(docs/**)"), {"PERM-001"})

    def test_plugin_skill_folder_chars_are_not_flagged(self) -> None:
        # Em plugin, a doc diz que os caracteres viram hífen no nome do comando.
        files = {
            ".claude-plugin/plugin.json": '{"name": "demo"}\n',
            "skills/de​ploy/SKILL.md": "---\ndescription: Faz deploy.\n---\n",
        }
        self.assertEqual(findings_for(files), [])

    def test_plugin_skill_category_listed_in_manifest_is_not_flagged(self) -> None:
        # A chave `skills` do manifesto soma pastas; a da categoria não é uma skill.
        files = {
            ".claude-plugin/plugin.json": '{"name": "demo", "skills": ["./skills/eng/tdd"]}\n',
            "skills/eng/tdd/SKILL.md": "---\ndescription: Faz TDD.\n---\n",
        }
        self.assertEqual(findings_for(files), [])

    def test_plugin_skill_folder_not_in_manifest_is_a_warning(self) -> None:
        # Com a chave `skills`, a pasta de fora pode ser de propósito: aviso, não erro
        files = {
            ".claude-plugin/plugin.json": '{"name": "demo", "skills": ["./skills/eng/tdd"]}\n',
            "skills/eng/tdd/SKILL.md": "---\ndescription: Faz TDD.\n---\n",
            "skills/vazia/README.md": "Sem SKILL.md.\n",
        }
        found = [(f.rule_id, f.severity, f.path) for f in findings_for(files)]
        self.assertEqual(found, [("SKILL-006", "warn", "skills/vazia")])

    def test_plugin_without_skills_key_keeps_the_error(self) -> None:
        files = {
            ".claude-plugin/plugin.json": '{"name": "demo"}\n',
            "skills/vazia/README.md": "Sem SKILL.md.\n",
        }
        found = [(f.rule_id, f.severity) for f in findings_for(files)]
        self.assertEqual(found, [("SKILL-001", "error")])


class AgentsMdTest(unittest.TestCase):
    """INSTR-002: AGENTS.md ao lado de um CLAUDE.md só é lido se o CLAUDE.md o importar."""

    def ids(self, files: dict[str, str]) -> list[str]:
        return [f.rule_id for f in findings_for(files)]

    def test_only_agents_md_is_fine(self) -> None:
        self.assertEqual(self.ids({"AGENTS.md": "# P\n"}), [])

    def test_local_claude_md_also_shadows(self) -> None:
        self.assertEqual(self.ids({"AGENTS.md": "# P\n", "CLAUDE.local.md": "minhas notas\n"}), ["INSTR-002"])

    def test_import_in_dot_claude_counts(self) -> None:
        self.assertEqual(self.ids({"AGENTS.md": "# P\n", ".claude/CLAUDE.md": "@./AGENTS.md\n"}), [])

    def test_import_inside_code_block_does_not_count(self) -> None:
        files = {"AGENTS.md": "# P\n", "CLAUDE.md": "Exemplo:\n\n```\n@AGENTS.md\n```\n"}
        self.assertEqual(self.ids(files), ["INSTR-002"])

    def test_symlink_to_agents_md_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = materialize({"AGENTS.md": "# P\n"}, Path(tmp))
            try:
                (root / "CLAUDE.md").symlink_to("AGENTS.md")
            except OSError:
                self.skipTest("sem permissão para criar link simbólico")
            self.assertEqual([f.rule_id for f in run(Target(root))], [])


class TraceabilityTest(unittest.TestCase):
    """Cada regra aponta para um trecho que ainda existe na doc oficial."""

    def test_every_rule_has_a_bad_case(self) -> None:
        self.assertEqual({r.id for r in RULES}, set(BAD_CASES))

    def test_rule_evidence_is_still_in_the_snapshot(self) -> None:
        for r in RULES:
            with self.subTest(rule=r.id):
                snapshot = SNAPSHOTS / r.source
                self.assertTrue(snapshot.is_file(), f"snapshot ausente: {r.source}")
                self.assertIn(
                    r.evidence, snapshot.read_text(encoding="utf-8"),
                    f"o trecho que sustenta {r.id} sumiu de {r.source}: revise a regra",
                )

    def test_coverage_note_names_every_rule_prefix(self) -> None:
        # Prefixo novo sem área na nota faria o resumo omitir o que a regra cobre.
        import validate
        for prefix in {r.id.split("-")[0] for r in RULES}:
            with self.subTest(prefix=prefix):
                self.assertIn(prefix, validate.AREAS)
        self.assertIn("Não cobre: hooks", validate.coverage_note())

    def test_since_is_a_version(self) -> None:
        for r in RULES:
            if r.since is not None:
                self.assertRegex(r.since, r"^\d+\.\d+\.\d+$", r.id)

    def test_field_lists_match_the_docs_table(self) -> None:
        text = (SNAPSHOTS / "claude-directory.md").read_text(encoding="utf-8")
        expected = {
            "skills/<name>/SKILL.md": checks.SKILL_FIELDS,
            "agents/*.md": checks.AGENT_FIELDS,
            "rules/*.md": checks.RULE_FIELDS,
        }
        for file_label, fields in expected.items():
            with self.subTest(file=file_label):
                row = re.search(rf"^\| `{re.escape(file_label)}` \| (.+?) \|", text, re.M)
                self.assertIsNotNone(row, f"linha de {file_label} sumiu da tabela")
                documented = set(re.findall(r"`([^`]+)`", row.group(1)))
                self.assertEqual(set(fields), documented, "campo novo ou removido na doc")


class FrontmatterTest(unittest.TestCase):
    def test_scalars_lists_and_continuation(self) -> None:
        fm, body = frontmatter.parse(
            "---\nname: x\ndescription: linha um\n  linha dois\ntools:\n  - Read\n  - Grep\n"
            "skills: [a, b]\nquoted: \"oi\"\nfolded: >\n  um\n  dois\n---\ncorpo\n"
        )
        self.assertEqual(fm.text("description"), "linha um linha dois")
        self.assertEqual(fm.items("tools"), ["Read", "Grep"])
        self.assertEqual(fm.items("skills"), ["a", "b"])
        self.assertEqual(fm.text("quoted"), "oi")
        self.assertEqual(fm.text("folded"), "um dois")
        self.assertEqual(body, "corpo")

    def test_no_frontmatter(self) -> None:
        fm, body = frontmatter.parse("# Título\n")
        self.assertFalse(fm.present)
        self.assertEqual(body, "# Título\n")

    def test_errors(self) -> None:
        for text in ("---\nname: x\n", "---\n  recuo: x\n---\n", "---\na: 1\na: 2\n---\n", "---\nlixo\n---\n"):
            with self.subTest(text=text), self.assertRaises(frontmatter.FrontmatterError):
                frontmatter.parse(text)


if __name__ == "__main__":
    unittest.main()
