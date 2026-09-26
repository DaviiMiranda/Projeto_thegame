extends CanvasLayer
## O HUD: o que fica na tela durante o jogo, por cima da sala.
##   - os espaços de gadget no canto (teclas 1, 2 e 3), com a carga do pote;
##   - o aviso "[E] Pegar ..." em cima do interagível mais perto;
##   - a mensagem "Você pegou ..." quando um item entra no inventário.
##
## Fica num CanvasLayer: é desenhado na tela, não no mundo. Assim não anda
## com a câmera e não é escurecido pela escuridão da sala (CanvasModulate).
## Ele só LÊ o Inventario; quem muda o inventário é o jogo.

const CENA_ESPACO := preload("res://cenas/interface/espaco_item.tscn")

## Quanto tempo a mensagem de item pego fica na tela, em segundos.
@export var duracao_mensagem: float = 3.5

var _espacos: Array[EspacoItem] = []
var _tween_mensagem: Tween

@onready var caixa_gadgets: HBoxContainer = $Gadgets
@onready var aviso: Label = $Aviso
@onready var mensagem: Label = $Mensagem


func _ready() -> void:
	for i in Inventario.ESPACOS_GADGET:
		var espaco := CENA_ESPACO.instantiate() as EspacoItem
		espaco.mouse_filter = Control.MOUSE_FILTER_IGNORE
		caixa_gadgets.add_child(espaco)
		_espacos.append(espaco)
	Inventario.item_pego.connect(_ao_pegar_item)
	mensagem.modulate.a = 0.0
	aviso.hide()


func _process(_delta: float) -> void:
	_atualizar_gadgets()
	_atualizar_aviso()


## Redesenha os 3 espaços. É a cada quadro porque a carga do pote muda o
## tempo todo (são só 3 quadradinhos, custa quase nada).
func _atualizar_gadgets() -> void:
	for i in _espacos.size():
		var item: Item = Inventario.gadgets[i]
		var carga := -1.0
		var aceso := false
		if item:
			var estado: Dictionary = Inventario.estado.get(item.id, {})
			carga = estado.get("carga", -1.0)
			aceso = estado.get("aceso", false)
		# Borda acesa = gadget em uso (ex.: pote destampado).
		_espacos[i].mostrar(item, aceso, str(i + 1), carga)


## Põe o aviso em cima do interagível mais perto do Gabriel.
func _atualizar_aviso() -> void:
	var jogador := get_tree().get_first_node_in_group("jogador") as Node2D
	var alvo: Interagivel = null
	if jogador:
		alvo = Interagivel.mais_perto(get_tree(), jogador.global_position)
	aviso.visible = alvo != null
	if alvo == null:
		return
	aviso.text = "[E] " + alvo.texto_acao
	aviso.reset_size()
	# get_global_transform_with_canvas: onde o nó do MUNDO aparece na TELA
	# (já descontando a posição da câmera). É isso que liga o mundo ao HUD.
	var na_tela := alvo.get_global_transform_with_canvas().origin
	var pos := na_tela + Vector2(-aviso.size.x / 2.0, -alvo.altura_aviso - aviso.size.y)
	# Não deixa o aviso sair da tela (320 x 180).
	pos.x = clampf(pos.x, 2.0, 318.0 - aviso.size.x)
	pos.y = clampf(pos.y, 2.0, 178.0 - aviso.size.y)
	aviso.position = pos.round()


func _ao_pegar_item(item: Item) -> void:
	var texto := "Você pegou: " + item.nome
	var espaco := Inventario.espaco_do_gadget(item)
	if espaco != -1:
		texto += "   [%d] usar" % (espaco + 1)
	texto += "   [Tab] inventário"
	mensagem.text = texto
	# Aparece, espera e some devagar.
	if _tween_mensagem:
		_tween_mensagem.kill()
	mensagem.modulate.a = 1.0
	_tween_mensagem = create_tween()
	_tween_mensagem.tween_interval(duracao_mensagem)
	_tween_mensagem.tween_property(mensagem, "modulate:a", 0.0, 0.8)
