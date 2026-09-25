@tool
class_name ObjetoCenario
extends StaticBody2D
## Um objeto do cenário que o Gabriel contorna: estante, mesa, árvore...
##
## Cada objeto do kit (cenas/cenario/objetos/) é uma cena com:
##   - Sprite2D: o desenho, com o offset ajustado para a ORIGEM do nó ficar
##     no "pé" do objeto (o ponto que encosta no chão, na frente);
##   - Pegada (CollisionShape2D, opcional): um retângulo baixo no chão, onde
##     o Gabriel esbarra. Só o pé colide, então ele pode passar com a cabeça
##     na frente de uma estante (vista 2.5D).
##
## Como a origem é o pé, basta colocar o objeto dentro do nó "Objetos" da
## sala (que tem y_sort_enabled): quem tem o pé mais embaixo na tela aparece
## na frente. É o mesmo truque do Gabriel.
##
## @tool: este script também roda DENTRO do editor, para o "espelhado"
## aparecer na hora em que você marca a caixa no Inspetor.

## Vira o objeto de lado (desenho e pegada). Use para variar a sala sem
## precisar de um desenho novo.
@export var espelhado: bool = false:
	set(valor):
		espelhado = valor
		_aplicar_espelho()

# O offset "de fábrica" do Sprite2D (sem espelho), guardado na primeira vez.
var _offset_original: Vector2
var _pegada_x_original: float
var _pronto := false


func _ready() -> void:
	_aplicar_espelho()


func _aplicar_espelho() -> void:
	var sprite := get_node_or_null("Sprite2D") as Sprite2D
	if sprite == null or sprite.texture == null:
		return
	var pegada := get_node_or_null("Pegada") as Node2D
	if not _pronto:
		_offset_original = sprite.offset
		_pegada_x_original = pegada.position.x if pegada else 0.0
		_pronto = true
	sprite.flip_h = espelhado
	# O Sprite2D espelha o desenho dentro do mesmo retângulo, então o pé
	# (que estava a -offset.x da borda esquerda) vai para largura + offset.x.
	# Para o pé continuar na origem, o retângulo muda de lugar:
	#   offset espelhado = -(largura) - offset original
	var largura := sprite.texture.get_width()
	if espelhado:
		sprite.offset.x = -largura - _offset_original.x
	else:
		sprite.offset.x = _offset_original.x
	if pegada:
		pegada.position.x = -_pegada_x_original if espelhado else _pegada_x_original
