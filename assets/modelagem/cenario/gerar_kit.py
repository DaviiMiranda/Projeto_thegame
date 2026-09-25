# gerar_kit.py — desenha, por código, as PEÇAS MODULARES do kit de cenário:
# pedaços de parede, de chão e o céu, que se encaixam lado a lado para
# montar qualquer sala no mesmo estilo da Biblioteca (FNAF: Into the Pit).
#
# Como rodar (Python 3 + numpy, igual ao gerar_biblioteca.py):
#
#   python assets/modelagem/cenario/gerar_kit.py
#
# O que sai (em assets/sprites/cenario/):
#   paredes/<peça>.png   80 x 112 px: um pedaço da parede do fundo
#   paredes/pilar.png    16 x 112 px: acabamento para as pontas da sala
#   chao/<peça>.png      128 x 68 px: um pedaço do chão (a faixa onde se anda)
#   ceu/ceu.png          320 x 180 px: céu e mata lá fora, repete sem emenda
# E as folhas de catálogo, com o nome de cada peça, para o guia
# (docs/imagens/kit_*.png).
#
# Os objetos (estantes, mesa, árvore...) e a textura das luzes saem do
# gerar_biblioteca.py, que também desenha a Biblioteca inteira. Este script
# IMPORTA as funções de lá (paleta, dithering, rachadura, janela...), então
# as peças têm exatamente o mesmo estilo.
#
# ---------------------------------------------------------------------------
# COMO UMA PEÇA "ENCAIXA" NA OUTRA SEM EMENDA
# ---------------------------------------------------------------------------
#
# Se cada peça tivesse manchas sorteadas à parte, a borda direita de uma não
# combinaria com a borda esquerda da próxima: apareceria uma "costura".
# A solução é usar ruído CÍCLICO: a grade de números sorteados dá a volta
# (a última coluna é a primeira de novo). Com uma grade de passo 40 numa
# peça de 80 px, por exemplo, a coluna 80 = coluna 0. Assim a textura sai
# pela direita exatamente como entra pela esquerda, e TODAS as paredes usam
# a mesma base de concreto: só muda o que vai por cima (janela, estante...).
# É a mesma ideia de "textura que repete" (tileable) dos jogos.
#
# A junta das placas de concreto fica na coluna 0 de cada peça de parede:
# ela disfarça ainda mais a passagem de uma peça para a outra.

import importlib.util
import os

import numpy as np

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.normpath(os.path.join(PASTA_SCRIPT, "..", "..", ".."))
PASTA_KIT = os.path.join(PASTA_PROJETO, "assets", "sprites", "cenario")
PASTA_DOCS = os.path.join(PASTA_PROJETO, "docs", "imagens")

# Importa o gerar_biblioteca.py como um módulo (sem rodar o main dele).
_spec = importlib.util.spec_from_file_location(
    "gerar_biblioteca",
    os.path.join(PASTA_PROJETO, "assets", "modelagem", "salas", "biblioteca", "gerar_biblioteca.py"))
bib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bib)

Imagem, RAMPAS, SOMBRA, dilatar = bib.Imagem, bib.RAMPAS, bib.SOMBRA, bib.dilatar

# ---------------------------------------------------------------------------
# Medidas do kit (as mesmas da Biblioteca e do guia docs/guia_montar_salas.md)
# ---------------------------------------------------------------------------

LARGURA_PAREDE = 80      # peças de parede: 80 px (4 por tela de 320)
LARGURA_PILAR = 16
LARGURA_CHAO = 128       # peças de chão: 128 px (múltiplo das lajotas de 32)
Y_CHAO = bib.Y_CHAO      # 112: onde a parede encontra o chão
ALTURA = bib.ALTURA_SALA  # 180
LUZ = 0.7                # luz "neutra" pintada: o resto vem das luzes do Godot


def ruido_ciclico(largura, altura, escala_x, escala_y, semente):
    """Igual ao ruido() da Biblioteca, mas a grade dá a volta na horizontal:
    a coluna gw da grade é a coluna 0. A largura precisa ser múltipla de
    escala_x para a volta cair exatamente na borda da imagem."""
    assert largura % escala_x == 0, "a largura precisa ser múltipla da escala"
    rng = np.random.default_rng(semente)
    gw = largura // escala_x
    gh = int(altura / escala_y) + 3
    grade = rng.random((gh, gw))
    xs = np.arange(largura) / escala_x
    ys = np.arange(altura) / escala_y
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = xs - x0
    fy = ys - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    x1 = (x0 + 1) % gw                      # a volta: depois da última, a primeira
    x0 = x0 % gw
    a = grade[y0][:, x0]
    b = grade[y0][:, x1]
    c = grade[y0 + 1][:, x0]
    d = grade[y0 + 1][:, x1]
    fx = fx[None, :]
    fy = fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# ---------------------------------------------------------------------------
# Paredes
# ---------------------------------------------------------------------------


def parede_base(largura=LARGURA_PAREDE):
    """Concreto, juntas, rodapé e teto: a base comum de toda peça de parede
    (os mesmos passos 1 a 3 do desenhar_fundo da Biblioteca)."""
    img = Imagem(largura, Y_CHAO)
    X, Y = img.X, img.Y
    parede = img.ret(0, 0, img.w, Y_CHAO)
    manchas = ruido_ciclico(img.w, img.h, 40, 18, 10)
    fino = ruido_ciclico(img.w, img.h, 2, 2, 11)
    escorrido = ruido_ciclico(img.w, img.h, 4, 60, 12)
    v = (0.30 + 0.22 * manchas + 0.08 * fino - 0.18 * (escorrido > 0.7)) * LUZ
    v = v - 0.12 * np.clip((Y - 90) / 22, 0, 1) - 0.15 * np.clip((24 - Y) / 14, 0, 1)
    img.pintar(parede, "concreto", v)
    junta = parede & ((X % 80 == 0) | (Y == 58)) & (Y > 14) & (Y < 100)
    img.pintar(junta, "concreto", v - 0.2, achatar=False)
    realce = parede & ((X % 80 == 1) | (Y == 59)) & (Y > 14) & (Y < 100)
    img.pintar(realce, "concreto", v + 0.12, achatar=False)
    rodape = img.ret(0, 100, img.w, Y_CHAO)
    img.pintar(rodape, "madeira", 0.22 + 0.1 * fino + 0.1 * (Y == 100))
    img.pintar(img.ret(0, 0, img.w, 12), "concreto", 0.1 + 0.08 * fino + 0.12 * (Y == 11))
    img.cor(img.ret(0, 12, img.w, 15), RAMPAS["concreto"][0])
    img.v, img.fino = v, fino            # guardados para os detalhes por cima
    return img


def rachadura(img, x_ini, semente):
    """Passeio aleatório descendo do teto (igual ao da Biblioteca)."""
    rng = np.random.default_rng(semente)
    x, y = float(x_ini), 15.0
    pontos = [(x, y)]
    for _ in range(rng.integers(6, 11)):
        x = float(np.clip(x + rng.uniform(-5, 5), 4, img.w - 5))
        y += rng.uniform(4, 9)
        pontos.append((x, y))
    parede = img.ret(0, 0, img.w, Y_CHAO)
    risco = img.caminho(pontos, 0.5) & parede
    img.cor(risco, RAMPAS["concreto"][1])
    brilho = np.roll(risco, 1, axis=1) & ~risco & parede
    img.pintar(brilho, "concreto", img.v + 0.15, achatar=False)


def buraco_no_teto(img, pontos, semente, cipos=()):
    """Apaga um buraco (o céu aparece atrás), com borda quebrada clara,
    vergalhões, musgo e cipós. Mesma receita do desenhar_fundo."""
    parede = img.ret(0, 0, img.w, Y_CHAO)
    buraco = img.poligono(pontos)
    borda = dilatar(buraco, 2) & ~buraco & parede
    img.pintar(borda, "concreto", 0.62 + 0.15 * img.fino)
    img.cor(dilatar(buraco, 3) & ~dilatar(buraco, 2) & parede, RAMPAS["concreto"][2])
    img.apagar(buraco)
    rng = np.random.default_rng(semente)
    for _ in range(3):
        x0 = rng.uniform(8, img.w - 8)
        coluna = buraco[:, int(x0)]
        y0 = int(np.nonzero(coluna)[0].max()) + 2 if coluna.any() else 12
        ferro = img.linha(x0, y0, x0 + rng.uniform(-6, 6), y0 - rng.uniform(6, 12), 0.5)
        img.cor(ferro & ~buraco, RAMPAS["ferrugem"][3])
    perto = dilatar(buraco, 7) & ~dilatar(buraco, 2) & parede
    musgo = perto & (ruido_ciclico(img.w, img.h, 5 if img.w % 5 == 0 else 4, 4, semente + 1) > 0.45)
    img.pintar(musgo, "verde", 0.35 + 0.5 * img.fino)
    for x0 in cipos:
        comp = rng.integers(20, 60)
        linha = [(x0 + 1.5 * np.sin(k * 0.8), 8 + k * comp / 8) for k in range(9)]
        cipo = img.caminho(linha, 0.6) & ~buraco
        img.pintar(cipo, "verde", 0.35 + 0.3 * img.fino)
        img.pintar(dilatar(cipo) & (img.fino > 0.72) & parede & ~buraco, "verde", 0.55 + 0.3 * img.fino)


def parede_lisa():
    return parede_base()


def parede_rachada():
    img = parede_base()
    rachadura(img, 22, 13)
    rachadura(img, 58, 14)
    return img


def parede_janela():
    img = parede_base()
    bib.desenhar_janela(img, 20, 24, 40, 30)
    return img


def parede_estante():
    img = parede_base()
    luz = np.full((img.h, img.w), LUZ)
    bib.desenhar_estante_parede(img, 8, 72, 30, 100, luz)
    return img


def parede_placa():
    img = parede_base()
    bib.desenhar_placa(img, 21, 42, "SILENCIO")
    return img


def parede_porta():
    img = parede_base()
    bib.desenhar_porta(img, 20, 62, 46)
    return img


def parede_buraco():
    """Um buraco no teto que começa e termina dentro da peça."""
    img = parede_base()
    buraco_no_teto(img, bib.contorno_buraco(6, 74, 52, 20), 30, cipos=(10, 70))
    return img


def parede_desabada():
    """Teto caído de ponta a ponta: várias em sequência formam um buraco
    comprido. A borda de baixo é uma onda que começa e termina na mesma
    altura (sen(2πx/80) vale o mesmo em x = 0 e x = 80), então encaixa."""
    img = parede_base()
    xs = np.linspace(-1, img.w + 1, 21)
    fundo = 34 + 8 * np.sin(2 * np.pi * xs / img.w) + 4 * np.sin(6 * np.pi * xs / img.w + 1)
    pontos = [(-1, -1)] + list(zip(xs, fundo)) + [(img.w + 1, -1)]
    buraco_no_teto(img, pontos, 31, cipos=(18, 52))
    return img


def parede_fungos():
    """Canto úmido e escuro: musgo perto do chão e tufos de fungos."""
    img = parede_base()
    rachadura(img, 40, 15)
    parede = img.ret(0, 0, img.w, Y_CHAO)
    musgo = parede & (img.Y > 70) & (ruido_ciclico(img.w, img.h, 8, 4, 16) > 0.6)
    img.pintar(musgo, "verde", 0.15 + 0.2 * img.fino)
    for (cx, cy) in ((14, 98), (24, 94), (52, 72), (66, 99)):
        bib.colar_fungos(img, cx, cy, cx + cy)
    return img


def pilar():
    img = Imagem(LARGURA_PILAR, Y_CHAO)
    fino = ruido_ciclico(img.w, img.h, 2, 2, 17)
    lado = img.X / img.w
    img.pintar(img.ret(0, 0, img.w, Y_CHAO), "concreto", 0.12 + 0.2 * (1 - abs(lado - 0.35)) + 0.05 * fino)
    return img


PAREDES = {
    "parede_lisa": parede_lisa,
    "parede_rachada": parede_rachada,
    "parede_janela": parede_janela,
    "parede_estante": parede_estante,
    "parede_placa": parede_placa,
    "parede_porta": parede_porta,
    "parede_buraco": parede_buraco,
    "parede_desabada": parede_desabada,
    "parede_fungos": parede_fungos,
    "pilar": pilar,
}

# ---------------------------------------------------------------------------
# Chão
# ---------------------------------------------------------------------------


def chao_base():
    """Lajotas em perspectiva (fileiras mais baixas nas de cima, mais altas
    nas de baixo), iguais às da Biblioteca. Desenhamos na altura da sala
    inteira (180) para usar as mesmas medidas e cortamos a parte de cima no
    final (a peça tem só a faixa do chão, de y = 112 a 180)."""
    img = Imagem(LARGURA_CHAO, ALTURA)
    X, Y = img.X, img.Y
    chao = img.ret(0, Y_CHAO, img.w, img.h)
    fino = ruido_ciclico(img.w, img.h, 2, 2, 60)
    manchas = ruido_ciclico(img.w, img.h, 32, 10, 61)
    valor = np.zeros((img.h, img.w))
    junta = np.zeros((img.h, img.w), dtype=bool)
    for i in range(len(bib.FILEIRAS) - 1):
        ya, yb = bib.FILEIRAS[i], bib.FILEIRAS[i + 1]
        desloc = (i % 2) * 16
        faixa = (Y >= ya) & (Y < yb)
        # 4 tons sorteados por fileira, usados em ciclo (coluna % 4): a
        # lajota cortada na borda direita tem o mesmo tom que a da esquerda.
        coluna = ((X + desloc) // 32) % 4
        sorteio = np.random.default_rng(100 + i).random(4)
        valor[faixa] = (0.35 + 0.18 * sorteio[coluna])[faixa]
        junta |= faixa & ((Y == ya) | ((X + desloc) % 32 == 0))
    valor = (valor + 0.1 * manchas + 0.05 * fino) * LUZ - 0.2 * np.clip((122 - Y) / 10, 0, 1)
    img.pintar(chao, "piso", valor)
    img.pintar(chao & junta, "piso", valor - 0.22, achatar=False)
    # Pé da parede: sombra de 1 px e terra acumulada.
    img.cor(img.ret(0, Y_CHAO, img.w, Y_CHAO + 1), SOMBRA)
    img.pintar(img.ret(0, Y_CHAO + 1, img.w, Y_CHAO + 3) & (manchas > 0.4), "areia", 0.25 * LUZ)
    img.chao, img.fino, img.manchas = chao, fino, manchas
    return img


def folhas_secas(img, quantas, semente):
    rng = np.random.default_rng(semente)
    for _ in range(quantas):
        x = int(rng.integers(1, img.w - 2))
        y = int(rng.integers(Y_CHAO + 3, img.h))
        rampa = "areia" if rng.random() < 0.6 else "ferrugem"
        img.pintar(img.ret(x, y, x + 2, y + 1), rampa, 0.5 + 0.3 * rng.random())


def lajotas_faltando(img, quantas, semente):
    rng = np.random.default_rng(semente)
    for _ in range(quantas):
        x, y = rng.integers(12, img.w - 12), rng.integers(118, 174)
        buraco = img.elipse(x, y, rng.uniform(4, 9), rng.uniform(2, 4)) & img.chao
        img.pintar(buraco, "areia", (0.2 + 0.15 * img.fino) * LUZ)


def chao_lajotas():
    img = chao_base()
    lajotas_faltando(img, 2, 70)
    folhas_secas(img, 18, 71)
    return img


def chao_areia():
    img = chao_base()
    for (cx, cy, rx, ry) in ((40, 130, 34, 8), (96, 156, 30, 7), (70, 172, 22, 5)):
        monte = img.elipse(cx, cy, rx, ry) & (img.manchas + 0.3 * img.fino > 0.4) & img.chao
        img.pintar(monte, "areia", (0.45 + 0.35 * img.fino) * LUZ)
    lajotas_faltando(img, 3, 72)
    folhas_secas(img, 10, 73)
    return img


def chao_mato():
    img = chao_base()
    rng = np.random.default_rng(74)
    musgo = img.chao & (ruido_ciclico(img.w, img.h, 8, 4, 75) > 0.6)
    img.pintar(musgo, "verde", 0.2 + 0.25 * img.fino)
    for _ in range(70):
        x = int(rng.integers(1, img.w - 1))
        y = int(rng.integers(Y_CHAO + 4, img.h))
        altura = int(rng.integers(2, 6))
        img.pintar(img.ret(x, y - altura, x + 1, y + 1), "verde", 0.4 + 0.45 * rng.random())
        img.pintar(img.ret(x, y - altura, x + 1, y - altura + 1), "verde", 0.85)
    return img


def chao_tapete():
    """Tapete podre: a borda esquerda e a direita são retas e verticais,
    então vários em sequência formam um tapete comprido."""
    img = chao_base()
    X, Y = img.X, img.Y
    tapete = img.ret(0, 132, img.w, 172)
    buracos = ruido_ciclico(img.w, img.h, 8, 4, 63) > 0.66
    img.pintar(tapete & ~buracos, "tapete", (0.45 + 0.25 * img.manchas + 0.1 * img.fino) * LUZ)
    img.pintar(tapete & ~buracos & ((X + Y) % 6 == 0), "tapete", 0.25 * LUZ, achatar=False)
    folhas_secas(img, 8, 76)
    return img


CHAOS = {
    "chao_lajotas": chao_lajotas,
    "chao_areia": chao_areia,
    "chao_mato": chao_mato,
    "chao_tapete": chao_tapete,
}

# ---------------------------------------------------------------------------
# Céu (repete na horizontal a cada 320 px)
# ---------------------------------------------------------------------------


def ceu():
    """O desenhar_ceu da Biblioteca, com ruído cíclico e senos que dão a volta
    certinho em 320 px: sen(2π·k·x/320) vale o mesmo em x = 0 e x = 320 para
    qualquer k inteiro, então o recorte das matas também encaixa."""
    img = Imagem(320, ALTURA)
    x = img.X
    onda = lambda k: 2 * np.pi * k * x / img.w
    todo = img.ret(0, 0, img.w, img.h)
    img.pintar(todo, "ceu", 0.25 + 0.7 * (img.Y / 110) + 0.08 * ruido_ciclico(img.w, img.h, 40, 12, 1))
    n = ruido_ciclico(img.w, img.h, 32, 9, 2) * 0.7 + ruido_ciclico(img.w, img.h, 16, 5, 3) * 0.3
    img.pintar((n > 0.62) & (img.Y < 60), "ceu", 0.75 + (n - 0.62) * 2)
    topo_longe = 62 + 6 * np.sin(onda(3)) + 4 * np.sin(onda(7) + 1) + 3 * np.sin(onda(16))
    img.pintar(img.Y >= topo_longe, "mata_longe",
               0.8 - (img.Y - topo_longe) / 40 + 0.2 * ruido_ciclico(img.w, img.h, 8, 5, 4))
    topo_perto = 78 + 8 * np.sin(onda(2) + 2) + 5 * np.sin(onda(6)) + 3 * np.sin(onda(22) + 3)
    img.pintar(img.Y >= topo_perto, "mata_perto",
               0.85 - (img.Y - topo_perto) / 30 + 0.25 * ruido_ciclico(img.w, img.h, 4, 4, 5))
    return img


# ---------------------------------------------------------------------------
# Catálogo (folhas com o nome de cada peça, para o guia)
# ---------------------------------------------------------------------------

# Fonte 3x5 (maiúsculas, números e _) para os nomes no catálogo.
FONTE = {
    "A": "010101111101101", "B": "110101110101110", "C": "111100100100111",
    "D": "110101101101110", "E": "111100110100111", "F": "111100110100100",
    "G": "111100101101111", "H": "101101111101101", "I": "111010010010111",
    "J": "001001001101111", "K": "101101110101101", "L": "100100100100111",
    "M": "101111111101101", "N": "110101101101101", "O": "111101101101111",
    "P": "111101111100100", "Q": "111101101111001", "R": "110101110101101",
    "S": "111100111001111", "T": "111010010010010", "U": "101101101101111",
    "V": "101101101101010", "W": "101101111111101", "X": "101101010101101",
    "Y": "101101010010010", "Z": "111001010100111", "_": "000000000000111",
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111",
    "3": "111001111001111", "4": "101101111001001", "5": "111100111001111",
    "6": "111100111101111", "7": "111001001001001", "8": "111101111101111",
    "9": "111101111001111", " ": "000000000000000",
}
FUNDO_CATALOGO = (24, 24, 30, 255)
TEXTO_CATALOGO = (200, 200, 190, 255)


def escrever(px, x, y, texto):
    for i, letra in enumerate(texto.upper()):
        bits = FONTE.get(letra, FONTE[" "])
        for j in range(15):
            if bits[j] == "1":
                px[y + j // 3, x + 4 * i + j % 3] = TEXTO_CATALOGO


def catalogo(pecas, colunas, fundo_ceu=None, escala=2):
    """Monta uma folha com as peças lado a lado e o nome embaixo de cada uma.
    'pecas' é uma lista de (nome, Imagem). Onde a peça é transparente (buraco
    do teto, janela), mostramos o céu atrás, como no jogo."""
    margem, texto = 6, 10
    larg = max(p.w for _, p in pecas)
    larg = max(larg, max(4 * len(n) for n, _ in pecas))
    alt = max(p.h for _, p in pecas)
    linhas = (len(pecas) + colunas - 1) // colunas
    W = colunas * (larg + margem) + margem
    H = linhas * (alt + texto + margem) + margem
    folha = np.zeros((H, W, 4), dtype=np.uint8)
    folha[:] = FUNDO_CATALOGO
    for k, (nome, p) in enumerate(pecas):
        x = margem + (k % colunas) * (larg + margem)
        y = margem + (k // colunas) * (alt + texto + margem)
        area = folha[y:y + p.h, x:x + p.w]
        if fundo_ceu is not None:
            area[:] = fundo_ceu.px[:p.h, :p.w]
        cheio = p.px[..., 3] > 0
        area[cheio] = p.px[cheio]
        escrever(folha, x, y + alt + 3, nome)
    folha = folha.repeat(escala, axis=0).repeat(escala, axis=1)
    return folha


def main():
    print("Gerando o kit de cenário em", os.path.relpath(PASTA_KIT, PASTA_PROJETO))
    paredes = {nome: f() for nome, f in PAREDES.items()}
    for nome, img in paredes.items():
        img.salvar(f"{nome}.png", os.path.join(PASTA_KIT, "paredes"))
    chaos = {}
    for nome, f in CHAOS.items():
        img = f()
        # Corta a parte de cima: a peça de chão é só a faixa de y = 112 a 180.
        img.px = img.px[Y_CHAO:].copy()
        img.h = img.px.shape[0]
        img.salvar(f"{nome}.png", os.path.join(PASTA_KIT, "chao"))
        chaos[nome] = img
    img_ceu = ceu()
    img_ceu.salvar("ceu.png", os.path.join(PASTA_KIT, "ceu"))

    # Catálogo para o guia.
    objetos = [(nome, f()[0]) for nome, f in bib.FUNCOES_OBJETOS.items()]
    os.makedirs(PASTA_DOCS, exist_ok=True)
    for nome, pecas, colunas, com_ceu in (("kit_paredes", list(paredes.items()), 5, True),
                                          ("kit_chao", list(chaos.items()), 4, False),
                                          ("kit_objetos", objetos, 6, False)):
        bib.salvar_png(os.path.join(PASTA_DOCS, f"{nome}.png"),
                       catalogo(pecas, colunas, img_ceu if com_ceu else None))
        print("  catálogo:", f"docs/imagens/{nome}.png")


if __name__ == "__main__":
    main()
