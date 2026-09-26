@tool
class_name Interagivel
extends Area2D
## Algo no cenário com que o Gabriel interage apertando E: um item no chão,
## uma colônia de fungos, e no futuro portas, armários, documentos...
##
## É uma Area2D: uma região que não bloqueia ninguém, só percebe quem entra
## e quem sai (sinais body_entered e body_exited). Enquanto o Gabriel está
## dentro, o interagível entra no grupo "interagiveis_perto". Ao apertar E,
## o Gabriel pega o MAIS PERTO desse grupo e chama interagir(). O aviso
## "[E] Pegar" na tela é desenhado pelo HUD (cenas/interface/hud.tscn), que
## usa a mesma conta para saber qual mostrar.
##
## Para criar um interagível novo: um script com "extends Interagivel" que
## muda texto_acao e escreve a função interagir() (e pode_interagir(), se
## ele só funcionar às vezes). Veja item_no_chao.gd e colonia_fungos.gd.
##
## @tool: roda também no editor (o item no chão mostra o desenho enquanto
## você monta a sala). As partes de jogo só rodam fora do editor.

const GRUPO_PERTO := "interagiveis_perto"

## O que aparece no aviso depois do "[E]" (ex.: "Pegar", "Recarregar pote").
@export var texto_acao: String = "Interagir"
## Altura do aviso acima da origem do nó, em pixels.
@export var altura_aviso: float = 18.0


func _ready() -> void:
	if Engine.is_editor_hint():
		return
	body_entered.connect(_ao_entrar)
	body_exited.connect(_ao_sair)


## Se agora dá para interagir (ex.: só recarrega o pote se ele tiver um).
## Os scripts filhos podem mudar esta função.
func pode_interagir() -> bool:
	return true


## O que acontece ao apertar E. Os scripts filhos escrevem esta função.
func interagir() -> void:
	pass


func _ao_entrar(corpo: Node2D) -> void:
	if corpo is Gabriel:
		add_to_group(GRUPO_PERTO)


func _ao_sair(corpo: Node2D) -> void:
	if corpo is Gabriel:
		remove_from_group(GRUPO_PERTO)


## O interagível disponível mais perto do ponto dado, ou null.
## "static": é chamada pela classe, sem precisar de um interagível:
##   Interagivel.mais_perto(get_tree(), global_position)
static func mais_perto(arvore: SceneTree, ponto: Vector2) -> Interagivel:
	var melhor: Interagivel = null
	var menor_distancia := INF
	for no in arvore.get_nodes_in_group(GRUPO_PERTO):
		var alvo := no as Interagivel
		if alvo == null or not alvo.pode_interagir():
			continue
		# distance_squared_to evita a raiz quadrada: para comparar quem está
		# mais perto, comparar os quadrados dá o mesmo resultado.
		var d := ponto.distance_squared_to(alvo.global_position)
		if d < menor_distancia:
			menor_distancia = d
			melhor = alvo
	return melhor
