// Vinheta com dithering: escurece as bordas da tela em pixels "xadrez",
// como nos jogos 16 bits (e no FNAF: Into the Pit), em vez de um degradê liso.
//
// Vai num ColorRect do tamanho da tela, dentro de um CanvasLayer por cima
// da sala (a vinheta fica parada na tela enquanto a câmera anda).
//
// A matemática, em 3 passos:
//
// 1. Distância ao centro. Levamos o UV (0 a 1 na tela) para -1 a 1 com
//    uv * 2 - 1: o centro vira (0, 0) e os cantos, (±1, ±1). Como a tela é
//    mais larga que alta (320×180), achatamos o x pela proporção, senão a
//    vinheta ficaria um losango esticado. "d" é o comprimento desse vetor:
//    0 no centro, cerca de 1 nas bordas e mais nos cantos.
//
// 2. Força da vinheta. smoothstep(inicio, fim, d) é uma rampa suave: vale 0
//    até d = inicio, 1 a partir de d = fim, e sobe em S no meio. Assim o
//    centro da tela (onde está o Gabriel) fica intacto e só a borda escurece.
//
// 3. Dithering ordenado (matriz de Bayer 4×4). A tela não pode mostrar
//    "meio preto" se quisermos o visual de paleta limitada. Então cortamos
//    a escuridão em poucos níveis e, para cada pixel, decidimos se ele
//    arredonda para cima ou para baixo comparando a parte fracionária com um
//    limiar da matriz de Bayer. A matriz espalha os limiares de 0 a 15/16
//    de forma que vizinhos tenham valores bem diferentes: quanto mais escura
//    a região, mais pixels do "xadrez" acendem, e de longe o olho mistura
//    os pixels e vê um degradê. O mesmo truque está no gerador da arte
//    (assets/modelagem/salas/biblioteca/gerar_biblioteca.py, função pintar).
shader_type canvas_item;
render_mode unshaded;

// Cor da borda (quase preto, um pouco azulado: frio).
uniform vec4 cor : source_color = vec4(0.02, 0.02, 0.04, 1.0);
// Onde a vinheta começa e onde fica no máximo (distância ao centro).
uniform float inicio : hint_range(0.0, 2.0) = 0.55;
uniform float fim : hint_range(0.0, 2.0) = 1.25;
// Escuridão máxima (1 = preto total nos cantos).
uniform float forca : hint_range(0.0, 1.0) = 0.85;
// Quantos níveis de escuridão. Poucos = mais "pixel art".
uniform float niveis = 4.0;
// Tamanho da tela em pixels do jogo (para achar o pixel de cada fragmento).
uniform vec2 tamanho = vec2(320.0, 180.0);

// Matriz de Bayer 4×4, lida linha a linha. Somamos 0,5 e dividimos por 16
// para os limiares ficarem entre 0 e 1 (1/32, 3/32, ... 31/32).
const float BAYER[16] = float[](
	0.0,  8.0,  2.0, 10.0,
	12.0, 4.0, 14.0,  6.0,
	3.0, 11.0,  1.0,  9.0,
	15.0, 7.0, 13.0,  5.0
);

void fragment() {
	// Qual pixel do jogo é este (coluna e linha inteiras).
	vec2 pixel = floor(UV * tamanho);

	// 1. Distância ao centro, com o x achatado pela proporção da tela.
	vec2 p = (pixel + 0.5) / tamanho * 2.0 - 1.0;
	p.x *= tamanho.x / tamanho.y * 0.62;
	float d = length(p);

	// 2. Força: 0 no centro, "forca" na borda.
	float v = smoothstep(inicio, fim, d) * forca;

	// 3. Dithering: posição do pixel dentro do bloco 4×4 -> limiar.
	int i = int(mod(pixel.x, 4.0)) + int(mod(pixel.y, 4.0)) * 4;
	float limiar = (BAYER[i] + 0.5) / 16.0;
	float a = floor(v * niveis + limiar) / niveis;

	COLOR = vec4(cor.rgb, clamp(a, 0.0, 1.0));
}
