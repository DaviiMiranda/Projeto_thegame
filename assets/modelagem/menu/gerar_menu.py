# gerar_menu.py — monta no Blender, por código, a cena 3D do menu principal
# e renderiza cada camada de paralaxe como um PNG de pixel art.
#
# Como rodar (não precisa abrir o Blender; ele roda "sem janela"):
#
#   blender -b --factory-startup --python assets/modelagem/menu/gerar_menu.py
#
# O que sai:
#   assets/sprites/menu/menu_fundo.png   parede, estante com livros, relógio
#   assets/sprites/menu/menu_mesa.png    mesa, monitor CRT, teclado, papéis, luminária
#   assets/sprites/menu/menu_frente.png  caneca e cadeira (primeiro plano, silhueta)
#   assets/modelagem/menu/menu.blend     a cena montada, para quem quiser abrir e mexer
#
# A cena: a cabine de estudo da Biblioteca à noite, na véspera das provas.
# Tudo apagado; a única luz é o brilho azulado e frio da tela do monitor.
#
# Ideia geral do script:
#   1. Posicionar a câmera de forma que a TELA do monitor caia exatamente
#      no retângulo x 90–230, y 24–126 da tela do jogo (320×180). É ali
#      que o Godot desenha a Tela, os botões e o efeito CRT.
#   2. Modelar os objetos com caixas e cilindros simples (low poly: na
#      resolução 320×180 detalhe fino não aparece).
#   3. Renderizar três vezes, uma por camada, escondendo da câmera os
#      objetos das outras camadas (mas eles continuam fazendo sombra).
#   4. Reduzir as cores para uma paleta fixa pequena (pixel art) e cortar
#      o alfa em 0 ou 1, sem bordas semitransparentes.
#
# Unidades: 1 unidade do Blender = 2,5 cm. O tampo da mesa fica em z = 0.
# O eixo +Y aponta "para dentro" da cena (para longe da câmera).

import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

# ---------------------------------------------------------------------------
# Pastas
# ---------------------------------------------------------------------------

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.normpath(os.path.join(PASTA_SCRIPT, "..", "..", ".."))
PASTA_SAIDA = os.path.join(PASTA_PROJETO, "assets", "sprites", "menu")
ARQUIVO_BLEND = os.path.join(PASTA_SCRIPT, "menu.blend")

# ---------------------------------------------------------------------------
# Tamanho da imagem
# ---------------------------------------------------------------------------

# O jogo tem 320×180. As camadas se mexem até 10 px para cada lado
# (paralaxe), então renderizamos com 10 px de sobra em cada borda:
# 340×200. No Godot o Sprite2D fica em (-10, -10).
MARGEM = 10
LARGURA = 320 + 2 * MARGEM
ALTURA = 180 + 2 * MARGEM

# Retângulo da tela do monitor, em pixels da IMAGEM (já somada a margem).
# No jogo ele é x 90–230, y 24–126.
TELA_X0, TELA_X1 = 90 + MARGEM, 230 + MARGEM
TELA_Y0, TELA_Y1 = 24 + MARGEM, 126 + MARGEM

# ---------------------------------------------------------------------------
# Câmera
# ---------------------------------------------------------------------------
# Escolha: câmera em PERSPECTIVA leve, olhando reto para a frente (+Y).
#
# Por que perspectiva e não ortográfica? A câmera é o ponto de vista de
# quem está sentado na cabine. Com perspectiva, o que está longe (a
# estante) fica menor e cabe mais dela no quadro, e o que está perto
# (cadeira, caneca) fica grande: isso já é a sensação 2.5D que a
# paralaxe reforça. Numa ortográfica a estante do fundo teria o mesmo
# tamanho da mesa e quase não apareceria atrás do monitor.
#
# Por que olhar RETO (sem inclinar para baixo)? Um plano paralelo ao
# sensor da câmera vira um retângulo perfeito na imagem, mesmo em
# perspectiva. A tela do monitor é um plano vertical em y = 0, então ela
# sai como um retângulo exato, alinhado aos pixels. Para enquadrar
# (mostrar mais mesa embaixo) usamos o "shift" da lente, que desloca o
# quadro sem girar a câmera, como uma câmera de arquitetura.

DIST_TELA = 25.0      # distância da câmera até o plano da tela (62 cm)
OLHO_X = -6.0         # câmera um pouco à esquerda: vemos a lateral do CRT
OLHO_Z = 14.0         # altura do olho acima do tampo (35 cm)
PX_POR_UNIDADE = 10.0 # no plano da tela, 1 unidade = 10 pixels

# Tela do monitor no mundo: plano y = 0. Largura e altura saem do
# tamanho em pixels (140×102 px ÷ 10 px por unidade).
TELA_LARG = (TELA_X1 - TELA_X0) / PX_POR_UNIDADE   # 14,0
TELA_ALT = (TELA_Y1 - TELA_Y0) / PX_POR_UNIDADE    # 10,2
TELA_Z0 = 2.0                                       # base da tela (acima do tampo)
TELA_Z1 = TELA_Z0 + TELA_ALT
TELA_XC = 0.0                                       # a tela é centrada em x = 0


def criar_camera():
    dados = bpy.data.cameras.new("Camera")
    dados.type = 'PERSP'
    dados.sensor_fit = 'HORIZONTAL'
    dados.sensor_width = 36.0
    # Semelhança de triângulos: largura visível a uma distância d é
    # d * sensor / lente. Queremos 340 px = 34 unidades a 25 unidades.
    largura_visivel = LARGURA / PX_POR_UNIDADE
    dados.lens = dados.sensor_width * DIST_TELA / largura_visivel
    # Shift: quanto o quadro anda, em fração da largura da imagem.
    # Horizontal: o centro da tela (x = 0) está 6 unidades à direita do
    # olho; sem shift ele cairia em 170 + 60 px. Queremos que caia no
    # centro do retângulo da tela.
    centro_tela_px_x = (TELA_X0 + TELA_X1) / 2
    desvio_x_px = (TELA_XC - OLHO_X) * PX_POR_UNIDADE - (centro_tela_px_x - LARGURA / 2)
    dados.shift_x = desvio_x_px / LARGURA
    # Vertical: o centro da tela está abaixo do olho. (Em pixels, y cresce
    # para baixo; no Blender, shift_y positivo sobe o quadro.)
    centro_tela_px_y = (TELA_Y0 + TELA_Y1) / 2
    desvio_y_px = (OLHO_Z - (TELA_Z0 + TELA_Z1) / 2) * PX_POR_UNIDADE - (centro_tela_px_y - ALTURA / 2)
    dados.shift_y = -desvio_y_px / LARGURA
    dados.clip_start = 0.5
    dados.clip_end = 500.0

    cam = bpy.data.objects.new("Camera", dados)
    cam.location = (OLHO_X, -DIST_TELA, OLHO_Z)
    cam.rotation_euler = (math.radians(90), 0, 0)  # olhando para +Y
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


# ---------------------------------------------------------------------------
# Cores e materiais
# ---------------------------------------------------------------------------

def hex_para_linear(hexa):
    """Converte '#rrggbb' (sRGB, como num editor de imagem) para RGB linear,
    que é o espaço em que o Blender faz as contas de luz."""
    hexa = hexa.lstrip("#")
    srgb = [int(hexa[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def material(nome, cor_hex, aspereza=0.7, emissao_hex=None, forca_emissao=0.0):
    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*hex_para_linear(cor_hex), 1)
    bsdf.inputs["Roughness"].default_value = aspereza
    if emissao_hex:
        bsdf.inputs["Emission Color"].default_value = (*hex_para_linear(emissao_hex), 1)
        bsdf.inputs["Emission Strength"].default_value = forca_emissao
    return mat


# ---------------------------------------------------------------------------
# Construção de malhas simples
# ---------------------------------------------------------------------------

def colecao(nome):
    col = bpy.data.collections.new(nome)
    bpy.context.scene.collection.children.link(col)
    return col


def objeto_de_bmesh(nome, bm, mat, col):
    malha = bpy.data.meshes.new(nome)
    bm.to_mesh(malha)
    bm.free()
    obj = bpy.data.objects.new(nome, malha)
    if isinstance(mat, list):
        for m in mat:
            obj.data.materials.append(m)
    else:
        obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj


def cubo_em(bm, x0, x1, y0, y1, z0, z1, indice_material=0):
    """Acrescenta ao bmesh uma caixa alinhada aos eixos, de (x0,y0,z0) a (x1,y1,z1)."""
    centro = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    escala = Matrix.Diagonal((x1 - x0, y1 - y0, z1 - z0, 1))
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(centro) @ escala)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = indice_material


def caixa(nome, x0, x1, y0, y1, z0, z1, mat, col):
    bm = bmesh.new()
    cubo_em(bm, x0, x1, y0, y1, z0, z1)
    return objeto_de_bmesh(nome, bm, mat, col)


def cilindro(nome, raio, altura, mat, col, lados=16, raio_topo=None):
    """Cilindro (ou cone, se raio_topo for diferente) com a base em z = 0."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=lados,
                          radius1=raio, radius2=raio if raio_topo is None else raio_topo,
                          depth=altura, matrix=Matrix.Translation((0, 0, altura / 2)))
    return objeto_de_bmesh(nome, bm, mat, col)


def chanfro(obj, largura=0.3, segmentos=2):
    """Bisel nas quinas: pega um pouco de luz na borda e ajuda a ler a forma."""
    mod = obj.modifiers.new("Bisel", 'BEVEL')
    mod.width = largura
    mod.segments = segmentos
    return obj


# ---------------------------------------------------------------------------
# A cena
# ---------------------------------------------------------------------------

def estante(nome, ex0, ex1, parede_y, m_madeira, m_livros, col):
    """Estante de 2 m encostada na parede, de x = ex0 a x = ex1, cheia de
    livros de largura, altura e cor sorteadas."""
    ey0, ey1 = parede_y - 12, parede_y
    ez0, ez1 = -30.0, 50.0
    bm = bmesh.new()
    cubo_em(bm, ex0, ex0 + 1.2, ey0, ey1, ez0, ez1)          # lateral esquerda
    cubo_em(bm, ex1 - 1.2, ex1, ey0, ey1, ez0, ez1)          # lateral direita
    cubo_em(bm, ex0, ex1, ey1 - 0.5, ey1, ez0, ez1)          # fundo da estante
    prateleiras = [-30.0, -16.0, -2.0, 12.0, 26.0, 40.0]
    for z in prateleiras:
        cubo_em(bm, ex0, ex1, ey0, ey1, z, z + 1.0)
    objeto_de_bmesh(nome, bm, m_madeira, col)

    # Alguns livros tombados e algumas prateleiras com buracos
    # (a Biblioteca já está meio vazia).
    bm = bmesh.new()
    for z in prateleiras[:-1]:
        x = ex0 + 1.4
        base = z + 1.0
        while x < ex1 - 2.5:
            if random.random() < 0.12:        # buraco na prateleira
                x += random.uniform(1.5, 4.0)
                continue
            larg = random.uniform(0.9, 2.0)
            alt = random.uniform(8.0, 12.0)
            prof = random.uniform(7.0, 9.5)
            if x + larg > ex1 - 1.3:
                break
            if random.random() < 0.08:        # livro deitado
                cubo_em(bm, x, x + alt, ey1 - prof - 0.6, ey1 - 0.6, base, base + larg,
                        random.randrange(len(m_livros)))
                x += alt + 0.2
            else:
                cubo_em(bm, x, x + larg, ey1 - prof - 0.6, ey1 - 0.6, base, base + alt,
                        random.randrange(len(m_livros)))
                x += larg + 0.1
    objeto_de_bmesh(nome + "Livros", bm, m_livros, col)


def montar_cena():
    random.seed(7)  # mesma "aleatoriedade" toda vez: os livros não mudam de uma rodada para outra

    # Paleta de materiais (cores base, antes da luz).
    m_parede = material("parede", "#3a3f4a", 0.9)
    m_madeira = material("madeira", "#6b4a33", 0.55)
    m_madeira_escura = material("madeira_escura", "#3d2a1e", 0.6)
    m_bege = material("plastico_bege", "#b8ae98", 0.45)
    m_bege_escuro = material("plastico_bege_escuro", "#8a8272", 0.5)
    m_vidro = material("vidro_tela", "#05080c", 0.15, "#1a3a66", 0.6)
    m_tecla = material("tecla", "#c4bba6", 0.5)
    m_papel = material("papel", "#e6e2d6", 0.8)
    m_caderno = material("caderno", "#2f4f6f", 0.6)
    m_caderno2 = material("caderno_vermelho", "#6f2f2f", 0.6)
    m_metal = material("metal_escuro", "#2a2c30", 0.35)
    m_caneca = material("caneca", "#d8d4cc", 0.3)
    m_cadeira = material("cadeira", "#1c1d22", 0.7)
    m_relogio = material("relogio", "#d0ccc0", 0.5)
    m_preto = material("preto", "#0a0a0a", 0.6)
    m_bilhete = material("bilhete", "#b8ad62", 0.8)
    cores_livros = ["#5a2a2a", "#2a4a3a", "#2a3a5a", "#6a5a3a", "#4a2a4a",
                    "#3a3a3a", "#7a6a50", "#2a2a2a", "#5a4030"]
    m_livros = [material(f"livro_{i}", c, 0.8) for i, c in enumerate(cores_livros)]

    fundo = colecao("fundo")
    mesa = colecao("mesa")
    frente = colecao("frente")

    # ---------------- FUNDO ----------------
    PAREDE_Y = 60.0
    caixa("Parede", -120, 120, PAREDE_Y, PAREDE_Y + 1, -40, 80, m_parede, fundo)
    caixa("Chao", -120, 120, -40, PAREDE_Y, -31, -30, m_madeira_escura, fundo)

    # Duas estantes encostadas na parede, uma de cada lado do monitor.
    estante("EstanteEsquerda", -46.0, -12.0, PAREDE_Y, m_madeira_escura, m_livros, fundo)
    estante("EstanteDireita", 50.0, 84.0, PAREDE_Y, m_madeira_escura, m_livros, fundo)

    # Relógio de parede, parado perto da meia-noite.
    RX, RZ = 46.0, 11.0
    relogio = cilindro("Relogio", 4.0, 0.8, m_relogio, fundo, lados=24)
    relogio.rotation_euler = (math.radians(90), 0, 0)
    relogio.location = (RX, PAREDE_Y, RZ)
    aro = cilindro("RelogioAro", 4.4, 0.6, m_preto, fundo, lados=24)
    aro.rotation_euler = (math.radians(90), 0, 0)
    aro.location = (RX, PAREDE_Y + 0.2, RZ)
    ponteiro_h = caixa("PonteiroHora", -0.25, 0.25, -0.1, 0.1, 0, 2.2, m_preto, fundo)
    ponteiro_h.location = (RX, PAREDE_Y - 0.9, RZ)
    ponteiro_h.rotation_euler = (0, math.radians(-10), 0)    # quase 12
    ponteiro_m = caixa("PonteiroMinuto", -0.15, 0.15, -0.1, 0.1, 0, 3.3, m_preto, fundo)
    ponteiro_m.location = (RX, PAREDE_Y - 0.9, RZ)
    ponteiro_m.rotation_euler = (0, math.radians(20), 0)      # 23h55

    # ---------------- MESA ----------------
    # Tampo: vai de bem na frente (fora do quadro) até atrás do monitor.
    MESA_Y1 = 14.0
    caixa("Tampo", -60, 60, -14, MESA_Y1, -1.5, 0, m_madeira, mesa)

    # Monitor CRT. A moldura é uma caixa com um buraco do tamanho da tela
    # (modificador Boolean: caixa MENOS o buraco), com a face da frente
    # exatamente no plano y = 0. Assim a borda do buraco coincide com o
    # retângulo de pixels da tela. Depois um bisel arredonda as quinas,
    # como o plástico dos monitores antigos.
    tx0, tx1 = TELA_XC - TELA_LARG / 2, TELA_XC + TELA_LARG / 2
    mold = 1.4  # largura da moldura
    moldura = caixa("MonitorMoldura", tx0 - mold, tx1 + mold, 0, 3.0, 0.4, TELA_Z1 + mold + 0.3, m_bege, mesa)
    buraco = caixa("MonitorBuraco", tx0, tx1, -1.0, 1.0, TELA_Z0, TELA_Z1, m_bege, mesa)
    buraco.hide_render = True
    buraco.hide_viewport = True
    furo = moldura.modifiers.new("Buraco", 'BOOLEAN')
    furo.operation = 'DIFFERENCE'
    furo.object = buraco
    chanfro(moldura, 0.35, 2)
    # Bilhete colado na moldura: a véspera da prova.
    # Fica na parte de baixo da moldura, fora do retângulo da tela.
    bilhete = caixa("Bilhete", -0.8, 0.8, -0.05, 0.0, -0.75, 0.75, m_bilhete, mesa)
    bilhete.location = (tx0 + 1.6, 0.0, 1.15)
    bilhete.rotation_euler = (0, math.radians(8), 0)
    # Corpo do tubo: uma caixa menor atrás, afinando (o "traseiro" do CRT).
    bm = bmesh.new()
    cubo_em(bm, tx0 - mold + 0.6, tx1 + mold - 0.6, 3.0, 9.0, 0.8, TELA_Z1 + mold - 0.2)
    cubo_em(bm, tx0 + 1.5, tx1 - 1.5, 9.0, 15.0, 2.0, TELA_Z1 - 1.0)
    objeto_de_bmesh("MonitorCorpo", bm, m_bege_escuro, mesa)
    # Pezinho giratório.
    caixa("MonitorPe", -5, 5, 1.0, 11.0, 0, 0.5, m_bege_escuro, mesa)
    # Botão de ligar e LED (apagado — só a tela está viva).
    caixa("MonitorBotao", tx1 - 1.8, tx1 - 0.8, -0.2, 0.1, 0.9, 1.5, m_bege_escuro, mesa)
    # Vidro da tela, um pouco para dentro da moldura.
    caixa("MonitorVidro", tx0, tx1, 0.3, 0.5, TELA_Z0, TELA_Z1, m_vidro, mesa)

    # Teclado bege: base + grade de teclas (a barra de espaço é uma tecla comprida).
    bm = bmesh.new()
    kx0, kx1, ky0, ky1 = -6.5, 6.5, -5.6, -1.6
    cubo_em(bm, kx0, kx1, ky0, ky1, 0, 0.6)
    colunas, linhas = 15, 5
    passo_x = (kx1 - kx0 - 0.6) / colunas
    passo_y = (ky1 - ky0 - 0.6) / linhas
    for i in range(colunas):
        for j in range(linhas):
            if j == 0 and 3 <= i <= 10 and i != 3:
                continue  # espaço da barra de espaço
            x = kx0 + 0.3 + i * passo_x
            y = ky0 + 0.3 + j * passo_y
            cubo_em(bm, x + 0.06, x + passo_x - 0.06, y + 0.06, y + passo_y - 0.06, 0.6, 0.95, 1)
    cubo_em(bm, kx0 + 0.3 + 4 * passo_x, kx0 + 0.3 + 11 * passo_x - 0.06,
            ky0 + 0.36, ky0 + 0.3 + passo_y - 0.06, 0.6, 0.95, 1)  # barra de espaço
    objeto_de_bmesh("Teclado", bm, [m_bege_escuro, m_tecla], mesa)

    # Papéis soltos e cadernos: a véspera da prova.
    for i, (x, y, ang) in enumerate([(-15.0, -4.0, 12), (-11.5, -6.5, -8), (12.5, -1.0, 25)]):
        p = caixa(f"Papel{i}", -2.6, 2.6, -3.4, 3.4, 0, 0.05, m_papel, mesa)
        p.location = (x, y, 0.02 * i)
        p.rotation_euler = (0, 0, math.radians(ang))
    c1 = caixa("Caderno", -3.2, 3.2, -4.2, 4.2, 0, 0.7, m_caderno, mesa)
    c1.location = (-12.5, -1.5, 0)
    c1.rotation_euler = (0, 0, math.radians(-6))
    c2 = caixa("CadernoVermelho", -3.0, 3.0, -4.0, 4.0, 0, 0.6, m_caderno2, mesa)
    c2.location = (-12.0, -1.2, 0.7)
    c2.rotation_euler = (0, 0, math.radians(9))
    livro = caixa("LivroMesa", -3.5, 3.5, -4.8, 4.8, 0, 1.6, m_livros[2], mesa)
    livro.location = (-12.7, -1.4, 1.3)
    livro.rotation_euler = (0, 0, math.radians(2))
    # Um lápis largado.
    lapis = caixa("Lapis", -3.0, 3.0, -0.12, 0.12, 0, 0.24, m_livros[6], mesa)
    lapis.location = (-11.0, -3.0, 0.1)
    lapis.rotation_euler = (0, 0, math.radians(30))

    # Luminária de mesa APAGADA, à direita do monitor.
    lx, ly = 13.0, 9.0
    base = cilindro("LuminariaBase", 2.2, 0.6, m_metal, mesa, lados=16)
    base.location = (lx, ly, 0)
    haste1 = caixa("LuminariaHaste1", -0.25, 0.25, -0.25, 0.25, 0, 10.0, m_metal, mesa)
    haste1.location = (lx, ly, 0.5)
    haste1.rotation_euler = (math.radians(-12), 0, math.radians(0))
    haste2 = caixa("LuminariaHaste2", -0.25, 0.25, -0.25, 0.25, 0, 7.0, m_metal, mesa)
    haste2.location = (lx, ly - 2.0, 10.2)
    haste2.rotation_euler = (math.radians(-110), 0, math.radians(-25))
    cupula = cilindro("LuminariaCupula", 2.6, 3.5, m_metal, mesa, lados=16, raio_topo=0.8)
    cupula.location = (lx - 2.6, ly - 8.0, 9.0)
    cupula.rotation_euler = (math.radians(200), math.radians(20), 0)

    # ---------------- FRENTE ----------------
    # Caneca na ponta direita da mesa (esfriou há horas).
    caneca = cilindro("Caneca", 1.3, 3.4, m_caneca, frente, lados=20)
    caneca.location = (11.0, -2.0, 0)
    # Alça: um toro (rosquinha) em pé, meio enfiado na lateral da caneca.
    bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.22,
                                     major_segments=16, minor_segments=6,
                                     location=(11.0 + 1.25, -2.0, 1.8),
                                     rotation=(math.radians(90), 0, 0))
    alca = bpy.context.active_object
    alca.name = "CanecaAlca"
    alca.data.materials.append(m_caneca)
    for c in alca.users_collection:
        c.objects.unlink(alca)
    frente.objects.link(alca)

    # Cadeira de escritório, afastada para a esquerda, vista de costas.
    encosto = chanfro(caixa("CadeiraEncosto", -7.0, 7.0, -1.2, 1.2, -9.0, 7.5, m_cadeira, frente), 1.0, 3)
    encosto.location = (-15.0, -13.0, -1.5)
    encosto.rotation_euler = (math.radians(-8), 0, math.radians(18))
    assento = chanfro(caixa("CadeiraAssento", -7.5, 7.5, -7.5, 7.5, -12.5, -10.0, m_cadeira, frente), 0.8, 2)
    assento.location = (-14.0, -7.0, 0)
    assento.rotation_euler = (0, 0, math.radians(18))

    return {"fundo": fundo, "mesa": mesa, "frente": frente}


def criar_luzes():
    """A tela é a única fonte de luz: uma luz de área do tamanho da tela,
    colada no vidro, virada para a frente (para a câmera)."""
    cor_tela = (0.45, 0.65, 1.0)  # a mesma cor da PointLight2D do Godot

    dados = bpy.data.lights.new("LuzTela", 'AREA')
    dados.shape = 'RECTANGLE'
    dados.size = TELA_LARG
    dados.size_y = TELA_ALT
    dados.color = cor_tela
    dados.energy = 900.0
    luz = bpy.data.objects.new("LuzTela", dados)
    # Luz de área aponta para o -Z local. Girando 90° em X ela aponta para -Y.
    luz.rotation_euler = (math.radians(-90), 0, 0)
    luz.location = (TELA_XC, -0.05, (TELA_Z0 + TELA_Z1) / 2)
    bpy.context.scene.collection.objects.link(luz)

    # Luz rebatida: a tela ilumina o teto e as costas de quem está sentado,
    # e isso volta, bem fraco, para a estante do fundo. Sem ela o fundo
    # seria preto puro e a estante sumiria.
    dados2 = bpy.data.lights.new("LuzRebatida", 'AREA')
    dados2.shape = 'DISK'
    dados2.size = 40.0
    dados2.color = (0.35, 0.5, 0.85)
    dados2.energy = 30000.0
    reb = bpy.data.objects.new("LuzRebatida", dados2)
    reb.location = (0, 0, 55.0)
    reb.rotation_euler = (math.radians(35), 0, 0)  # do alto, virada para o fundo (+Y)
    bpy.context.scene.collection.objects.link(reb)

    # Rebatida frontal, bem fraca: a luz da tela volta do corpo de quem está
    # sentado e do teto e bate de leve na moldura do monitor e na mesa.
    dados3 = bpy.data.lights.new("LuzRebatidaFrente", 'AREA')
    dados3.shape = 'DISK'
    dados3.size = 30.0
    dados3.color = (0.4, 0.55, 0.9)
    dados3.energy = 1500.0
    reb2 = bpy.data.objects.new("LuzRebatidaFrente", dados3)
    reb2.location = (0, -30.0, 30.0)
    reb2.rotation_euler = (math.radians(60), 0, 0)  # vinda de trás da câmera, do alto
    bpy.context.scene.collection.objects.link(reb2)

    # Mundo quase preto, levemente azul: só para as silhuetas não sumirem.
    mundo = bpy.data.worlds.new("Noite")
    mundo.use_nodes = True
    fundo = mundo.node_tree.nodes.get("Background")
    fundo.inputs["Color"].default_value = (*hex_para_linear("#0c1220"), 1)
    fundo.inputs["Strength"].default_value = 0.6
    bpy.context.scene.world = mundo


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def configurar_render():
    cena = bpy.context.scene
    cena.render.engine = 'CYCLES'
    # Cycles na CPU funciona em qualquer máquina, até sem janela (-b).
    # A imagem é minúscula (340×200), então muitas amostras custam pouco
    # e evitam ruído, que viraria "sujeira" depois da redução de paleta.
    cena.cycles.device = 'CPU'
    cena.cycles.samples = 1024
    cena.cycles.use_denoising = False       # o denoiser borra; pixel art não pode borrar
    cena.cycles.use_adaptive_sampling = False
    cena.cycles.max_bounces = 4
    # Filtro de pixel quase zero = sem antialiasing: cada pixel é "um
    # ponto" da cena, com borda dura, como pixel art.
    cena.cycles.filter_width = 0.01
    cena.render.resolution_x = LARGURA
    cena.render.resolution_y = ALTURA
    cena.render.resolution_percentage = 100
    cena.render.film_transparent = True     # fundo transparente (alfa)
    cena.render.image_settings.file_format = 'PNG'
    cena.render.image_settings.color_mode = 'RGBA'
    cena.render.image_settings.color_depth = '8'
    # "Standard" = cores sem curva de filme: o que a gente pinta é o que sai.
    cena.view_settings.view_transform = 'Standard'
    cena.view_settings.look = 'None'
    cena.view_settings.exposure = 0.0
    cena.view_settings.gamma = 1.0


def conferir_alinhamento(cam):
    """Projeta os cantos da tela e imprime onde caíram, em pixels do jogo."""
    cena = bpy.context.scene
    bpy.context.view_layer.update()  # atualiza as matrizes antes de projetar
    for nome, (x, z) in {"sup_esq": (TELA_XC - TELA_LARG / 2, TELA_Z1),
                         "inf_dir": (TELA_XC + TELA_LARG / 2, TELA_Z0)}.items():
        p = world_to_camera_view(cena, cam, Vector((x, 0.0, z)))
        px = p.x * LARGURA - MARGEM
        py = (1 - p.y) * ALTURA - MARGEM
        print(f"[menu] canto {nome} da tela: x={px:.2f} y={py:.2f} (jogo)")


# Paleta fixa da cena, em sRGB. Poucos tons: pretos azulados para as
# sombras, azuis frios para o que a tela ilumina, e alguns tons quentes
# (madeira, bege do monitor, lombadas) já "esfriados" pela luz azul.
PALETA = [
    "#06070a", "#0b0d13", "#10141d", "#161c29", "#1e2738", "#29354a",
    "#36465f", "#475b78", "#5c7494", "#7890b0", "#98b0cc", "#c0d4e8",
    "#130e0d", "#1e1614", "#2b201c", "#3a2c26", "#4d3c34",   # madeira no escuro
    "#1f2126", "#2c2f35", "#3c3e44", "#555961", "#737985", "#959ba6",              # bege/cinza do CRT sob luz fria
    "#2a1519", "#1a2622", "#3a3040",                         # lombadas
    "#6e6a4a", "#9a9468",                                    # bilhete amarelo sob luz azul
]


def srgb_para_lab(rgb):
    """RGB sRGB (0–1) -> CIELAB. No Lab, a distância entre duas cores é
    parecida com a diferença que o olho percebe; por isso escolhemos a cor
    mais próxima da paleta nesse espaço, e não direto no RGB."""
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805],
                  [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = lin @ m.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def reduzir_paleta(caminho, pintar_tela=False):
    """Abre o PNG, troca cada pixel pela cor mais próxima da PALETA e corta
    o alfa em 0 ou 1. Salva por cima.

    Com pintar_tela=True, pinta o retângulo da tela de um azul bem escuro:
    no Godot a Tela, os botões e o efeito CRT ficam por cima dele, e o
    reflexo que o vidro pegou no render só atrapalharia."""
    img = bpy.data.images.load(caminho)
    img.colorspace_settings.name = 'Non-Color'  # ler os bytes como estão, sem conversão
    px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)

    paleta = np.array([[int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)] for h in PALETA], dtype=np.float32)
    lab_px = srgb_para_lab(px[:, :3])
    lab_pal = srgb_para_lab(paleta)
    # Distância de cada pixel para cada cor da paleta; fica o índice da menor.
    dist = ((lab_px[:, None, :] - lab_pal[None, :, :]) ** 2).sum(axis=2)
    px[:, :3] = paleta[dist.argmin(axis=1)]
    px[:, 3] = (px[:, 3] >= 0.5).astype(np.float32)
    px[px[:, 3] == 0, :3] = 0.0

    if pintar_tela:
        # O Blender guarda as linhas de baixo para cima; convertemos o y.
        grade = px.reshape(ALTURA, LARGURA, 4)
        y0, y1 = ALTURA - TELA_Y1, ALTURA - TELA_Y0
        grade[y0:y1, TELA_X0:TELA_X1] = (*paleta[PALETA.index("#0b0d13")], 1.0)

    img.pixels[:] = px.ravel()
    img.filepath_raw = caminho
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


def renderizar_camadas(colecoes):
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    cena = bpy.context.scene
    for nome_camada in ("fundo", "mesa", "frente"):
        # Esconde da CÂMERA os objetos das outras camadas. Eles continuam
        # na cena: fazem sombra e rebatem luz, só não aparecem no PNG.
        for nome, col in colecoes.items():
            for obj in col.objects:
                obj.visible_camera = (nome == nome_camada)
        caminho = os.path.join(PASTA_SAIDA, f"menu_{nome_camada}.png")
        cena.render.filepath = caminho
        bpy.ops.render.render(write_still=True)
        reduzir_paleta(caminho, pintar_tela=(nome_camada == "mesa"))
        print(f"[menu] camada salva: {caminho}")
    # Deixa tudo visível de novo no .blend salvo.
    for col in colecoes.values():
        for obj in col.objects:
            obj.visible_camera = True


def main():
    # Começa de uma cena vazia (sem o cubo, a luz e a câmera padrão).
    bpy.ops.wm.read_factory_settings(use_empty=True)
    configurar_render()
    cam = criar_camera()
    colecoes = montar_cena()
    criar_luzes()
    conferir_alinhamento(cam)
    renderizar_camadas(colecoes)
    bpy.context.preferences.filepaths.save_version = 0  # não criar menu.blend1 de backup
    bpy.ops.wm.save_as_mainfile(filepath=ARQUIVO_BLEND)
    print(f"[menu] cena salva em {ARQUIVO_BLEND}")


main()
