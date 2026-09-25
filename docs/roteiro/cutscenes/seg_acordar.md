# seg_acordar

- **Quando:** início do jogo, depois de "Novo jogo" no menu.
- **Onde:** Biblioteca, na cabine de estudo onde Gabriel pegou no sono.
- **Personagens:** Gabriel.
- **O que acontece:** Gabriel acorda na Biblioteca. Pelo GDD (item 3, "O começo"): luz do sol entrando por um teto que não existe mais, uma árvore no meio da sala, as estantes caídas e vazias.
- **Falas:** _a definir._
- **O que o jogador descobre:** _a definir._
- **Status:** aprovada

## Nota da cena (arte)

A cena `cenas/cutscenes/seg_acordar.tscn` já existe, com uma animação **provisória** de ~10 s, feita só para testar a arte e o fluxo do menu. Ela não decide nada da história:

- a tela sai do preto e os raios de sol aparecem aos poucos;
- as camadas (fundo, meio, frente) andam 1 px de cada vez, em velocidades diferentes (paralaxe);
- o Gabriel usa os 8 quadros de `seg_acordar_gabriel.png`: dorme, respira, se mexe, se ergue, senta, olha para cima, para a esquerda e para a direita.

Quando as falas e o "o que o jogador descobre" estiverem escritos, a animação `principal` é refeita em cima deles (tempo das falas, ordem dos olhares).
A `proxima_cena` está vazia porque a primeira sala ainda não existe: a cutscene termina e fica parada no último quadro. O "Novo jogo" do menu já abre esta cena.
