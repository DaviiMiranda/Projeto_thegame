class_name Gabriel
extends CharacterBody2D
## O Gabriel controlado pelo jogador: andar, correr e agachar em 2.5D.
##
## "2.5D" aqui é o jeito do FNAF: Into the Pit: a sala é vista de lado, mas
## o chão tem profundidade. Ele anda para a esquerda/direita (eixo x) e
## também para o fundo/frente da sala (eixo y da tela: para cima = mais
## longe, para baixo = mais perto). Não existe pulo nem gravidade.
##
## A posição do nó (o ponto de origem) fica nos PÉS. Isso importa por dois
## motivos:
##   1. Colisão: só os pés colidem (um retângulo baixo), como se fosse a
##      "pegada" dele no chão. Assim ele pode passar com a cabeça na frente
##      de uma estante sem bater nela.
##   2. Y-sort: a sala ordena quem é desenhado na frente pelo y do nó. Quem
##      tem o pé mais embaixo na tela está mais perto da câmera e aparece na
##      frente. Com o pé como origem, o Gabriel passa atrás e na frente das
##      estantes, da árvore e da mesa sozinho.
##
## Versão mínima para a primeira sala ficar jogável. Estamina, ruído dos
## passos e esconderijos ficam para o papel 2 (docs/mecanicas/).
## As teclas estão em Projeto > Configurações do Projeto > Mapa de Entrada:
## mover_esquerda, mover_direita, mover_cima, mover_baixo, correr e agachar.

## Velocidade andando para os lados, em pixels por segundo.
@export var velocidade_andar: float = 45.0
## Andar para o fundo/frente é mais lento que para os lados. Na tela, o chão
## está "achatado" pela perspectiva (1 px na vertical vale mais distância que
## 1 px na horizontal), então a mesma velocidade pareceria rápida demais.
@export var fator_profundidade: float = 0.65
## Quantas vezes mais rápido ao correr (docs/mecanicas: 180%).
@export var multiplicador_correr: float = 1.8
## Quantas vezes mais devagar agachado (docs/mecanicas: 50%).
@export var multiplicador_agachar: float = 0.5

@export_group("Sprites")
## Uma imagem para cada direção em que ele anda (geradas por
## assets/modelagem/personagens/gerar_gabriel.py). Lado e 3/4 olham para a
## direita; para a esquerda, o sprite é espelhado.
@export var sprite_lado: Texture2D
@export var sprite_frente: Texture2D
@export var sprite_tres_quartos: Texture2D
@export var sprite_costas: Texture2D

@export_group("Caminhada")
## Tiras com os quadros da caminhada, lado a lado, uma para cada vista.
@export var andar_lado: Texture2D
@export var andar_frente: Texture2D
@export var andar_tres_quartos: Texture2D
@export var andar_costas: Texture2D
## Quantos quadros cada tira tem.
@export var quadros_andar: int = 6
## Quantos pixels ele anda a cada quadro da caminhada. O quadro avança pela
## DISTÂNCIA andada, e não pelo tempo: correndo, a animação acelera sozinha;
## agachado, fica mais lenta; batendo numa estante, para. Com ~5,5 px o pé
## acompanha o chão sem "patinar" (um ciclo de dois passos tem ~34 px).
@export var px_por_quadro: float = 5.5

## Verdadeiro enquanto o jogador segura a tecla de agachar.
var agachado := false
## Verdadeiro enquanto ele está correndo (e se mexendo). O papel 2 vai usar
## isso para a estamina e o barulho dos passos.
var correndo := false

## Para qual lado ele está virado: "lado", "frente", "tres_quartos" ou "costas".
var vista := "lado"
## Distância andada desde que começou a andar (escolhe o quadro).
var _distancia := 0.0

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	# Modo "flutuante": o CharacterBody2D não tem chão nem teto, todas as
	# direções são iguais. É o modo certo para jogos vistos de cima/2.5D.
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING


func _physics_process(delta: float) -> void:
	# get_vector junta as 4 teclas num vetor (x, y), cada eixo de -1 a 1.
	# Na diagonal ele daria (1, 1), de comprimento √2 ≈ 1,41: andaria 41%
	# mais rápido. get_vector já corrige isso, "normalizando": se o
	# comprimento passa de 1, divide o vetor pelo comprimento. Resultado:
	# a diagonal tem comprimento 1, como as outras direções.
	var direcao := Input.get_vector("mover_esquerda", "mover_direita", "mover_cima", "mover_baixo")

	agachado = Input.is_action_pressed("agachar")
	correndo = false
	var velocidade := velocidade_andar
	if agachado:
		velocidade *= multiplicador_agachar
	elif Input.is_action_pressed("correr") and direcao != Vector2.ZERO:
		velocidade *= multiplicador_correr
		correndo = true

	# Multiplica cada eixo separado: o y fica mais lento (profundidade).
	velocity = Vector2(direcao.x, direcao.y * fator_profundidade) * velocidade
	# move_and_slide anda e, se bater em algo, desliza ao longo da parede
	# em vez de parar seco (é o que deixa ele "raspar" na estante).
	move_and_slide()

	_virar(direcao)
	# get_real_velocity é quanto ele REALMENTE andou: se esbarrou numa
	# estante, é menos do que o jogador pediu, e as pernas param junto.
	_animar(get_real_velocity().length() * delta)

	# Provisório até existir o sprite agachado: achata o desenho.
	sprite.scale.y = 0.75 if agachado else 1.0


## Escolhe a vista do Gabriel pela direção em que ele anda:
##   para a frente (S) -> de frente     para o fundo (W) -> de costas
##   para os lados     -> de lado       diagonal para a frente -> 3/4
## Na diagonal para o fundo ele fica de lado (não temos 3/4 de costas).
## Parado, ele continua virado para onde estava.
func _virar(direcao: Vector2) -> void:
	if direcao == Vector2.ZERO:
		return
	if direcao.x == 0.0:
		vista = "frente" if direcao.y > 0.0 else "costas"
	elif direcao.y > 0.0:
		vista = "tres_quartos"
	else:
		vista = "lado"
	# Lado e 3/4 olham para a direita; espelha quando anda para a esquerda.
	# Andando só para a frente/fundo, fica espelhado como estava.
	if direcao.x != 0.0:
		sprite.flip_h = direcao.x < 0.0


## Andando: mostra a tira da caminhada da vista atual, no quadro que
## corresponde à distância andada. Parado: volta para o sprite parado.
func _animar(andou: float) -> void:
	var parado := {"lado": sprite_lado, "frente": sprite_frente,
			"tres_quartos": sprite_tres_quartos, "costas": sprite_costas}
	var andando := {"lado": andar_lado, "frente": andar_frente,
			"tres_quartos": andar_tres_quartos, "costas": andar_costas}
	var tira: Texture2D = andando[vista]
	if andou > 0.01 and tira:
		_distancia += andou
		sprite.texture = tira
		sprite.hframes = quadros_andar
		# O resto da divisão (%) faz a conta voltar ao quadro 0 depois do
		# último: o ciclo se repete enquanto ele anda.
		sprite.frame = int(_distancia / px_por_quadro) % quadros_andar
	else:
		_distancia = 0.0
		sprite.hframes = 1
		sprite.frame = 0
		if parado[vista]:
			sprite.texture = parado[vista]
