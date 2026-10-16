---
type: llm
---

PASS se a resposta aponta que `autoCompactWindow: 200k` está errado porque o valor precisa
ser um inteiro puro (como `200000`) e `200k` não vale ou é ignorado.

FAIL se a resposta não menciona o `autoCompactWindow`, ou o trata como válido.
