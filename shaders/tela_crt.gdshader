// Efeito de monitor antigo (CRT), desenhado por cima da tela do menu.
// Não mexe nos botões embaixo: só escurece por cima com linhas, bordas e cintilação.
shader_type canvas_item;
render_mode unshaded;

// Quanto as linhas horizontais escurecem a imagem.
uniform float forca_linhas : hint_range(0.0, 1.0) = 0.3;
// Quanto as bordas da tela escurecem (vinheta).
uniform float forca_vinheta : hint_range(0.0, 3.0) = 1.6;
// Quanto a tela pisca.
uniform float forca_cintilacao : hint_range(0.0, 0.3) = 0.04;

void fragment() {
	// Linhas: um pixel sim, um pixel não, fica mais escuro.
	float linha = mod(floor(FRAGCOORD.y), 2.0) * forca_linhas;

	// Vinheta: quanto mais longe do centro (UV = 0.5, 0.5), mais escuro.
	vec2 do_centro = UV - vec2(0.5);
	float vinheta = dot(do_centro, do_centro) * forca_vinheta;

	// Cintilação: uma onda rápida que sobe e desce com o tempo.
	float cintilacao = (sin(TIME * 50.0) * 0.5 + 0.5) * forca_cintilacao;

	// Preto com transparência: quanto maior o alfa, mais escuro fica o que está embaixo.
	COLOR = vec4(0.0, 0.0, 0.0, clamp(linha + vinheta + cintilacao, 0.0, 1.0));
}
