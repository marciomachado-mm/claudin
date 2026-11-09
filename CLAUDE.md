# claudin

Plugin `claudin` (claud(e) + (plug)in) e o marketplace dele. O que é instalado nas
máquinas é só `plugins/claudin/`.

## Layout

- `plugins/claudin/`: o plugin distribuído. Tudo que estiver aqui vai para quem instala
- `.claude-plugin/marketplace.json`: este repo é também o marketplace do plugin
- `tools/`: baixa as docs oficiais (`fetch_docs.py`) e detecta defasagem (`check_drift.py`)
- `tests/`: testes (stdlib `unittest`, sem dependências)

## Regras

- Código dentro de `plugins/claudin/scripts/` usa só a biblioteca padrão do Python: a cópia
  instalada não tem venv
- Skill do plugin roda no projeto do usuário, onde ler a pasta do plugin com Read pede
  permissão (e falha em `claude -p`). Guias, snapshots e metadados chegam pelo
  `scripts/kb.py`, pré-aprovado em `allowed-tools` como
  `Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)`. A skill manda rodar cada comando
  sozinho e com barras `/`, porque só a forma exata casa com a pré-aprovação. Template vai
  dentro do próprio `SKILL.md`
- `scripts/sessions.py` lê o histórico de sessões do usuário. Só roda com permissão, e a
  skill nunca lê transcrição direto: só a saída mascarada do script
  (guia `knowledge/guides/usage-evidence.md`)
- Toda afirmação sobre o Claude Code cita a fonte (página da doc oficial)
- Exemplos em teste usam nomes genéricos e IPs de documentação (`192.0.2.x`,
  `198.51.100.x`, `203.0.113.x`)
- Textos para o usuário em português; nomes de código em inglês

## Validador

`plugins/claudin/scripts/validator/checks.py` tem as regras. Cada regra declara `source`
(snapshot), `evidence` (trecho literal dele) e `since` (versão, quando a doc data). Regra
nova exige um caso ruim em `tests/validator_fixtures.py`; os testes falham sem ele, e
também falham se o trecho de `evidence` sumir do snapshot.

## Docs oficiais

Snapshots em `plugins/claudin/knowledge/snapshots/` (vão junto com o plugin). Uma Action
semanal baixa as docs e abre um PR com o relatório de defasagem. Todo arquivo dos
`coverage_globs` precisa estar em `tools/knowledge-map.json`.

## Comandos

No Windows o nome é `python`; no Linux e no macOS sem `python`, `python3`.

```bash
claude plugin validate .
python -m unittest discover -s tests -v
python plugins/claudin/scripts/validate.py <caminho>
```

Evals (`plugins/claudin/evals/`) consomem o limite do plano a cada execução
(`plugin-evals.md`): rode só os casos afetados, com `--runs 1 --ablation none`.
