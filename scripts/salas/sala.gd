@tool
class_name Sala
extends Node2D
## Base de toda sala do jogo.
##
## Cada sala é um nó do grafo do campus (docs/equipe.md, "1 ↔ 4"): o id
## identifica a sala para a IA dos Insones e para as portas.
## Ao abrir, a tela sai do preto, para a troca de cena não ser um corte seco.
##
## Para montar uma sala nova, veja docs/guia_montar_salas.md: você cria uma
## cena herdada de cenas/salas/modelo_sala.tscn e só ajusta os números
## abaixo. A sala cuida sozinha de:
##   - criar as paredes invisíveis que prendem o Gabriel na faixa de chão;
##   - limitar a câmera ao tamanho da sala.
## No editor, o nó "Guias" (scripts/salas/guias_sala.gd) desenha o
## retângulo da sala (amarelo) e a faixa de chão onde o Gabriel anda (azul).
## É o "@tool" que faz os números daqui atualizarem as guias na hora.

## Nome da sala no grafo, em snake_case (ex.: "biblioteca").
@export var id: String = ""
## Quanto tempo a tela leva para sair do preto, em segundos.
@export var duracao_entrada: float = 1.0

@export_group("Tamanho")
## Largura da sala em pixels. Uma tela tem 320; use múltiplos de 80 (o
## tamanho das peças de parede do kit).
@export var largura: int = 960:
	set(valor):
		largura = valor
		_redesenhar_guias()
## Linha mais ao fundo onde os pés do Gabriel podem ir (y, em pixels).
## As peças de parede do kit acabam em y = 112.
@export var chao_fundo: int = 120:
	set(valor):
		chao_fundo = valor
		_redesenhar_guias()
## Linha mais à frente onde os pés do Gabriel podem ir.
@export var chao_frente: int = 176:
	set(valor):
		chao_frente = valor
		_redesenhar_guias()
## Distância das paredes da esquerda e da direita até onde ele pode andar.
@export var margem_lados: int = 20:
	set(valor):
		margem_lados = valor
		_redesenhar_guias()
## Desligue se a sala tiver um nó "Limites" feito à mão.
@export var criar_limites: bool = true

const ALTURA := 180

## Retângulo preto por cima de tudo, dentro de um CanvasLayer (opcional).
@onready var escuro: ColorRect = get_node_or_null("Transicao/Escuro")


func _ready() -> void:
	if Engine.is_editor_hint():
		return
	if criar_limites:
		_criar_limites()
	_ajustar_camera()
	if escuro:
		escuro.color.a = 1.0
		var tween := create_tween()
		tween.tween_property(escuro, "color:a", 0.0, duracao_entrada)


## Quatro retângulos de colisão em volta da faixa de chão. Cada um é grosso
## (40 px) para o Gabriel nunca "atravessar" mesmo correndo.
func _criar_limites() -> void:
	var corpo := StaticBody2D.new()
	corpo.name = "LimitesAutomaticos"
	var grossura := 40.0
	var larg := float(largura)
	# (centro, tamanho) de cada parede invisível.
	var paredes := [
		[Vector2(larg / 2, chao_fundo - grossura / 2), Vector2(larg + 2 * grossura, grossura)],
		[Vector2(larg / 2, chao_frente + grossura / 2), Vector2(larg + 2 * grossura, grossura)],
		[Vector2(margem_lados - grossura / 2, ALTURA / 2.0), Vector2(grossura, ALTURA * 2)],
		[Vector2(larg - margem_lados + grossura / 2, ALTURA / 2.0), Vector2(grossura, ALTURA * 2)],
	]
	for p in paredes:
		var forma := CollisionShape2D.new()
		var ret := RectangleShape2D.new()
		ret.size = p[1]
		forma.shape = ret
		forma.position = p[0]
		corpo.add_child(forma)
	add_child(corpo)


## A câmera do Gabriel não mostra nada fora da sala.
func _ajustar_camera() -> void:
	var camera := get_node_or_null("Objetos/Gabriel/Camera2D") as Camera2D
	if camera:
		camera.limit_left = 0
		camera.limit_top = 0
		camera.limit_right = largura
		camera.limit_bottom = ALTURA


func _redesenhar_guias() -> void:
	var guias := get_node_or_null("Guias") as CanvasItem
	if guias:
		guias.queue_redraw()
