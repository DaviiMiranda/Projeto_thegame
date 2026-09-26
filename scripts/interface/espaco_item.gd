class_name EspacoItem
extends Control
## Um espaço (quadradinho) que mostra um item: usado na grade do inventário
## e nos espaços de gadget do HUD. Ele só MOSTRA: quem decide o que vai
## dentro é a tela que o usa, chamando mostrar().

## Clicaram neste espaço com o mouse.
signal clicado

const MOLDURA := preload("res://assets/sprites/interface/espaco.png")
const MOLDURA_ACESA := preload("res://assets/sprites/interface/espaco_selecionado.png")

@onready var moldura: TextureRect = $Moldura
@onready var icone: TextureRect = $Icone
@onready var numero: Label = $Numero
@onready var carga: ColorRect = $Carga


func _ready() -> void:
	gui_input.connect(_ao_receber_input)


## item: o que mostrar (null = vazio); aceso: borda de selecionado;
## texto_numero: o número no canto ("1", "2"... ou "" para nada);
## valor_carga: barrinha embaixo, de 0 a 1 (negativo = sem barra).
func mostrar(item: Item, aceso: bool = false, texto_numero: String = "", valor_carga: float = -1.0) -> void:
	moldura.texture = MOLDURA_ACESA if aceso else MOLDURA
	icone.texture = item.icone if item else null
	numero.text = texto_numero
	carga.visible = valor_carga >= 0.0
	# A barra tem 16 px no máximo; arredonda para o pixel (pixel art).
	carga.size.x = roundf(16.0 * clampf(valor_carga, 0.0, 1.0))


func _ao_receber_input(evento: InputEvent) -> void:
	if evento is InputEventMouseButton and evento.pressed and evento.button_index == MOUSE_BUTTON_LEFT:
		clicado.emit()
