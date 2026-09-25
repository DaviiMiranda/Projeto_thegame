class_name Gabriel
extends CharacterBody2D
## O Gabriel controlado pelo jogador: andar, correr e agachar.
##
## Versão mínima para a primeira sala ficar jogável. Estamina, ruído dos
## passos e esconderijos ficam para o papel 2 (docs/mecanicas/).
## As teclas estão em Projeto > Configurações do Projeto > Mapa de Entrada:
## mover_esquerda, mover_direita, correr e agachar.

## Velocidade andando, em pixels por segundo.
@export var velocidade_andar: float = 45.0
## Quantas vezes mais rápido ao correr (docs/mecanicas: 180%).
@export var multiplicador_correr: float = 1.8
## Quantas vezes mais devagar agachado (docs/mecanicas: 50%).
@export var multiplicador_agachar: float = 0.5
## Aceleração da gravidade, em pixels por segundo ao quadrado.
@export var gravidade: float = 600.0

## Verdadeiro enquanto o jogador segura a tecla de agachar.
var agachado := false

@onready var sprite: Sprite2D = $Sprite2D


func _physics_process(delta: float) -> void:
	# Gravidade: só puxa para baixo quando ele não está no chão.
	if not is_on_floor():
		velocity.y += gravidade * delta

	# -1 = esquerda, 0 = parado, 1 = direita.
	var direcao := Input.get_axis("mover_esquerda", "mover_direita")

	agachado = Input.is_action_pressed("agachar")
	var velocidade := velocidade_andar
	if agachado:
		velocidade *= multiplicador_agachar
	elif Input.is_action_pressed("correr"):
		velocidade *= multiplicador_correr

	velocity.x = direcao * velocidade
	move_and_slide()

	# O sprite olha para a direita; espelha quando anda para a esquerda.
	if direcao != 0.0:
		sprite.flip_h = direcao < 0.0

	# Provisório até existir o sprite agachado: achata o desenho.
	sprite.scale.y = 0.75 if agachado else 1.0
