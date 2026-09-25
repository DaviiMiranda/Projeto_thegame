class_name Sala
extends Node2D
## Base de toda sala do jogo.
##
## Cada sala é um nó do grafo do campus (docs/equipe.md, "1 ↔ 4"): o id
## identifica a sala para a IA dos Insones e para as portas.
## Ao abrir, a tela sai do preto, para a troca de cena não ser um corte seco.

## Nome da sala no grafo, em snake_case (ex.: "biblioteca").
@export var id: String = ""
## Quanto tempo a tela leva para sair do preto, em segundos.
@export var duracao_entrada: float = 1.0

## Retângulo preto por cima de tudo, dentro de um CanvasLayer (opcional).
@onready var escuro: ColorRect = get_node_or_null("Transicao/Escuro")


func _ready() -> void:
	if escuro:
		escuro.color.a = 1.0
		var tween := create_tween()
		tween.tween_property(escuro, "color:a", 0.0, duracao_entrada)
