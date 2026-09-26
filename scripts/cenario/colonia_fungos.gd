@tool
class_name ColoniaFungos
extends Interagivel
## Uma colônia de fungos frescos, onde o Gabriel recarrega o pote.
##
## docs/mecanicas/iluminacao_e_fungos.md: o brilho do pote enfraquece com o
## uso e, para voltar ao máximo, o Gabriel interage com colônias frescas.
## Todo objeto "fungo" do kit de cenário (cenas/cenario/objetos/fungo.tscn)
## já vem com uma colônia, então qualquer sala com fungos serve.

## O id do item que esta colônia recarrega.
const ID_POTE := "pote_fungos"


func _ready() -> void:
	texto_acao = "Recarregar pote"
	super()


## Só dá para recarregar se ele tem o pote e o pote não está cheio.
func pode_interagir() -> bool:
	if not Inventario.tem(ID_POTE):
		return false
	return Inventario.estado_de(ID_POTE).get("carga", 1.0) < 1.0


func interagir() -> void:
	Inventario.estado_de(ID_POTE)["carga"] = 1.0
