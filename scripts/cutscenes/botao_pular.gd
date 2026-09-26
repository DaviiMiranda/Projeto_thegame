extends CanvasLayer
## Botão "Pular" que aparece no canto da tela durante as cutscenes.
##
## Fica num CanvasLayer para ser desenhado por cima da cutscene e não andar
## junto com a câmera. Ele não sabe nada da cutscene: só avisa, pelo sinal
## "pular", que o jogador clicou. Quem decide o que fazer é a cutscene
## (scripts/cutscenes/cutscene.gd), que coloca este botão sozinha.

## O jogador clicou no botão.
signal pular

## Segundos até o botão aparecer (a cutscene começa limpa, sem nada por cima).
@export var espera: float = 1.0
## Segundos que o botão leva para aparecer (sai do transparente).
@export var duracao_aparecer: float = 0.6

@onready var botao: Button = $Botao


func _ready() -> void:
	botao.pressed.connect(pular.emit)
	# Começa invisível e aparece devagar. "modulate:a" é a transparência:
	# 0 = invisível, 1 = normal.
	botao.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_interval(espera)
	tween.tween_property(botao, "modulate:a", 1.0, duracao_aparecer)
