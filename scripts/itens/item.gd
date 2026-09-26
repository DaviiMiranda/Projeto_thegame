class_name Item
extends Resource
## Um TIPO de item: o que ele é, como aparece e o que faz quando equipado.
##
## Cada item do jogo é um arquivo .tres em dados/itens/ (ex.:
## dados/itens/pote_fungos.tres). Para criar um item novo no Godot:
## Sistema de Arquivos > botão direito em dados/itens/ > Novo > Recurso... >
## Item, e preencha os campos no Inspetor.
##
## O item não guarda nada que muda durante o jogo (quanta carga o pote tem,
## se está aceso...). Isso fica no Inventario (scripts/sistemas/inventario.gd),
## no dicionário "estado". Assim o mesmo arquivo .tres serve para o jogo
## inteiro e não é alterado sem querer.

## Nome curto e único, em snake_case (ex.: "pote_fungos").
@export var id: String = ""
## Nome que aparece para o jogador (ex.: "Pote de fungos").
@export var nome: String = ""
## Texto que aparece no inventário quando o item está selecionado.
@export_multiline var descricao: String = ""
## Ícone de 16 x 16 px (inventário e espaços de gadget).
@export var icone: Texture2D
## Desenho do item caído no chão, na escala do cenário. Vazio = usa o ícone.
@export var sprite_chao: Texture2D

@export_group("Gadget")
## Se o item pode ir para um espaço de gadget (teclas 1, 2 e 3) e ser usado.
@export var equipavel: bool = false
## Cena criada junto do Gabriel enquanto o item está equipado: é ela que faz
## o efeito (a luz do pote, por exemplo). Precisa ter a função usar().
@export var cena_gadget: PackedScene
