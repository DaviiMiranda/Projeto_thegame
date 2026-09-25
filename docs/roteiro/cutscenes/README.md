# Cutscenes

Uma ficha por cutscene nesta pasta. O roteiro (papel 4) escreve aqui, sem precisar abrir o Godot.

## Nomes

`dia_o_que`, em `snake_case`, sem acento. O dia vem primeiro, como em `docs/fases.md`: `seg_`, `ter_`, `qua_`, `qui_`, `sex_`.
O mesmo nome é usado em todas as pastas da cutscene (ficha, cena, falas, sprites).

## Onde fica cada parte

| Parte | Pasta | Quem cuida |
|---|---|---|
| Ficha (o que acontece) | `docs/roteiro/cutscenes/<nome>.md` | roteiro |
| Falas | `dialogos/<nome>.json` | roteiro |
| Cena do Godot | `cenas/cutscenes/<nome>.tscn` | arte e jogabilidade |
| Imagens | `assets/sprites/cutscenes/<nome>/` | arte |
| Modelos do Blender | `assets/modelagem/cutscenes/<nome>/` | arte |

Toda cena de cutscene usa o script `scripts/cutscenes/cutscene.gd`: ela toca a animação `principal` do seu `AnimationPlayer`, pode ser pulada com Esc e, ao terminar, avisa o jogo pelo sinal `cutscene_terminou` e troca para a `proxima_cena`.

## Ficha

```
# nome_da_cutscene

- Quando:
- Onde:
- Personagens:
- O que acontece:
- Falas:
- O que o jogador descobre:
- Status: ideia / aprovada / feita
```

## Lista

| Cutscene | Status |
|---|---|
| [`seg_acordar`](seg_acordar.md) | aprovada |
