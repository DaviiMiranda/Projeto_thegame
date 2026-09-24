class_name CamadaParalaxe
extends Node2D
## Uma camada de profundidade que se desloca conforme o mouse (paralaxe 2.5D).
##
## Coloque os objetos de uma mesma "distância" como filhos deste nó.
## Camadas perto da câmera devem ter deslocamento_maximo maior que as do fundo:
## é essa diferença de velocidade que dá a sensação de profundidade.

## Quantos pixels a camada anda, no máximo, quando o mouse vai até a borda da tela.
@export var deslocamento_maximo: float = 4.0
## Quanto maior, mais rápido a camada alcança a posição do mouse.
@export var suavidade: float = 6.0

var _posicao_inicial: Vector2
var _posicao_atual: Vector2


func _ready() -> void:
	_posicao_inicial = position
	_posicao_atual = position


func _process(delta: float) -> void:
	var tamanho_tela := get_viewport_rect().size
	var mouse := get_viewport().get_mouse_position()

	# Onde o mouse está em relação ao centro da tela, de -1 a 1 em cada eixo.
	var direcao := (mouse / tamanho_tela - Vector2(0.5, 0.5)) * 2.0
	direcao = direcao.clamp(Vector2(-1, -1), Vector2(1, 1))

	# A camada anda para o lado contrário do mouse, como se a câmera virasse.
	var alvo := _posicao_inicial - direcao * deslocamento_maximo

	# Interpolação suave: a cada quadro, anda uma fração do caminho até o alvo.
	_posicao_atual = _posicao_atual.lerp(alvo, 1.0 - exp(-suavidade * delta))

	# Arredonda para pixel inteiro, senão a pixel art fica tremida.
	position = _posicao_atual.round()
