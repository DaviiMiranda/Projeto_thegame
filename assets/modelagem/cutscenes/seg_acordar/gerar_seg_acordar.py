# gerar_seg_acordar.py — monta no Blender, por código, a cabine de estudo da
# Biblioteca MIL ANOS DEPOIS e renderiza as camadas e os quadros do Gabriel
# para a cutscene "seg_acordar" (docs/roteiro/cutscenes/seg_acordar.md).
#
# Como rodar (sem abrir a janela do Blender):
#
#   blender -b --factory-startup --python assets/modelagem/cutscenes/seg_acordar/gerar_seg_acordar.py
#
# Para testar o enquadramento rápido (poucas amostras, imagem 3x maior,
# tudo junto numa imagem só, sem salvar nada no projeto):
#
#   PREVIA=1 POSE=0 blender -b --factory-startup --python .../gerar_seg_acordar.py
#
# O que sai (em assets/sprites/cutscenes/seg_acordar/):
#   seg_acordar_fundo.png    céu, parede rachada, estantes caídas, teto quebrado
#   seg_acordar_meio.png     mesa podre, monitor morto, árvore, raízes
#   seg_acordar_gabriel.png  folha com os quadros do Gabriel acordando (lado a lado)
#   seg_acordar_frente.png   primeiro plano: cipós pendurados, entulho
#   e assets/modelagem/cutscenes/seg_acordar/seg_acordar.blend
#
# A cena é a MESMA cabine do menu (assets/modelagem/menu/gerar_menu.py): a
# mesa, o monitor, o teclado, a pilha de livros e a caneca estão nos mesmos
# lugares. Só que agora o teto caiu, o sol entra, uma árvore cresceu onde
# ficava a cabine vizinha (docs/gdd.md, item 3) e as estantes estão caídas e
# vazias. A câmera está no mesmo eixo da câmera do menu, só que mais para
# trás e mais alta: o monitor fica no meio do quadro, como no menu, e agora
# dá para ver o Gabriel dormindo debruçado na mesa.
#
# Técnicas (as mesmas já aprovadas no menu e nos personagens):
#   - Cycles na CPU, sem janela, filtro de pixel mínimo (sem antialiasing),
#     sem denoise, transformação de cor "Standard", alfa cortado em 0 ou 1.
#   - Camadas renderizadas separadas (os objetos das outras camadas somem da
#     câmera mas continuam fazendo sombra), para a paralaxe no Godot.
#   - Cenário: paleta reduzida escolhida por k-means no espaço CIELAB.
#   - Gabriel: o truque dos personagens (passe de luz + passe de ID, rampa de
#     4 tons por material, contorno de 1 px), para ele ficar igual ao sprite
#     aprovado. A mesa e o que está na frente dele viram "holdout" (buraco
#     transparente) no render dele, então a perna que fica embaixo da mesa
#     some do quadro sozinha.
#
# Unidades: as do menu, 1 unidade = 2,5 cm. Tampo da mesa em z = 0, chão em
# z = -30 (75 cm abaixo). O eixo +Y aponta para dentro da cena.

import math
import os
import random
import sys

sys.dont_write_bytecode = True   # não criar __pycache__ nas pastas do projeto

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

# ---------------------------------------------------------------------------
# Pastas e scripts reaproveitados
# ---------------------------------------------------------------------------

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.normpath(os.path.join(PASTA_SCRIPT, "..", "..", "..", ".."))
PASTA_SAIDA = os.path.join(PASTA_PROJETO, "assets", "sprites", "cutscenes", "seg_acordar")
ARQUIVO_BLEND = os.path.join(PASTA_SCRIPT, "seg_acordar.blend")
PASTA_PERSONAGENS = os.path.join(PASTA_PROJETO, "assets", "modelagem", "personagens")
PASTA_MENU = os.path.join(PASTA_PROJETO, "assets", "modelagem", "menu")

sys.path.insert(0, PASTA_PERSONAGENS)
import comum as c  # noqa: E402


class Modulo:
    """Um 'saco' de nomes: modulo.funcao em vez de dicionario['funcao']."""

    def __init__(self, nomes):
        self.__dict__.update(nomes)


def carregar_sem_rodar(caminho):
    """Carrega as funções de outro script do projeto SEM rodar a main() dele.

    gerar_menu.py e gerar_gabriel.py terminam com a linha 'main()', que
    renderiza e salva tudo. Aqui lemos o texto do script, tiramos essa
    última chamada e executamos o resto: ficam só as definições (funções,
    constantes), que reaproveitamos. Assim o Gabriel e a cabine continuam
    tendo UMA fonte só: se alguém mudar o modelo lá, muda aqui também."""
    with open(caminho, encoding="utf-8") as arq:
        fonte = arq.read()
    fonte = fonte.rstrip()
    assert fonte.endswith("main()"), f"esperava 'main()' no fim de {caminho}"
    fonte = fonte[: -len("main()")]
    nomes = {"__file__": caminho, "__name__": os.path.basename(caminho)[:-3]}
    exec(compile(fonte, caminho, "exec"), nomes)
    return Modulo(nomes)


menu = carregar_sem_rodar(os.path.join(PASTA_MENU, "gerar_menu.py"))
gabriel = carregar_sem_rodar(os.path.join(PASTA_PERSONAGENS, "gerar_gabriel.py"))

# ---------------------------------------------------------------------------
# Imagem e câmera
# ---------------------------------------------------------------------------

# 320×180 do jogo + 10 px de sobra em cada borda, para as camadas poderem
# andar (paralaxe) sem mostrar a borda vazia. No Godot: posição (-10, -10).
MARGEM = 10
LARGURA = 320 + 2 * MARGEM
ALTURA = 180 + 2 * MARGEM

PREVIA = bool(os.environ.get("PREVIA"))
ESCALA_PREVIA = 3

# Câmera no MESMO eixo da câmera do menu (x = -6), mas 2,1 m mais para trás
# e mais alta: é como se a gente tivesse dado uns passos para trás da
# cadeira. Continua olhando reto para +Y (sem inclinar), então as linhas
# verticais da sala (parede, tronco, estantes em pé) continuam verticais,
# como numa foto de arquitetura. O enquadramento para cima (mostrar o teto
# quebrado) é feito com o "shift" da lente, igual ao menu.
CAM_X, CAM_Y, CAM_Z = -6.0, -110.0, 48.0
# Escala: a 100 unidades (2,5 m) da câmera, 1 unidade = 2 px. O Gabriel
# está a ~90 unidades, então 1 m ≈ 85 px: a cabeça dele tem ~20 px, quase o
# tamanho da folha de referência aprovada (128 px de altura = 73 px/m).
DIST_REF = 100.0
PX_POR_UNIDADE_REF = 2.0
SHIFT_Y = -0.13  # desce o quadro 13% da largura (44 px): a mesa entra no quadro


def criar_camera():
    dados = bpy.data.cameras.new("Camera")
    dados.type = 'PERSP'
    dados.sensor_fit = 'HORIZONTAL'
    dados.sensor_width = 36.0
    # Semelhança de triângulos: largura visível a uma distância d é
    # d * sensor / lente. Queremos LARGURA px = LARGURA/2 unidades a DIST_REF.
    largura_visivel = LARGURA / PX_POR_UNIDADE_REF
    dados.lens = dados.sensor_width * DIST_REF / largura_visivel
    dados.shift_y = SHIFT_Y
    dados.clip_start = 1.0
    dados.clip_end = 2000.0
    cam = bpy.data.objects.new("Camera", dados)
    cam.location = (CAM_X, CAM_Y, CAM_Z)
    cam.rotation_euler = (math.radians(90), 0, 0)   # olhando para +Y
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def projetar(cam, ponto):
    """Onde um ponto 3D cai na tela do JOGO (pixels, sem a margem)."""
    cena = bpy.context.scene
    bpy.context.view_layer.update()
    p = world_to_camera_view(cena, cam, Vector(ponto))
    return p.x * LARGURA - MARGEM, (1 - p.y) * ALTURA - MARGEM


# ---------------------------------------------------------------------------
# Materiais do cenário
# ---------------------------------------------------------------------------
# Mil anos depois: tudo desbotado, empoeirado, com musgo. Os tons quentes
# (madeira, bege) ficam acinzentados; o verde entra por todo lado.

def criar_materiais_cenario():
    m = menu.material
    return {
        "concreto": m("concreto", "#8d877b", 0.95),
        "concreto_escuro": m("concreto_escuro", "#5f5a52", 0.95),
        "reboco": m("reboco", "#a39c8c", 0.95),
        "chao": m("chao", "#6f624f", 0.95),
        "terra": m("terra", "#5c4a36", 1.0),
        "areia": m("areia", "#b9a57c", 1.0),
        "madeira_podre": m("madeira_podre", "#5e4a36", 0.9),
        "madeira_podre_escura": m("madeira_podre_escura", "#3e3126", 0.9),
        "bege_velho": m("bege_velho", "#a09474", 0.8),       # plástico do monitor, amarelado
        "bege_velho_escuro": m("bege_velho_escuro", "#766c55", 0.85),
        "vidro_morto": m("vidro_morto", "#15191c", 0.3),       # a tela apagada
        "tecla": m("tecla", "#9b927c", 0.8),
        "papel_velho": m("papel_velho", "#a89c7c", 1.0),
        "livro_podre": m("livro_podre", "#4a3a44", 0.95),
        "livro_podre2": m("livro_podre2", "#3a4640", 0.95),
        "ferrugem": m("ferrugem", "#6a4632", 0.7),
        "caneca": m("caneca", "#b9b3a6", 0.6),
        "musgo": m("musgo", "#4c6a32", 1.0),
        "musgo_claro": m("musgo_claro", "#7b8f45", 1.0),
        "folha": m("folha", "#3f6b2f", 0.8),
        "folha_clara": m("folha_clara", "#76a042", 0.8),
        "folha_escura": m("folha_escura", "#2c4a26", 0.8),
        "casca": m("casca", "#5d4c3d", 1.0),
        "casca_escura": m("casca_escura", "#3f3329", 1.0),
        "relogio": m("relogio", "#c4bfae", 0.6),
        "preto": m("preto", "#141414", 0.6),
    }


# ---------------------------------------------------------------------------
# Peças de montar
# ---------------------------------------------------------------------------

def cubos(nome, lista, mats, col):
    """Um objeto feito de várias caixas. lista = [(x0,x1,y0,y1,z0,z1,indice_mat), ...]."""
    bm = bmesh.new()
    for x0, x1, y0, y1, z0, z1, i in lista:
        menu.cubo_em(bm, x0, x1, y0, y1, z0, z1, i)
    return menu.objeto_de_bmesh(nome, bm, mats, col)


def bolota(nome, raio, pos, mat, col, escala=(1, 1, 1), subdiv=1, rot=(0, 0, 0)):
    """Icosfera facetada: moita de folhas, pedaço de entulho, monte de terra."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=raio,
                               matrix=Matrix.Diagonal((*escala, 1)))
    obj = menu.objeto_de_bmesh(nome, bm, mat, col)
    obj.location = pos
    obj.rotation_euler = [math.radians(a) for a in rot]
    return obj


def galho(nome, inicio, fim, raio0, raio1, mat, col, lados=7):
    """Cone de 'inicio' a 'fim' (pontos 3D): tronco, galho ou raiz."""
    a, b = Vector(inicio), Vector(fim)
    direcao = b - a
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=lados,
                          radius1=raio0, radius2=raio1, depth=direcao.length,
                          matrix=Matrix.Translation((0, 0, direcao.length / 2)))
    obj = menu.objeto_de_bmesh(nome, bm, mat, col)
    obj.location = a
    # Gira o eixo Z do cone para apontar na direção do galho.
    obj.rotation_euler = direcao.to_track_quat('Z', 'Y').to_euler()
    return obj


def estante_vazia(nome, largura, altura, prof, mat, col):
    """Estante sem nenhum livro (mil anos depois não sobrou nenhum).
    Montada com a base no ponto (0,0,0), frente virada para -Y."""
    lista = [
        (0, 1.2, 0, prof, 0, altura, 0),                           # lateral esquerda
        (largura - 1.2, largura, 0, prof, 0, altura, 0),           # lateral direita
        (0, largura, prof - 0.5, prof, 0, altura, 0),              # fundo
    ]
    for z in np.linspace(0, altura - 1, 6):
        lista.append((0, largura, 0, prof, z, z + 1.0, 0))       # prateleiras
    return cubos(nome, lista, [mat], col)


# ---------------------------------------------------------------------------
# A cena
# ---------------------------------------------------------------------------

CHAO_Z = -30.0
TETO_Z = 100.0          # a laje ficava a 3,25 m do chão
PAREDE_Y = 60.0         # mesma parede do menu
ARVORE = Vector((50.0, 22.0))   # onde ficava a cabine vizinha (docs/gdd.md)


def montar_fundo(mt, col):
    """Céu (é o 'mundo'), parede quebrada, laje do teto com um rombo,
    estantes caídas, chão com terra e mato."""
    # Chão: um piso grande, com montes de terra e areia que entraram.
    menu.caixa("Chao", -200, 200, -140, PAREDE_Y, CHAO_Z - 1, CHAO_Z, mt["chao"], col)
    for i, (x, y, r, esc, mat) in enumerate([
            (-70, 40, 22, (1.6, 1.0, 0.25), "terra"), (20, 45, 18, (1.8, 0.9, 0.22), "areia"),
            (80, 30, 25, (1.4, 1.2, 0.3), "terra"), (-110, 10, 20, (1.5, 1.4, 0.25), "areia"),
            (-35, -40, 14, (1.6, 1.0, 0.2), "terra")]):
        bolota(f"MonteTerra{i}", r, (x, y, CHAO_Z), mt[mat], col, esc)

    # Parede do fundo: tiras verticais de 6 unidades, cada uma com uma altura.
    # Onde o teto desabou, a parede desabou junto (tiras mais baixas).
    random.seed(11)
    lista = []
    # A altura de cada tira é um "passeio aleatório": parte da altura da
    # anterior e sobe ou desce um pouco. Assim a borda quebrada é contínua,
    # e não um monte de degraus soltos.
    x = -220.0
    topo = TETO_Z
    while x < 220:
        larg = random.choice((2.0, 3.0, 4.0))
        if -45 < x < 95:                 # embaixo do rombo, a parede desabou
            alvo = 62 + 14 * math.sin(x / 23.0)
        else:
            alvo = TETO_Z
        topo += (alvo - topo) * 0.35 + random.uniform(-4, 4)
        topo = min(topo, TETO_Z)
        lista.append((x, x + larg, PAREDE_Y, PAREDE_Y + 4, CHAO_Z, topo, 0))
        x += larg
    cubos("Parede", lista, [mt["reboco"]], col)
    # Rodapé de concreto aparente e rachaduras (tiras escuras finas).
    menu.caixa("Rodape", -220, 220, PAREDE_Y - 0.3, PAREDE_Y, CHAO_Z, CHAO_Z + 6, mt["concreto_escuro"], col)
    for i, (xr, z0, z1, ang) in enumerate([(-95, 10, 60, 12), (-20, 20, 50, -18), (100, -5, 55, 8)]):
        r = menu.caixa(f"Rachadura{i}", -0.5, 0.5, -0.3, 0, 0, z1 - z0, mt["concreto_escuro"], col)
        r.location = (xr, PAREDE_Y - 0.05, z0)
        r.rotation_euler = (0, math.radians(ang), 0)

    # Laje do teto: uma grade de placas de 10×10. As que ficam dentro do
    # "rombo" (uma elipse torta em cima da cabine e da árvore) caíram.
    # Em volta do rombo, algumas placas soltas também caíram: a borda fica
    # serrilhada, como um desenho em pixel.
    random.seed(5)
    lista = []
    for gx in range(-24, 24):
        for gy in range(-16, 7):
            x0, y0 = gx * 10.0, gy * 10.0
            cx, cy = x0 + 5 - 15, y0 + 5 - 5          # centro do rombo em (15, 5)
            d = (cx / 95) ** 2 + (cy / 120) ** 2
            if d < 1.0 or (d < 1.5 and random.random() < 0.55):
                continue
            lista.append((x0, x0 + 10, y0, y0 + 10, TETO_Z, TETO_Z + 8, 0))
    cubos("Laje", lista, [mt["concreto"]], col)
    # Uma viga que sobrou atravessando o rombo, quebrada no meio (pende).
    viga = menu.caixa("Viga", 0, 70, -4, 4, -8, 0, mt["concreto_escuro"], col)
    viga.location = (-80, -20, TETO_Z)
    viga.rotation_euler = (0, math.radians(14), 0)

    # Estante da esquerda (a do menu, em x -46..-12): tombou para a frente e
    # ficou escorada, torta. Vazia.
    e1 = estante_vazia("EstanteTombada", 34, 80, 12, mt["madeira_podre_escura"], col)
    e1.location = (-58, 36, CHAO_Z)
    e1.rotation_euler = (math.radians(-8), math.radians(-22), math.radians(4))
    # Estante da direita (x 50..84 no menu): caída no chão, de lado.
    e2 = estante_vazia("EstanteCaida", 34, 80, 12, mt["madeira_podre_escura"], col)
    e2.location = (70, 28, CHAO_Z + 12)
    e2.rotation_euler = (math.radians(90), 0, math.radians(8))
    # Mais estantes do salão, ao fundo à esquerda, em pé e vazias.
    for i, x in enumerate((-150, -112)):
        e = estante_vazia(f"EstanteSalao{i}", 34, 80, 12, mt["madeira_podre"], col)
        e.location = (x, 44, CHAO_Z)

    # O relógio do menu (parado em 23h55): caiu e ficou encostado na parede.
    rel = menu.cilindro("Relogio", 4.0, 0.8, mt["relogio"], col, lados=16)
    rel.rotation_euler = (math.radians(75), 0, math.radians(10))
    rel.location = (-2, PAREDE_Y - 3, CHAO_Z + 4)
    aro = menu.cilindro("RelogioAro", 4.4, 0.6, mt["preto"], col, lados=16)
    aro.rotation_euler = (math.radians(75), 0, math.radians(10))
    aro.location = (-2, PAREDE_Y - 2.6, CHAO_Z + 4.2)

    # Mato no chão, onde bate sol: tufos de folhas finas (cones).
    random.seed(9)
    for i in range(40):
        x = random.uniform(-120, 120)
        y = random.uniform(20, PAREDE_Y - 4)
        for j in range(3):
            g = galho(f"Mato{i}_{j}", (x + j, y, CHAO_Z), (x + j + random.uniform(-3, 3), y, CHAO_Z + random.uniform(4, 9)),
                      0.8, 0.1, mt["folha_clara" if j % 2 else "folha"], col, lados=4)

    # Folhagem da árvore lá no alto (a copa passa por cima do rombo). Fica
    # no fundo: está longe e alta, anda pouco na paralaxe.
    random.seed(21)
    for i in range(70):
        ang = random.uniform(0, 2 * math.pi)
        r = random.uniform(10, 95)
        x = ARVORE.x - 10 + math.cos(ang) * r * 1.2
        y = ARVORE.y + 10 + math.sin(ang) * r * 0.6
        z = TETO_Z + 25 + random.uniform(-10, 40)
        mat = random.choice(("folha", "folha", "folha_clara", "folha_escura"))
        bolota(f"Copa{i}", random.uniform(9, 17), (x, y, z), mt[mat], col, (1.3, 1.0, 0.8),
               rot=(0, 0, random.uniform(0, 90)))


def montar_meio(mt, col):
    """A cabine: mesa, monitor, teclado, livros, caneca — nos lugares do
    menu, mas podres — e a árvore com as raízes."""
    # Tampo podre: vai da divisória da esquerda até perto da árvore, onde
    # quebrou. A ponta quebrada caiu no chão.
    menu.caixa("Tampo", -40, 26, -14, 14, -1.5, 0, mt["madeira_podre"], col)
    ponta = menu.caixa("TampoQuebrado", 0, 16, -14, 12, -1.5, 0, mt["madeira_podre"], col)
    ponta.location = (26, 2, -8)
    ponta.rotation_euler = (math.radians(5), math.radians(35), 0)
    # Pés e divisória da cabine (painel lateral à esquerda).
    menu.caixa("PeMesa", -39, -37, -12, 12, CHAO_Z, -1.5, mt["madeira_podre_escura"], col)
    menu.caixa("Divisoria", -42, -40, -16, 16, CHAO_Z, 26, mt["madeira_podre_escura"], col)
    menu.caixa("DivisoriaMusgo", -42.3, -39.7, -16.3, 16.3, 20, 26.5, mt["musgo"], col)

    # Monitor CRT: a mesma construção do menu (moldura com o buraco da tela),
    # agora apagado, amarelado e com musgo em cima.
    tx0, tx1 = -menu.TELA_LARG / 2, menu.TELA_LARG / 2
    z0, z1 = menu.TELA_Z0, menu.TELA_Z1
    mold = 1.4
    moldura = menu.caixa("MonitorMoldura", tx0 - mold, tx1 + mold, 0, 3.0, 0.4, z1 + mold + 0.3, mt["bege_velho"], col)
    buraco = menu.caixa("MonitorBuraco", tx0, tx1, -1.0, 1.0, z0, z1, mt["bege_velho"], col)
    buraco.hide_render = True
    buraco.hide_viewport = True
    furo = moldura.modifiers.new("Buraco", 'BOOLEAN')
    furo.operation = 'DIFFERENCE'
    furo.object = buraco
    menu.chanfro(moldura, 0.35, 2)
    cubos("MonitorCorpo", [(tx0 - mold + 0.6, tx1 + mold - 0.6, 3.0, 9.0, 0.8, z1 + mold - 0.2, 0),
                           (tx0 + 1.5, tx1 - 1.5, 9.0, 15.0, 2.0, z1 - 1.0, 0)], [mt["bege_velho_escuro"]], col)
    menu.caixa("MonitorPe", -5, 5, 1.0, 11.0, 0, 0.5, mt["bege_velho_escuro"], col)
    menu.caixa("MonitorVidro", tx0, tx1, 0.3, 0.5, z0, z1, mt["vidro_morto"], col)
    # Musgo em cima do monitor e escorrendo pela lateral.
    random.seed(3)
    for i in range(9):
        x = random.uniform(tx0 - 1, tx1 + 1)
        bolota(f"MusgoMonitor{i}", random.uniform(1.2, 2.2), (x, random.uniform(1, 12), z1 + mold + 0.4),
               mt["musgo" if i % 3 else "musgo_claro"], col, (1.6, 1.2, 0.45))

    # Teclado: mesma grade do menu, com musgo nas teclas.
    bm = bmesh.new()
    kx0, kx1, ky0, ky1 = -6.5, 6.5, -5.6, -1.6
    menu.cubo_em(bm, kx0, kx1, ky0, ky1, 0, 0.6)
    passo_x, passo_y = (kx1 - kx0 - 0.6) / 15, (ky1 - ky0 - 0.6) / 5
    for i in range(15):
        for j in range(5):
            if random.random() < 0.15:
                continue      # teclas que soltaram
            x = kx0 + 0.3 + i * passo_x
            y = ky0 + 0.3 + j * passo_y
            menu.cubo_em(bm, x + 0.06, x + passo_x - 0.06, y + 0.06, y + passo_y - 0.06, 0.6, 0.95, 1)
    teclado = menu.objeto_de_bmesh("Teclado", bm, [mt["bege_velho_escuro"], mt["tecla"]], col)
    teclado.rotation_euler = (0, 0, math.radians(6))   # empurrado quando ele deitou

    # Pilha de livros e cadernos da véspera da prova (onde a cabeça dele está).
    for nome, dx, dy, dz, alt, ang, mat in [("Caderno", -12.5, -1.5, 0, 0.7, -6, "livro_podre2"),
                                            ("CadernoVermelho", -12.0, -1.2, 0.7, 0.6, 9, "livro_podre"),
                                            ("LivroMesa", -12.7, -1.4, 1.3, 1.6, 2, "livro_podre2")]:
        o = menu.caixa(nome, -3.3, 3.3, -4.4, 4.4, 0, alt, mt[mat], col)
        o.location = (dx, dy, dz)
        o.rotation_euler = (0, 0, math.radians(ang))
    for i, (x, y, ang) in enumerate([(-20.0, -6.0, 22), (14.5, -3.0, 40)]):
        p = menu.caixa(f"Papel{i}", -2.6, 2.6, -3.4, 3.4, 0, 0.05, mt["papel_velho"], col)
        p.location = (x, y, 0.02)
        p.rotation_euler = (0, 0, math.radians(ang))

    # Caneca: no mesmo lugar do menu. Mil anos depois, nasceu uma planta nela.
    caneca = menu.cilindro("Caneca", 1.3, 3.4, mt["caneca"], col, lados=10)
    caneca.location = (11.0, -2.0, 0)
    for i, (dx, dz, ang) in enumerate([(-1.5, 5.5, -30), (1.2, 6.5, 25), (0.2, 7.5, 5)]):
        galho(f"Broto{i}", (11.0, -2.0, 2.5), (11.0 + dx, -2.0, dz), 0.25, 0.1, mt["folha"], col, lados=4)
        bolota(f"BrotoFolha{i}", 0.9, (11.0 + dx, -2.0, dz), mt["folha_clara"], col, (1.4, 0.6, 0.7))

    # Luminária: a haste enferrujou e ela tombou por cima da mesa.
    base = menu.cilindro("LuminariaBase", 2.2, 0.6, mt["ferrugem"], col, lados=10)
    base.location = (17.0, 8.0, 0)
    galho("LuminariaHaste", (17, 8, 0.5), (20, -2, 1.5), 0.3, 0.3, mt["ferrugem"], col, lados=4)
    cup = menu.cilindro("LuminariaCupula", 2.6, 3.5, mt["ferrugem"], col, lados=10, raio_topo=0.8)
    cup.location = (21.0, -4.0, 2.4)
    cup.rotation_euler = (math.radians(100), 0, math.radians(-20))

    # A ÁRVORE: cresceu onde ficava a cabine vizinha. Tronco largo que
    # atravessa o rombo do teto, raízes que racharam o chão e subiram na mesa.
    ax, ay = ARVORE
    galho("Tronco", (ax, ay, CHAO_Z - 2), (ax - 6, ay + 4, TETO_Z + 40), 12, 7, mt["casca"], col, lados=11)
    galho("TroncoSulco", (ax - 12, ay - 10, CHAO_Z), (ax - 14, ay - 4, TETO_Z + 10), 4, 3, mt["casca_escura"], col, lados=5)
    galho("TroncoSulco2", (ax + 10, ay - 11, CHAO_Z), (ax + 5, ay - 6, TETO_Z + 20), 3.5, 2.5, mt["casca_escura"], col, lados=5)
    galho("GalhoEsq", (ax - 5, ay + 3, 70), (ax - 60, ay - 5, TETO_Z + 30), 7, 3, mt["casca"], col)
    galho("GalhoDir", (ax - 4, ay + 3, 85), (ax + 40, ay + 10, TETO_Z + 45), 6, 3, mt["casca"], col)
    # Raízes: cones deitados saindo da base do tronco.
    for i, (dx, dy, alt) in enumerate([(-45, -30, 3), (-30, -55, 2), (15, -60, 3), (50, -20, 2), (-60, 10, 2)]):
        galho(f"Raiz{i}", (ax, ay - 4, CHAO_Z + 6), (ax + dx, ay + dy, CHAO_Z + alt), 6, 1.2, mt["casca_escura"], col, lados=6)
    # Uma raiz subiu pela ponta da mesa quebrada.
    galho("RaizMesa", (ax - 10, ay - 12, CHAO_Z + 20), (24, -8, 1.0), 3.5, 0.8, mt["casca"], col, lados=6)
    galho("RaizMesa2", (24, -8, 1.0), (12, -12, 0.6), 1.0, 0.4, mt["casca"], col, lados=5)
    # Musgo na base do tronco.
    for i in range(6):
        ang = math.radians(150 + i * 35)
        bolota(f"MusgoTronco{i}", 5, (ax + math.cos(ang) * 16, ay + math.sin(ang) * 16, CHAO_Z + 2),
               mt["musgo" if i % 2 else "musgo_claro"], col, (1.4, 1.2, 0.6))

    # Folhas e entulho caídos na mesa e no chão da cabine.
    random.seed(4)
    for i in range(16):
        x, y = random.uniform(-38, 24), random.uniform(-13, 12)
        if -8 < x < 8 and -6 < y < 16:
            continue          # não cobrir o teclado nem o monitor
        bolota(f"FolhaMesa{i}", random.uniform(0.6, 1.1), (x, y, 0.1), mt[random.choice(("folha", "musgo_claro", "terra"))],
               col, (1.6, 1.0, 0.25), subdiv=1)
    for i in range(10):
        bolota(f"Entulho{i}", random.uniform(2, 5), (random.uniform(-90, 100), random.uniform(-60, 10), CHAO_Z + 1),
               mt["concreto" if i % 2 else "concreto_escuro"], col, (1.2, 1.0, 0.7), rot=(0, 0, random.uniform(0, 90)))


def montar_frente(mt, col):
    """Primeiro plano: coisas bem perto da câmera, que correm mais na
    paralaxe. Cipós pendurados da borda do teto e um bloco de laje caído."""
    random.seed(17)
    # Pedaço da laje do teto que quebrou e ficou pendurado pela ferragem, no
    # canto de cima à direita, bem perto da câmera: é o "teto que não
    # existe mais" emoldurando o quadro.
    laje = cubos("LajePendurada", [(0, 30, 0, 26, 0, 5, 0), (3, 9, 26, 31, 1, 4, 0), (16, 27, 26, 29, 1, 4, 0)],
                 [mt["concreto_escuro"]], col)
    laje.location = (22, -62, 60)
    laje.rotation_euler = (math.radians(-10), math.radians(-24), math.radians(8))
    for i in range(4):     # ferros da armadura saindo da borda
        galho(f"Ferro{i}", (22.5 + i * 0.4, -60 + i * 6, 61), (20.5 + i * 1.2, -59 + i * 6, 51 + i * 1.5),
              0.35, 0.3, mt["ferrugem"], col, lados=4)
    # Cipós: correntes de folhinhas descendo da laje, perto da câmera
    # (y ≈ -62, a meio caminho entre a câmera e o Gabriel).
    for i, (x, z, comp) in enumerate([(-48, 80, 44), (-44, 78, 30), (25, 60, 26), (29, 62, 40), (35, 66, 18)]):
        xx = x
        for j in range(int(comp / 2.2)):
            xx += random.uniform(-0.5, 0.5)
            mat = mt["folha" if j % 3 else "folha_escura"]
            bolota(f"Cipo{i}_{j}", random.uniform(0.6, 1.1), (xx + random.uniform(-0.8, 0.8), -62, z), mat, col,
                   (1.0, 0.6, 1.4), rot=(0, random.uniform(-30, 30), 0))
            z -= random.uniform(1.8, 2.6)
    # Bloco de laje caído no chão, à direita, com mato em cima.
    bloco = menu.caixa("BlocoLaje", -12, 12, -8, 8, -5, 5, mt["concreto"], col)
    bloco.location = (34, -66, CHAO_Z + 4)
    bloco.rotation_euler = (math.radians(8), math.radians(-14), math.radians(20))
    for i in range(5):
        bolota(f"MatoBloco{i}", random.uniform(1.8, 3.0), (26 + i * 4, -68, CHAO_Z + 10 + random.uniform(-1, 1)),
               mt["folha" if i % 2 else "folha_clara"], col, (1.2, 1.0, 0.8))
    # Samambaia no chão, à esquerda.
    for i in range(7):
        ang = math.radians(100 + i * 12)
        galho(f"Samambaia{i}", (-40, -66, CHAO_Z), (-40 + math.cos(ang) * 22, -66, CHAO_Z + math.sin(ang) * 22 + 4),
              1.5, 0.3, mt["folha" if i % 2 else "folha_escura"], col, lados=4)


# ---------------------------------------------------------------------------
# Gabriel e a cadeira
# ---------------------------------------------------------------------------

# Onde fica o quadril do Gabriel sentado (unidades da cena). Ele está à
# esquerda do teclado, com a cabeça em cima da pilha de livros — o mesmo
# lugar dos livros no menu ("tufos arrepiados de quem deitou a cabeça em
# cima do livro", gerar_gabriel.py).
QUADRIL_CENA = Vector((-15.0, -22.0, -8.0))
ESCALA_GABRIEL = 40.0          # o modelo dele é em metros; 1 m = 40 unidades

# Poses: rotação (graus) de cada junta. Nomes das juntas = pivôs criados em
# gerar_gabriel.montar(). Lembrete dos eixos (comum.py): rotação X positiva
# inclina para a FRENTE o tronco e a cabeça, e para TRÁS braços e pernas.
# Na cabeça, Z gira para os lados (olhar) e Y tomba a cabeça de lado.
#
# Conta que ajuda a posar o braço: as rotações em X se SOMAM ao longo da
# corrente tronco -> ombro -> cotovelo. O ângulo do braço "no mundo" é
# tronco + ombro (0 = pendurado, -90 = esticado para a frente). Com o
# tronco a 50° e o ombro a -135°, o braço fica a -85°: quase deitado na
# mesa. Para dobrar o antebraço DE LADO (braços cruzados embaixo da
# cabeça), o cotovelo gira em Y, não em X: em X ele dobraria para cima.
POSE_SENTADO = {
    "PernaDirQuadril": (-88, 0, -4), "PernaDirJoelho": (82, 0, 0), "PernaDirTornozelo": (6, 0, 0),
    "PernaEsqQuadril": (-86, 0, 6), "PernaEsqJoelho": (78, 0, 0), "PernaEsqTornozelo": (8, 0, 0),
}
# Braços de quem está sentado com as mãos no colo (poses 4 a 7).
BRACOS_COLO = {"BracoDirOmbro": (-18, -8, 0), "BracoDirCotovelo": (-80, 0, 0),
               "BracoEsqOmbro": (-16, 8, 0), "BracoEsqCotovelo": (-82, 0, 0)}

POSES = [
    # 0 — dormindo: debruçado, cabeça deitada de lado em cima dos braços cruzados.
    {"Tronco": (50, 0, 4), "Cabeca": (35, 45, -10),
     "BracoDirOmbro": (-135, -12, 0), "BracoDirCotovelo": (0, -100, 0),
     "BracoEsqOmbro": (-135, 12, 0), "BracoEsqCotovelo": (0, 100, 0)},
    # 1 — dormindo, respirando (as costas sobem um pouco).
    {"Tronco": (46, 0, 4), "Cabeca": (39, 45, -10),
     "BracoDirOmbro": (-131, -12, 0), "BracoDirCotovelo": (0, -100, 0),
     "BracoEsqOmbro": (-131, 12, 0), "BracoEsqCotovelo": (0, 100, 0)},
    # 2 — se mexe: a cabeça desgruda dos braços.
    {"Tronco": (44, 0, 2), "Cabeca": (20, 18, -4),
     "BracoDirOmbro": (-129, -12, 0), "BracoDirCotovelo": (0, -95, 0),
     "BracoEsqOmbro": (-129, 12, 0), "BracoEsqCotovelo": (0, 95, 0)},
    # 3 — se ergue, empurrando a mesa com as mãos.
    {"Tronco": (25, 0, 0), "Cabeca": (8, 4, 0),
     "BracoDirOmbro": (-85, -10, 0), "BracoDirCotovelo": (-30, 0, 0),
     "BracoEsqOmbro": (-85, 10, 0), "BracoEsqCotovelo": (-30, 0, 0)},
    # 4 — sentado, olhando para o monitor.
    {"Tronco": (8, 0, 0), "Cabeca": (4, 0, 0), **BRACOS_COLO},
    # 5 — olha para cima: o teto não existe mais.
    {"Tronco": (2, 0, 0), "Cabeca": (-34, 0, 0), **BRACOS_COLO},
    # 6 — olha para a esquerda (as estantes caídas).
    {"Tronco": (6, 0, 12), "Cabeca": (0, 0, 55), **BRACOS_COLO},
    # 7 — olha para a direita (a árvore): o rosto aparece de perfil.
    {"Tronco": (6, 0, -14), "Cabeca": (-4, 0, -62), **BRACOS_COLO},
]
NOMES_POSES = ["dormindo", "respirando", "mexendo", "erguendo", "sentado",
               "olhando_cima", "olhando_esquerda", "olhando_direita"]


def montar_gabriel(col):
    """Monta o Gabriel (gerar_gabriel.montar) e a cadeira. Devolve a raiz,
    os pivôs por nome e os materiais (para o passe de ID)."""
    c.COLECAO_ATUAL = col
    materiais, mt = gabriel.criar_materiais()
    raiz = gabriel.montar(mt)
    # A mochila fica no chão, do lado da cadeira (ninguém dorme de mochila):
    # escondemos a que vem presa nas costas do modelo.
    for obj in list(col.objects):
        if obj.name.startswith(("Mochila", "Alca")):
            obj.hide_render = True
            obj.hide_viewport = True
    pivos = {o.name: o for o in col.objects if o.type == 'EMPTY'}

    # Cadeira de escritório (a do menu), enferrujada, com materiais do
    # mesmo sistema do Gabriel (rampa de 4 tons).
    m_cad = materiais.novo("cadeira", "#3a3c42")
    m_fer = materiais.novo("cadeira_ferrugem", "#6e4a34")
    cad = c.pivo("Cadeira", (0, 0, 0))
    c.caixa("CadeiraAssento", (0.44, 0.42, 0.07), (0, 0, 0.44), m_cad, cad, bisel=0.02)
    c.caixa("CadeiraEncosto", (0.40, 0.05, 0.20), (0, 0.24, 0.66), m_cad, cad, (-8, 0, 0), bisel=0.03)
    c.caixa("CadeiraHasteEncosto", (0.05, 0.04, 0.16), (0, 0.23, 0.50), m_fer, cad)
    c.cone("CadeiraColuna", 0.03, 0.03, 0.36, (0, 0, 0.23), m_fer, cad, lados=6)
    for i in range(5):
        pe = c.caixa(f"CadeiraPe{i}", (0.05, 0.30, 0.04), (0, 0, 0.04), m_fer, cad, (0, 0, 72 * i + 10),
                     desloc=(0, 0.15, 0))
    # Mochila no chão, encostada na cadeira.
    moch = c.pivo("MochilaChao", (-0.42, 0.10, 0.0), None, (0, 0, 25))
    c.caixa("MochilaChaoCorpo", (0.31, 0.17, 0.38), (0, 0, 0.19), mt["mochila"], moch, (-10, 0, 0), bisel=0.04)
    c.caixa("MochilaChaoBolso", (0.25, 0.06, 0.16), (0, -0.10, 0.12), mt["mochila_escura"], moch, (-10, 0, 0), bisel=0.02)
    c.caixa("MochilaChaoAlca", (0.05, 0.04, 0.30), (0.08, 0.10, 0.20), mt["mochila_escura"], moch, (-10, 0, 0))

    # Tudo junto num pivô só, virado para a mesa (+Y) e na escala da cena.
    # O modelo olha para -Y; girando 180° em Z ele passa a olhar para +Y.
    grupo = c.pivo("GabrielNaCena", (0, 0, 0))
    for o in (raiz, cad, moch):
        o.parent = grupo
    grupo.rotation_euler = (0, 0, math.radians(168))   # 12° virado para o monitor
    grupo.scale = (ESCALA_GABRIEL,) * 3
    # O quadril do modelo fica 0,88 m acima da raiz; sentado, ele desce até o
    # assento (0,47 m). A cadeira fica embaixo do quadril.
    raiz.location = (0, 0, 0.51 - 0.88)
    cad.location = (0, 0.06, 0)
    grupo.location = (QUADRIL_CENA.x, QUADRIL_CENA.y, CHAO_Z)
    for nome, rot in POSE_SENTADO.items():
        pivos[nome].rotation_euler = [math.radians(a) for a in rot]
    return grupo, pivos, materiais


def posar(pivos, pose):
    for nome, rot in pose.items():
        pivos[nome].rotation_euler = [math.radians(a) for a in rot]


# ---------------------------------------------------------------------------
# Luz
# ---------------------------------------------------------------------------

def criar_luzes():
    """Sol entrando pelo rombo do teto + céu. Nenhuma luz elétrica: nada
    elétrico funciona depois de mil anos (docs/gdd.md, item 2)."""
    # Direção em que a luz do sol ANDA: para a direita, um pouco para dentro
    # da cena e bem para baixo (sol alto, vindo da esquerda): entra pelo
    # rombo do teto e bate na parede, na mesa e nas costas do Gabriel.
    direcao = Vector((0.50, 0.15, -0.85)).normalized()
    dados = bpy.data.lights.new("Sol", 'SUN')
    dados.energy = 6.0
    dados.angle = math.radians(1.5)          # sombra bem recortada
    dados.color = (1.0, 0.93, 0.78)          # sol de manhã, quente
    sol = bpy.data.objects.new("Sol", dados)
    # A luz SUN aponta para o -Z dela: giramos -Z para a direção desejada.
    sol.rotation_euler = direcao.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(sol)

    # Céu claro e frio: ilumina as sombras de azul (contraste quente x frio).
    mundo = bpy.data.worlds.new("Ceu")
    try:
        mundo.use_nodes = True
    except Exception:
        pass
    fundo = mundo.node_tree.nodes.get("Background")
    fundo.inputs["Color"].default_value = (*menu.hex_para_linear("#b4d2e6"), 1)
    fundo.inputs["Strength"].default_value = 0.7
    bpy.context.scene.world = mundo


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def configurar_render():
    cena = c.cena_vazia()           # Cycles CPU, filtro mínimo, sem denoise, Standard
    cena.cycles.samples = 1024
    cena.cycles.max_bounces = 4
    cena.render.resolution_x = LARGURA * (ESCALA_PREVIA if PREVIA else 1)
    cena.render.resolution_y = ALTURA * (ESCALA_PREVIA if PREVIA else 1)
    if PREVIA:
        cena.cycles.samples = 48
        if os.environ.get("ZOOM"):
            # Só o pedaço em volta do Gabriel, bem ampliado, para ver a pose.
            cena.render.resolution_x = LARGURA * 6
            cena.render.resolution_y = ALTURA * 6
            cena.render.use_border = True
            cena.render.use_crop_to_border = True
            cena.render.border_min_x, cena.render.border_max_x = 0.28, 0.62
            cena.render.border_min_y, cena.render.border_max_y = 0.05, 0.55
    return cena


def renderizar(caminho, transparente=True, amostras=None):
    cena = bpy.context.scene
    cena.render.film_transparent = transparente
    if amostras:
        cena.cycles.samples = amostras
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    return c._ler_png(caminho)


def mostrar_camada(colecoes, visivel, holdout=()):
    """Deixa visíveis para a câmera só as coleções em 'visivel'. As de
    'holdout' aparecem como BURACO (alfa 0): tapam o que está atrás delas,
    mas não aparecem. Todas continuam fazendo sombra."""
    for nome, col in colecoes.items():
        for obj in col.all_objects:
            obj.visible_camera = nome in visivel or nome in holdout
            obj.is_holdout = nome in holdout


# --- Paleta do cenário: k-means no espaço CIELAB ----------------------------
#
# O render tem milhares de tons. Queremos poucos (pixel art). O k-means
# escolhe os K tons que melhor representam a imagem:
#   1. começa com K cores sorteadas entre os pixels;
#   2. cada pixel "vota" na cor mais próxima (distância no Lab, que é
#      parecida com a diferença que o olho percebe);
#   3. cada cor vira a MÉDIA dos pixels que votaram nela;
#   4. repete 2 e 3 até estabilizar.
# No fim trocamos cada pixel pela cor da paleta mais próxima.

def paleta_kmeans(imagens, k, iteracoes=30, semente=7):
    rgb = np.concatenate([im[im[..., 3] > 0][:, :3] for im in imagens]).astype(np.float64)
    lab = c.srgb_para_lab(rgb)
    rng = np.random.default_rng(semente)
    amostra = rng.choice(len(lab), min(60000, len(lab)), replace=False)
    pts, pts_rgb = lab[amostra], rgb[amostra]
    centros = pts[rng.choice(len(pts), k, replace=False)].copy()
    for _ in range(iteracoes):
        voto = ((pts[:, None, :] - centros[None]) ** 2).sum(axis=2).argmin(axis=1)
        for j in range(k):
            grupo = pts[voto == j]
            if len(grupo):
                centros[j] = grupo.mean(axis=0)
    # A cor final de cada grupo é o pixel de verdade mais perto do centro
    # (assim não precisamos converter Lab de volta para RGB).
    voto = ((pts[:, None, :] - centros[None]) ** 2).sum(axis=2).argmin(axis=0)
    paleta = np.unique(np.round(pts_rgb[voto] * 255), axis=0) / 255
    return paleta


def aplicar_paleta(img, paleta):
    saida = img.copy()
    opaco = img[..., 3] >= 0.5
    pal_lab = c.srgb_para_lab(paleta)
    px_lab = c.srgb_para_lab(img[opaco][:, :3].astype(np.float64))
    idx = np.concatenate([((bloco[:, None, :] - pal_lab[None]) ** 2).sum(axis=2).argmin(axis=1)
                          for bloco in np.array_split(px_lab, max(1, len(px_lab) // 20000))])
    saida[opaco, :3] = paleta[idx]
    saida[opaco, 3] = 1.0
    saida[~opaco] = 0.0
    return saida


# --- Gabriel: passe de luz + passe de ID (comum.py, item 5) -----------------

# Degraus de luz (ver comum.DEGRAUS_LUZ). Aqui a luz é a do sol e do céu,
# mais forte que a do estúdio dos personagens. Rodando com DEBUG_LUZ=1, o
# histograma mostra dois grupos: a sombra da cabine (luz do céu, 0,55 a
# 0,8) e o sol direto (0,985 ou mais: estoura no branco). Então:
#   abaixo de 0,55 = sombra funda (dobras, embaixo do braço)
#   0,55 a 0,68   = sombra (lado virado para longe do céu)
#   0,68 a 0,985  = luz (lado virado para o céu)
#   acima         = brilho (mancha de sol que entra pelo teto)
DEGRAUS_LUZ = (0.55, 0.68, 0.985)


def renderizar_gabriel(pasta_tmp, materiais):
    """Um quadro do Gabriel na pose atual. Devolve RGBA (pixel art) e o
    índice do material em cada pixel."""
    cena = bpy.context.scene
    argila = bpy.data.materials.get("argila_passe_luz") or bpy.data.materials.new("argila_passe_luz")
    argila.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
    bpy.context.view_layer.material_override = argila
    luz = renderizar(os.path.join(pasta_tmp, "luz.png"), amostras=1024)
    bpy.context.view_layer.material_override = None
    materiais.modo_id(True)
    ids = renderizar(os.path.join(pasta_tmp, "id.png"), amostras=1)
    materiais.modo_id(False)

    alfa = ids[..., 3] >= 0.5
    r = np.round(ids[..., 0] * 255 / 8).astype(int) - 1
    g = np.round(ids[..., 1] * 255 / 8).astype(int) - 1
    indice = np.clip(g * 31 + r, 0, len(materiais.lista) - 1)
    lum = luz[..., 0] * 0.2126 + luz[..., 1] * 0.7152 + luz[..., 2] * 0.0722
    if os.environ.get("DEBUG_LUZ"):
        hist, _ = np.histogram(lum[alfa], bins=20, range=(0, 1))
        print("[luz]", " ".join(str(v) for v in hist))
    degrau = np.digitize(lum, DEGRAUS_LUZ)
    rampas = np.array(materiais.rampas())
    saida = np.zeros(ids.shape, dtype=np.float32)
    saida[..., :3] = rampas[indice, degrau]
    saida[..., 3] = alfa
    saida[~alfa] = 0
    return saida, np.where(alfa, indice, -1)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    configurar_render()
    cam = criar_camera()
    mt = criar_materiais_cenario()
    colecoes = {nome: menu.colecao(nome) for nome in ("fundo", "meio", "gabriel", "frente")}
    grupo, pivos, materiais = montar_gabriel(colecoes["gabriel"])
    montar_fundo(mt, colecoes["fundo"])
    montar_meio(mt, colecoes["meio"])
    montar_frente(mt, colecoes["frente"])
    criar_luzes()

    for nome, p in {"cabeca_dormindo": (-12, -4, 6), "monitor": (0, 0, 7), "arvore": (ARVORE.x, ARVORE.y, 40),
                    "rombo_teto": (15, 5, TETO_Z)}.items():
        x, y = projetar(cam, p)
        print(f"[seg_acordar] {nome} cai em x={x:.0f} y={y:.0f} (pixels do jogo)")

    pasta_tmp = os.path.join(os.environ.get("TEMP", "/tmp"), "seg_acordar_render")
    os.makedirs(pasta_tmp, exist_ok=True)

    if PREVIA:
        # Tudo junto, com cores "de verdade" (sem paleta), para conferir o
        # enquadramento e a pose.
        posar(pivos, POSES[int(os.environ.get("POSE", "0"))])
        mostrar_camada(colecoes, set(colecoes))
        caminho = os.path.join(pasta_tmp, f"previa_{os.environ.get('POSE', '0')}.png")
        renderizar(caminho, transparente=False)
        print(f"[seg_acordar] prévia salva em {caminho}")
        return

    os.makedirs(PASTA_SAIDA, exist_ok=True)
    posar(pivos, POSES[0])

    # 1. Cenário: três camadas. O fundo inclui o céu (sem transparência).
    camadas = {}
    for nome in ("fundo", "meio", "frente"):
        mostrar_camada(colecoes, {nome})
        camadas[nome] = renderizar(os.path.join(pasta_tmp, f"{nome}.png"), transparente=(nome != "fundo"))
        print(f"[seg_acordar] camada {nome} renderizada")
    paleta = paleta_kmeans(list(camadas.values()), k=40)
    print(f"[seg_acordar] paleta do cenário: {len(paleta)} cores")
    for nome, img in camadas.items():
        c.salvar_png(aplicar_paleta(img, paleta), os.path.join(PASTA_SAIDA, f"seg_acordar_{nome}.png"))

    # 2. Gabriel: um quadro por pose. A mesa (meio) é holdout: o que dele
    # fica embaixo do tampo some. Fundo e frente somem da câmera.
    mostrar_camada(colecoes, {"gabriel"}, holdout={"meio"})
    quadros = []
    for i, pose in enumerate(POSES):
        posar(pivos, pose)
        img, indice = renderizar_gabriel(pasta_tmp, materiais)
        quadros.append(c.contorno(img, indice, materiais))
        print(f"[seg_acordar] quadro {i} ({NOMES_POSES[i]}) renderizado")
    quadros, pal_gabriel = c.unificar_paleta(quadros, materiais, 32)

    # Recorta todos os quadros no MESMO retângulo (o que cobre todos) e
    # monta a folha lado a lado. No Godot: Sprite2D com hframes = número de
    # quadros, posicionado no canto do recorte.
    ocupado = np.any([q[..., 3] > 0 for q in quadros], axis=0)
    linhas, colunas = ocupado.any(axis=1).nonzero()[0], ocupado.any(axis=0).nonzero()[0]
    y0, y1, x0, x1 = linhas[0], linhas[-1] + 1, colunas[0], colunas[-1] + 1
    folha = np.concatenate([q[y0:y1, x0:x1] for q in quadros], axis=1)
    c.salvar_png(folha, os.path.join(PASTA_SAIDA, "seg_acordar_gabriel.png"))
    print(f"[seg_acordar] Gabriel: {len(quadros)} quadros de {x1 - x0}x{y1 - y0} px; "
          f"canto do recorte na imagem com margem: ({x0}, {y0}) -> no jogo ({x0 - MARGEM}, {y0 - MARGEM})")

    # Deixa tudo visível de novo e salva o .blend.
    posar(pivos, POSES[0])
    mostrar_camada(colecoes, set(colecoes))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=ARQUIVO_BLEND)
    print(f"[seg_acordar] pronto: {PASTA_SAIDA}")


main()
