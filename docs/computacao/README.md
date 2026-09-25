# Computação — Requisitos Acadêmicos e Algoritmos

Este módulo documenta a aplicação direta de conceitos fundamentais da Ciência da Computação e da Computação Gráfica na jogabilidade e arquitetura de *Projeto The Game*.

> [!IMPORTANT]
> **Requisito Obrigatório da Disciplina:** Todos os conteúdos listados abaixo não são meros detalhes de implementação interna, mas componentes mecânicos ativos e perceptíveis na experiência do jogador.

---

## 📊 Matriz de Conceitos e Aplicação no Jogo

| Conceito da Computação | Onde é Aplicado no Jogo | Documento Técnico |
|---|---|---|
| **Grafos Ponderados** | O campus inteiro é modelado como um grafo: cada cômodo/sala é um nó; portas, corredores e buracos são arestas com pesos (distância e barulho). Desabamentos removem arestas; atalhos criam novas arestas. | [`grafos_e_navegacao.md`](grafos_e_navegacao.md) |
| **Coloração de Grafos** | A grade horária da semana de provas é gerada através do problema clássico de coloração de vértices: turmas que dividem professor ou sala não podem colidir em cores/horários. Essa grade dita a posição de cada Insone no presente. | [`grade_e_coloracao.md`](grade_e_coloracao.md) |
| **Busca em Largura (BFS)** | Propagação de ruído acústico: passos correndo, objetos arremessados e estantes caindo emitem ondas que viajam pelos nós vizinhos do grafo com atenuação por distância. | [`ia_e_perseguicao.md`](ia_e_perseguicao.md) |
| **Algoritmo A\* (A-Star)** | Pathfinding e perseguição ativa: quando um Insone avista ou ouve Gabriel, calcula a rota ótima de menor custo pelo grafo do campus para interceptá-lo. | [`ia_e_perseguicao.md`](ia_e_perseguicao.md) |
| **Cadeias de Markov** | Movimentação errante dos Insones fora da rotina: matriz de probabilidades de transição entre salas vizinhas, modelando o comportamento imprevisível estilo FNAF. | [`ia_e_perseguicao.md`](ia_e_perseguicao.md) |
| **Máquina de Estados Finita (FSM)** | Controla a inteligência e o comportamento de cada Insone (Rotina, Investigando, Caçando, Atordoado, Retornando). | [`ia_e_perseguicao.md`](ia_e_perseguicao.md) |
| **Geometria / Produto Escalar** | Campo de visão cônico dos Insones calculado via $\vec{u} \cdot \vec{v}$ (produto escalar entre vetor de olhar e vetor para o jogador) e verificação de oclusão por raycasting 2D. | [`geometria_e_shaders.md`](geometria_e_shaders.md) |
| **Shaders em GDShader** | Simulação de iluminação volumétrica, decaimento de luz dos fungos e feixes solares atravessando lajes desabadas. | [`geometria_e_shaders.md`](geometria_e_shaders.md) |
