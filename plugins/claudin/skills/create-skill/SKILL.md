---
name: create-skill
description: Cria uma skill num projeto, checando antes se skill é o recurso certo, com a description que faz ela ser usada e proteção para o que tem efeito colateral.
disable-model-invocation: true
argument-hint: "<o que a skill deve fazer>"
allowed-tools:
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py *)
  - Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
  - Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py *)
---

Crie uma skill para: $ARGUMENTS

Se não houver descrição acima, pergunte só o que a skill deve fazer. O destino é
`.claude/skills/<nome>/SKILL.md` do projeto atual, salvo se o usuário indicar outro; ele
aparece na proposta do passo 3, onde o usuário pode trocá-lo, e não vira pergunta.

## 1. É skill mesmo?

Os comandos do claudin são pré-aprovados só na forma exata: rode cada um **sozinho**
(sem `cd`, `&&` ou `;`) e escreva o caminho com barras `/`.
Escolha o interpretador pelo sistema antes do primeiro comando: `python` no Windows, `python3` no Linux e no macOS, com o resto do comando igual. Só se o nome escolhido não existir, use o outro.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide choosing-features writing-for-agents
```

Se alguém vai querer
**chamar**, é skill; se o Claude deve **já saber**, é rule ou CLAUDE.md; se precisa
acontecer **sempre** num evento, é hook. Fora do caso de skill, proponha o recurso certo e
pare, a menos que o usuário insista.

**Pedido de verificação** ("conferir se funciona", "rodar antes do commit", "testar a
mudança"): o Claude Code já traz o `/verify`, que compila e roda o app e grava a receita
que deu certo em `.claude/skills/verify/SKILL.md` (`skills.md`). Ofereça rodar o `/verify`
uma vez antes de escrever à mão; escreva a skill quando o usuário já sabe quais checks
quer, ou quando a receita gravada não basta. Nesse caso, siga o passo 2 com o modelo de
verificação do passo 3.

## 2. Decida as peças

Escreva o corpo seguindo o guia `writing-for-agents`. Pergunte só o que é decisão:

- **Quem chama** (`skills.md`, tabela de invocação):
  - efeito colateral (deploy, commit, envio, escrita) → `disable-model-invocation: true`;
    a description também sai do contexto. Exceção: a skill de verificação, abaixo
  - conhecimento de fundo, que não é ação → `user-invocable: false`
  - os dois chamam → nenhum dos campos
- **`description`:** o caso de uso principal primeiro. Gatilhos extras vão em
  `when_to_use`. A soma é cortada em 1.536 caracteres
- **Nome:** é o nome da pasta, em minúsculas e hífens. Sem `<`, `>`, espaço invisível ou
  duplicado. A pasta não pode se chamar `synced`
- **Skill de verificação:** com o nome `verify` (ou `simplify`), o Claude a roda antes de
  cada commit, salvo em mudança só de docs ou testes (v2.1.286+, `skills.md`). Só vale se
  ela estiver no projeto, nas pessoais ou nas da empresa (de plugin não conta), se o Claude puder chamá-la (**sem**
  `disable-model-invocation`, mesmo rodando comandos) e com `includeGitInstructions`
  ligado. Outro nome não ganha esse gatilho
- **Isolamento:** `context: fork` roda num subagente sem a conversa, escolhido em `agent`.
  O padrão é rodar em background; `background: false` espera o resultado no turno
  (v2.1.218+). Só use fork se a skill não precisa conversar
- **Comandos sem prompt:** `allowed-tools` pré-aprova enquanto a skill roda; não bloqueia
  outros comandos
- **Material grande ou opcional:** arquivos ao lado do `SKILL.md`, referenciados por
  `${CLAUDE_SKILL_DIR}`, em vez de inflar o corpo

## 3. Proponha e confirme

Base do `SKILL.md`:

```markdown
---
description: O que faz e quando usar, caso de uso principal primeiro.
argument-hint: "<argumento>"
---

<Uma frase: o que este fluxo resolve.> Alvo: $ARGUMENTS

## 1. <Primeiro passo>
<instrução concreta; se houver comando, o comando>

## 2. Confirme antes de agir
<se escreve, publica ou envia: mostre o resultado e só execute após confirmação>

## 3. Verifique
<o check que volta passou/falhou: teste, build, linter, script que compara com o esperado>
Mostre o comando e a saída. Falhou: corrija e rode de novo antes de dizer que terminou.

Pronto quando <condição verificável>.
```

O passo "Verifique" entra quando a skill produz algo que dá para checar (código, arquivo,
deploy). Sem check possível, o último passo diz o que ficou sem verificar. A doc pede
evidência, não "os testes passaram" (`best-practices.md`, Give Claude a check to run).

Modelo para a skill de verificação:

```markdown
---
name: verify
description: Confere que a mudança funciona rodando os checks do projeto e mostrando a saída. Use antes de dizer que terminou e antes de cada commit.
allowed-tools:
  - Bash(<comando do check> *)
---

Rode cada check sozinho, do mais rápido ao mais lento:

1. `<lint ou typecheck>`
2. `<testes da parte mexida>`
3. `<o comportamento de verdade: rodar o app, o script, a consulta>`

Mostre o comando e a saída de cada um. Se um falhar, pare, corrija e rode de novo a
partir dele. Não diga que terminou com check falhando ou sem rodar.

Pronto quando todos passaram e a saída de cada um está na resposta.
```

Mostre a estrutura e o conteúdo
completos e espere a confirmação. Só então crie a pasta e os arquivos.

## 4. Valide

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <raiz-do-projeto>
```

Corrija o que o validador apontar na skill nova. Pronto quando a skill existe e o
validador não acusa nada nela.
