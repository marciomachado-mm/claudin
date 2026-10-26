"""Testes do sessions.py com transcrições sintéticas, incluindo linhas quebradas."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "claudin" / "scripts"))

import sessions  # noqa: E402

SECRET = "hunter2-senha-temporaria"
IP = "192.168.15.240"


def user(text: str, ts: str = "2026-10-20T10:00:00Z", **extra: object) -> dict:
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": text}, **extra}


def assistant(msg_id: str, blocks: list[dict], ts: str = "2026-10-20T10:01:00Z", tokens: int = 100) -> dict:
    usage = {"input_tokens": tokens, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0,
             "output_tokens": 10}
    return {"type": "assistant", "timestamp": ts,
            "message": {"id": msg_id, "role": "assistant", "content": blocks, "usage": usage}}


def tool_use(tid: str, name: str, **inp: object) -> dict:
    return {"type": "tool_use", "id": tid, "name": name, "input": inp}


def tool_error(tid: str, text: str, ts: str = "2026-10-20T10:02:00Z", **extra: object) -> dict:
    block = {"type": "tool_result", "tool_use_id": tid, "is_error": True, "content": text}
    return {"type": "user", "timestamp": ts, "message": {"role": "user", "content": [block]}, **extra}


def write(path: Path, records: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [r if isinstance(r, str) else json.dumps(r) for r in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class SessionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.project = root / "repo"
        (self.project / ".claude" / "skills" / "deploy").mkdir(parents=True)
        (self.project / ".claude" / "skills" / "deploy" / "SKILL.md").write_text("x", encoding="utf-8")
        (self.project / ".claude" / "skills" / "orfa").mkdir(parents=True)
        (self.project / ".claude" / "skills" / "orfa" / "SKILL.md").write_text("x", encoding="utf-8")
        self.projects_dir = root / "projects"
        self.dir = self.projects_dir / sessions.project_slug(self.project)

        main = [
            {"type": "custom-title", "customTitle": "sessão principal"},
            user("Faz o deploy, por favor"),
            user("<command-name>/deploy</command-name>"),
            user("<command-name>/exit</command-name>"),
            assistant("m1", [tool_use("t1", "Bash", command=f"rm -rf /tmp/build # senha={SECRET} em {IP}")]),
            assistant("m1", [{"type": "text", "text": "mesma mensagem, outro bloco"}]),  # usage repetido
            tool_error("t1", "BLOQUEADO pelo guard: remocao recursiva", toolDenialKind="permission-rule"),
            assistant("m2", [tool_use("t2", "Bash", command="ls")]),
            tool_error("t2", "Permission to use Bash with command ls has been denied.",
                       toolDenialKind="permission-rule"),
            assistant("m3", [tool_use("t3", "Bash", command="echo")]),
            tool_error("t3", "Exit code 2\nbash: syntax error near unexpected token `)'"),
            assistant("m4", [tool_use("t4", "Bash", command="python x.py")]),
            tool_error("t4", "Exit code 1\nUnicodeDecodeError: 'charmap' codec can't decode"),
            assistant("m5", [tool_use("t5", "Bash", command=f"ssh {IP}")]),
            tool_error("t5", f"Exit code 255\nssh: connect to host {IP} port 22: Connection refused"),
            assistant("m6", [tool_use("t6", "Edit")]),
            tool_error("t6", "<tool_use_error>File has not been read yet</tool_use_error>"),
            assistant("m7", [tool_use("t7", "Write")]),
            tool_error("t7", "The user doesn't want to proceed", toolDenialKind="user-rejected"),
            assistant("m8", [tool_use("t8", "Skill", skill="claudin:audit")]),
            user("pera, não entendi o que você fez", ts="2026-10-20T12:00:00Z"),
            user("[Request interrupted by user]"),
            user("contexto injetado", isMeta=True),
            {"type": "system", "subtype": "api_error", "uuid": "e1", "timestamp": "2026-10-20T12:30:00Z"},
            {"type": "api-request-blob", "message": {"content": [tool_use("tx", "Bash", command="duplicado")]}},
            "{isto não é json",
            "[1, 2, 3]",
        ]
        write(self.dir / "aaaa1111.jsonl", main)
        # Duplicata: mesmo título e mesmo primeiro prompt, menos prompts.
        write(self.dir / "bbbb2222.jsonl", [main[0], main[1]])
        # Cópia posta de lado: a doc diz que não aparece no seletor. Ignorada.
        write(self.dir / "aaaa1111.orphaned-20261020-x.jsonl", [user("não conte isto")])
        write(self.dir / "aaaa1111.jsonl.superseded-20261020", [user("nem isto")])
        # Sessão atual.
        write(self.dir / "cccc3333.jsonl", [user("sessão em andamento")])
        # Subagente da sessão principal.
        write(self.dir / "aaaa1111" / "subagents" / "agent-1.jsonl",
              [assistant("s1", [tool_use("u1", "Bash", command="x")]), tool_error("u1", "Exit code 1")])
        self.report = sessions.collect(self.project, self.dir, None, "cccc3333")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_counts_only_real_sessions(self) -> None:
        j = self.report["janela"]
        self.assertEqual(j["sessoes"], 1)
        self.assertEqual(j["duplicadas_removidas"], 1)
        self.assertTrue(j["atual_excluida"])

    def test_prompts_ignore_meta_commands_and_interruptions(self) -> None:
        t = self.report["totais"]
        self.assertEqual(t["prompts"], 2)
        self.assertEqual(t["interrupcoes"], 1)
        self.assertEqual(t["erros_api"], 1)
        self.assertEqual(self.report["sinais_de_confusao"], 1)

    def test_usage_is_counted_once_per_message(self) -> None:
        self.assertEqual(self.report["totais"]["tokens"]["entrada"], 800)

    def test_request_copies_are_not_counted(self) -> None:
        self.assertEqual(self.report["tools"]["Bash"], 5)

    def test_error_families(self) -> None:
        self.assertEqual(self.report["erros_por_causa"], {
            "bloqueio_de_hook": 1, "permissao_negada": 1, "sintaxe_shell": 1, "encoding": 1,
            "rede_ssh": 1, "uso_de_tool": 1, "recusado_pelo_usuario": 1,
        })

    def test_hook_block_names_the_command(self) -> None:
        hook = self.report["hooks"][0]
        self.assertEqual(hook["bloqueios"], 1)
        self.assertIn("rm -rf /tmp/build", hook["exemplos"][0])

    def test_skills_used_and_never_used(self) -> None:
        self.assertEqual(self.report["skills"]["usadas"], {"deploy": 1, "claudin:audit": 1})
        self.assertEqual(self.report["skills"]["nunca_usadas"], ["orfa"])

    def test_subagents_are_counted_apart(self) -> None:
        self.assertEqual(self.report["subagentes"], {"transcricoes": 1, "erros_por_causa": {"comando_falhou": 1}})

    def test_malformed_lines_are_reported_not_fatal(self) -> None:
        self.assertTrue(any("2 linha(s)" in n for n in self.report["nao_verificado"]))

    def test_no_secret_reaches_the_output(self) -> None:
        dumped = json.dumps(self.report, ensure_ascii=False) + sessions.render(self.report)
        self.assertNotIn(SECRET, dumped)
        self.assertNotIn(IP, dumped)


class EdgeCasesTest(unittest.TestCase):
    def test_slug_matches_observed_rule(self) -> None:
        self.assertEqual(sessions.project_slug(Path("C:\\GitHub\\market_data")), "C--GitHub-market-data")

    def test_project_dir_ignores_drive_letter_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "Repo"
            slug = sessions.project_slug(project)
            (Path(tmp) / "projects" / slug.swapcase()).mkdir(parents=True)
            self.assertIsNotNone(sessions.find_project_dir(project, Path(tmp) / "projects"))

    def test_missing_fields_become_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "s"
            write(d / "x.jsonl", [{"type": "user"}, {"type": "assistant", "message": {"content": []}}])
            report = sessions.collect(Path(tmp), d, None, None)
            self.assertTrue(any("message.usage" in n for n in report["nao_verificado"]))
            self.assertTrue(any("timestamp" in n for n in report["nao_verificado"]))

    def test_mask(self) -> None:
        out = sessions.mask(f"curl https://user:pw@host api_key={SECRET} {IP} /c/Users/fulano/x")
        self.assertNotIn(SECRET, out)
        self.assertNotIn("pw@", out)
        self.assertNotIn(IP, out)
        self.assertNotIn("fulano", out)


if __name__ == "__main__":
    unittest.main()
