# Evidência de uso: histórico de sessões do projeto

Como o `audit`, o `fix` e o `design` usam a saída de `scripts/sessions.py`. O script lê as
transcrições do projeto em `~/.claude/projects/<projeto>/` e devolve só agregados.

## Regras de privacidade

- **Só com permissão.** Pergunte antes de rodar, a cada vez; o padrão é não rodar. Se não
  der para perguntar (sessão sem interação), não rode
- **Nunca leia transcrição.** Nada de Read, Grep ou `cat` em `~/.claude/projects`: só a
  saída do script. Ela já vem mascarada (IPs, e-mails, tokens, `senha=`, home do usuário)
- **Não copie para fora da conversa.** Nem para arquivo do projeto, nem para o lab do
  claudin. No relatório, use contagens; os exemplos de comando bloqueado só aparecem se
  ajudarem a decidir uma correção
- Se o usuário preferir sem nenhum trecho literal, rode com `--no-samples`

## O que cada sinal sugere

| Sinal na saída | Leitura | Achado possível |
|---|---|---|
| `skills.nunca_usadas` | Skill do projeto sem nenhuma invocação na janela | Se o Claude pode chamá-la, ela custa contexto em todo turno sem uso: candidata a `disable-model-invocation: true` ou remoção. Confirme com o usuário: pode ser rara e importante |
| `skills.usadas` com muito uso | Fluxo central do projeto | Prioridade alta para qualquer problema nessa skill |
| `hooks` com o mesmo motivo várias vezes | Bloqueio recorrente | Leia os exemplos: comando inofensivo (heredoc, script, `/tmp`) é falso positivo do hook. Correção: estreitar o padrão do hook, ou checar o comando de fato e não o texto inteiro |
| `erros_por_causa.permissao_negada` alto | Regra de permissão travando trabalho legítimo | Candidata a `allow` específico, se o comando for seguro |
| `erros_por_causa.recusado_pelo_usuario` | O usuário disse não a uma ação | Instrução que leva o Claude a propor o que o usuário não quer: revisar CLAUDE.md ou rule |
| `erros_por_causa.sintaxe_shell` | Aspas aninhadas, heredoc quebrado | Nota no CLAUDE.md (preferir arquivo de script a heredoc longo, `ssh host 'bash -s' < script`) |
| `erros_por_causa.encoding` | CRLF ou cp1252 | No Windows: `encoding="utf-8"` e `newline` explícitos em scripts; `.gitattributes` com `eol=lf` |
| `erros_por_causa.rede_ssh` | Host fora do ar ou chave | Problema de ambiente, não de configuração; só registre |
| `erros_por_causa.classificador_auto` | O modo auto bloqueou | Ação que precisa de regra explícita, ou que não deveria ser feita |
| `sessoes_pesadas` com muitas horas ou erros de API | Sessão longa demais | Recomendar `/compact` mais cedo, dividir o trabalho em sessões, e `/usage` para ver onde o consumo vai |
| `sinais_de_confusao` alto | O usuário pediu explicação várias vezes | Rever a rule ou o trecho do CLAUDE.md sobre estilo de explicação |
| `nao_verificado` não vazio | O formato das transcrições pode ter mudado | Diga isso ao usuário: os números afetados podem estar zerados |

## Ressalvas que vão no relatório

- A janela é o que ainda existe no disco: o Claude Code apaga transcrições mais velhas que
  `cleanupPeriodDays`, 30 dias por padrão (`settings-reference.md`)
- O formato das transcrições não é documentado; só o local dos arquivos é
  (`claude-directory.md`). As categorias de erro vêm de padrões de texto
- Uso é sinal, não veredito: skill pouco usada pode ser rara e importante
- O `/insights` nativo faz uma leitura narrativa das sessões da máquina inteira; é
  complemento, não substituto
