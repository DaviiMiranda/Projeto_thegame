extends Node
## O inventário do Gabriel: o que ele carrega e o que está equipado.
##
## É um "autoload" (Projeto > Configurações do Projeto > Globais): o Godot cria
## este nó uma vez só, antes de qualquer cena, e ele continua vivo quando a
## sala muda. Por isso o inventário não se perde ao passar de uma sala para
## outra. De qualquer script, ele é acessado pelo nome: Inventario.adicionar(...)
##
## ESTRUTURA DE DADOS (docs/gdd.md, item 2.4: "inventário em grade (matriz)"):
##
##   grade = [ [item, null, null, null],     <- linha 0
##             [null, null, null, null],     <- linha 1
##             [null, null, null, null] ]    <- linha 2
##
## Uma matriz é uma lista de linhas, e cada linha é uma lista de colunas:
## grade[linha][coluna]. null = espaço vazio. Para achar um espaço livre,
## percorremos linha por linha, coluna por coluna (a ordem de leitura de um
## texto), e o primeiro null é o escolhido.
##
## Os GADGETS são outra lista, de 3 posições (teclas 1, 2 e 3). Ela não tira
## o item da grade: só aponta para ele, como um atalho. Equipar é colocar o
## item numa dessas posições.
##
## Ninguém mexe nas listas direto: usam as funções daqui, que avisam pelo
## sinal "mudou" (a interface e o Gabriel se atualizam ao ouvir o sinal).

## Algo mudou (item entrou, saiu, foi equipado ou desequipado).
signal mudou
## O Gabriel pegou um item (a interface mostra a mensagem).
signal item_pego(item: Item)

const LINHAS := 3
const COLUNAS := 4
## Um espaço para cada ferramenta equipável prevista no GDD: pote de fungos,
## cápsulas de clarão e objetos de arremesso (docs/personagens/gabriel.md).
const ESPACOS_GADGET := 3

## A matriz LINHAS x COLUNAS de itens (null = vazio).
var grade: Array = []
## Os itens equipados, um por espaço de gadget (null = vazio).
var gadgets: Array = []
## O que muda durante o jogo em cada item, pelo id. Ex.:
##   estado["pote_fungos"] = {"carga": 0.8, "aceso": true}
## Fica aqui (e não no Item) para sobreviver à troca de sala.
var estado: Dictionary = {}
## Itens do mundo que já foram pegos (pelo id único de cada um no mapa).
## Assim, ao voltar para a sala, o item não aparece de novo no chão.
var pegos: Dictionary = {}


func _ready() -> void:
	limpar()


## Começa do zero: grade vazia, nada equipado. Chame no "Novo jogo".
func limpar() -> void:
	grade = []
	for linha in LINHAS:
		var colunas := []
		colunas.resize(COLUNAS)   # resize enche a lista com null
		grade.append(colunas)
	gadgets = []
	gadgets.resize(ESPACOS_GADGET)
	estado = {}
	pegos = {}
	mudou.emit()


## Guarda o item no primeiro espaço livre da grade. Se for um gadget e
## houver espaço de gadget livre, já equipa (é o que o jogador espera ao
## pegar a lanterna). Devolve false se o inventário estiver cheio.
func adicionar(item: Item) -> bool:
	for linha in LINHAS:
		for coluna in COLUNAS:
			if grade[linha][coluna] == null:
				grade[linha][coluna] = item
				if item.equipavel and espaco_do_gadget(item) == -1:
					var livre := gadgets.find(null)
					if livre != -1:
						gadgets[livre] = item
				item_pego.emit(item)
				mudou.emit()
				return true
	return false


## O item na posição (linha, coluna) da grade, ou null.
func item_em(linha: int, coluna: int) -> Item:
	return grade[linha][coluna]


## Se o Gabriel tem um item com esse id.
func tem(id: String) -> bool:
	for linha in grade:
		for item in linha:
			if item != null and item.id == id:
				return true
	return false


## Coloca o item no espaço de gadget (0, 1 ou 2). Se ele já estava em outro
## espaço, sai de lá (um item não fica equipado duas vezes).
func equipar(item: Item, espaco: int) -> void:
	if item == null or not item.equipavel:
		return
	var antigo := espaco_do_gadget(item)
	if antigo != -1:
		gadgets[antigo] = null
	gadgets[espaco] = item
	mudou.emit()


func desequipar(espaco: int) -> void:
	gadgets[espaco] = null
	mudou.emit()


## Em qual espaço de gadget o item está (0, 1 ou 2), ou -1 se não está.
func espaco_do_gadget(item: Item) -> int:
	return gadgets.find(item)


## O dicionário de estado de um item (cria vazio na primeira vez).
func estado_de(id: String) -> Dictionary:
	if not estado.has(id):
		estado[id] = {}
	return estado[id]
