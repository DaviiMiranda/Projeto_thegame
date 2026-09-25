class_name Cutscene
extends Node2D
## Base de toda cutscene do jogo.
##
## A cena da cutscene precisa ter um AnimationPlayer filho com uma animação
## chamada "principal". Tudo o que acontece (câmera, personagens, luz, falas)
## fica nas trilhas dessa animação.

## Avisa o resto do jogo que a cutscene acabou (terminou ou foi pulada).
signal cutscene_terminou(id: String)

## Nome da cutscene, igual ao da ficha em docs/roteiro/cutscenes/.
@export var id: String = ""
## Cena que começa quando a cutscene acaba. Vazia = fica parada no fim.
@export var proxima_cena: PackedScene
## Se o jogador pode pular apertando Esc.
@export var pode_pular: bool = true

@onready var animacao: AnimationPlayer = $AnimationPlayer

# Garante que o fim só acontece uma vez (pular e terminar ao mesmo tempo).
var _terminou := false


func _ready() -> void:
	animacao.animation_finished.connect(_ao_terminar_animacao)
	animacao.play("principal")


func _unhandled_input(event: InputEvent) -> void:
	if pode_pular and event.is_action_pressed("ui_cancel"):
		_terminar()


func _ao_terminar_animacao(_nome: StringName) -> void:
	_terminar()


func _terminar() -> void:
	if _terminou:
		return
	_terminou = true
	cutscene_terminou.emit(id)
	if proxima_cena:
		get_tree().change_scene_to_packed(proxima_cena)
