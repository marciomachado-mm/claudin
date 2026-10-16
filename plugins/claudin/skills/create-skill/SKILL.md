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

Se não houver descrição acima, pergunte o que a skill deve fazer. O destino é
`.claude/skills/<nome>/SKILL.md` do projeto atual, salvo se o usuário indicar outro.

## 1. É skill mesmo?

Os comandos do claudin são pré-aprovados só na forma exata: rode cada um **sozinho**
(sem `cd`, `&&` ou `;`) e escreva o caminho com barras `/`.
Use `python` no Windows; no Linux ou macOS, se `python` não existir, use `python3` no lugar, com o resto do comando igual.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/kb.py guide choosing-features writing-for-agents
```

Se alguém vai querer
**chamar**, é skill; se o Claude deve **já saber**, é rule ou CLAUDE.md; se precisa
acontecer **sempre** num evento, é hook. Fora do caso de skill, proponha o recurso certo e
pare, a menos que o usuário insista.

## 2. Decida as peças

Escreva o corpo seguindo o guia `writing-for-agents`. Pergunte só o que é decisão:

- **Quem chama** (`skills.md`, tabela de invocação):
  - efeito colateral (deploy, commit, envio, escrita) → `disable-model-invocation: true`;
    a description também sai do contexto
  - conhecimento de fundo, que não é ação → `user-invocable: false`
  - os dois chamam → nenhum dos campos
- **`description`:** o caso de uso principal primeiro. Gatilhos extras vão em
  `when_to_use`. A soma é cortada em 1.536 caracteres
- **Nome:** é o nome da pasta, em minúsculas e hífens. Sem `<`, `>`, espaço invisível ou
  duplicado. A pasta não pode se chamar `synced`. Uma skill `verify` ou `simplify` passa a
  ser rodada antes de cada commit (v2.1.286+, `skills.md`)
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

Pronto quando <condição verificável>.
```

Mostre a estrutura e o conteúdo
completos e espere a confirmação. Só então crie a pasta e os arquivos.

## 4. Valide

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py <raiz-do-projeto>
```

Corrija o que o validador apontar na skill nova. Pronto quando a skill existe e o
validador não acusa nada nela.
