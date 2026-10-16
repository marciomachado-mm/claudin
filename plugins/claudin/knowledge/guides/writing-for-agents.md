# Como escrever documento que agente lê

Referência para SKILL.md, CLAUDE.md, rule e prompt de agente. O empacotamento muda; a
escrita não. O alvo não é uma saída idêntica a cada execução: é o agente seguir o **mesmo
processo** toda vez.

O vocabulário vem de [mattpocock/skills](https://github.com/mattpocock/skills)
(`writing-for-agents`), contribuição da comunidade sob licença MIT, não documentação
oficial. O que é fato do Claude Code cita `knowledge/snapshots/`; o resto é **[prática]**.

## Ponteiro

Ponteiro é uma referência que vive no contexto, nomeia material que está fora dele e diz
quando ir buscá-lo. A `description` de uma skill é um ponteiro; uma linha do CLAUDE.md que
nomeia um doc também.

- **O gatilho vem primeiro.** A doc diz o mesmo: "Put the key use case first" (`skills.md`)
- **Um gatilho por ramificação.** Sinônimos da mesma ramificação são duplicação
- **Limite duro:** `description` + `when_to_use` são cortados em 1.536 caracteres na
  listagem (`skills.md`)

Material bom atrás de ponteiro vago é bug de redação: afie o ponteiro antes de copiar o
material para dentro do contexto. **[prática]**

## As duas cargas

| Carga | Quem paga | O que gasta |
|---|---|---|
| Contexto | a janela do agente | CLAUDE.md, rule sem `paths:`, description de skill automática, corpo de skill já invocada |
| Cognitiva | o humano | lembrar que o documento existe e quando usá-lo |

Fatos: rule sem `paths:` carrega em toda sessão como o CLAUDE.md (`memory.md`); a
description de skill com `disable-model-invocation: true` **não** fica em contexto
(`skills.md`, tabela de invocação); o corpo de uma skill invocada permanece nos turnos
seguintes (`skills.md`).

## Hierarquia

1. **Passo no arquivo:** o que o agente faz, em ordem
2. **Referência no arquivo:** consultada quando precisa
3. **Referência revelada:** em arquivo separado, alcançada por ponteiro. Inline o que toda
   execução precisa; empurre o que só algumas precisam

Junte definição, regra e ressalva de um conceito no mesmo lugar. Documento longo demais,
mesmo com toda linha útil, dilui a atenção: a cura é descer o material de degrau.
**[prática]**

## Critério de conclusão

Todo passo termina numa condição verificável que diz ao agente que acabou. "Entendimento
alcançado" convida a parar cedo; "todo agente do repo auditado" não. Os melhores critérios
são verificáveis e exaustivos. **[prática]**

## Palavra-âncora

Um conceito compacto que o modelo já conhece (*fronteira*, *auditoria*, *sedimento*),
repetido como token, ancora um comportamento inteiro com poucas palavras. Prefira a palavra
existente a uma inventada. **[prática]**

**Prompte o positivo.** Proibição traz o comportamento proibido para o contexto. Diga o
comportamento desejado; use proibição só como guarda-corpo, e acompanhada do alvo positivo.
**[prática]**

## Poda

- **Fonte única:** cada significado em um lugar só
- **O ambiente é fonte de verdade:** não repita o que `settings.json`, o layout ou o
  `--help` já dizem. Documente o que não dá para descobrir olhando: a convenção não escrita,
  o porquê de uma escolha
- **Sedimento:** sem poda, camadas velhas se acumulam porque adicionar parece seguro e
  remover parece arriscado
- **No-op:** instrução que o modelo já segue sozinho só custa. Discordância sobre no-op se
  resolve rodando o documento, não debatendo. **[prática]**

## Mecânica de skills

| Quem precisa chamar | Frontmatter | Description em contexto |
|---|---|---|
| Usuário e Claude | nenhum dos dois campos | sim |
| Só o usuário | `disable-model-invocation: true` | não |
| Só o Claude | `user-invocable: false` | sim |

Fonte: `skills.md`, tabela de invocação.

- Para uma skill chamar outra, escreva "chame a tool Skill com `<nome>`". Só funciona se a
  alvo for chamável pelo Claude; para skill só do usuário, peça ao usuário que a rode
- O `SKILL.md` entra uma vez, na invocação, e não é relido. Regra que precisa valer sempre
  vira hook; depois de compactação, invoque de novo. As instruções mais importantes vão no
  topo (`skills.md` § Claude stops following a skill)
- Material que várias skills compartilham fica num arquivo comum, alcançado pelo caminho do
  plugin (`${CLAUDE_PLUGIN_ROOT}`) ou da skill (`${CLAUDE_SKILL_DIR}`) (`skills.md`)

## Onde cada material mora

| Material | Onde |
|---|---|
| Vale em toda sessão | CLAUDE.md |
| Vale para uma área do repo | rule com `paths:` (carrega com Read, Write ou Edit em arquivo correspondente; Grep e Bash não disparam) |
| Conhecimento de uma tarefa | skill chamável pelo Claude |
| Fluxo com efeito colateral | skill com `disable-model-invocation: true` |
| Referência que uma skill usa às vezes | arquivo ao lado do `SKILL.md` |
| Conhecimento que um agente sempre precisa | campo `skills:` do agente (injeta o conteúdo inteiro no início) |

Fontes: `memory.md`, `skills.md`, `sub-agents.md`.
