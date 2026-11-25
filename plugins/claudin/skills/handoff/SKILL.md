---
name: handoff
description: Fecha o trabalho da sessão num HANDOFF.md (objetivo, estado, decisões, o que não funcionou e próximo passo) para uma sessão nova, outra pessoa ou outra ferramenta continuar de onde parou.
disable-model-invocation: true
argument-hint: "[caminho.md] [notas sobre a sessão]"
allowed-tools:
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git branch *)
---

Escreva a passagem de bastão desta sessão. Quem vai ler não viu a conversa: uma sessão nova
depois de `/clear`, outra pessoa ou outra ferramenta. A doc recomenda justamente isso
quando a conversa ficou pesada: `/clear` e um prompt novo que junte o que se aprendeu
(`best-practices.md`). O arquivo é esse prompt.

Não é para continuar a mesma conversa: para isso existe `claude --continue`
(`cli-reference.md`). Para mandar um achado a outra sessão que já está aberta, peça ao
Claude que envie a ela (`features-overview.md`).

## 1. Onde escrever

Argumento: $ARGUMENTS

Se ele começar por um caminho terminado em `.md`, escreva nele; senão, use `HANDOFF.md` na
raiz do repositório. O resto do argumento são notas do usuário sobre a sessão (o que
tentou, o que decidiu): elas valem como a conversa e entram no arquivo. Se o arquivo já existir, leia
antes: ele é a passagem anterior. Reescreva com o estado de agora e mantenha só o que
ainda vale (uma tentativa que falhou continua valendo).

## 2. Junte os fatos

Rode cada comando sozinho:

```bash
git status --short
git branch --show-current
git log --oneline -5
git diff --stat
```

Fora de um repositório git, pule esta parte e diga isso no arquivo.

O resto vem da conversa. Separe o que foi **verificado** (teste rodou, comando deu certo,
o usuário confirmou) do que só foi feito. Na dúvida, é "feito, não verificado".

## 3. Escreva

Use este modelo. Seção sem conteúdo leva "nada" em vez de sumir: quem lê precisa saber
que não há pendência, e não ficar na dúvida se você esqueceu.

```markdown
# Handoff: <o trabalho, em poucas palavras>

<data> · branch `<branch>` · último commit `<hash> <mensagem>`

## Objetivo

<o que o usuário pediu, com as palavras dele quando forem curtas, e o critério de pronto>

## Estado

- Feito e verificado: <item> (<como foi verificado>)
- Feito, não verificado: <item>
- Não começado: <item>
- Mudanças sem commit: <arquivos do git status, ou "nenhuma">

## Decisões

- <decisão>: <por quê>. <quem decidiu, se foi o usuário>

## O que não funcionou

- <tentativa>: <por que falhou, ou o erro em uma linha>

## Arquivos que importam

- `<caminho>`: <papel no trabalho>

## Próximo passo

<um passo só, concreto, com o comando ou o arquivo por onde começar>

## Perguntas abertas

- <o que só o usuário decide>
```

Regras:

- **O que não funcionou é a seção mais valiosa.** Sem ela, a próxima sessão tenta de novo
  o mesmo caminho. Inclua o erro exato quando for curto
- **Curto:** o arquivo entra inteiro no contexto de quem continua. Aponte para arquivos e
  commits em vez de copiar o conteúdo deles
- **Nada de segredo:** token, senha, chave e conteúdo de `.env` não entram, nem como
  exemplo. Se um segredo fez parte do trabalho, diga só onde ele fica
- **Fatos, não transcrição:** não cole trechos da conversa, resuma

## 4. Feche

1. Confira se o arquivo está no `.gitignore` (`git status --short` mostra se ele aparece
   como novo). Se não estiver, diga ao usuário e pergunte se ele quer versionar a passagem
   ou ignorá-la; não edite o `.gitignore` sem a resposta
2. Mostre o caminho do arquivo e o próximo passo
3. Dê o prompt para a sessão nova, pronto para colar depois do `/clear`:
   `Leia <caminho> e continue do próximo passo. Confirme o estado com git status antes de mexer.`
