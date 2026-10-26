# claudin

Repo de desenvolvimento do plugin `claudin` (claud(e) + (plug)in). Este repo é a
**oficina**: aqui se mantém o plugin. O que é instalado nas máquinas é só
`plugins/claudin/`.

## Layout

- `plugins/claudin/`: o plugin distribuído. Tudo que estiver aqui vai para quem instala
- `.claude-plugin/marketplace.json`: este repo é também o marketplace do plugin
- `tests/`: testes (stdlib `unittest`, sem dependências)
- `lab/`: clone do repo **privado** `claudin_lab`. Está no `.gitignore` e nunca entra aqui

## Regras

- Nada do `lab/` vai para o repo público: nem arquivo, nem trecho copiado para commit,
  issue ou PR. O teste `tests/test_repo_hygiene.py` falha se algo do `lab/` for rastreado
- Código dentro de `plugins/claudin/scripts/` usa só a biblioteca padrão do Python: a cópia
  instalada não tem venv
- Skill do plugin roda no projeto do usuário, onde ler a pasta do plugin com Read pede
  permissão (e falha em `claude -p`). Guias, snapshots e metadados chegam pelo
  `scripts/kb.py`, pré-aprovado em `allowed-tools` como
  `Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)`. A skill manda rodar cada comando
  sozinho e com barras `/`, porque só a forma exata casa com a pré-aprovação. Template vai
  dentro do próprio `SKILL.md`
- Toda afirmação sobre o Claude Code cita a fonte (página da doc oficial)
- Textos para o usuário em português; nomes de código em inglês

## Validador

`plugins/claudin/scripts/validator/checks.py` tem as regras. Cada regra declara `source`
(snapshot), `evidence` (trecho literal dele) e `since` (versão, quando a doc data). Regra
nova exige um caso ruim em `tests/validator_fixtures.py`; os testes falham sem ele, e
também falham se o trecho de `evidence` sumir do snapshot.

## Docs oficiais

Snapshots em `plugins/claudin/knowledge/snapshots/` (vão junto com o plugin). Ciclo:

1. `python tools/fetch_docs.py`
2. `python tools/check_drift.py`: afirmações novas, documentadas com atraso, artefatos a
   revisar e itens "Added" do changelog
3. Revisar, corrigir, commitar os snapshots
4. `python tools/check_drift.py --set-aligned <versão>`

Todo arquivo dos `coverage_globs` precisa estar em `tools/knowledge-map.json`.

## Comandos

Os comandos usam `python`, que é o nome no Windows. Na VM 101 e em outros Linux sem
`python`, troque por `python3`.

```bash
claude plugin validate .
python -m unittest discover -s tests -v
python plugins/claudin/scripts/validate.py <caminho>
```
