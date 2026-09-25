# Mecânicas — Furtividade e Esconderijos

## 1. Esconderijos no Cenário

Quando um Insone está patrulhando ou perseguindo Gabriel, a principal forma de quebrar a linha de visão é entrar em um esconderijo interativo pressionando `E`:

| Esconderijo | Ocorrência Típica | Microgame Associado | Nível de Segurança |
|---|---|---|---|
| **Armário Metálico de Vestiário** | Blocos de Aula e NAMI | Segurar a porta contra a vibração | Alto |
| **Cabine Individual de Estudo** | Biblioteca Central | Prender a respiração no timing correto | Médio (visível se tiver frestas) |
| **Raízes Caídas e Mesas Quebradas** | Centro de Convivência | Ficar imóvel (manter tecla pressionada) | Médio |
| **Macas com Cortinas Desfiadas** | Enfermarias do NAMI | Controle de batimento cardíaco / respiração | Médio-Alto |

---

## 2. Microgames de Tensão (*Into the Pit Style*)

Ficar dentro de um esconderijo não é garantia passiva de imunidade. Se um Insone se aproximar da mesma sala ou passar em frente ao esconderijo, um **microgame de tensão rápida** é acionado:

### A. Prender a Respiração (*Timing Bar*)
- Uma barra oscilante surge na tela com uma pequena zona segura verde.
- O jogador precisa pressionar a tecla `Espaço` no compasso correto para que Gabriel contenha a respiração ofegante.
- Falhar em três pulsos faz Gabriel soltar um engasgo audível, denunciando o esconderijo.

### B. Segurar a Porta (*Tensão Mecânica*)
- A porta enferrujada do armário tende a ranger e se abrir pela ação do vento ou vibração dos passos pesados do Insone.
- O jogador deve manter a tecla de ação pressionada com força contínua, ajustando a pressão conforme os solavancos.

### C. Imobilidade Absoluta (*Dead Silence*)
- Requer não tocar em nenhum controle de direção ou ação durante a passagem do perseguidor por um período de 3 a 5 segundos.

---

## 3. Mecânica de Distração por Arremesso

Gabriel pode carregar pequenos fragmentos de concreto, pedras ou cacos de cerâmica recolhidos pelo chão:
- **Arremesso (Botão Direito do Mouse / `F`):** Uma linha pontilhada simples indica o arco parabólico de lançamento.
- **Impacto e Ruído:** Ao atingir uma parede ou piso distante, o objeto emite um estalo sonoro pontual.
- **Desvio de Rota:** O som ativa o algoritmo BFS nos nós do grafo: se o Insone estiver dentro do raio de alcance auditivo, ele transita do estado *Rotina* para *Desconfiado/Investigando*, movendo-se em direção ao ponto de impacto e liberando o caminho para Gabriel.
