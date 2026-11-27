---
type: llm
---

O usuário pediu o desenho da estrutura Claude Code de um projeto novo, descrito numa frase:
acompanhar preço de passagem aérea e avisar quando cair. Muita coisa ainda está aberta.

PASS se a resposta conversa sobre a ideia e faz no máximo três perguntas, sobre o que mais
muda a estrutura (por exemplo, como os preços serão obtidos, como e com que frequência
avisar, quem usa), e não entrega ainda a arquitetura completa. Declarar suposições ou
esboçar caminhos possíveis não conta contra.

FAIL se fizer quatro perguntas ou mais, se anunciar rodada, fase ou etapa, ou se já
entregar a arquitetura completa (diagrama com skills, agentes e hooks) sem ter entendido o
problema.
