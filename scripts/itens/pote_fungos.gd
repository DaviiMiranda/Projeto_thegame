extends Node2D
## O pote de fungos equipado: a "lanterna" do Gabriel.
##
## Regras em docs/mecanicas/iluminacao_e_fungos.md:
##   - destampado (aceso), ilumina uns 2 a 3 m em volta dele, com luz ciano;
##   - tampado (apagado), não ilumina nada;
##   - o brilho enfraquece ao longo de 4 a 5 minutos de uso contínuo;
##   - recarrega numa colônia de fungos (scripts/cenario/colonia_fungos.gd).
##
## Esta cena é criada pelo Gabriel enquanto o pote está num espaço de gadget
## (Item.cena_gadget). A carga e o "aceso" ficam no Inventario, e não aqui:
## ao trocar de sala o Gabriel é criado de novo, e o pote continua como
## estava.
##
## A CARGA vai de 1 (cheio) a 0 (apagado). Aceso, ela cai em linha reta:
##   carga = carga - delta / duracao
## (delta = segundos desde o último quadro). Em "duracao" segundos, 1 vira 0.
## A luz acompanha: a força e o alcance diminuem junto com a carga.

## Segundos de uso contínuo até apagar (4,5 minutos).
@export var duracao: float = 270.0
## Força da luz com o pote cheio.
@export var energia_maxima: float = 1.4
## Escala da textura da luz com o pote cheio. A luz.png tem 64 px (raio 32),
## mas ela enfraquece rápido perto da borda: na escala 3,2 o raio da textura
## é ~100 px e a luz que se VÊ no chão chega a ~70 px ≈ 2,5 m (no sprite,
## 1 m ≈ 27 px).
@export var alcance_maximo: float = 3.2

## O item deste gadget (o Gabriel preenche ao criar a cena).
var item: Item

var _estado: Dictionary
var _tempo := 0.0

@onready var luz: PointLight2D = $Luz


func _ready() -> void:
	_estado = Inventario.estado_de(item.id if item else "pote_fungos")
	# Na primeira vez, o pote vem cheio e tampado.
	if not _estado.has("carga"):
		_estado["carga"] = 1.0
	if not _estado.has("aceso"):
		_estado["aceso"] = false
	_atualizar_luz()


## Apertar a tecla do gadget: tampa ou destampa o pote.
func usar() -> void:
	if _estado["carga"] > 0.0:
		_estado["aceso"] = not _estado["aceso"]
	_atualizar_luz()


## Chamado pelo Gabriel quando o pote sai do espaço de gadget: tampa o pote.
func ao_desequipar() -> void:
	_estado["aceso"] = false


func _process(delta: float) -> void:
	_tempo += delta
	if _estado["aceso"]:
		_estado["carga"] = maxf(_estado["carga"] - delta / duracao, 0.0)
		if _estado["carga"] <= 0.0:
			_estado["aceso"] = false
	_atualizar_luz()


func _atualizar_luz() -> void:
	luz.visible = _estado["aceso"]
	var carga: float = _estado["carga"]
	# Mesmo quase sem carga, ainda sobra um pouco de luz (25%) até apagar.
	var forca := 0.25 + 0.75 * carga
	# Um tremor leve e lento (fungo vivo, não lâmpada): duas ondas seno de
	# velocidades diferentes somadas, para não parecer um pisca regular.
	var tremor := 1.0 + 0.05 * sin(_tempo * 2.3) + 0.03 * sin(_tempo * 5.1)
	luz.energy = energia_maxima * forca * tremor
	luz.texture_scale = alcance_maximo * (0.6 + 0.4 * carga)
