extends CanvasLayer
## A tela de inventário: abre com Tab (ou I) e pausa o jogo.
##
##   - setas / WASD: escolhem um espaço da grade (o cursor);
##   - 1, 2, 3: equipam o item escolhido naquele espaço de gadget (apertar
##     de novo o número em que ele já está desequipa);
##   - mouse: clicar num espaço da grade escolhe; clicar num espaço de
##     gadget faz o mesmo que apertar o número dele;
##   - Tab, I ou Esc: fecham.
##
## A grade aqui é o desenho da MATRIZ do Inventario: o espaço da linha l e
## coluna c mostra Inventario.grade[l][c]. O cursor também é uma posição
## (linha, coluna), e andar com as setas é somar 1 ou -1 numa delas.
##
## process_mode = Sempre: com o jogo pausado (get_tree().paused), só os nós
## marcados assim continuam recebendo teclas e rodando.

const CENA_ESPACO := preload("res://cenas/interface/espaco_item.tscn")

var aberto := false
var _cursor := Vector2i(0, 0)   # x = coluna, y = linha
var _espacos_grade: Array[EspacoItem] = []
var _espacos_gadget: Array[EspacoItem] = []

@onready var grade: GridContainer = $Janela/Grade
@onready var caixa_gadgets: HBoxContainer = $Janela/Gadgets
@onready var nome: Label = $Janela/Nome
@onready var descricao: Label = $Janela/Descricao
@onready var situacao: Label = $Janela/Situacao


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	grade.columns = Inventario.COLUNAS
	for linha in Inventario.LINHAS:
		for coluna in Inventario.COLUNAS:
			var espaco := CENA_ESPACO.instantiate() as EspacoItem
			grade.add_child(espaco)
			espaco.clicado.connect(_escolher.bind(Vector2i(coluna, linha)))
			_espacos_grade.append(espaco)
	for i in Inventario.ESPACOS_GADGET:
		var espaco := CENA_ESPACO.instantiate() as EspacoItem
		caixa_gadgets.add_child(espaco)
		espaco.clicado.connect(_equipar_no_espaco.bind(i))
		_espacos_gadget.append(espaco)
	Inventario.mudou.connect(_atualizar)
	visible = false


func _unhandled_input(evento: InputEvent) -> void:
	if evento.is_action_pressed("inventario") or (aberto and evento.is_action_pressed("ui_cancel")):
		_abrir(not aberto)
		get_viewport().set_input_as_handled()
		return
	if not aberto:
		return
	var passo := Vector2i.ZERO
	if evento.is_action_pressed("mover_esquerda") or evento.is_action_pressed("ui_left"):
		passo = Vector2i.LEFT
	elif evento.is_action_pressed("mover_direita") or evento.is_action_pressed("ui_right"):
		passo = Vector2i.RIGHT
	elif evento.is_action_pressed("mover_cima") or evento.is_action_pressed("ui_up"):
		passo = Vector2i.UP
	elif evento.is_action_pressed("mover_baixo") or evento.is_action_pressed("ui_down"):
		passo = Vector2i.DOWN
	if passo != Vector2i.ZERO:
		# posmod é o resto da divisão que nunca dá negativo: passar da última
		# coluna volta para a primeira, e da primeira para a última.
		_escolher(Vector2i(posmod(_cursor.x + passo.x, Inventario.COLUNAS),
				posmod(_cursor.y + passo.y, Inventario.LINHAS)))
	for i in Inventario.ESPACOS_GADGET:
		if evento.is_action_pressed("gadget_%d" % (i + 1)):
			_equipar_no_espaco(i)
	get_viewport().set_input_as_handled()


func _abrir(abrir: bool) -> void:
	aberto = abrir
	visible = abrir
	# Pausa o jogo inteiro (Gabriel, Insones, animações) enquanto está aberto.
	get_tree().paused = abrir
	_atualizar()


func _escolher(posicao: Vector2i) -> void:
	_cursor = posicao
	_atualizar()


## Equipa o item do cursor no espaço de gadget (ou desequipa, se ele já
## estava ali).
func _equipar_no_espaco(espaco: int) -> void:
	var item := Inventario.item_em(_cursor.y, _cursor.x)
	if item and item.equipavel:
		if Inventario.espaco_do_gadget(item) == espaco:
			Inventario.desequipar(espaco)
		else:
			Inventario.equipar(item, espaco)
	elif item == null and Inventario.gadgets[espaco] != null:
		# Cursor num espaço vazio: clicar no gadget só tira o que está lá.
		Inventario.desequipar(espaco)


func _atualizar() -> void:
	if not is_node_ready():
		return
	var i := 0
	for linha in Inventario.LINHAS:
		for coluna in Inventario.COLUNAS:
			var item := Inventario.item_em(linha, coluna)
			var selecionado := Vector2i(coluna, linha) == _cursor
			# O número no canto do item diz em qual gadget ele está equipado.
			var equipado := Inventario.espaco_do_gadget(item) if item else -1
			var texto := str(equipado + 1) if equipado != -1 else ""
			_espacos_grade[i].mostrar(item, selecionado, texto)
			i += 1
	for g in Inventario.ESPACOS_GADGET:
		_espacos_gadget[g].mostrar(Inventario.gadgets[g], false, str(g + 1))
	var escolhido := Inventario.item_em(_cursor.y, _cursor.x)
	nome.text = escolhido.nome if escolhido else ""
	descricao.text = escolhido.descricao if escolhido else ""
	situacao.text = ""
	if escolhido and escolhido.equipavel:
		var espaco := Inventario.espaco_do_gadget(escolhido)
		if espaco != -1:
			situacao.text = "Equipado na tecla %d" % (espaco + 1)
		else:
			situacao.text = "Aperte 1, 2 ou 3 para equipar"
