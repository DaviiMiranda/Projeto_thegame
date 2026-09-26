# gerar_biblioteca.py — desenha, por código, a pixel art da Biblioteca MIL
# ANOS DEPOIS, a primeira sala jogável (docs/gdd.md, itens 3 e 4).
#
# Como rodar (precisa só de Python 3 e numpy; não precisa do Blender):
#
#   python assets/modelagem/salas/biblioteca/gerar_biblioteca.py
#
# (Sem numpy? "pip install numpy". O Python que vem com o Blender também
# serve: blender -b --python assets/modelagem/salas/biblioteca/gerar_biblioteca.py)
#
# Com PREVIA=1 ele também monta uma prévia da sala inteira (camadas uma em
# cima da outra, objetos ordenados pelo pé) em previa_biblioteca.png, nesta
# pasta. A prévia NÃO vai para o jogo e não deve ser commitada.
#
# O que sai (em assets/sprites/salas/biblioteca/):
#   biblioteca_ceu.png       céu e mata lá fora (vista pelos buracos do teto)
#   biblioteca_fundo.png     parede do fundo, teto quebrado, estantes de parede
#   biblioteca_chao.png      o chão (a faixa onde o Gabriel anda), raízes, areia
#   biblioteca_frente.png    primeiro plano: copa da árvore, cipós, entulho
#
# E, no kit de cenário que qualquer sala pode usar (assets/sprites/cenario/):
#   objetos/<objeto>.png     cada objeto que o Gabriel contorna (y-sort)
#   luzes/luz.png            textura das luzes (PointLight2D)
# As peças modulares (paredes, chão, céu) saem de
# assets/modelagem/cenario/gerar_kit.py, que reaproveita as funções daqui.
#
# ---------------------------------------------------------------------------
# O ESTILO (FNAF: Into the Pit, adaptado ao nosso GDD)
# ---------------------------------------------------------------------------
#
# - Vista lateral "2.5D": a parede do fundo é vista de frente e o chão é
#   visto um pouco de cima, como um palco. O Gabriel anda para os lados E
#   para cima/baixo nessa faixa de chão (mais para cima = mais para o fundo).
# - Paleta limitada e escura (cerca de 60 cores no total, em rampas de 4 a 8
#   tons por material). As cores base vêm da cutscene seg_acordar, para a
#   troca cutscene -> sala não destoar.
# - Sombreamento em "degraus" com dithering ordenado (matriz de Bayer): em
#   vez de degradê liso, cada material tem poucos tons e a passagem de um
#   tom para outro é feita com um xadrez de pixels. É o visual 16 bits.
# - Contorno escuro de 1 px nos objetos, para eles se destacarem do fundo.
# - Luz: a arte já vem com uma luz "pintada" suave (sol quente pelos buracos
#   do teto à esquerda, escuro frio à direita). O resto (sol forte, brilho
#   dos fungos, a escuridão geral) é feito no Godot com CanvasModulate e
#   PointLight2D, que também iluminam o Gabriel quando ele passa.
#
# ---------------------------------------------------------------------------
# COMO O DESENHO É FEITO
# ---------------------------------------------------------------------------
#
# Cada imagem é uma matriz numpy de (altura, largura, 4) bytes: R, G, B, A.
# Em vez de pintar pixel por pixel com laços, montamos MÁSCARAS: matrizes de
# verdadeiro/falso do tamanho da imagem, que dizem "este pixel faz parte da
# forma". Exemplo: a máscara de um círculo é (X-cx)² + (Y-cy)² <= r², onde X
# e Y são matrizes com a coordenada de cada pixel. Depois pintamos todos os
# pixels da máscara de uma vez. É rápido e cada forma vira uma linha de conta.
#
# Tudo é determinístico: os números "aleatórios" (manchas, rachaduras, folhas)
# saem de geradores com semente fixa, então rodar de novo dá a mesma imagem.

import os
import struct
import sys
import zlib

import numpy as np

sys.dont_write_bytecode = True

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.normpath(os.path.join(PASTA_SCRIPT, "..", "..", "..", ".."))
PASTA_SAIDA = os.path.join(PASTA_PROJETO, "assets", "sprites", "salas", "biblioteca")
# Objetos e luz são do kit de cenário: servem para qualquer sala.
PASTA_KIT = os.path.join(PASTA_PROJETO, "assets", "sprites", "cenario")
# PREVIA=1 salva a prévia nesta pasta; PREVIA=<pasta> salva nela.
PREVIA = os.environ.get("PREVIA", "")

# ---------------------------------------------------------------------------
# Medidas da sala (em pixels do jogo). Os mesmos números estão na cena
# cenas/salas/biblioteca.tscn: se mudar aqui, mude lá.
# ---------------------------------------------------------------------------

LARGURA_SALA = 960        # 3 telas de 320
ALTURA_TELA = 180         # altura de uma tela do jogo
ALTURA_SALA = 300         # a parte sul (a frente do chão) passa da tela:
                          # a câmera também anda na vertical
Y_CHAO = 112              # linha onde a parede encontra o chão
PARALAXE_CEU = 0.5        # o céu anda na metade da velocidade da câmera
# O céu precisa cobrir a tela quando a câmera está no fim da sala:
# 320 + (960 - 320) * 0,5 = 640 px.
LARGURA_CEU = int(320 + (LARGURA_SALA - 320) * PARALAXE_CEU)

# Buracos no teto: (x inicial, x final, até que altura a parede caiu).
BURACO_GRANDE = (150, 338, 58)   # em cima da árvore
BURACO_PEQUENO = (606, 672, 26)  # em cima do carrinho de livros

# Onde cada objeto fica na sala: (nome do sprite, x do pé, y do pé, espelhado).
# "Pé" = ponto do objeto que encosta no chão, na frente. É por esse y que o
# Godot ordena quem aparece na frente de quem (y-sort).
OBJETOS = [
    ("cabine", 96, 128, False),
    ("cadeira", 152, 142, False),
    ("arvore", 238, 140, False),
    ("entulho", 318, 126, False),
    ("estante_caida", 362, 174, False),
    ("estante_vazia", 440, 134, False),
    ("livros", 494, 170, False),
    ("mesa_leitura", 572, 156, False),
    ("entulho", 652, 124, True),
    ("carrinho", 706, 150, False),
    ("estante_quebrada", 800, 134, False),
    ("livros", 878, 164, True),
    ("fungo", 758, 168, False),
    ("fungo", 846, 140, True),
    ("fungo", 912, 124, False),
    # Parte sul (a frente da sala, abaixo da primeira tela).
    ("mesa_leitura", 170, 232, False),
    ("cadeira", 116, 246, False),
    ("cadeira", 228, 214, True),
    ("entulho", 404, 212, False),
    ("livros", 340, 264, False),
    ("estante_vazia", 560, 208, False),
    ("estante_quebrada", 640, 246, True),
    ("carrinho", 520, 282, True),
    ("livros", 604, 290, True),
    ("estante_caida", 744, 226, True),
    ("cabine", 860, 272, True),
    ("entulho", 72, 288, True),
    ("fungo", 800, 262, False),
    ("fungo", 884, 212, True),
    ("fungo", 934, 288, False),
]

# ---------------------------------------------------------------------------
# Paleta. Cada material é uma RAMPA: do tom mais escuro ao mais claro.
# ---------------------------------------------------------------------------


def hexa(*cores):
    """Converte '#rrggbb' em [r, g, b, 255]."""
    return [[int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255] for c in cores]


RAMPAS = {
    # concreto esverdeado da parede (tons da cutscene: #454c49, #5b5c53)
    "concreto": hexa("#0f1112", "#181b1c", "#222627", "#2d3231", "#3a403d",
                     "#48504b", "#5b6259", "#737a6c", "#8f9380"),
    # madeira velha e escura (cutscene: #3c332a, #615242, #826950)
    "madeira": hexa("#110d0b", "#1c1612", "#2a211a", "#3a2e24", "#4d3e30",
                    "#615242", "#7b6650", "#968063"),
    # casca da árvore: marrom acinzentado
    "casca": hexa("#100e0c", "#1b1815", "#28231e", "#383029", "#4a4036",
                  "#5f5445", "#7a6d58", "#978a6e"),
    # musgo e folhas (cutscene: #223521, #2a492b, #547c45)
    "verde": hexa("#0a130c", "#122015", "#1a2f1c", "#223d22", "#2e5029",
                  "#3f6633", "#547c45", "#76995a"),
    # piso cerâmico antigo
    "piso": hexa("#131312", "#1d1d1b", "#282824", "#34342e", "#424138",
                 "#514f43", "#646052", "#7b7563"),
    # terra e areia que entrou pelo teto
    "areia": hexa("#1d1913", "#2b251c", "#3b3326", "#4f4532", "#665a41",
                  "#80734f", "#9c8d63", "#b8a87a"),
    # carpete podre embaixo das mesas de leitura
    "tapete": hexa("#120c0b", "#1c1311", "#281a17", "#34221d", "#402b24",
                   "#4e352b"),
    # céu da manhã (cutscene: #99b3c4)
    "ceu": hexa("#6b8ba0", "#7f9db0", "#93afbf", "#a9c1cb", "#c1d3d6",
                "#d9e3dc"),
    # mata lá fora, azulada pela distância (perspectiva atmosférica)
    "mata_longe": hexa("#4c6670", "#58737a", "#668287", "#779193"),
    "mata_perto": hexa("#2c4240", "#34504a", "#3f5f53", "#4d6f5b"),
    # sol (cutscene: #eacd92)
    "sol": hexa("#a2875a", "#c9a86a", "#eacd92", "#f6e7bd"),
    # fungos bioluminescentes: ciano frio
    "fungo": hexa("#0b2326", "#124248", "#1b6d70", "#2aa3a0", "#63dcc9",
                  "#bdfbea"),
    # metal enferrujado (carrinho, vergalhões)
    "ferrugem": hexa("#170e0a", "#2a1810", "#422516", "#5d3620", "#7a4a2a",
                     "#94643c"),
    "metal": hexa("#121416", "#1e2124", "#2c3034", "#3d4247", "#52585c",
                  "#6c7275"),
    # lombadas de livro desbotadas
    "livro_vermelho": hexa("#1f0d0c", "#361815", "#50241d", "#6b3527"),
    "livro_azul": hexa("#0e1219", "#18202b", "#243142", "#35465a"),
    "livro_ocre": hexa("#201a0d", "#3a2f17", "#574624", "#756038"),
    "papel": hexa("#3d3a30", "#5a5647", "#7a7460", "#9a927a"),
    # tecido verde das divisórias da cabine (como na cutscene)
    "tecido": hexa("#0f1712", "#16231a", "#1f3022", "#2a3f2c", "#375036"),
}
CONTORNO = hexa("#08080b")[0]      # contorno dos objetos (quase preto, frio)
SOMBRA = hexa("#060607")[0]        # sombra de contato no chão

# Matriz de Bayer 4x4: os números de 0 a 15 estão espalhados de um jeito que
# qualquer "limiar" acende pixels bem distribuídos. Dividindo por 16 viram
# limiares entre 0 e 1. É a base do dithering ordenado (ver pintar()).
BAYER = (np.array([[0, 8, 2, 10],
                   [12, 4, 14, 6],
                   [3, 11, 1, 9],
                   [15, 7, 13, 5]], dtype=float) + 0.5) / 16.0


# ---------------------------------------------------------------------------
# A "tela" onde desenhamos
# ---------------------------------------------------------------------------


class Imagem:
    def __init__(self, largura, altura):
        self.w, self.h = largura, altura
        self.px = np.zeros((altura, largura, 4), dtype=np.uint8)
        # Y[i, j] = i e X[i, j] = j: a coordenada de cada pixel.
        self.Y, self.X = np.mgrid[0:altura, 0:largura]
        # Limiar de Bayer para cada pixel (a matriz 4x4 repetida).
        self.limiar = BAYER[self.Y % 4, self.X % 4]

    # --- formas (devolvem máscaras) ---------------------------------------

    def ret(self, x0, y0, x1, y1):
        """Retângulo com canto superior esquerdo (x0, y0), sem incluir x1/y1."""
        return (self.X >= x0) & (self.X < x1) & (self.Y >= y0) & (self.Y < y1)

    def elipse(self, cx, cy, rx, ry):
        """Pixels cujo centro está dentro da elipse ((x-cx)/rx)² + ((y-cy)/ry)² <= 1."""
        dx = (self.X + 0.5 - cx) / rx
        dy = (self.Y + 0.5 - cy) / ry
        return dx * dx + dy * dy <= 1.0

    def poligono(self, pontos):
        """Regra par-ímpar: um ponto está dentro se uma semirreta saindo dele
        para a esquerda cruza as bordas do polígono um número ÍMPAR de vezes."""
        px, py = self.X + 0.5, self.Y + 0.5
        dentro = np.zeros((self.h, self.w), dtype=bool)
        n = len(pontos)
        for i in range(n):
            x1, y1 = pontos[i]
            x2, y2 = pontos[(i + 1) % n]
            if y1 == y2:
                continue
            cruza = (y1 > py) != (y2 > py)
            x_corte = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            dentro ^= cruza & (px < x_corte)
        return dentro

    def linha(self, x0, y0, x1, y1, raio=0.5):
        """Pixels a no máximo 'raio' do segmento. Distância de ponto a segmento:
        projeta o ponto na reta (produto escalar), limita ao segmento, mede."""
        px, py = self.X + 0.5, self.Y + 0.5
        dx, dy = x1 - x0, y1 - y0
        comp2 = dx * dx + dy * dy or 1.0
        t = np.clip(((px - x0) * dx + (py - y0) * dy) / comp2, 0.0, 1.0)
        qx, qy = x0 + t * dx, y0 + t * dy
        return (px - qx) ** 2 + (py - qy) ** 2 <= raio * raio

    def caminho(self, pontos, raio=0.5):
        m = np.zeros((self.h, self.w), dtype=bool)
        for a, b in zip(pontos, pontos[1:]):
            m |= self.linha(a[0], a[1], b[0], b[1], raio)
        return m

    # --- pintura ------------------------------------------------------------

    def cor(self, mascara, rgba):
        self.px[mascara] = rgba

    def pintar(self, mascara, rampa, valor, achatar=True):
        """Pinta a máscara com uma rampa de cores, escolhendo o tom pelo
        'valor' (0 = mais escuro, 1 = mais claro) de cada pixel.

        Dithering ordenado: o valor contínuo cai entre dois tons da rampa,
        t = valor * (n - 1) = k + f (k inteiro, f a fração). Somamos o limiar
        de Bayer do pixel (entre 0 e 1) e arredondamos para baixo: o pixel
        vai para o tom k+1 quando f + limiar >= 1, o que acontece numa
        fração f dos pixels, bem espalhados. De longe, o olho mistura e vê
        o tom intermediário.

        'achatar' deixa o tom chapado no meio de cada faixa e só faz o
        xadrez perto da passagem de um tom para outro, como um pixel artist
        faria (senão a imagem inteira vira chuvisco)."""
        cores = np.array(RAMPAS[rampa] if isinstance(rampa, str) else rampa, dtype=np.uint8)
        n = len(cores)
        v = np.broadcast_to(np.clip(valor, 0.0, 1.0), mascara.shape)
        t = v * (n - 1)
        if achatar:
            k = np.floor(t)
            f = np.clip((t - k - 0.3) / 0.4, 0.0, 1.0)
            t = k + f
        idx = np.clip(np.floor(t + self.limiar), 0, n - 1).astype(int)
        self.px[mascara] = cores[idx[mascara]]

    def opaco(self):
        return self.px[..., 3] > 0

    def apagar(self, mascara):
        self.px[mascara] = 0

    def contornar(self, rgba=CONTORNO):
        """Contorno de 1 px: pixels vazios que encostam (em cruz) num cheio."""
        a = self.opaco()
        borda = dilatar(a) & ~a
        self.px[borda] = rgba

    def colar(self, outra, x, y):
        """Cola outra imagem (respeitando a transparência) com o canto em (x, y)."""
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + outra.w, self.w), min(y + outra.h, self.h)
        if x0 >= x1 or y0 >= y1:
            return
        pedaco = outra.px[y0 - y:y1 - y, x0 - x:x1 - x]
        cheio = pedaco[..., 3] > 0
        self.px[y0:y1, x0:x1][cheio] = pedaco[cheio]

    def espelhar(self):
        self.px = self.px[:, ::-1].copy()

    def salvar(self, nome, pasta=None):
        caminho = os.path.join(pasta or PASTA_SAIDA, nome)
        salvar_png(caminho, self.px)
        print("  salvo:", os.path.relpath(caminho, PASTA_PROJETO), f"({self.w}x{self.h})")


def dilatar(m, vezes=1):
    """Engorda a máscara em 1 px (em cruz) 'vezes' vezes."""
    for _ in range(vezes):
        p = np.pad(m, 1)
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


def ruido(largura, altura, escala_x, escala_y, semente):
    """Ruído de valor: sorteia números numa grade grossa (um a cada escala_x
    por escala_y pixels) e interpola entre eles com uma curva suave
    (3t² - 2t³, a 'smoothstep'). Dá manchas macias, de 0 a 1.
    escala_y bem maior que escala_x dá listras verticais (escorridos)."""
    rng = np.random.default_rng(semente)
    gw = int(largura / escala_x) + 3
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
    a = grade[y0][:, x0]
    b = grade[y0][:, x0 + 1]
    c = grade[y0 + 1][:, x0]
    d = grade[y0 + 1][:, x0 + 1]
    fx = fx[None, :]
    fy = fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def salvar_png(caminho, px):
    """Grava um PNG RGBA 8 bits sem precisar de biblioteca de imagem.
    Um PNG é: assinatura + blocos (IHDR = tamanho e formato, IDAT = pixels
    comprimidos com zlib, IEND = fim). Cada linha de pixels começa com um
    byte de 'filtro' (0 = nenhum)."""
    h, w, _ = px.shape
    cru = b"".join(b"\x00" + px[y].tobytes() for y in range(h))

    def bloco(tipo, dados):
        crc = zlib.crc32(tipo + dados) & 0xFFFFFFFF
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", crc)

    png = (b"\x89PNG\r\n\x1a\n"
           + bloco(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + bloco(b"IDAT", zlib.compress(cru, 9))
           + bloco(b"IEND", b""))
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "wb") as arq:
        arq.write(png)


# ---------------------------------------------------------------------------
# Luz pintada: quanto de luz chega em cada ponto da sala (0 a ~1,2).
# ---------------------------------------------------------------------------


def luz_pintada(X, Y):
    """Sol entrando pelos buracos do teto, caindo na diagonal (desce 1 px e
    anda 0,5 px para a direita, a mesma direção dos raios da cutscene).
    Para saber se um ponto (x, y) recebe sol, voltamos pelo raio até o
    teto: x_no_teto = x - 0,5 * y. Se x_no_teto cai dentro de um buraco,
    o ponto está no sol. Longe dos buracos, a sala escurece para a direita."""
    luz = 0.55 - 0.25 * np.clip((X - 600) / 300, 0, 1)
    x_teto = X - 0.5 * Y
    for (xa, xb, _), forca in ((BURACO_GRANDE, 0.55), (BURACO_PEQUENO, 0.35)):
        # 1 no meio do buraco, caindo suave até 0 a 30 px da borda.
        dentro = np.clip(np.minimum(x_teto - xa, xb - x_teto) / 30 + 0.6, 0, 1)
        luz = luz + forca * dentro
    return luz


# ---------------------------------------------------------------------------
# Céu (fica atrás de tudo e só aparece pelos buracos e janelas)
# ---------------------------------------------------------------------------


def desenhar_ceu():
    # O céu só aparece pelos buracos e janelas, lá em cima: uma tela basta.
    img = Imagem(LARGURA_CEU, ALTURA_TELA)
    todo = img.ret(0, 0, img.w, img.h)
    # Degradê vertical: mais claro perto do horizonte (embaixo).
    v = 0.25 + 0.7 * (img.Y / 110) + 0.08 * ruido(img.w, img.h, 40, 12, 1)
    img.pintar(todo, "ceu", v)
    # Nuvens: onde o ruído passa de um limite, vira nuvem clara.
    n = ruido(img.w, img.h, 36, 9, 2) * 0.7 + ruido(img.w, img.h, 12, 5, 3) * 0.3
    nuvem = (n > 0.62) & (img.Y < 60)
    img.pintar(nuvem, "ceu", 0.75 + (n - 0.62) * 2)
    # Mata lá longe (azulada) e mais perto (mais escura): dois recortes de
    # "montanha" feitos com senos de frequências diferentes.
    x = img.X
    topo_longe = 62 + 6 * np.sin(x * 0.05) + 4 * np.sin(x * 0.13 + 1) + 3 * np.sin(x * 0.31)
    longe = img.Y >= topo_longe
    img.pintar(longe, "mata_longe", 0.8 - (img.Y - topo_longe) / 40
               + 0.2 * ruido(img.w, img.h, 6, 5, 4))
    topo_perto = 78 + 8 * np.sin(x * 0.037 + 2) + 5 * np.sin(x * 0.11) + 3 * np.sin(x * 0.43 + 3)
    perto = img.Y >= topo_perto
    img.pintar(perto, "mata_perto", 0.85 - (img.Y - topo_perto) / 30
               + 0.25 * ruido(img.w, img.h, 4, 4, 5))
    return img


# ---------------------------------------------------------------------------
# Parede do fundo
# ---------------------------------------------------------------------------

# Fonte de 3x5 pixels para a placa "SILÊNCIO".
FONTE = {
    "S": ["111", "100", "111", "001", "111"],
    "I": ["111", "010", "010", "010", "111"],
    "L": ["100", "100", "100", "100", "111"],
    "E": ["111", "100", "110", "100", "111"],
    "N": ["110", "101", "101", "101", "101"],
    "C": ["111", "100", "100", "100", "111"],
    "O": ["111", "101", "101", "101", "111"],
}


def contorno_buraco(xa, xb, fundo, semente):
    """Polígono serrilhado do buraco: começa no teto (y = -1), desce pela
    borda esquerda, faz um 'U' irregular até 'fundo' e sobe pela direita."""
    rng = np.random.default_rng(semente)
    pts = [(xa, -1)]
    passos = 9
    for i in range(1, passos):
        t = i / passos
        x = xa + (xb - xa) * t
        # Parábola: mais fundo no meio; mais um pouco de sorteio = serrilhado.
        y = fundo * (1 - (2 * t - 1) ** 2) ** 0.6 + rng.integers(-6, 5)
        pts.append((x, max(y, 4)))
    pts.append((xb, -1))
    return pts


def desenhar_fundo():
    # A parede acaba em Y_CHAO: a imagem não precisa descer até a parte sul.
    img = Imagem(LARGURA_SALA, ALTURA_TELA)
    X, Y = img.X, img.Y
    luz = luz_pintada(X, Y)
    parede = img.ret(0, 0, img.w, Y_CHAO)

    # 1. Concreto: manchas grandes + textura fina + escorridos de água.
    manchas = ruido(img.w, img.h, 30, 18, 10)
    fino = ruido(img.w, img.h, 3, 3, 11)
    escorrido = ruido(img.w, img.h, 4, 60, 12)
    v = (0.30 + 0.22 * manchas + 0.08 * fino - 0.18 * (escorrido > 0.7)) * luz
    # Mais escuro perto do chão e perto do teto (oclusão de ambiente: cantos
    # recebem menos luz rebatida).
    v = v - 0.12 * np.clip((Y - 90) / 22, 0, 1) - 0.15 * np.clip((24 - Y) / 14, 0, 1)
    img.pintar(parede, "concreto", v)

    # 2. Placas de concreto: juntas verticais a cada 80 px e uma horizontal.
    junta = parede & ((X % 80 == 0) | (Y == 58)) & (Y > 14) & (Y < 100)
    img.pintar(junta, "concreto", v - 0.2, achatar=False)
    realce = parede & ((X % 80 == 1) | (Y == 59)) & (Y > 14) & (Y < 100)
    img.pintar(realce, "concreto", v + 0.12, achatar=False)

    # 3. Rodapé escuro (faixa de madeira podre) e a linha do teto.
    rodape = img.ret(0, 100, img.w, Y_CHAO)
    img.pintar(rodape, "madeira", 0.22 + 0.1 * fino + 0.1 * (Y == 100) + 0.15 * (luz - 0.5))
    teto = img.ret(0, 0, img.w, 12)
    img.pintar(teto, "concreto", 0.1 + 0.08 * fino + 0.12 * (Y == 11))
    viga = img.ret(0, 12, img.w, 15)
    img.cor(viga, RAMPAS["concreto"][0])

    # 4. Rachaduras: "passeios aleatórios" que descem do teto.
    rng = np.random.default_rng(13)
    for x_ini in (40, 128, 372, 470, 560, 700, 770, 880):
        x, y = float(x_ini), 15.0
        pontos = [(x, y)]
        for _ in range(rng.integers(6, 11)):
            x += rng.uniform(-5, 5)
            y += rng.uniform(4, 9)
            pontos.append((x, y))
        risco = img.caminho(pontos, 0.5) & parede
        img.cor(risco, RAMPAS["concreto"][1])
        # Um pixel claro ao lado da rachadura dá o efeito de "borda quebrada".
        brilho = np.roll(risco, 1, axis=1) & ~risco & parede
        img.pintar(brilho, "concreto", v + 0.15, achatar=False)

    # 5. Estantes embutidas na parede, vazias.
    for (xa, xb) in ((350, 400), (476, 610), (720, 790), (820, 880)):
        desenhar_estante_parede(img, xa, xb, 30, 100, luz)

    # 6. Janelas altas à esquerda (vidro quebrado, a mata aparece atrás).
    for xa in (26, 84):
        desenhar_janela(img, xa, 24, 40, 30)

    # 7. Placa "SILÊNCIO" (regra da Biblioteca e regra do jogo: correr aqui
    #    chama a Bibliotecária).
    desenhar_placa(img, 642, 42, "SILENCIO")

    # 8. Porta de saída no fim da sala (para os Blocos de aula, no futuro).
    desenhar_porta(img, 900, 942, 46)

    # 9. Pilares nas pontas.
    for (xa, xb) in ((0, 18), (942, 960)):
        pilar = img.ret(xa, 0, xb, Y_CHAO)
        lado = (X - xa) / (xb - xa)
        img.pintar(pilar, "concreto", 0.12 + 0.2 * (1 - abs(lado - 0.35)) + 0.05 * fino)

    # 10. Buracos do teto: onde a laje e a parede caíram, apagamos os pixels
    #     (fica transparente e o céu aparece atrás).
    for i, (xa, xb, fundo) in enumerate((BURACO_GRANDE, BURACO_PEQUENO)):
        buraco = img.poligono(contorno_buraco(xa, xb, fundo, 20 + i))
        borda = dilatar(buraco, 2) & ~buraco
        # Borda quebrada do concreto: a de cima, que recebe sol, fica clara.
        img.pintar(borda, "concreto", 0.62 + 0.15 * fino)
        img.cor(dilatar(buraco, 3) & ~dilatar(buraco, 2), RAMPAS["concreto"][2])
        img.apagar(buraco)
        # Vergalhões enferrujados saindo da borda.
        rng = np.random.default_rng(30 + i)
        for _ in range(5 if i == 0 else 3):
            x0 = rng.uniform(xa + 6, xb - 6)
            coluna = buraco[:, int(x0)]
            y0 = int(np.nonzero(coluna)[0].max()) + 2 if coluna.any() else 12
            ferro = img.linha(x0, y0, x0 + rng.uniform(-8, 8), y0 - rng.uniform(6, 14), 0.5)
            img.cor(ferro, RAMPAS["ferrugem"][3])
        # Musgo e mato crescendo na borda (sol + água da chuva).
        perto = dilatar(buraco, 7) & ~dilatar(buraco, 2) & parede
        musgo = perto & (ruido(img.w, img.h, 5, 4, 40 + i) > 0.45)
        img.pintar(musgo, "verde", 0.35 + 0.5 * fino)

    # 11. Cipós descendo da borda dos buracos pela parede.
    rng = np.random.default_rng(50)
    for x0 in list(range(154, 336, 17)) + list(range(610, 672, 15)):
        x0 += rng.integers(-3, 4)
        comp = rng.integers(20, 70)
        pontos = [(x0 + 1.5 * np.sin(k * 0.8), 8 + k * comp / 8) for k in range(9)]
        cipo = img.caminho(pontos, 0.6) & ~img.poligono(contorno_buraco(*BURACO_GRANDE, 20))
        img.pintar(cipo, "verde", 0.35 + 0.3 * fino)
        folhas = dilatar(cipo) & (fino > 0.72) & parede
        img.pintar(folhas, "verde", 0.55 + 0.3 * fino)

    # 12. Fungos na parede do lado escuro: tufos pequenos, perto do chão e
    #     das rachaduras (onde a umidade fica).
    for (cx, cy) in ((752, 98), (764, 94), (870, 72), (926, 98), (934, 104), (60, 99)):
        colar_fungos(img, cx, cy, cx + cy)

    # Tudo que está abaixo de Y_CHAO fica para a camada do chão.
    img.apagar(img.Y >= Y_CHAO)
    return img


def desenhar_estante_parede(img, xa, xb, ya, yb, luz):
    X, Y = img.X, img.Y
    fino = ruido(img.w, img.h, 2, 2, xa)
    caixa = img.ret(xa, ya, xb, yb)
    img.pintar(caixa, "madeira", 0.08 + 0.05 * fino)          # fundo, na sombra
    # Sombra embaixo de cada prateleira (a de cima tapa a luz).
    for y in range(ya + 3, yb, 14):
        sombra = img.ret(xa, y, xb, y + 4)
        img.pintar(sombra, "madeira", 0.0)
    moldura = caixa & ~img.ret(xa + 3, ya + 3, xb - 3, yb)
    img.pintar(moldura, "madeira", (0.35 + 0.1 * fino) * luz * 1.3)
    rng = np.random.default_rng(xa)
    for y in range(ya + 14, yb, 14):
        tabua = img.ret(xa + 3, y, xb - 3, y + 2)
        img.pintar(tabua, "madeira", (0.45 + 0.1 * fino) * luz * 1.3)
        img.pintar(img.ret(xa + 3, y, xb - 3, y + 1), "madeira", 0.6 * luz * 1.3)
        # Poucos livros que sobraram, caídos e inclinados.
        x = xa + 4 + rng.integers(0, 10)
        while x < xb - 8:
            if rng.random() < 0.25:
                alt = rng.integers(7, 11)
                larg = rng.integers(2, 4)
                rampa = ["livro_vermelho", "livro_azul", "livro_ocre"][rng.integers(0, 3)]
                if rng.random() < 0.5:
                    lombada = img.ret(x, y - alt, x + larg, y)
                else:  # deitado
                    lombada = img.ret(x, y - larg, x + alt, y)
                img.pintar(lombada, rampa, 0.35 + 0.4 * fino)
                x += alt
            x += rng.integers(3, 12)
    # Uma tábua quebrada, caída na diagonal.
    meio = (xa + xb) // 2
    img.pintar(img.linha(meio - 12, ya + 30, meio + 10, ya + 40, 1.0), "madeira", 0.4 * luz * 1.3)


def desenhar_janela(img, xa, ya, larg, alt):
    X, Y = img.X, img.Y
    fino = ruido(img.w, img.h, 2, 2, xa + 7)
    moldura = img.ret(xa - 2, ya - 2, xa + larg + 2, ya + alt + 3)
    img.pintar(moldura, "concreto", 0.5 + 0.1 * fino)
    img.pintar(img.ret(xa - 3, ya + alt + 1, xa + larg + 3, ya + alt + 3), "concreto", 0.62)
    vao = img.ret(xa, ya, xa + larg, ya + alt)
    img.apagar(vao)
    # Caixilho em cruz (metal) e cacos de vidro presos nos cantos.
    caixilho = vao & ((X == xa + larg // 2) | (Y == ya + alt // 2))
    img.pintar(caixilho, "metal", 0.2)
    cacos = vao & (img.poligono([(xa, ya), (xa + 9, ya), (xa, ya + 7)])
                   | img.poligono([(xa + larg, ya + alt), (xa + larg - 11, ya + alt),
                                   (xa + larg, ya + alt - 6)]))
    img.pintar(cacos, "ceu", 0.15 + 0.5 * (fino > 0.6))
    # Trepadeira entrando pela janela.
    folhas = img.ret(xa - 3, ya - 3, xa + larg + 3, ya + 12) & (ruido(img.w, img.h, 3, 3, xa) > 0.55)
    img.pintar(folhas, "verde", 0.2 + 0.4 * fino)


def desenhar_placa(img, x, y, texto):
    larg = 4 * len(texto) + 5
    img.pintar(img.ret(x - 1, y - 1, x + larg + 1, y + 11), "madeira", 0.1)
    img.pintar(img.ret(x, y, x + larg, y + 10), "madeira", 0.3)
    for i, letra in enumerate(texto):
        for j, linha in enumerate(FONTE[letra]):
            for k, ch in enumerate(linha):
                if ch == "1":
                    img.cor(img.ret(x + 3 + 4 * i + k, y + 3 + j, x + 4 + 4 * i + k, y + 4 + j),
                            RAMPAS["papel"][2])
    # Acento circunflexo do Ê (quarta letra).
    xe = x + 3 + 4 * 3
    for (dx, dy) in ((0, 2), (1, 1), (2, 2)):
        img.cor(img.ret(xe + dx, y + dy, xe + dx + 1, y + dy + 1), RAMPAS["papel"][1])
    # Musgo comendo o canto da placa.
    musgo = img.elipse(x + larg, y + 9, 6, 4) & (ruido(img.w, img.h, 2, 2, 77) > 0.4)
    img.pintar(musgo, "verde", 0.3)


def desenhar_porta(img, xa, xb, ya):
    X, Y = img.X, img.Y
    batente = img.ret(xa - 3, ya - 3, xb + 3, Y_CHAO)
    img.pintar(batente, "concreto", 0.3 + 0.05 * ruido(img.w, img.h, 2, 2, 90))
    vao = img.ret(xa, ya, xb, Y_CHAO)
    # O corredor do outro lado: escuro, com um fundo levemente visível.
    prof = (Y - ya) / (Y_CHAO - ya)
    img.pintar(vao, "concreto", 0.02 + 0.08 * prof)
    img.cor(img.ret(xa, ya, xb, ya + 3), SOMBRA)
    # Uma folha da porta caída, encostada no batente.
    folha = img.poligono([(xb - 2, ya + 4), (xb + 6, ya + 2), (xb + 10, Y_CHAO), (xb, Y_CHAO)])
    img.pintar(folha, "madeira", 0.25 + 0.1 * (X == xb + 6))


# ---------------------------------------------------------------------------
# Chão (a faixa onde o Gabriel anda)
# ---------------------------------------------------------------------------

# Onde começa cada fileira de lajotas. A distância entre as linhas cresce
# para baixo (3, 4, 5, 6... px): é a perspectiva — o que está longe (em cima)
# fica achatado, o que está perto (embaixo) fica maior. Na parte sul ela
# para de crescer em 16 px, senão as lajotas da frente ficariam enormes.
FILEIRAS = [112, 115, 119, 124, 130, 137, 145, 154, 164, 175, 188,
            202, 217, 233, 249, 265, 281, 297, 313]


def desenhar_chao():
    img = Imagem(LARGURA_SALA, ALTURA_SALA)
    X, Y = img.X, img.Y
    luz = luz_pintada(X, Y)
    chao = img.ret(0, Y_CHAO, img.w, img.h)
    fino = ruido(img.w, img.h, 2, 2, 60)
    manchas = ruido(img.w, img.h, 24, 10, 61)
    rng = np.random.default_rng(62)

    # 1. Lajotas: cada uma tem um tom próprio (sorteado) e o valor cai para
    #    perto da parede (sombra do canto).
    valor = np.zeros((img.h, img.w))
    junta = np.zeros((img.h, img.w), dtype=bool)
    for i in range(len(FILEIRAS) - 1):
        ya, yb = FILEIRAS[i], FILEIRAS[i + 1]
        larg = 32
        desloc = (i % 2) * 16                  # fileiras desencontradas
        faixa = (Y >= ya) & (Y < yb)
        coluna = (X + desloc) // larg
        sorteio = np.random.default_rng(100 + i).random(img.w // larg + 3)
        valor[faixa] = (0.35 + 0.18 * sorteio[coluna])[faixa]
        junta |= faixa & ((Y == ya) | ((X + desloc) % larg == 0))
    valor = valor + 0.1 * manchas + 0.05 * fino
    # Escurece no canto com a parede e, de leve, na beira da frente (a
    # parte sul fica longe dos buracos do teto).
    valor = valor * luz - 0.2 * np.clip((122 - Y) / 10, 0, 1)         - 0.08 * np.clip((Y - 240) / 60, 0, 1)
    img.pintar(chao, "piso", valor)
    img.pintar(chao & junta, "piso", valor - 0.22, achatar=False)

    # 2. Tapete podre embaixo da área das mesas de leitura.
    tapete = img.poligono([(500, 132), (660, 132), (668, 172), (492, 172)])         | img.poligono([(96, 206), (246, 206), (256, 258), (86, 258)])   # parte sul
    buracos = ruido(img.w, img.h, 6, 4, 63) > 0.66
    img.pintar(tapete & ~buracos, "tapete", (0.45 + 0.25 * manchas + 0.1 * fino) * luz)
    img.pintar(tapete & ~buracos & ((X + Y) % 6 == 0), "tapete", 0.25 * luz, achatar=False)

    # 3. Lajotas faltando: terra aparecendo.
    for _ in range(60):
        x = rng.integers(20, 940)
        y = rng.integers(118, ALTURA_SALA - 4)
        buraco = img.elipse(x, y, rng.uniform(4, 10), rng.uniform(2, 4)) & chao
        img.pintar(buraco, "areia", (0.2 + 0.15 * fino) * luz)

    # 4. Areia e terra que caíram pelo buraco grande (e um pouco pelo
    #    pequeno), em montinhos com a borda irregular.
    #    Na parte sul, a areia cai onde o sol do buraco grande chega (o raio
    #    anda para a direita enquanto desce).
    for (cx, cy, rx, ry) in ((250, 128, 90, 12), (300, 150, 60, 9), (660, 130, 40, 7),
                             (190, 160, 40, 6), (370, 238, 80, 12), (430, 272, 50, 8),
                             (770, 250, 34, 6)):
        monte = img.elipse(cx, cy, rx, ry) & (manchas + 0.3 * fino > 0.45) & chao
        img.pintar(monte, "areia", (0.45 + 0.35 * fino) * luz)

    # 5. Raízes da árvore se espalhando pelo chão.
    xa, ya = 238, 138
    for (dx, dy, curva) in ((-70, 10, 6), (-40, 30, -4), (-95, -14, 4), (60, 22, -5),
                            (95, 4, 3), (30, 36, 4), (-20, -18, 2),
                            (70, 110, -6), (-10, 90, 5)):   # duas raízes longas para o sul
        pontos = [(xa + dx * t + curva * np.sin(t * 6), ya + dy * t + 2 * np.sin(t * 9))
                  for t in np.linspace(0, 1, 12)]
        grossa = img.caminho(pontos[:6], 2.2) | img.caminho(pontos[5:], 1.3)
        grossa &= chao
        img.cor(dilatar(grossa) & chao & ~grossa, RAMPAS["casca"][0])
        img.pintar(grossa, "casca", (0.45 + 0.3 * fino) * luz)
        topo = grossa & ~np.roll(grossa, 1, axis=0)
        img.pintar(topo, "casca", 0.75 * luz, achatar=False)

    # 6. Mato nas partes com sol: tufos de 1 px de largura e 2 a 5 de altura.
    x_teto = X - 0.5 * Y
    no_sol = ((x_teto > BURACO_GRANDE[0] - 10) & (x_teto < BURACO_GRANDE[1] + 10)) | \
             ((x_teto > BURACO_PEQUENO[0]) & (x_teto < BURACO_PEQUENO[1]))
    # Quantidade proporcional ao tamanho do chão (420 para os 68 px da tela).
    for _ in range(420 * (ALTURA_SALA - Y_CHAO) // 68):
        x = int(rng.integers(0, img.w))
        y = int(rng.integers(Y_CHAO + 3, img.h))
        if not no_sol[y, x] and rng.random() > 0.08:
            continue
        altura = int(rng.integers(2, 6))
        folha = img.ret(x, y - altura, x + 1, y + 1)
        img.pintar(folha, "verde", 0.4 + 0.45 * rng.random())
        img.pintar(img.ret(x, y - altura, x + 1, y - altura + 1), "verde", 0.85)

    # 7. Folhas secas espalhadas.
    for _ in range(160 * (ALTURA_SALA - Y_CHAO) // 68):
        x = int(rng.integers(0, img.w))
        y = int(rng.integers(Y_CHAO + 2, img.h))
        rampa = "areia" if rng.random() < 0.6 else "ferrugem"
        img.pintar(img.ret(x, y, x + 2, y + 1), rampa, 0.5 + 0.3 * rng.random())

    # 8. Musgo e fungos no chão do lado escuro.
    musgo = chao & (X > 740) & (ruido(img.w, img.h, 7, 4, 64) > 0.68)
    img.pintar(musgo, "verde", 0.15 + 0.2 * fino)
    for (cx, cy) in ((786, 150), (884, 130), (934, 162), (822, 174),
                     (700, 250), (910, 240)):
        colar_fungos(img, cx, cy, cx)

    # 9. Sombras de contato: embaixo de cada objeto, uma elipse escura.
    #    É o que "cola" o objeto no chão (sem ela, parece flutuar).
    for nome, x, y, _ in OBJETOS:
        larg = LARGURA_SOMBRA.get(nome, 0)
        if larg:
            s = img.elipse(x, y - 2, larg / 2, 4) & chao
            img.cor(s & ((X + Y) % 2 == 0), SOMBRA)
            img.cor(img.elipse(x, y - 2, larg / 2 - 3, 2.5) & chao, SOMBRA)

    # 10. Pé da parede: sombra de 2 px e linha de terra acumulada.
    img.cor(img.ret(0, Y_CHAO, img.w, Y_CHAO + 1), SOMBRA)
    acumulo = img.ret(0, Y_CHAO + 1, img.w, Y_CHAO + 3) & (manchas > 0.4)
    img.pintar(acumulo, "areia", 0.25 * luz)
    return img


LARGURA_SOMBRA = {
    "cabine": 76, "cadeira": 18, "arvore": 60, "entulho": 40, "estante_caida": 92,
    "estante_vazia": 70, "livros": 26, "mesa_leitura": 90, "carrinho": 38,
    "estante_quebrada": 70, "fungo": 0,
}


# ---------------------------------------------------------------------------
# Objetos (y-sort). Cada função devolve (imagem, x_do_pe, y_do_pe) em
# coordenadas da própria imagem. No Godot, o Sprite2D fica com
# offset = (-x_do_pe, -y_do_pe), para o nó ficar exatamente no pé.
# ---------------------------------------------------------------------------


def madeira(img, mascara, base, semente, veio=True):
    """Madeira: tom base + manchas + veios horizontais (ruído esticado)."""
    fino = ruido(img.w, img.h, 2, 2, semente)
    veios = ruido(img.w, img.h, 14, 1.5, semente + 1)
    v = base + 0.08 * fino + (0.1 * (veios - 0.5) if veio else 0)
    img.pintar(mascara, "madeira", v)


def musgo_por_cima(img, forca=0.5, semente=0):
    """Musgo nos pixels de cima (onde cai poeira, água e luz)."""
    a = img.opaco()
    topo = a & ~np.roll(a, 1, axis=0)
    perto = dilatar(topo, 1) & a
    m = perto & (ruido(img.w, img.h, 3, 2, semente) > 1 - forca)
    img.pintar(m, "verde", 0.3 + 0.4 * ruido(img.w, img.h, 2, 2, semente + 1))


def estante(larg=66, alt=80, prof=8, semente=0, quebrada=False):
    img = Imagem(larg + 2, alt + prof + 2)
    x0, y0 = 1, 1 + prof            # canto de cima da face da frente
    frente = img.ret(x0, y0, x0 + larg, y0 + alt)
    topo = img.ret(x0, 1, x0 + larg, y0)
    madeira(img, topo, 0.62, semente)
    madeira(img, frente, 0.42, semente + 2)
    # Vãos das prateleiras (escuros, com sombra embaixo de cada tábua).
    rng = np.random.default_rng(semente)
    n_prat = 5
    alt_vao = (alt - 6) // n_prat
    for i in range(n_prat):
        ya = y0 + 3 + i * alt_vao
        for (xa, xb) in ((x0 + 3, x0 + larg // 2 - 1), (x0 + larg // 2 + 1, x0 + larg - 3)):
            vao = img.ret(xa, ya, xb, ya + alt_vao - 2)
            img.pintar(vao, "madeira", 0.1 + 0.12 * (img.Y - ya) / alt_vao)
            img.cor(img.ret(xa, ya, xb, ya + 2), RAMPAS["madeira"][0])
            # Livros esquecidos (a Bibliotecária arruma estantes vazias...).
            x = xa + 1
            while x < xb - 3:
                if rng.random() < 0.18:
                    a = int(rng.integers(6, alt_vao - 3))
                    l = int(rng.integers(2, 4))
                    rampa = ["livro_vermelho", "livro_azul", "livro_ocre"][rng.integers(0, 3)]
                    base_y = ya + alt_vao - 2
                    if rng.random() < 0.6:
                        livro = img.ret(x, base_y - a, x + l, base_y)
                    else:
                        livro = img.poligono([(x, base_y), (x + l, base_y), (x + l + a * 0.6, base_y - a),
                                              (x + a * 0.6, base_y - a)])
                    img.pintar(livro, rampa, 0.3 + 0.6 * ruido(img.w, img.h, 1.5, 3, int(x)))
                    x += l + 2
                x += int(rng.integers(2, 7))
            # Poeira acumulada na tábua (linha clara).
            img.pintar(img.ret(xa, ya + alt_vao - 2, xb, ya + alt_vao - 1), "madeira", 0.7)
    # Divisória do meio e rodapé.
    img.pintar(img.ret(x0 + larg // 2 - 1, y0, x0 + larg // 2 + 1, y0 + alt), "madeira", 0.5)
    img.pintar(img.ret(x0, y0 + alt - 4, x0 + larg, y0 + alt), "madeira", 0.28)
    # Quina iluminada (luz de cima-esquerda) e lado direito na sombra.
    img.pintar(img.ret(x0, y0, x0 + larg, y0 + 1), "madeira", 0.78)
    img.pintar(img.ret(x0, y0, x0 + 1, y0 + alt), "madeira", 0.6)
    img.pintar(img.ret(x0 + larg - 2, y0, x0 + larg, y0 + alt), "madeira", 0.2)
    if quebrada:
        # Pedaço de cima-direita arrancado (borda serrilhada).
        pts = [(x0 + larg * 0.45, 0), (x0 + larg + 2, 0), (x0 + larg + 2, y0 + alt * 0.55)]
        for k in range(7):
            t = k / 6
            pts.append((x0 + larg - t * larg * 0.55 + (k % 2) * 4, y0 + alt * 0.55 * (1 - t) + (k % 2) * 5))
        img.apagar(img.poligono(pts))
        # Tábua solta pendurada na diagonal.
        img.pintar(img.linha(x0 + 34, y0 + 26, x0 + 58, y0 + 44, 1.1), "madeira", 0.5)
        # Fungos crescendo na madeira úmida.
        for (cx, cy) in ((x0 + 12, y0 + 60), (x0 + 40, y0 + 70), (x0 + 22, y0 + 34),
                         (x0 + 50, y0 + 58)):
            colar_fungos(img, cx, cy, semente + cx)
    musgo_por_cima(img, 0.55, semente + 5)
    img.contornar()
    return img, x0 + larg // 2, y0 + alt


def colar_fungos(img, cx, cy, semente):
    """Tufo de cogumelos pequenos brilhantes: chapéu claro, borda escura."""
    rng = np.random.default_rng(semente)
    for _ in range(3):
        x = cx + rng.integers(-4, 5)
        y = cy + rng.integers(-2, 3)
        r = rng.integers(1, 3)
        img.pintar(img.ret(x, y, x + 1, y + 2), "fungo", 0.45)
        chapeu = img.elipse(x + 0.5, y, r + 0.6, r * 0.7 + 0.3)
        img.pintar(chapeu, "fungo", 0.75)
        img.cor(img.ret(x, y - 1, x + 1, y), RAMPAS["fungo"][5])


def estante_caida():
    """Estante tombada de costas: vemos os vãos de cima (achatados) e a
    lateral de frente para nós."""
    larg, prof, alt = 92, 14, 12
    img = Imagem(larg + 2, prof + alt + 2)
    x0, y0 = 1, 1
    topo = img.ret(x0, y0, x0 + larg, y0 + prof)
    madeira(img, topo, 0.5, 70)
    for i in range(6):
        xa = x0 + 3 + i * 15
        vao = img.ret(xa, y0 + 2, xa + 12, y0 + prof - 2)
        img.pintar(vao, "madeira", 0.08 + 0.1 * (img.Y - y0) / prof)
    frente = img.ret(x0, y0 + prof, x0 + larg, y0 + prof + alt)
    madeira(img, frente, 0.34, 71)
    img.pintar(img.ret(x0, y0 + prof, x0 + larg, y0 + prof + 1), "madeira", 0.62)
    # Uma ponta quebrada e livros espalhados no vão.
    img.apagar(img.poligono([(x0 + larg - 12, 0), (x0 + larg + 2, 0), (x0 + larg + 2, 12)]))
    img.pintar(img.ret(x0 + 20, y0 + 5, x0 + 28, y0 + 8), "livro_vermelho", 0.6)
    img.pintar(img.ret(x0 + 50, y0 + 6, x0 + 55, y0 + 9), "livro_azul", 0.7)
    musgo_por_cima(img, 0.5, 72)
    img.contornar()
    return img, x0 + larg // 2, y0 + prof + alt


def cabine():
    """A cabine de estudo onde o Gabriel dormiu: mesa, divisórias de tecido
    verde (como na cutscene), o monitor morto com planta em cima, livros e a
    caneca. É a mesma cabine do menu e da cutscene, mil anos depois."""
    larg, alt = 78, 66
    img = Imagem(larg + 2, alt + 2)
    X, Y = img.X, img.Y
    x0 = 1
    y_mesa = 40                       # topo da face de cima da mesa
    # Painel do fundo (divisória de tecido) e as laterais.
    painel = img.ret(x0 + 4, 4, x0 + larg - 4, y_mesa + 2)
    img.pintar(painel, "tecido", 0.45 + 0.35 * ruido(img.w, img.h, 6, 4, 80)
               + 0.15 * ((X + Y) % 3 == 0))
    img.pintar(img.ret(x0 + 4, 3, x0 + larg - 4, 5), "metal", 0.6)
    for xa in (x0, x0 + larg - 5):
        lateral = img.ret(xa, 2, xa + 5, alt)
        img.pintar(lateral, "tecido", 0.3 + 0.2 * (X == xa + 1))
        img.pintar(img.ret(xa, 1, xa + 5, 3), "metal", 0.7)
    # Mesa: tampo (visto de cima) e a borda da frente.
    tampo = img.ret(x0 + 5, y_mesa, x0 + larg - 5, y_mesa + 9)
    madeira(img, tampo, 0.55, 81)
    borda = img.ret(x0 + 5, y_mesa + 9, x0 + larg - 5, y_mesa + 13)
    madeira(img, borda, 0.32, 82)
    img.pintar(img.ret(x0 + 5, y_mesa + 9, x0 + larg - 5, y_mesa + 10), "madeira", 0.6)
    # Embaixo da mesa: escuro, com o painel de pernas.
    baixo = img.ret(x0 + 5, y_mesa + 13, x0 + larg - 5, alt)
    img.pintar(baixo, "madeira", 0.03 + 0.05 * (Y - y_mesa - 13) / 12)
    for xa in (x0 + 6, x0 + larg - 10):
        img.pintar(img.ret(xa, y_mesa + 13, xa + 4, alt), "madeira", 0.3)
    # Monitor morto (tubo), com uma plantinha crescendo em cima.
    mx, my = x0 + 26, y_mesa - 14
    img.pintar(img.ret(mx, my, mx + 20, my + 16), "metal", 0.35)
    img.pintar(img.ret(mx + 2, my + 2, mx + 18, my + 13), "metal", 0.08)
    img.pintar(img.linha(mx + 5, my + 3, mx + 13, my + 11, 0.5), "metal", 0.3)  # tela trincada
    img.pintar(img.ret(mx + 2, my + 2, mx + 5, my + 3), "metal", 0.5)           # reflexo
    img.pintar(img.ret(mx + 7, my + 16, mx + 13, y_mesa + 3), "metal", 0.25)    # pé
    planta = img.elipse(mx + 10, my - 2, 9, 3.5) & (ruido(img.w, img.h, 2, 2, 83) > 0.3)
    img.pintar(planta, "verde", 0.45 + 0.4 * ruido(img.w, img.h, 2, 2, 84))
    # Teclado, livros empilhados e a caneca.
    img.pintar(img.ret(mx - 1, y_mesa + 4, mx + 21, y_mesa + 6), "metal", 0.45)
    for i, rampa in enumerate(("livro_azul", "livro_vermelho", "livro_ocre")):
        yl = y_mesa + 2 - 3 * i
        img.pintar(img.ret(x0 + 9 + i, yl, x0 + 22 - i, yl + 3), rampa, 0.55)
        img.pintar(img.ret(x0 + 9 + i, yl, x0 + 22 - i, yl + 1), "papel", 0.6)
    cx = x0 + 56
    img.pintar(img.ret(cx, y_mesa - 1, cx + 5, y_mesa + 5), "papel", 0.75)
    img.pintar(img.ret(cx + 5, y_mesa + 1, cx + 7, y_mesa + 3), "papel", 0.5)
    img.pintar(img.ret(cx + 1, y_mesa - 1, cx + 4, y_mesa), "madeira", 0.1)
    # Folhas de papel podres espalhadas no tampo.
    img.pintar(img.poligono([(x0 + 48, y_mesa + 5), (x0 + 58, y_mesa + 4), (x0 + 60, y_mesa + 8),
                             (x0 + 49, y_mesa + 9)]), "papel", 0.5)
    musgo_por_cima(img, 0.45, 85)
    img.contornar()
    return img, x0 + larg // 2, alt


def cadeira():
    """A cadeira do Gabriel, empurrada para trás quando ele levantou."""
    img = Imagem(22, 30)
    x0 = 3
    encosto = img.ret(x0 + 11, 2, x0 + 15, 17)
    madeira(img, encosto, 0.45, 90)
    img.pintar(img.ret(x0 + 11, 2, x0 + 15, 3), "madeira", 0.7)
    assento = img.ret(x0, 15, x0 + 15, 19)
    madeira(img, assento, 0.55, 91)
    img.pintar(img.ret(x0, 15, x0 + 15, 16), "madeira", 0.72)
    for xa in (x0 + 1, x0 + 12):
        img.pintar(img.ret(xa, 19, xa + 2, 29), "madeira", 0.3)
    img.contornar()
    return img, 11, 29


def arvore():
    """A árvore que cresceu onde ficava a cabine vizinha à do Gabriel.
    O tronco é desenhado linha por linha: para cada altura y, calculamos o
    centro e a largura; dentro do tronco, a posição horizontal t (de -1 na
    borda esquerda a +1 na direita) decide o tom: a luz vem de cima e da
    esquerda (do buraco no teto), então o lado esquerdo é mais claro."""
    larg, alt = 120, 158
    img = Imagem(larg, alt)
    X, Y = img.X, img.Y
    base = alt - 4                     # linha do pé
    y_rel = (base - Y) / base          # 0 no pé, 1 no alto
    centro = 60 + 3 * np.sin(Y / 23.0) - 6 * np.clip(y_rel - 0.6, 0, 1)
    meia = 13 + 16 * np.clip(1 - y_rel * 6, 0, 1) ** 2 - 3 * y_rel
    t = (X + 0.5 - centro) / meia
    tronco = (np.abs(t) <= 1) & (Y <= base)
    # Galhos subindo para fora do buraco do teto.
    galho1 = img.caminho([(56, 50), (44, 30), (30, 12), (24, -2)], 6)
    galho2 = img.caminho([(62, 44), (74, 26), (86, 10), (96, -2)], 5)
    galho3 = img.caminho([(60, 30), (58, 10), (60, -2)], 4)
    galhos = (galho1 | galho2 | galho3) & (Y < 60)
    # Raízes que abraçam o chão.
    raizes = img.caminho([(58, base - 8), (36, base - 2), (18, base + 1)], 4) | \
        img.caminho([(64, base - 8), (84, base - 1), (104, base + 2)], 4) | \
        img.caminho([(60, base - 6), (58, base + 2)], 6)
    forma = tronco | galhos | raizes
    sulcos = ruido(img.w, img.h, 2.2, 18, 95)       # listras verticais da casca
    fino = ruido(img.w, img.h, 2, 2, 96)
    lado = np.where(tronco, -t, (60 - X) / 30.0)
    v = 0.42 + 0.28 * lado + 0.22 * (sulcos - 0.5) + 0.06 * fino
    v = v - 0.2 * np.clip((Y - base + 10) / 10, 0, 1)   # pé na sombra
    img.pintar(forma, "casca", v)
    # Frestas fundas na casca.
    img.pintar(forma & (sulcos < 0.22), "casca", 0.08, achatar=False)
    # Hera subindo pelo lado iluminado, musgo e orelhas-de-pau.
    hera = forma & (lado > 0.1) & (ruido(img.w, img.h, 3, 6, 97) > 0.62) & (Y > 40)
    img.pintar(hera, "verde", 0.35 + 0.45 * fino)
    for (cx, cy, r) in ((50, 92, 6), (71, 112, 5), (47, 128, 4)):
        orelha = img.elipse(cx, cy, r, r * 0.45) & (Y <= cy)
        img.pintar(orelha, "areia", 0.55 + 0.35 * (Y == cy - int(r * 0.45)))
        img.cor(img.ret(cx - r + 1, cy, cx + r, cy + 1), RAMPAS["casca"][1])
    img.contornar()
    # O contorno não pode aparecer onde a árvore sai pelo alto da imagem.
    return img, 60, base


def mesa_leitura():
    larg, prof, borda = 90, 11, 4
    img = Imagem(larg + 26, 42)
    X, Y = img.X, img.Y
    x0, y0 = 4, 12
    # Cadeira do outro lado da mesa: só o encosto aparece por cima.
    encosto = img.ret(x0 + 56, 2, x0 + 70, y0 + 1)
    madeira(img, encosto, 0.4, 100)
    img.pintar(img.ret(x0 + 56, 2, x0 + 70, 3), "madeira", 0.68)
    tampo = img.ret(x0, y0, x0 + larg, y0 + prof)
    madeira(img, tampo, 0.5, 101)
    img.pintar(img.ret(x0, y0, x0 + larg, y0 + 1), "madeira", 0.68)
    frente = img.ret(x0, y0 + prof, x0 + larg, y0 + prof + borda)
    madeira(img, frente, 0.3, 102)
    img.pintar(img.ret(x0, y0 + prof, x0 + larg, y0 + prof + 1), "madeira", 0.58)
    baixo = img.ret(x0 + 2, y0 + prof + borda, x0 + larg - 2, 40)
    img.pintar(baixo, "madeira", 0.02)
    img.apagar(baixo & (Y > y0 + prof + borda + 3))      # vão livre embaixo
    for xa in (x0 + 2, x0 + larg - 6):
        img.pintar(img.ret(xa, y0 + prof + borda, xa + 4, 40), "madeira", 0.28)
    # Luminária de mesa (cúpula verde de biblioteca), tombada.
    img.pintar(img.ret(x0 + 14, y0 + 3, x0 + 16, y0 + 7), "metal", 0.4)
    cupula = img.poligono([(x0 + 8, y0 + 1), (x0 + 22, y0 - 2), (x0 + 24, y0 + 3), (x0 + 10, y0 + 5)])
    img.pintar(cupula, "verde", 0.55 + 0.2 * (Y <= y0))
    # Livros abertos, podres, e folhas soltas.
    livro = img.poligono([(x0 + 38, y0 + 3), (x0 + 50, y0 + 2), (x0 + 52, y0 + 7), (x0 + 39, y0 + 8)])
    img.pintar(livro, "papel", 0.45 + 0.3 * ruido(img.w, img.h, 2, 2, 103))
    img.pintar(img.linha(x0 + 44, y0 + 2.5, x0 + 45, y0 + 7.5, 0.5), "papel", 0.1)
    img.pintar(img.ret(x0 + 70, y0 + 4, x0 + 80, y0 + 7), "livro_azul", 0.6)
    # Cadeira caída no chão, na frente-direita da mesa.
    cx = x0 + larg + 2
    img.pintar(img.ret(cx - 6, 34, cx + 18, 38), "madeira", 0.42)
    img.pintar(img.ret(cx - 6, 34, cx + 18, 35), "madeira", 0.65)
    img.pintar(img.ret(cx + 14, 24, cx + 18, 34), "madeira", 0.36)
    img.pintar(img.linha(cx, 33, cx - 4, 26, 0.9), "madeira", 0.3)
    musgo_por_cima(img, 0.35, 104)
    img.contornar()
    return img, x0 + larg // 2, 40


def carrinho():
    """Carrinho de devolver livros. Alguém ainda empurra ele por aí..."""
    img = Imagem(44, 40)
    x0 = 3
    X, Y = img.X, img.Y
    # Estrutura de metal enferrujado.
    for xa in (x0 + 1, x0 + 34):
        img.pintar(img.ret(xa, 4, xa + 2, 34), "ferrugem", 0.5 + 0.2 * (xa == x0 + 1))
    img.pintar(img.linha(x0 - 1, 4, x0 + 4, 0, 0.7), "metal", 0.5)   # alça
    for y in (12, 24, 32):
        img.pintar(img.ret(x0, y, x0 + 37, y + 2), "metal", 0.45)
        img.pintar(img.ret(x0, y, x0 + 37, y + 1), "metal", 0.7)
    # Livros em pé e deitados nas prateleiras.
    rng = np.random.default_rng(110)
    for y in (12, 24):
        x = x0 + 4
        while x < x0 + 32:
            a = int(rng.integers(5, 9))
            rampa = ["livro_vermelho", "livro_azul", "livro_ocre", "papel"][rng.integers(0, 4)]
            img.pintar(img.ret(x, y - a, x + 2, y), rampa, 0.35 + 0.4 * rng.random())
            x += int(rng.integers(2, 6))
    # Rodinhas.
    for xa in (x0 + 2, x0 + 33):
        img.pintar(img.elipse(xa + 0.5, 36, 2.2, 2.2), "metal", 0.25)
    img.contornar()
    return img, x0 + 18, 38


def livros():
    """Pilha de livros podres: lombadas de cores diferentes, páginas
    inchadas de umidade (tom de papel) e um pouco de musgo."""
    img = Imagem(30, 18)
    rng = np.random.default_rng(120)
    y = 16
    for i in range(4):
        l = int(rng.integers(14, 22))
        x = 3 + int(rng.integers(0, 6))
        rampa = ["livro_vermelho", "livro_azul", "livro_ocre", "livro_vermelho"][i]
        img.pintar(img.ret(x, y - 3, x + l, y), rampa, 0.5)
        img.pintar(img.ret(x + 2, y - 3, x + l - 1, y - 2), "papel", 0.55)
        y -= 3
    img.pintar(img.poligono([(18, 16), (27, 13), (28, 16)]), "papel", 0.4)   # livro aberto no chão
    musgo_por_cima(img, 0.4, 121)
    img.contornar()
    return img, 14, 16


def entulho():
    """Pedaços da laje que caíram: blocos de concreto com vergalhões."""
    img = Imagem(46, 26)
    fino = ruido(img.w, img.h, 2, 2, 130)
    blocos = [
        ([(3, 24), (5, 12), (16, 8), (22, 14), (20, 24)], 0.55),
        ([(16, 24), (20, 13), (32, 10), (40, 16), (42, 24)], 0.45),
        ([(12, 12), (18, 3), (28, 5), (26, 12), (18, 14)], 0.62),
    ]
    for pts, tom in blocos:
        m = img.poligono(pts)
        # Face de cima (mais clara) = pixels que não têm nada do mesmo bloco acima.
        cima = m & ~np.roll(m, 2, axis=0)
        img.pintar(m, "concreto", tom + 0.1 * fino - 0.15 * (img.X > pts[2][0]))
        img.pintar(cima, "concreto", tom + 0.2, achatar=False)
    for (a, b) in (((26, 6), (34, 0)), ((38, 14), (44, 8)), ((8, 12), (4, 5))):
        img.pintar(img.linha(a[0], a[1], b[0], b[1], 0.6), "ferrugem", 0.6)
    musgo_por_cima(img, 0.35, 131)
    img.contornar()
    return img, 23, 24


def fungo():
    """Tufo de fungos bioluminescentes no chão. O brilho de verdade vem de
    uma PointLight2D fria no Godot; aqui só o desenho."""
    img = Imagem(16, 12)
    for (x, y, r, a) in ((4, 8, 2, 5), (9, 6, 3, 7), (12, 9, 1.5, 3)):
        img.pintar(img.ret(x, y, x + 1, 11), "fungo", 0.35)
        chapeu = img.elipse(x + 0.5, y, r + 0.5, r * 0.6 + 0.4)
        img.pintar(chapeu, "fungo", 0.7)
        img.cor(img.ret(x, y - 1, x + 1, y), RAMPAS["fungo"][5])
    img.contornar(RAMPAS["fungo"][0])
    return img, 8, 11


# ---------------------------------------------------------------------------
# Primeiro plano (por cima do Gabriel): copa, cipós, laje e entulho escuros
# ---------------------------------------------------------------------------


def desenhar_frente():
    img = Imagem(LARGURA_SALA, ALTURA_SALA)
    X, Y = img.X, img.Y
    fino = ruido(img.w, img.h, 2, 2, 140)
    # 1. Copa da árvore saindo pelo buraco (lado de cima da tela). A copa
    #    recebe o sol de frente: folhas claras em cima, escuras embaixo.
    folhas = ruido(img.w, img.h, 5, 4, 141) * 0.6 + ruido(img.w, img.h, 2, 2, 142) * 0.4
    copa = (img.elipse(222, -4, 70, 22) | img.elipse(300, -8, 40, 18)
            | img.elipse(180, -2, 30, 16)) & (folhas > 0.42 + 0.02 * Y / 4)
    img.pintar(copa, "verde", 0.95 - Y / 26 + 0.25 * fino)
    # 2. Laje escura por cima de tudo, fora dos buracos (silhueta).
    for (xa, xb) in ((0, 146), (344, 602), (676, 960)):
        # Borda de baixo irregular: ruído em x decide até onde a laje desce.
        borda = 3 + 6 * ruido(img.w, 1, 5, 1, 144)[0][None, :] ** 2
        laje = img.ret(xa, 0, xb, 12) & (Y < borda)
        img.cor(laje, SOMBRA)
    # 3. Cipós pendurados (silhuetas verde-escuras).
    rng = np.random.default_rng(143)
    for x0 in (22, 70, 132, 176, 318, 360, 420, 598, 690, 742, 830, 905, 948):
        comp = int(rng.integers(14, 46))
        pontos = [(x0 + 2 * np.sin(k * 0.9 + x0), k * comp / 8) for k in range(9)]
        cipo = img.caminho(pontos, 0.7)
        img.pintar(cipo, "verde", 0.08 + 0.12 * fino)
        folha = dilatar(cipo) & (fino > 0.7)
        img.pintar(folha, "verde", 0.12)
    # 4. Entulho e mato no primeiro plano, na beira de baixo da sala, só em
    #    alguns pontos (não pode esconder o Gabriel).
    for (cx, larg, alt) in ((30, 60, 9), (300, 44, 6), (520, 30, 5), (840, 70, 9)):
        topo = ALTURA_SALA - alt * (1 - ((X - cx) / (larg / 2)) ** 2) - 2 * fino
        monte = (np.abs(X - cx) < larg / 2) & (Y >= topo)
        img.pintar(monte, "verde", 0.05 + 0.08 * fino)
        img.cor(monte & (Y < topo + 1), RAMPAS["verde"][2])
    return img


# ---------------------------------------------------------------------------
# Textura das luzes
# ---------------------------------------------------------------------------


def desenhar_luz():
    """Textura de uma PointLight2D: branco no centro, sumindo até a borda.
    Decaimento suave: (1 - d)², onde d é a distância ao centro (0 a 1).
    Depois cortamos em 6 degraus, para a luz ter anéis como em pixel art."""
    n = 64
    img = Imagem(n, n)
    d = np.sqrt((img.X + 0.5 - n / 2) ** 2 + (img.Y + 0.5 - n / 2) ** 2) / (n / 2)
    i = np.clip(1 - d, 0, 1) ** 2
    i = np.floor(i * 6 + img.limiar * 0.999) / 6       # degraus + dithering nas bordas
    img.px[..., :3] = 255
    img.px[..., 3] = (np.clip(i, 0, 1) * 255).astype(np.uint8)
    return img


# ---------------------------------------------------------------------------


FUNCOES_OBJETOS = {
    "cabine": cabine,
    "cadeira": cadeira,
    "arvore": arvore,
    "entulho": entulho,
    "estante_caida": estante_caida,
    "estante_vazia": lambda: estante(semente=1),
    "estante_quebrada": lambda: estante(semente=7, quebrada=True),
    "livros": livros,
    "mesa_leitura": mesa_leitura,
    "carrinho": carrinho,
    "fungo": fungo,
}


def main():
    print("Gerando a Biblioteca em", os.path.relpath(PASTA_SAIDA, PASTA_PROJETO))
    ceu = desenhar_ceu()
    fundo = desenhar_fundo()
    chao = desenhar_chao()
    frente = desenhar_frente()
    ceu.salvar("biblioteca_ceu.png")
    fundo.salvar("biblioteca_fundo.png")
    chao.salvar("biblioteca_chao.png")
    frente.salvar("biblioteca_frente.png")
    desenhar_luz().salvar("luz.png", os.path.join(PASTA_KIT, "luzes"))

    sprites = {}
    print("Objetos (offset do Sprite2D no Godot = -pé):")
    for nome, funcao in FUNCOES_OBJETOS.items():
        img, px, py = funcao()
        img.salvar(f"{nome}.png", os.path.join(PASTA_KIT, "objetos"))
        print(f"    {nome}: pé em ({px}, {py}) -> offset = Vector2({-px}, {-py})")
        sprites[nome] = (img, px, py)

    if PREVIA:
        # Monta a sala inteira como o Godot vai mostrar (sem as luzes).
        sala = Imagem(LARGURA_SALA, ALTURA_SALA)
        sala.colar(ceu, 0, 0)
        sala.colar(fundo, 0, 0)
        sala.colar(chao, 0, 0)
        for nome, x, y, espelhado in sorted(OBJETOS, key=lambda o: o[2]):
            img, px, py = sprites[nome]
            if espelhado:
                img = Imagem.__new__(Imagem)
                img.__dict__.update(sprites[nome][0].__dict__)
                img.px = sprites[nome][0].px[:, ::-1]
                px = img.w - 1 - px
            sala.colar(img, x - px, y - py)
        sala.colar(frente, 0, 0)
        pasta = PASTA_SCRIPT if PREVIA == "1" else PREVIA
        salvar_png(os.path.join(pasta, "previa_biblioteca.png"), sala.px)
        print("  prévia: previa_biblioteca.png (não commitar)")


# Só desenha quando o arquivo é rodado direto. Assim o gerar_kit.py pode
# importar as funções daqui sem gerar a Biblioteca de novo.
if __name__ == "__main__":
    main()
