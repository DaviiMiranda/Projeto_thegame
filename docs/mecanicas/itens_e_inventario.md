# Mecânicas — Itens, Inventário e Gadgets

Como o Gabriel pega, guarda, equipa e usa itens. As regras de cada item estão no documento da mecânica dele (o pote de fungos, por exemplo, em [`iluminacao_e_fungos.md`](iluminacao_e_fungos.md)). Aqui fica o sistema que serve para todos.

---

## 1. Como funciona no jogo

| Tecla | O que faz |
|---|---|
| `E` | Interage com o que está mais perto: pega um item do chão, recarrega o pote numa colônia de fungos |
| `Tab` ou `I` | Abre e fecha o inventário (o jogo pausa enquanto ele está aberto) |
| `1`, `2`, `3` | Usam o gadget equipado naquele espaço. Com o inventário aberto, equipam o item escolhido |

- **Inventário:** uma grade de **3 linhas × 4 colunas**. Todo item pego entra no primeiro espaço livre.
- **Gadgets:** **3 espaços**, um para cada ferramenta equipável prevista em [`docs/personagens/gabriel.md`](../personagens/gabriel.md): pote de fungos, cápsulas de clarão e objetos de arremesso. Equipar não tira o item da grade; o espaço de gadget é um atalho para ele.
- Ao pegar um gadget com um espaço livre, ele já é equipado.
- Na tela, os espaços de gadget ficam no canto de baixo à esquerda, com o número da tecla. A borda acende enquanto o gadget está em uso (pote destampado), e a barrinha embaixo mostra a carga.

### Pote de fungos (a lanterna)

- Está no chão da Biblioteca, perto de onde o Gabriel acorda, brilhando.
- Tecla do espaço dele: tampa e destampa. Destampado, ilumina ~2,5 m em volta do Gabriel com luz ciano.
- A carga cai ao longo de 4,5 minutos destampado; a luz fica mais fraca e menor junto. Com a carga no zero, o pote se tampa sozinho.
- Recarrega em qualquer objeto `fungo` do kit de cenário (`E` perto dele: "Recarregar pote").

---

## 2. Conteúdo de computação: inventário em grade (matriz)

O inventário é uma **matriz**: uma lista de linhas, e cada linha uma lista de colunas. `grade[linha][coluna]` é o item naquela posição, ou `null` se está vazia.

```
grade = [ [pote, null, null, null],     linha 0
          [null, null, null, null],     linha 1
          [null, null, null, null] ]    linha 2
```

- **Guardar:** percorre linha por linha e coluna por coluna (a ordem de leitura de um texto) até o primeiro `null`. No pior caso olha os 12 espaços: O(linhas × colunas).
- **Cursor da tela:** também é uma posição (coluna, linha). Andar com as setas soma 1 ou −1 numa delas; o resto da divisão (`posmod`) faz o cursor dar a volta de uma borda para a outra.
- **Gadgets:** uma lista de 3 posições que aponta para itens da matriz (uma referência, não uma cópia).
- **Estado dos itens** (carga do pote, aceso ou não) e **itens já pegos** no mapa: dicionários, pelo id. Por isso o pote não volta a aparecer no chão ao entrar de novo na sala.

---

## 3. Onde está no projeto

| O quê | Onde |
|---|---|
| Inventário (autoload `Inventario`, vive o jogo inteiro) | `scripts/sistemas/inventario.gd` |
| Tipo de item (`Item`, um recurso) | `scripts/itens/item.gd` |
| Os itens do jogo | `dados/itens/*.tres` |
| Item no chão | `cenas/itens/item_no_chao.tscn` |
| Base de tudo que interage com `E` (`Interagivel`) | `scripts/itens/interagivel.gd` |
| Efeito do pote equipado (a luz) | `cenas/itens/pote_fungos.tscn` |
| Colônia de fungos (recarga) | `scripts/cenario/colonia_fungos.gd`, dentro de `cenas/cenario/objetos/fungo.tscn` |
| HUD (espaços de gadget, aviso "[E]", mensagem) | `cenas/interface/hud.tscn` |
| Tela do inventário | `cenas/interface/tela_inventario.tscn` |
| Ícones e peças da interface (gerados por script) | `assets/modelagem/interface/gerar_interface.py` |

O HUD e a tela do inventário já estão no `modelo_sala.tscn`: toda sala nova herda os dois.

---

## 4. Como criar um item novo

1. **Desenho:** escreva a função do ícone (16 × 16) e, se quiser, a do item no chão em `gerar_interface.py`, adicione no dicionário `ICONES` e rode `python assets/modelagem/interface/gerar_interface.py`. Abra o Godot para gerar os `.import`.
2. **Dados:** no Godot, botão direito em `dados/itens/` → *Novo* → *Recurso...* → `Item`. Preencha `id`, `nome`, `descricao`, `icone` e `sprite_chao`.
3. **Se for gadget:** marque `equipavel` e crie a cena do efeito (como `cenas/itens/pote_fungos.tscn`), com um script que tenha a função `usar()`. Coloque essa cena em `cena_gadget`. Guarde o que precisa sobreviver à troca de sala em `Inventario.estado_de(id)`, não no script.
4. **No mapa:** arraste `cenas/itens/item_no_chao.tscn` para o nó `Objetos` da sala (a origem é o pé) e escolha o item no Inspetor.

---

## 5. Ainda não feito

- Itens que empilham (as cápsulas de clarão têm máximo de 2).
- Descartar ou usar itens que não são gadgets pelo inventário.
- A luz do pote chamar a atenção dos Insones (depende da IA deles).
- Salvar o inventário ao dormir (depende do sistema de save).
