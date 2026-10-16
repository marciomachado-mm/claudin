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
- Toda afirmação sobre o Claude Code cita a fonte (página da doc oficial)
- Textos para o usuário em português; nomes de código em inglês

## Comandos

```bash
claude plugin validate .
python -m unittest discover -s tests -v
```
