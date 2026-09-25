// Raios de sol entrando por um buraco no teto (cutscene seg_acordar).
//
// Vai num ColorRect por cima do cenário. Não desenha nada sólido: SOMA luz
// (blend_add) em faixas inclinadas, como a luz que atravessa a poeira do ar.
//
// A matemática, em 4 passos:
//
// 1. Girar o sistema de coordenadas. Os raios andam numa direção d (um
//    vetor unitário na tela). Para cada pixel p, calculamos:
//      ao_longo = p · d        (quanto o pixel já "desceu" pelo raio)
//      atraves  = p · d_perp   (em qual raio ele está, de lado a lado)
//    onde d_perp = (-d.y, d.x) é d girado 90°. O produto escalar (·) mede a
//    "sombra" de um vetor sobre o outro: é a mesma conta do campo de visão
//    dos Insones (docs/gdd.md, item 2.4).
//
// 2. Faixas. Uma onda seno de "atraves" dá faixas claras e escuras
//    paralelas. Três ondas com frequências que não se repetem juntas
//    (números "sem divisor comum") dão faixas de larguras irregulares, que
//    parecem raios de verdade e não um código de barras. pow() afina as
//    faixas: seno elevado a um expoente alto só fica claro perto do pico.
//    Cada onda anda devagar com o TEMPO, então os raios "respiram" como luz
//    passando por folhas que balançam.
//
// 3. Decaimento. A luz é mais forte perto do buraco no teto e some
//    descendo. smoothstep(a, b, x) é uma rampa suave de 0 (em x = a) a 1
//    (em x = b); 1 - smoothstep(...) faz o contrário. Outra janela em
//    "atraves" limita os raios à largura do buraco.
//
// 4. Degraus (visual de pixel art). A intensidade contínua é cortada em
//    poucos níveis: floor(i * degraus) / degraus. Em vez de um degradê
//    liso, aparecem faixas chapadas, como luz desenhada à mão em pixel art.
//    A posição também é arredondada para o pixel (floor), então cada
//    "pixel" do raio é exatamente um pixel do jogo.
shader_type canvas_item;
render_mode blend_add, unshaded;

// Cor da luz (sol da manhã, quente).
uniform vec4 cor : source_color = vec4(1.0, 0.9, 0.65, 1.0);
// Força geral: 0 = sem raios. A AnimationPlayer mexe nela.
uniform float forca : hint_range(0.0, 2.0) = 1.0;
// Direção em que a luz anda na tela (x para a direita, y para baixo).
uniform vec2 direcao = vec2(0.5, 1.0);
// Onde fica o buraco no teto, em pixels do ColorRect: os raios nascem aqui.
uniform vec2 origem = vec2(170.0, 0.0);
// Largura da faixa de raios (de um lado a outro) e comprimento até sumir.
uniform float largura = 200.0;
uniform float comprimento = 190.0;
// Quantos níveis de intensidade (degraus). Poucos = mais "pixel art".
uniform float degraus = 4.0;
// Tamanho do ColorRect em pixels (o UV vai de 0 a 1; vezes o tamanho = pixels).
uniform vec2 tamanho = vec2(340.0, 200.0);

void fragment() {
	// Posição deste pixel, em pixels do ColorRect, arredondada para o
	// centro do pixel (todos os pontos de um pixel têm a mesma cor).
	vec2 p = floor(UV * tamanho) + 0.5 - origem;

	// 1. Coordenadas giradas.
	vec2 d = normalize(direcao);
	vec2 d_perp = vec2(-d.y, d.x);
	float ao_longo = dot(p, d);
	float atraves = dot(p, d_perp);

	// 2. Faixas irregulares que se mexem devagar.
	float f1 = pow(0.5 + 0.5 * sin(atraves * 0.110 + TIME * 0.35), 6.0);
	float f2 = pow(0.5 + 0.5 * sin(atraves * 0.047 - TIME * 0.21 + 1.7), 3.0);
	float f3 = 0.5 + 0.5 * sin(atraves * 0.023 + TIME * 0.13 + 4.0);
	float faixas = (f1 * 0.6 + f2 * 0.8) * f3;

	// 3. Decaimento ao descer e janela da largura do buraco.
	float descida = 1.0 - smoothstep(0.0, comprimento, ao_longo);
	float subida = smoothstep(-20.0, 10.0, ao_longo);  // nada acima do buraco
	float janela = 1.0 - smoothstep(largura * 0.3, largura * 0.5, abs(atraves));
	float i = faixas * descida * subida * janela;

	// 4. Degraus: corta a intensidade em poucos níveis.
	i = floor(i * degraus) / degraus;

	// 0,35 = teto de intensidade: o raio clareia o que está atrás, sem estourar.
	COLOR = vec4(cor.rgb, i * 0.35 * forca);
}
