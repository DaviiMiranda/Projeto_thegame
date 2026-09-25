extends Node2D
## Menu principal: um monitor antigo numa sala escura, com as opções na tela.
##
## A única luz da cena é o brilho azulado da tela (nó Mesa/Luz), que oscila
## como uma tela com mau contato. As camadas Fundo, Mesa e Frente usam
## CamadaParalaxe para se deslocar com o mouse.

## Avisam o resto do jogo sobre a escolha do jogador (comunicação por sinais).
signal novo_jogo_pedido
signal continuar_pedido
signal opcoes_pedidas

## Cena que começa ao apertar "Novo jogo". Fica vazia até existir a primeira sala.
@export var cena_novo_jogo: PackedScene

## Brilho médio da tela.
@export var energia_luz: float = 0.9
## Quanto o brilho sobe e desce ao oscilar.
@export var oscilacao_luz: float = 0.15

@onready var luz: PointLight2D = $Mesa/Luz
@onready var botao_novo_jogo: Button = $Mesa/Menu/BotaoNovoJogo
@onready var botao_continuar: Button = $Mesa/Menu/BotaoContinuar
@onready var botao_opcoes: Button = $Mesa/Menu/BotaoOpcoes
@onready var botao_sair: Button = $Mesa/Menu/BotaoSair
## Trilha do menu. É filha desta cena, então para sozinha quando o jogo troca de cena.
@onready var musica: AudioStreamPlayer = $Musica

# Ruído suave para a luz oscilar de um jeito irregular, não em ritmo fixo.
var _ruido := FastNoiseLite.new()
var _tempo := 0.0


func _ready() -> void:
	botao_novo_jogo.pressed.connect(_ao_apertar_novo_jogo)
	botao_continuar.pressed.connect(_ao_apertar_continuar)
	botao_opcoes.pressed.connect(_ao_apertar_opcoes)
	botao_sair.pressed.connect(_ao_apertar_sair)

	# Continuar fica desligado até o sistema de salvar existir.
	botao_continuar.disabled = true

	# Com um botão focado, dá para navegar no menu pelo teclado ou controle.
	botao_novo_jogo.grab_focus()

	_ruido.frequency = 0.05

	# A trilha recomeça do início quando acaba, sem pausa.
	if musica.stream:
		musica.stream.set("loop", true)


func _process(delta: float) -> void:
	_tempo += delta
	luz.energy = energia_luz + _ruido.get_noise_1d(_tempo * 60.0) * oscilacao_luz


func _ao_apertar_novo_jogo() -> void:
	novo_jogo_pedido.emit()
	if cena_novo_jogo:
		get_tree().change_scene_to_packed(cena_novo_jogo)
	else:
		print("Menu: ainda não há cena de novo jogo configurada.")


func _ao_apertar_continuar() -> void:
	continuar_pedido.emit()


func _ao_apertar_opcoes() -> void:
	# A tela de opções ainda não existe; por enquanto só avisa.
	opcoes_pedidas.emit()
	print("Menu: tela de opções ainda não existe.")


func _ao_apertar_sair() -> void:
	get_tree().quit()
