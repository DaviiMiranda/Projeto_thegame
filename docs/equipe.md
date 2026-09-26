# Equipe e responsabilidades

*Ponto de partida, não contrato.* Como mecânicas e roteiro vão sendo definidos durante o projeto, as tarefas específicas saem daqui a cada sprint: **os papéis ficam, as tarefas mudam.** Quando mudar, mude aqui.

## Visão geral

Quatro pessoas, quatro papéis. Duas cuidam do **código** e duas são **roteiristas**, cada uma combinando a escrita com uma área de produção. A **produção de arte** fica com o Davi, e o resto do time pede o que precisa (ver [Como pedir arte](#como-pedir-arte)).

| # | Papel | Área principal | Pessoa |
|---|---|---|---|
| 1 | **Programador de sistemas e artista** | Sistemas de computação, IA dos inimigos e produção de toda a arte | **Davi Miranda** |
| 2 | **Programador de jogabilidade** | Tudo que o jogador controla e vê na interface | [preencher] |
| 3 | **Roteirista e diretor de arte** | Personagens, mundo e a história contada pela imagem: decide *o que* a arte mostra | [preencher] |
| 4 | **Roteirista e designer de fases** | Trama, mistério, textos, e a história contada pelo espaço e pelo som | [preencher] |

**Líder do projeto e revisor principal (code owner):** Davi Miranda, junto com o papel 1. Os PRs do Davi são revisados por outro integrante.

---

## 1. Programador de sistemas e artista — Davi Miranda

**Missão:** fazer o mundo do jogo funcionar por conta própria, garantir o requisito obrigatório de computação da disciplina, e produzir a arte do jogo.

**Como programador de sistemas:**
- Estrutura do campus em código (salas, conexões, navegação).
- Comportamento dos inimigos: rotina, percepção do jogador, perseguição, reação.
- Os algoritmos e estruturas de dados exigidos pela disciplina (grafos, busca, probabilidade, estruturas avançadas, matemática).
- Ferramentas de depuração que mostrem esses sistemas funcionando na tela.
- Documentar cada algoritmo: o que faz, por que foi escolhido e onde aparece no jogo.

**Como artista:**
- Pixel art de personagens, inimigos, objetos e cenários.
- Animações.
- Produzir a partir dos pedidos de arte do time, seguindo o guia de estilo e as fichas do diretor de arte.

**Entrega típica:** um sistema funcionando numa cena de teste, com modo de depuração e um resumo em `docs/`, ou um pacote de arte (sprites, animações, tiles) pronto para uso no Godot.

**Trabalha junto com:**
- **Jogabilidade**, para combinar como os inimigos avisam o resto do jogo (sinais) e quais animações cada ação precisa.
- **Fases**, para cada sala montada virar parte do mapa que os inimigos entendem.
- **Diretor de arte**, que define o que cada arte precisa mostrar.

**Não é responsável por:** controle do jogador, interface, decidir sozinho o que a arte conta (isso é do diretor de arte e dos roteiristas).

**Atenção à carga:** este papel acumula sistemas, toda a arte, liderança e revisão. Priorize os sistemas exigidos pela disciplina; na arte, **placeholder primeiro**: o time não espera a arte final para programar e montar as salas.

---

## 2. Programador de jogabilidade

**Missão:** fazer o jogador sentir o jogo: controle, resposta, tensão.

**Responsabilidades:**
- Movimento e ações do Gabriel.
- Mecânicas do jogador: esconder, distrair, se defender, usar itens, interagir com o cenário.
- Recursos e inventário.
- Salvar, carregar, morrer e recomeçar.
- Transição entre presente e sonho.
- Interface: HUD, diário, menus, caixas de diálogo.
- Colocar os textos do roteiro dentro do jogo.

**Entrega típica:** uma mecânica jogável numa sala de teste, com os parâmetros ajustáveis no editor.

**Trabalha junto com:**
- **Sistemas**, na interação entre jogador e inimigos.
- **Arte**, para animações e efeitos de cada ação.
- **Roteiristas**, para diálogos, documentos e sonhos aparecerem do jeito certo.

**Não é responsável por:** IA dos inimigos, montagem das salas, arte.

---

## 3. Roteirista e diretor de arte

**Missão:** decidir **quem** existe neste mundo e **como ele parece**, e garantir que a imagem conte a história.

**Como roteirista:**
- Personagens: Gabriel, os Insones, as pessoas dos sonhos. Quem eram, o que querem, o que escondem.
- Os sonhos: como era o campus antes, quem aparece, o que o jogador vê lá.
- A história contada sem palavras: o que está nas paredes, nos objetos, na aparência de cada Insone.
- Coescrever diálogos com o outro roteirista.

**Como diretor de arte:**
- Guia de estilo: paleta, tamanho dos sprites, padrão de nomes. Definido junto com o Davi antes da primeira arte.
- **Fichas de arte:** para cada personagem, inimigo ou cenário, uma descrição com referências do que precisa aparecer e do que aquilo conta da história. É a partir delas que o Davi produz.
- Aprovar se a arte pronta conta o que a história precisa.
- Iluminação e atmosfera dentro do Godot: posicionar luzes, cores e efeitos de cada sala, e a diferença visual entre presente e sonho. É trabalho de ajuste no editor, não de desenho.

**Entrega típica:** ficha de personagem ou cenário em `docs/roteiro/`, ou uma sala com iluminação e atmosfera prontas.

**Trabalha junto com:**
- **O outro roteirista**, em tudo que é história.
- **Davi**, que produz a arte a partir das fichas.
- **Fases**, para cada sala ter a aparência certa.

---

## 4. Roteirista e designer de fases

**Missão:** decidir **o que acontece** e **em que ordem o jogador descobre**, e montar os espaços onde isso acontece.

**Como roteirista:**
- A trama e o mistério: o que aconteceu, quais são as pistas, em que momento cada verdade é revelada.
- Estrutura do jogo: o que acontece em cada dia e em cada área.
- Textos do jogo: diálogos, documentos encontrados, descrições de itens, final.
- **Guardião do cânone:** manter `docs/roteiro/` e `docs/decisoes.md` coerentes. Quando dois textos se contradizem, é quem aponta.

**Como designer de fases:**
- Montar as salas e áreas no Godot com a arte pronta.
- Posicionar pistas, itens, esconderijos, inimigos e pontos de salvamento.
- Ritmo: onde o jogador respira e onde a tensão sobe.
- Som ambiente e efeitos.

**Entrega típica:** uma sala montada e jogável, com as pistas e os textos daquela parte da história.

**Trabalha junto com:**
- **O outro roteirista**, em tudo que é história.
- **Sistemas**, para as salas se ligarem ao mapa dos inimigos.
- **Jogabilidade**, para os textos entrarem na interface.

---

## Como o roteiro funciona com duas pessoas

- O **papel 3** cuida de **quem** existe e **como parece**: personagens, sonhos e a história contada pela imagem.
- O **papel 4** cuida de **o que acontece** e **em que ordem**: trama, mistério, textos. É o guardião do cânone e aponta quando dois textos se contradizem.
- Os diálogos são escritos pelos dois juntos.
- **Decisões grandes de história são do grupo todo**, numa conversa rápida na reunião semanal, e vão para `docs/decisoes.md`.
- Qualquer um pode sugerir ideia de história abrindo uma issue com o rótulo `roteiro`.

## Como pedir arte

Toda a arte é produzida pelo Davi. Para não virar pedido por mensagem que se perde:

1. Quem precisa abre uma **issue** com o rótulo `arte`, dizendo:
   - **O quê:** personagem, objeto, tile, animação, efeito.
   - **Para onde:** em qual sala ou mecânica vai ser usado.
   - **Como:** descrição e pelo menos uma imagem de referência. Para personagens e cenários, o link da ficha do diretor de arte.
   - **Tamanho e animações** necessárias (ex.: "32×48 px; parado, andando, correndo").
   - **Quando precisa.**
2. O Davi estima o prazo e coloca no sprint.
3. Enquanto a arte não fica pronta, quem pediu **usa placeholder** e segue trabalhando.
4. A arte chega por PR; quem pediu confere se ficou como precisava.

## Onde os papéis se encontram

Combinem isso no primeiro sprint:

- **1 → 2:** a IA avisa a jogabilidade por sinais do Godot (`jogador_detectado`, `jogador_perdido`, `insone_atordoado`). Nomes definidos uma vez e não mexe mais.
- **1 ↔ 4:** cada sala montada é um nó do grafo. Formato combinado: cada sala tem um ID e uma lista de portas com peso.
- **3 → 1:** guia de estilo (paleta, tamanho dos sprites, padrão de nome de arquivo) definido junto antes da primeira arte; depois, uma ficha de arte para cada personagem, inimigo ou cenário.
- **2 ↔ 3:** a luz dos fungos é mecânica (2 controla a intensidade) e visual (3 decide como aparece).
- **3 ↔ 4:** os dois roteiristas revisam juntos o que cada sala conta, pela imagem e pelo espaço.

## Sprints (exemplo)

Sprints de duas semanas. Ajustem a cada início de sprint conforme o que foi decidido.

| Sprint | 1. Sistemas e arte | 2. Jogabilidade | 3. Roteiro e direção de arte | 4. Roteiro e fases |
|---|---|---|---|---|
| 1 | Grafo com 3 salas de teste, um Insone com rotina fixa. Placeholders do Gabriel e do primeiro Insone | Movimento, corrida, colisão, câmera | Guia de estilo (com o Davi), ficha do Gabriel, primeira luz 2D | Roteiro da Segunda (Biblioteca): o que o jogador descobre e como. Sala de aula de protótipo |
| 2 | Som por BFS, perseguição por A\*, máquina de estados. Animações do Gabriel | Esconderijo com um microgame, cápsula de clarão | Ficha do primeiro Insone, atmosfera da Biblioteca | Textos e documentos da Biblioteca, montagem da Biblioteca no grafo |
| 3 | Grade horária, cadeia de Markov. Primeiro Insone e tiles da Biblioteca | Inventário, fungos como recurso | Roteiro do primeiro sonho, visual da luz dos fungos | Pistas e esconderijos da Biblioteca, som ambiente |
| 4 | Ajuste da IA na Biblioteca completa. Arte da versão "sonho" da Biblioteca | Dormir, salvar, transição para o sonho | Diferença visual entre presente e sonho, aprovação da arte | Diálogos do sonho (com o papel 3), polimento da Biblioteca |

**Marco do Sprint 4:** a Biblioteca jogável do começo ao fim: um Insone, esconderijo, luz, sono e sonho. Se o prazo apertar, isso já é um jogo entregável; o resto é expansão.

## Rotina

- **Reunião semanal curta:** cada um mostra o que fez **rodando**, não descrito, e o que vai fazer.
- **Início de sprint:** escolher as issues do sprint e distribuir.
- **Fim de sprint:** tudo que foi feito precisa estar mesclado na `main`.
