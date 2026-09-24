# Equipe e divisão de tarefas

*Ponto de partida, não contrato.* As mecânicas e o roteiro vão sendo definidos durante o projeto, então os papéis e as tarefas se ajustam a cada sprint. Quando mudar, mude aqui.

## Papéis

Cada pessoa tem **uma área principal**, pela qual é responsável, e pode ajudar nas outras. O roteiro é **compartilhado por duas pessoas**: uma dona do cânone e uma co-roteirista.

| # | Papel | Área principal | Papel secundário | Pessoa |
|---|---|---|---|---|
| 1 | **Sistemas e IA** | Grafo do campus, IA dos Insones (BFS, A\*, cadeia de Markov, máquina de estados), grade horária por coloração de grafos | Documentar os algoritmos para a apresentação | [preencher] |
| 2 | **Jogabilidade e interface** | Movimento do Gabriel, esconderijos e microgames, inventário, luz dos fungos como recurso, dormir e salvar, troca presente ↔ sonho, interface | Testes e balanceamento | [preencher] |
| 3 | **Arte e gráficos** | Pixel art de personagens e cenários, animações, iluminação 2D, shaders (fungos, poeira, visual do sonho) | **Co-roteirista** (aparência e história visual dos personagens) | [preencher] |
| 4 | **Roteiro e fases** | **Dono do roteiro:** história, diálogos, textos do jogo, documentos de lore. Montagem das salas, áudio | Manter o GDD e o `docs/decisoes.md` em dia | [preencher] |

**Revisor principal (code owner):** Davi. Os PRs do Davi são revisados por outro integrante.

### Como o roteiro funciona com duas pessoas

- O **dono do roteiro** (papel 4) mantém a história coerente e tem a palavra final quando há conflito.
- A **co-roteirista** (papel 3) escreve junto e cuida para que a história apareça na arte — o que está nas paredes, como cada Insone se parece, o que muda entre presente e sonho.
- **Decisões grandes de história são do grupo todo**, numa conversa rápida na reunião semanal, e vão para `docs/decisoes.md`.
- Qualquer um pode sugerir ideia de história abrindo uma issue com o rótulo `roteiro`.

## Onde os papéis se encontram

Combinem isso no primeiro sprint:

- **1 → 2:** a IA avisa a jogabilidade por sinais do Godot (`jogador_detectado`, `jogador_perdido`, `insone_atordoado`). Nomes definidos uma vez e não mexe mais.
- **1 ↔ 4:** cada sala montada é um nó do grafo. Formato combinado: cada sala tem um ID e uma lista de portas com peso.
- **3 → todos:** guia de estilo com paleta, tamanho dos sprites e padrão de nome de arquivo antes da primeira arte.
- **2 ↔ 3:** a luz dos fungos é mecânica (2 controla a intensidade) e visual (3 decide como aparece).
- **4 ↔ 3:** roteiro e arte revisam juntos o que cada sala conta.

## Sprints (exemplo)

Sprints de duas semanas. Ajustem a cada início de sprint conforme o que foi decidido.

| Sprint | 1. Sistemas e IA | 2. Jogabilidade | 3. Arte e gráficos | 4. Roteiro e fases |
|---|---|---|---|---|
| 1 | Grafo com 3 salas de teste, um Insone com rotina fixa | Movimento, corrida, colisão, câmera | Guia de estilo, primeiro sprite do Gabriel, primeira luz 2D | Roteiro da Segunda (Biblioteca): o que o jogador descobre e como. Sala de aula de protótipo |
| 2 | Som por BFS, perseguição por A\*, máquina de estados | Esconderijo com um microgame, cápsula de clarão | Animações do Gabriel, primeiro Insone | Textos e documentos da Biblioteca, montagem da Biblioteca no grafo |
| 3 | Grade horária, cadeia de Markov | Inventário, fungos como recurso | Tiles da Biblioteca, shader dos fungos | Roteiro do primeiro sonho, som ambiente |
| 4 | Ajuste da IA na Biblioteca completa | Dormir, salvar, transição para o sonho | Versão "sonho" da Biblioteca, shader do sonho | Diálogos do sonho, polimento da Biblioteca |

**Marco do Sprint 4:** a Biblioteca jogável do começo ao fim — um Insone, esconderijo, luz, sono e sonho. Se o prazo apertar, isso já é um jogo entregável; o resto é expansão.

## Rotina

- **Reunião semanal curta:** cada um mostra o que fez **rodando**, não descrito, e o que vai fazer.
- **Início de sprint:** escolher as issues do sprint e distribuir.
- **Fim de sprint:** tudo que foi feito precisa estar mesclado na `main`.
