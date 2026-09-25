@tool
extends Node2D
## Guias de montagem que só aparecem no EDITOR (no jogo, somem).
##
## Fica como o último filho da sala, então é desenhado por cima de tudo:
##   - amarelo: o tamanho da sala (a câmera nunca mostra nada fora dele);
##   - linhas amarelas fracas: onde acaba cada tela de 320 px;
##   - azul: a faixa de chão onde os pés do Gabriel podem andar.
## Os números vêm da sala (Inspetor da raiz: largura, chao_fundo...).


func _ready() -> void:
	visible = Engine.is_editor_hint()


func _draw() -> void:
	var sala := get_parent() as Sala
	if sala == null:
		return
	var altura := Sala.ALTURA
	draw_rect(Rect2(0, 0, sala.largura, altura), Color(1, 0.85, 0.2, 0.9), false, 1.0)
	for x in range(320, sala.largura, 320):
		draw_line(Vector2(x, 0), Vector2(x, altura), Color(1, 0.85, 0.2, 0.35), 1.0)
	var faixa := Rect2(sala.margem_lados, sala.chao_fundo,
			sala.largura - 2 * sala.margem_lados, sala.chao_frente - sala.chao_fundo)
	draw_rect(faixa, Color(0.3, 0.7, 1, 0.12), true)
	draw_rect(faixa, Color(0.3, 0.7, 1, 0.9), false, 1.0)
