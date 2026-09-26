@tool
class_name ItemNoChao
extends Interagivel
## Um item caído no cenário, que o Gabriel pega apertando E.
##
## Para colocar um item numa sala: arraste cenas/itens/item_no_chao.tscn
## para dentro do nó "Objetos" (y-sort) e escolha o item no Inspetor (um
## arquivo de dados/itens/). A origem do nó é o ponto em que o item encosta
## no chão, como nos objetos do kit de cenário.

## O item que está no chão.
@export var item: Item:
	set(valor):
		item = valor
		_mostrar_desenho()

@onready var sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	_mostrar_desenho()
	if Engine.is_editor_hint():
		return
	super()
	if item:
		texto_acao = "Pegar " + item.nome.to_lower()
	# Já foi pego numa visita anterior a esta sala? Então some.
	if Inventario.pegos.has(_id_unico()):
		queue_free()


func interagir() -> void:
	if Inventario.adicionar(item):
		Inventario.pegos[_id_unico()] = true
		queue_free()


## Um nome que identifica ESTE item NESTE lugar do mapa: o arquivo da sala
## mais o caminho do nó dentro dela (ex.: "res://cenas/salas/biblioteca.tscn:
## Objetos/PoteFungos"). Dois potes em salas diferentes têm nomes diferentes.
func _id_unico() -> String:
	var sala := owner if owner else get_tree().current_scene
	return "%s:%s" % [sala.scene_file_path, sala.get_path_to(self)]


func _mostrar_desenho() -> void:
	var s := get_node_or_null("Sprite2D") as Sprite2D
	if s == null:
		return
	var textura: Texture2D = null
	if item:
		textura = item.sprite_chao if item.sprite_chao else item.icone
	s.texture = textura
	if textura:
		# Pé no meio da borda de baixo do desenho (a origem do nó).
		s.offset = Vector2(-floorf(textura.get_width() / 2.0), -textura.get_height())
