class_name LuzPulsante
extends PointLight2D
## Luz que "respira" devagar: o brilho frio dos fungos bioluminescentes.
##
## A intensidade segue uma onda seno em volta da energia inicial:
##   energia(t) = energia_base * (1 + variacao * sen(2π * t / periodo + fase))
## sen() vai de -1 a 1, então a energia oscila entre base * (1 - variacao)
## e base * (1 + variacao), completando uma volta a cada "periodo" segundos.
## A fase vem da posição da luz, para os fungos não piscarem todos juntos.
##
## Mais tarde o papel 2 pode controlar a energia pela jogabilidade (o brilho
## dos fungos enfraquece com o tempo — docs/gdd.md); a aparência fica aqui.

## Quanto a energia sobe e desce (0,25 = 25% para cada lado).
@export var variacao: float = 0.25
## Duração de uma "respiração" completa, em segundos.
@export var periodo: float = 3.0

var _energia_base: float
var _fase: float
var _tempo := 0.0


func _ready() -> void:
	_energia_base = energy
	# Um número "qualquer" mas fixo para cada posição: fases diferentes.
	_fase = fmod(global_position.x * 0.37 + global_position.y * 0.11, TAU)


func _process(delta: float) -> void:
	_tempo += delta
	energy = _energia_base * (1.0 + variacao * sin(TAU * _tempo / periodo + _fase))
