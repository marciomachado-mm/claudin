# claudin

**claud(e) + (plug)in**: meu toolkit pessoal de Claude Code. O nome também é o Claudinho.

Um plugin que audita, cria e corrige estruturas `.claude/` em qualquer projeto, acompanha as
docs oficiais do Claude Code e só mantém o que comprovadamente funciona melhor que o Claude
Code puro.

> Em construção. Hoje: `/claudin:audit`, `/claudin:fix`, `/claudin:design`,
> `/claudin:create-project`, `/claudin:create-agent`, `/claudin:create-skill`,
> `/claudin:create-hook`, `/claudin:grill-me` e `/claudin:about`. A avaliação comparativa
> com o Claude Code puro está em andamento.

## Instalar

São três passos no Claude Code:

1. **Adicione o marketplace e instale o plugin:**

   ```
   /plugin marketplace add marciomachado-mm/claudin
   /plugin install claudin@claudin
   ```

2. **Ligue a atualização automática.** Em marketplace de terceiros ela vem desligada: em
   `/plugin`, abra **Marketplaces**, escolha `claudin` e selecione **Enable auto-update**
   ([doc oficial](https://code.claude.com/docs/en/plugins/install.md)).

3. **Teste em qualquer projeto:** `/claudin:about`.

### Outras formas de usar

<details>
<summary><strong>Abrir o Claude Code no próprio repo</strong></summary>

```bash
git clone https://github.com/marciomachado-mm/claudin.git
cd claudin
claude
```

Aceite a pergunta de confiança da pasta: o `.claude/settings.json` do repo registra a
própria pasta como marketplace e liga o plugin, que carrega direto dos arquivos, sem
instalar. Uma edição nas skills vale na próxima sessão ou com `/reload-plugins`
([doc oficial](https://code.claude.com/docs/en/plugins/org.md)). Se você já instalou o
claudin pelo marketplace, vale a cópia instalada; use a forma abaixo.

</details>

<details>
<summary><strong>Carregar da pasta só numa sessão</strong></summary>

```bash
claude --plugin-dir ./plugins/claudin
```

Tem precedência sobre um claudin já instalado
([doc oficial](https://code.claude.com/docs/en/plugins/loading.md)).

</details>

## Como o repo se organiza

| Pasta | O que é |
|---|---|
| `plugins/claudin/` | O plugin: o que é instalado |
| `.claude-plugin/marketplace.json` | Faz deste repo um marketplace com um plugin |
| `.claude/settings.json` | Carrega o plugin quando o Claude Code abre no próprio repo |
| `tools/` | Baixa as docs oficiais e detecta defasagem |
| `tests/` | Testes do repo e do validador |

## Créditos

O protocolo de `/claudin:grill-me` e o vocabulário de
`knowledge/guides/writing-for-agents.md` são adaptados de
[mattpocock/skills](https://github.com/mattpocock/skills), licença MIT,
Copyright (c) Matt Pocock.

## Licença

[MIT](LICENSE).

## Desenvolvimento

Validar e testar:

```bash
claude plugin validate .
python -m unittest discover -s tests -v
```
