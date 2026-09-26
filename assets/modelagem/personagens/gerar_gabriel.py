# gerar_gabriel.py — modela o Gabriel no Blender, por código, e renderiza
# os sprites de jogo (frente, 3/4, lado e costas) e a folha de referência.
#
# Como rodar (sem abrir a janela do Blender):
#
#   blender -b --factory-startup --python assets/modelagem/personagens/gerar_gabriel.py
#
# O que sai:
#   assets/sprites/personagens/gabriel/gabriel_lado.png        sprites de jogo, 48 px de altura:
#   assets/sprites/personagens/gabriel/gabriel_frente.png        de lado (olhando para a direita),
#   assets/sprites/personagens/gabriel/gabriel_tres_quartos.png  de frente, de 3/4 (virado para a
#   assets/sprites/personagens/gabriel/gabriel_costas.png        direita) e de costas
#   assets/sprites/personagens/gabriel/gabriel_andar_<vista>.png   caminhada: 12 quadros de 48 x 56
#                                                                 lado a lado, um arquivo por vista
#   assets/sprites/personagens/gabriel/gabriel_parado_<vista>.png  parado respirando: 8 quadros
#   assets/sprites/personagens/gabriel/gabriel_referencia.png  frente, 3/4, lado e costas, 128 px
#   assets/modelagem/personagens/gabriel.blend                 o modelo, para abrir e mexer
#
# Quem é (docs/gdd.md, item 3): aluno comum, cansado, que só queria passar
# nas provas. Pegou no sono estudando na Biblioteca na véspera da semana de
# provas e acordou mil anos depois — dormindo, não envelheceu. Então o
# visual é o de um estudante numa noite de estudo: moletom, calça jeans,
# tênis e mochila. Nada de herói: ombros caídos e cabeça um pouco baixa.
#
# Cores: o moletom é vermelho-tijolo de propósito. Os cenários do jogo são
# verdes (mato), bege (areia), cinza (concreto) e azul-frio (fungos); um
# tom quente e contrário a eles faz o jogador achar o Gabriel na tela.
#
# Modelagem: só primitivas (caixas, cones de 6 lados, esferas facetadas).
# Com 1 px ≈ 3,6 cm no sprite de jogo, detalhe menor que isso some, então
# o que importa é a SILHUETA: cabelo arrepiado, capuz nas costas e a
# mochila, que deixa o perfil do Gabriel inconfundível.

import math
import os
import sys

sys.dont_write_bytecode = True   # não criar a pasta __pycache__ ao importar o comum.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comum as c  # noqa: E402  (precisa vir depois do sys.path)
import numpy as np  # noqa: E402
import bpy  # noqa: E402

PASTA_SAIDA = os.path.join(c.PASTA_SPRITES, "gabriel")
ARQUIVO_BLEND = os.path.join(c.PASTA_SCRIPT, "gabriel.blend")
MAX_CORES = 32   # tamanho máximo da paleta do Gabriel
# Vistas dos sprites de jogo: (nome, giro do modelo em graus).
VISTAS_JOGO = (("lado", 90), ("frente", 0), ("tres_quartos", 35), ("costas", 180))
QUADROS_ANDAR = 12   # quadros do ciclo de caminhada (dois passos)
QUADROS_PARADO = 8   # quadros do ciclo de respiração


def criar_materiais():
    m = c.Materiais()
    return m, {
        "pele": m.novo("pele", "#b98260"),
        "cabelo": m.novo("cabelo", "#3a2c24"),
        "moletom": m.novo("moletom", "#a4453b"),
        "moletom_escuro": m.novo("moletom_escuro", "#7a3531"),
        "jeans": m.novo("jeans", "#40537a"),
        "tenis": m.novo("tenis", "#d3cfc4"),
        "sola": m.novo("sola", "#4d4d57"),
        "mochila": m.novo("mochila", "#556650"),
        "mochila_escura": m.novo("mochila_escura", "#3a4639"),
        # Detalhes de 1 px: cor chapada (modo 'plano'), sem sombreamento.
        "olho": m.novo("olho", "#1c1822", "plano"),
        "olheira": m.novo("olheira", "#8c5a48", "plano"),   # noite sem dormir
    }


def perna(nome, lado, mt, quadril, giro_coxa, giro_joelho):
    """Perna pendurada na junta do quadril. lado = -1 (direita dele) ou +1."""
    junta = c.pivo(f"{nome}Quadril", (0.095 * lado, 0.0, 0.0), quadril, (giro_coxa, 0, 0))
    c.membro(f"{nome}Coxa", 0.085, 0.066, 0.41, mt["jeans"], junta)
    joelho = c.pivo(f"{nome}Joelho", (0, 0, -0.41), junta, (giro_joelho, 0, 0))
    c.membro(f"{nome}Canela", 0.066, 0.056, 0.37, mt["jeans"], joelho)
    # Tênis: cabedal claro + sola escura, com a ponta para a frente (-Y).
    tornozelo = c.pivo(f"{nome}Tornozelo", (0, 0, -0.37), joelho, (-giro_coxa - giro_joelho, 0, 0))
    c.caixa(f"{nome}Tenis", (0.115, 0.26, 0.075), (0, -0.045, -0.05), mt["tenis"], tornozelo, bisel=0.02)
    c.caixa(f"{nome}Sola", (0.12, 0.275, 0.028), (0, -0.045, -0.086), mt["sola"], tornozelo)


def braco(nome, lado, mt, tronco, abertura, giro_ombro, giro_cotovelo):
    """Braço: manga do moletom (duas partes) e a mão."""
    ombro = c.pivo(f"{nome}Ombro", (0.235 * lado, 0.0, 0.47), tronco, (giro_ombro, abertura * lado, 0))
    c.membro(f"{nome}Braco", 0.068, 0.058, 0.30, mt["moletom"], ombro)
    cotovelo = c.pivo(f"{nome}Cotovelo", (0, 0, -0.30), ombro, (giro_cotovelo, 0, 0))
    c.membro(f"{nome}Antebraco", 0.058, 0.052, 0.24, mt["moletom"], cotovelo)
    c.cone(f"{nome}Punho", 0.054, 0.054, 0.035, (0, 0, -0.245), mt["moletom_escuro"], cotovelo, lados=6)
    c.caixa(f"{nome}Mao", (0.06, 0.085, 0.10), (0, 0, -0.31), mt["pele"], cotovelo, bisel=0.02)


def montar(mt):
    raiz = c.pivo("Gabriel")
    # Quadril a 0,88 m do chão. Leve inclinação do tronco para a frente:
    # cansaço, não curvatura de monstro (essa fica para o Vigia).
    quadril = c.pivo("Quadril", (0, 0, 0.88), raiz)
    perna("PernaDir", -1, mt, quadril, -3, 4)
    perna("PernaEsq", +1, mt, quadril, 3, 2)

    tronco = c.pivo("Tronco", (0, 0, 0), quadril, (4, 0, 0))
    c.caixa("Bacia", (0.30, 0.15, 0.16), (0, 0, 0.0), mt["jeans"], tronco, bisel=0.03)
    # Moletom: um bloco levemente mais largo em cima (ombros) e a barra.
    c.cone("Moletom", 0.215, 0.228, 0.54, (0, 0, 0.25), mt["moletom"], tronco, lados=8, achatar=0.58)
    c.cone("MoletomBarra", 0.222, 0.222, 0.07, (0, 0, 0.0), mt["moletom_escuro"], tronco, lados=8, achatar=0.60)
    c.caixa("Bolso", (0.24, 0.02, 0.11), (0, -0.128, 0.12), mt["moletom_escuro"], tronco)
    # Capuz caído nas costas: faz um "calombo" atrás do pescoço.
    c.caixa("Capuz", (0.28, 0.12, 0.13), (0, 0.10, 0.55), mt["moletom_escuro"], tronco, (-25, 0, 0), bisel=0.035)
    c.cone("Pescoco", 0.05, 0.05, 0.10, (0, 0, 0.58), mt["pele"], tronco, lados=6)

    # Mochila nas costas (alças por cima dos ombros).
    c.caixa("Mochila", (0.31, 0.16, 0.40), (0, 0.205, 0.30), mt["mochila"], tronco, (-4, 0, 0), bisel=0.04)
    c.caixa("MochilaBolso", (0.25, 0.06, 0.17), (0, 0.29, 0.18), mt["mochila_escura"], tronco, bisel=0.02)
    for lado in (-1, 1):
        c.caixa(f"Alca{lado}Cima", (0.05, 0.26, 0.03), (0.11 * lado, 0.0, 0.535), mt["mochila_escura"], tronco)
        c.caixa(f"Alca{lado}Frente", (0.05, 0.025, 0.30), (0.11 * lado, -0.13, 0.38), mt["mochila_escura"], tronco)

    braco("BracoDir", -1, mt, tronco, 7, -2, -8)
    braco("BracoEsq", +1, mt, tronco, 7, 4, -12)

    # Cabeça um pouco baixa (cansado).
    pescoco = c.pivo("Cabeca", (0, 0, 0.60), tronco, (5, 0, 0))
    c.caixa("Rosto", (0.21, 0.23, 0.25), (0, 0, 0.125), mt["pele"], pescoco, bisel=0.04)
    c.caixa("Nariz", (0.035, 0.05, 0.05), (0, -0.115, 0.10), mt["pele"], pescoco)
    for lado in (-1, 1):
        c.caixa(f"Orelha{lado}", (0.03, 0.05, 0.06), (0.105 * lado, 0.01, 0.12), mt["pele"], pescoco)
        c.caixa(f"Olho{lado}", (0.035, 0.01, 0.03), (0.048 * lado, -0.112, 0.135), mt["olho"], pescoco)
        c.caixa(f"Olheira{lado}", (0.04, 0.01, 0.014), (0.048 * lado, -0.111, 0.112), mt["olheira"], pescoco)
    # Cabelo: uma "tampa", a nuca e tufos arrepiados (de quem deitou a
    # cabeça em cima do livro).
    c.caixa("CabeloTopo", (0.225, 0.245, 0.075), (0, 0.005, 0.235), mt["cabelo"], pescoco, bisel=0.025)
    c.caixa("CabeloNuca", (0.225, 0.08, 0.17), (0, 0.085, 0.17), mt["cabelo"], pescoco, bisel=0.02)
    for lado in (-1, 1):
        c.caixa(f"CabeloLado{lado}", (0.03, 0.14, 0.09), (0.105 * lado, 0.04, 0.20), mt["cabelo"], pescoco)
    for i, (x, y, rx, ry) in enumerate([(-0.06, -0.09, -30, -15), (0.02, -0.10, -40, 10),
                                         (0.07, -0.06, -20, 25), (-0.05, -0.02, -10, -20)]):
        c.caixa(f"Tufo{i}", (0.06, 0.05, 0.07), (x, y, 0.265), mt["cabelo"], pescoco, (rx, ry, 0))
    return raiz


# ---------------------------------------------------------------------------
# Caminhada
# ---------------------------------------------------------------------------
#
# Um ciclo de caminhada são DOIS passos: a perna direita vai à frente, depois
# a esquerda. Chamamos de fase (φ) o ponto do ciclo, de 0 a 360 graus, e
# cada junta segue uma onda seno dessa fase:
#
#   coxa   = -AMPLITUDE_COXA · sen(φ)     a perna balança para a frente e
#                                        para trás (ângulo negativo = frente);
#                                        a outra perna usa φ + 180°, o oposto
#   joelho = dobra só enquanto a perna vem para a frente no ar, que é
#            quando cos(φ) > 0 (a coxa está indo para a frente)
#   ombro  = o braço balança ao contrário da perna do mesmo lado
#   quadril desce um pouco quando as pernas estão abertas (sen² φ = 1):
#            é o "sobe e desce" que dá peso ao andar
#
# Com 12 quadros, cada quadro avança 30° na fase. Mais quadros = passagem
# mais suave de uma pose para a outra (com 6, cada quadro pulava 60°).

AMPLITUDE_COXA = 22       # graus
AMPLITUDE_JOELHO = 55   # bem dobrado: de frente e de costas, é o pé subindo que mostra o passo
AMPLITUDE_BRACO = 16
DESCIDA_QUADRIL = 0.037   # metros: 1 px no sprite de jogo


def guardar_pose():
    """Guarda a rotação e a posição de todas as juntas, para voltar à pose
    parada depois de renderizar a caminhada."""
    return {o.name: (tuple(o.rotation_euler), tuple(o.location))
            for o in bpy.data.objects if o.type == 'EMPTY'}


def restaurar_pose(pose):
    for nome, (rot, pos) in pose.items():
        obj = bpy.data.objects[nome]
        obj.rotation_euler = rot
        obj.location = pos


def pose_andar(parado, fase):
    """Coloca o Gabriel na pose da caminhada para a fase dada (em graus).
    Os ângulos somam por cima da pose parada (que já tem o cansaço dele)."""
    def girar(nome, graus_x):
        rot, _ = parado[nome]
        bpy.data.objects[nome].rotation_euler = (rot[0] + math.radians(graus_x), rot[1], rot[2])

    for perna, desloc in (("PernaDir", 0), ("PernaEsq", 180)):
        phi = math.radians(fase + desloc)
        coxa = -AMPLITUDE_COXA * math.sin(phi)
        joelho = AMPLITUDE_JOELHO * max(0.0, math.cos(phi)) ** 1.5
        girar(f"{perna}Quadril", coxa)
        girar(f"{perna}Joelho", joelho)
        # O tornozelo desfaz o giro da coxa e do joelho: o tênis fica reto.
        girar(f"{perna}Tornozelo", -coxa - joelho)
    for braco, desloc in (("BracoDir", 0), ("BracoEsq", 180)):
        phi = math.radians(fase + desloc)
        girar(f"{braco}Ombro", AMPLITUDE_BRACO * math.sin(phi))
        girar(f"{braco}Cotovelo", -10 * max(0.0, -math.sin(phi)))
    _, pos = parado["Quadril"]
    subida = DESCIDA_QUADRIL * math.sin(math.radians(fase)) ** 2
    bpy.data.objects["Quadril"].location = (pos[0], pos[1], pos[2] - subida)


# ---------------------------------------------------------------------------
# Parado (respirando)
# ---------------------------------------------------------------------------
#
# Parado, o Gabriel respira devagar e cansado. Num sprite de 48 px, o menor
# movimento visível é 1 pixel, então a respiração é o tronco inteiro (com a
# cabeça e os braços) subindo 1 px ao puxar o ar, com as pernas paradas no
# chão. A cabeça pende um pouco e volta, atrasada em relação ao peito.
#
#   subida = SUBIDA_PEITO · (1 - cos φ) / 2     vai de 0 (fase 0) a 1 px (180°)
#
# Na fase 0 a subida é zero: o primeiro quadro é igual ao sprite parado.

SUBIDA_PEITO = 0.037      # metros: 1 px no sprite de jogo
BALANCO_CABECA = 3        # graus


def pose_parado(parado, fase):
    """Pose da respiração para a fase dada (em graus)."""
    phi = math.radians(fase)
    rot, pos = parado["Tronco"]
    subida = SUBIDA_PEITO * (1 - math.cos(phi)) / 2
    bpy.data.objects["Tronco"].location = (pos[0], pos[1], pos[2] + subida)
    rot, _ = parado["Cabeca"]
    # Atrasada 60° em relação ao peito: primeiro o peito sobe, depois a
    # cabeça acompanha. É esse atraso que faz parecer um corpo, não um bloco.
    pende = BALANCO_CABECA * (1 - math.cos(phi - math.radians(60))) / 2
    bpy.data.objects["Cabeca"].rotation_euler = (rot[0] + math.radians(pende), rot[1], rot[2])


def main():
    c.cena_vazia()
    materiais, mt = criar_materiais()
    c.usar_colecao("Gabriel")
    raiz = montar(mt)
    cam = c.criar_camera()
    c.criar_luzes()
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    # Sprites de jogo, um para cada direção em que ele anda (o scripts/
    # personagens/gabriel.gd escolhe qual mostrar). O ângulo é o giro do
    # modelo: 0 = de frente, 90 = de lado olhando para a direita, 180 = de
    # costas. Para a esquerda, o Godot espelha o sprite.
    jogo = {}
    for nome, angulo in VISTAS_JOGO:
        img, ind, _ = c.renderizar_vista(cam, raiz, materiais, angulo, c.QUADRO_JOGO, c.PX_POR_M_JOGO, c.PE_JOGO_PX)
        linhas = img[..., 3].any(axis=1).nonzero()[0]
        print(f"[gabriel] {nome}: altura do corpo no sprite: {linhas[-1] - linhas[0] + 1} px")
        jogo[nome] = c.contorno(img, ind, materiais)
    sprite = jogo["lado"]

    # Caminhada: QUADROS_ANDAR poses em cada vista, lado a lado numa tira.
    parado = guardar_pose()
    andar = {nome: [] for nome, _ in VISTAS_JOGO}
    for q in range(QUADROS_ANDAR):
        pose_andar(parado, 360 * q / QUADROS_ANDAR)
        for nome, angulo in VISTAS_JOGO:
            img, ind, _ = c.renderizar_vista(cam, raiz, materiais, angulo, c.QUADRO_JOGO, c.PX_POR_M_JOGO, c.PE_JOGO_PX)
            andar[nome].append(c.contorno(img, ind, materiais))
        print(f"[gabriel] andar: quadro {q + 1}/{QUADROS_ANDAR}")
    restaurar_pose(parado)

    # Parado respirando: QUADROS_PARADO poses em cada vista.
    respirar = {nome: [] for nome, _ in VISTAS_JOGO}
    for q in range(QUADROS_PARADO):
        pose_parado(parado, 360 * q / QUADROS_PARADO)
        for nome, angulo in VISTAS_JOGO:
            img, ind, _ = c.renderizar_vista(cam, raiz, materiais, angulo, c.QUADRO_JOGO, c.PX_POR_M_JOGO, c.PE_JOGO_PX)
            respirar[nome].append(c.contorno(img, ind, materiais))
        print(f"[gabriel] parado: quadro {q + 1}/{QUADROS_PARADO}")
    restaurar_pose(parado)

    # Folha de referência: frente, 3/4, lado e costas, em 128 px.
    vistas = []
    for angulo in (0, 35, 90, 180):
        img, ind, _ = c.renderizar_vista(cam, raiz, materiais, angulo, c.QUADRO_REF, c.PX_POR_M_REF, c.PE_REF_PX)
        vistas.append(c.contorno(img, ind, materiais))

    # Uma paleta só para tudo do Gabriel (sprites e referência). Ela é
    # calculada com o sprite de lado e a referência, e as outras vistas de
    # jogo só usam essa paleta: assim as cores de antes não mudam.
    (sprite, *vistas), paleta = c.unificar_paleta([sprite] + vistas, materiais, MAX_CORES)
    c.salvar_png(sprite, os.path.join(PASTA_SAIDA, "gabriel_lado.png"))
    outras = ["frente", "tres_quartos", "costas"]
    for nome, img in zip(outras, c.aplicar_paleta([jogo[n] for n in outras], paleta)):
        c.salvar_png(img, os.path.join(PASTA_SAIDA, f"gabriel_{nome}.png"))
    for nome, quadros in andar.items():
        tira = np.concatenate(c.aplicar_paleta(quadros, paleta), axis=1)
        c.salvar_png(tira, os.path.join(PASTA_SAIDA, f"gabriel_andar_{nome}.png"))
    for nome, quadros in respirar.items():
        tira = np.concatenate(c.aplicar_paleta(quadros, paleta), axis=1)
        c.salvar_png(tira, os.path.join(PASTA_SAIDA, f"gabriel_parado_{nome}.png"))
    c.salvar_png(c.montar_folha([vistas]), os.path.join(PASTA_SAIDA, "gabriel_referencia.png"))
    print("[gabriel] paleta:", " ".join(c.rgb_para_hex(np.array(cor) / 255) for cor in paleta))

    c.salvar_blend(ARQUIVO_BLEND, raiz)
    print("[gabriel] pronto")


main()
