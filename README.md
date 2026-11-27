# claudin

**claud(e) + (plug)in**: meu toolkit pessoal de Claude Code. O nome também é o Claudinho.

Um plugin que audita, cria e corrige estruturas `.claude/` em qualquer projeto, acompanha as
docs oficiais do Claude Code e só mantém o que comprovadamente funciona melhor que o Claude
Code puro.

> Em construção. Hoje: `/claudin:audit`, `/claudin:fix`, `/claudin:design`,
> `/claudin:create-project`, `/claudin:create-agent`, `/claudin:create-skill`,
> `/claudin:create-hook`, `/claudin:grill-me`, `/claudin:brainstorm`, `/claudin:handoff` e
> `/claudin:about`. A avaliação comparativa com o Claude Code puro está em andamento.

## Instalar

**Pré-requisito:** Python 3 no PATH (`python --version` no Windows, `python3 --version` no
Linux e no macOS). As skills rodam scripts Python só com a biblioteca padrão; não precisa
instalar pacote.

São três passos, todos dentro de uma sessão do Claude Code (não precisa do comando `claude`
no terminal):

1. **Adicione o marketplace e instale o plugin**, um comando de cada vez. O primeiro só
   registra o catálogo; quem instala é o segundo:

   ```
   /plugin marketplace add marciomachado-mm/claudin
   /plugin install claudin@claudin
   ```

   Depois, `/reload-plugins` ou uma sessão nova.

2. **Ligue a atualização automática.** Em marketplace de terceiros ela vem desligada. Em
   `/plugin`, vá para a aba **Marketplaces** (não é a tela do plugin, em Installed),
   escolha `claudin` e selecione **Enable auto-update**
   ([doc oficial](https://code.claude.com/docs/en/plugins/install.md)). Sem ela, atualize
   quando quiser com `/plugin marketplace update claudin`. O `/claudin:about` avisa quando
   sai versão nova.

   Se o marketplace foi adicionado de uma pasta local (um clone), o plugin é lido direto da
   pasta e a atualização automática não traz versão nova: atualize com `git pull` ou troque
   pelo marketplace do GitHub ([doc oficial](https://code.claude.com/docs/en/plugins/loading.md)).

3. **Teste em qualquer projeto:** `/claudin:about` mostra a versão instalada e os comandos.

### Usar direto de um clone

Para testar uma alteração sem instalar, carregue o plugin da pasta só naquela sessão:

```bash
git clone https://github.com/marciomachado-mm/claudin.git
cd claudin
claude --plugin-dir ./plugins/claudin
```

Tem precedência sobre um claudin já instalado e lê os arquivos direto da pasta, sem copiar
([doc oficial](https://code.claude.com/docs/en/plugins/loading.md)).

## Como o repo se organiza

| Pasta | O que é |
|---|---|
| `plugins/claudin/` | O plugin: o que é instalado |
| `.claude-plugin/marketplace.json` | Faz deste repo um marketplace com um plugin |
| `tools/` | Baixa as docs oficiais e detecta defasagem |
| `tests/` | Testes do repo e do validador |

## Problemas e contribuições

Issues são bem-vindas: falha, comportamento estranho ou sugestão, com a versão do claudin e
do Claude Code. Pull requests de terceiros não são aceitos.

## Créditos

O protocolo de `/claudin:grill-me` e o vocabulário de
`knowledge/guides/writing-for-agents.md` são adaptados de
[mattpocock/skills](https://github.com/mattpocock/skills), licença MIT,
Copyright (c) Matt Pocock. A ideia de `/claudin:handoff` vem da skill `handoff` do mesmo
repositório; o texto é nosso.

## Licença

[MIT](LICENSE).

## Desenvolvimento

Validar e testar:

```bash
claude plugin validate .
python -m unittest discover -s tests -v
```
