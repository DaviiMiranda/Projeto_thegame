# gerar_vigia.py — modela o Vigia (um dos Insones) no Blender, por código,
# nas duas versões do jogo, e renderiza sprites e folha de referência.
#
# Como rodar (sem abrir a janela do Blender):
#
#   blender -b --factory-startup --python assets/modelagem/personagens/gerar_vigia.py
#
# O que sai:
#   assets/sprites/personagens/vigia/vigia_presente_lado.png  sprite de jogo, presente
#   assets/sprites/personagens/vigia/vigia_sonho_lado.png     sprite de jogo, sonho
#   assets/sprites/personagens/vigia/vigia_referencia.png     presente (linha de cima) e
#                                                             sonho (linha de baixo), 4 vistas
#   assets/modelagem/personagens/vigia.blend                  as duas versões lado a lado
#
# Quem é (docs/gdd.md, item 3): faz a ronda noturna, é quem risca os dias
# nas paredes e é o Insone mais atento à luz. Como todo Insone, tomou o
# VIGÍLIA-7 e está há mil anos sem dormir, reduzido à rotina.
#
# As duas versões são o MESMO modelo com parâmetros diferentes (dicionário
# no fim do arquivo). Isso é de propósito: o jogador tem que reconhecer no
# monstro do presente o homem do sonho — mesmo quepe, mesmo uniforme,
# mesmo cinto. O que muda:
#
#   SONHO  (a última semana antes de tudo)
#     postura reta, corpo cheio, uniforme inteiro e de cor viva,
#     lanterna ACESA na mão, apontada para a frente: é a ronda.
#   PRESENTE (mil anos depois)
#     - corpo magro e curvado para a frente, joelhos dobrados;
#     - braços compridos, pendurados (mil anos reduzido à rotina);
#     - pescoço esticado e a cabeça erguida, olhando à frente: vigiando;
#     - olhos claros que brilham ao pegar luz, como os de bicho noturno —
#       é o "mais atento à luz", e é isso que o jogador vê no escuro;
#     - uniforme desbotado e rasgado (barra da camisa em tiras, manga
#       arrancada, calça rasgada na canela), cabelo comprido e grisalho
#       escapando do quepe amassado;
#     - a lanterna morta pendurada no cinto (a pilha acabou há séculos)
#       e uma pedra de giz na mão: é com ela que risca os dias.
#   Terror de tensão: nada de sangue nem ferida, o incômodo vem da
#   postura, da magreza e dos olhos.

import os
import sys

sys.dont_write_bytecode = True   # não criar a pasta __pycache__ ao importar o comum.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comum as c  # noqa: E402
import numpy as np  # noqa: E402

PASTA_SAIDA = os.path.join(c.PASTA_SPRITES, "vigia")
ARQUIVO_BLEND = os.path.join(c.PASTA_SCRIPT, "vigia.blend")
# Paleta máxima: 40 cores para as duas versões juntas (o sonho é colorido,
# o presente é quase todo cinza-azulado, e as duas dividem os escuros).
MAX_CORES = 40


def criar_materiais(m, cores, sufixo):
    """Cria os materiais de uma versão. 'cores' é o dicionário da versão."""
    mt = {}
    for nome, valor in cores.items():
        hexa, modo = valor if isinstance(valor, tuple) else (valor, "normal")
        mt[nome] = m.novo(f"{nome}_{sufixo}", hexa, modo)
    return mt


def semente(texto):
    """Número fixo a partir de um nome (soma dos códigos das letras), para o
    sorteio das tiras dar sempre o mesmo resultado. (O hash() do Python
    muda a cada execução, então não serve.)"""
    return sum(ord(ch) for ch in texto)


def tiras(nome, pai, raio, achatar, z, quantas, comprimento, mat, semente):
    """Barra rasgada: pontas (pirâmides de 4 lados) penduradas em volta de
    uma elipse. O comprimento varia de uma para outra, como pano puído."""
    import math
    import random
    rnd = random.Random(semente)
    for i in range(quantas):
        ang = 2 * math.pi * i / quantas + rnd.uniform(-0.2, 0.2)
        x = math.cos(ang) * raio
        y = math.sin(ang) * raio * achatar
        L = comprimento * rnd.uniform(0.5, 1.2)
        c.cone(f"{nome}{i}", 0.0, raio * 0.35, L, (x, y, z - L / 2), mat, pai, lados=4,
               rot=(rnd.uniform(-8, 8), rnd.uniform(-8, 8), math.degrees(ang)))


def perna(nome, lado, p, mt, quadril):
    fino = p["magreza"]
    junta = c.pivo(f"{nome}Quadril", (0.10 * lado, 0.0, 0.0), quadril, (p["coxa"], 0, 0))
    c.membro(f"{nome}Coxa", 0.095 * fino, 0.078 * fino, 0.43, mt["calca"], junta)
    joelho = c.pivo(f"{nome}Joelho", (0, 0, -0.43), junta, (p["joelho"], 0, 0))
    if p["rasgado"]:
        # Calça rasgada no meio da canela: embaixo aparece a perna fina.
        c.membro(f"{nome}CanelaCalca", 0.07 * fino, 0.066 * fino, 0.20, mt["calca"], joelho)
        c.membro(f"{nome}Canela", 0.045, 0.038, 0.38, mt["pele"], joelho)
        tiras(f"{nome}TiraCalca", joelho, 0.066 * fino, 1.0, -0.20, 5, 0.08, mt["calca"], semente(nome))
    else:
        c.membro(f"{nome}Canela", 0.078, 0.068, 0.38, mt["calca"], joelho)
    # Bota de cano curto, sempre plana no chão (desfaz o giro da perna).
    tornozelo = c.pivo(f"{nome}Tornozelo", (0, 0, -0.38), joelho, (-p["coxa"] - p["joelho"], 0, 0))
    c.caixa(f"{nome}Bota", (0.12, 0.27, 0.12), (0, -0.04, -0.03), mt["bota"], tornozelo, bisel=0.025)
    c.caixa(f"{nome}Sola", (0.125, 0.28, 0.03), (0, -0.04, -0.09), mt["cinto"], tornozelo)


def braco(nome, lado, p, mt, peito, giro_ombro, giro_cotovelo, manga_rasgada=False):
    fino = p["magreza"]
    L1, L2 = 0.30 * p["braco"], 0.26 * p["braco"]
    ombro = c.pivo(f"{nome}Ombro", (p["ombros"] * lado, 0.0, 0.22), peito, (giro_ombro, 6 * lado, 0))
    c.membro(f"{nome}Braco", 0.07 * fino, 0.06 * fino, L1, mt["camisa"], ombro)
    # Dragona (tira no ombro do uniforme).
    c.caixa(f"{nome}Dragona", (0.07, 0.13, 0.025), (0, 0, 0.0), mt["camisa_escura"], ombro)
    cotovelo = c.pivo(f"{nome}Cotovelo", (0, 0, -L1), ombro, (giro_cotovelo, 0, 0))
    if manga_rasgada:
        # Manga arrancada no cotovelo: antebraço à mostra, fino, e tiras.
        c.membro(f"{nome}Antebraco", 0.046, 0.038, L2, mt["pele"], cotovelo)
        tiras(f"{nome}TiraManga", cotovelo, 0.06 * fino, 1.0, 0.0, 5, 0.07, mt["camisa"], semente(nome))
    else:
        c.membro(f"{nome}Antebraco", 0.06 * fino, 0.052 * fino, L2, mt["camisa"], cotovelo)
        if p["rasgado"]:
            tiras(f"{nome}TiraPunho", cotovelo, 0.05 * fino, 1.0, -L2 + 0.01, 4, 0.06, mt["camisa"], semente(nome))
    mao = c.pivo(f"{nome}Mao", (0, 0, -L2), cotovelo)
    # Mão: no presente, mais comprida e ossuda.
    c.caixa(f"{nome}MaoPalma", (0.06, 0.09 * fino + 0.02, 0.11 * p["braco"]), (0, 0, -0.055 * p["braco"]),
            mt["pele"], mao, bisel=0.015)
    return mao


def montar_vigia(nome, p, mt, x):
    raiz = c.pivo(nome, (x, 0, 0))
    fino = p["magreza"]
    quadril = c.pivo(f"{nome}Quadril", (0, 0, p["altura_quadril"]), raiz)
    perna(f"{nome}PernaDir", -1, p, mt, quadril)
    perna(f"{nome}PernaEsq", +1, p, mt, quadril)

    # Tronco em dois pedaços (barriga e peito), cada um com sua inclinação:
    # somando as duas, as costas fazem uma curva, e não uma tábua torta.
    tronco = c.pivo(f"{nome}Tronco", (0, 0, 0), quadril, (p["curva_baixo"], 0, 0))
    r = 0.225 * fino
    c.caixa(f"{nome}Bacia", (0.30 * fino + 0.04, 0.15, 0.14), (0, 0, 0.0), mt["calca"], tronco, bisel=0.03)
    c.cone(f"{nome}Barriga", r * p["barriga"], r, 0.32, (0, 0, 0.14), mt["camisa"], tronco, lados=8, achatar=0.62)
    c.cone(f"{nome}Cinto", r * p["barriga"] + 0.008, r * p["barriga"] + 0.008, 0.05, (0, 0, 0.0),
           mt["cinto"], tronco, lados=8, achatar=0.64)
    c.caixa(f"{nome}Fivela", (0.05, 0.02, 0.04), (0, -r * p["barriga"] * 0.64 - 0.005, 0.0), mt["metal_claro"], tronco)
    # Rádio preso no cinto, do lado esquerdo dele.
    c.caixa(f"{nome}Radio", (0.05, 0.08, 0.13), (r * p["barriga"] + 0.02, 0.02, 0.01), mt["cinto"], tronco, bisel=0.01)
    if p["rasgado"]:
        tiras(f"{nome}TiraCamisa", tronco, r * p["barriga"], 0.62, -0.01, 11, 0.12, mt["camisa"], 7)

    peito = c.pivo(f"{nome}Peito", (0, 0, 0.29), tronco, (p["curva_cima"], 0, 0))
    c.cone(f"{nome}PeitoCamisa", r, r * 1.05 + 0.01, 0.30, (0, 0, 0.13), mt["camisa"], peito, lados=8, achatar=0.62)
    # Gola, bolso e distintivo do uniforme.
    c.cone(f"{nome}Gola", 0.075, 0.06, 0.05, (0, 0, 0.29), mt["camisa_escura"], peito, lados=6)
    c.caixa(f"{nome}Distintivo", (0.05, 0.02, 0.055), (0.08, -r * 0.62 - 0.012, 0.17), mt["metal_claro"], peito)
    c.caixa(f"{nome}Bolso", (0.08, 0.015, 0.07), (-0.085, -r * 0.62 - 0.008, 0.15), mt["camisa_escura"], peito)
    c.cone(f"{nome}Pescoco", 0.05 * fino + 0.01, 0.045 * fino + 0.01, p["pescoco"], (0, 0, 0.28 + p["pescoco"] / 2),
           mt["pele"], peito, lados=6)

    # Braços. Direito (lado -1) segura lanterna (sonho) ou a pedra (presente).
    mao_dir = braco(f"{nome}BracoDir", -1, p, mt, peito, *p["braco_dir"], manga_rasgada=p["rasgado"])
    mao_esq = braco(f"{nome}BracoEsq", +1, p, mt, peito, *p["braco_esq"])
    if p["lanterna_na_mao"]:
        # Lanterna comprida, deitada ao longo do antebraço, lente acesa na ponta.
        lant = c.pivo(f"{nome}Lanterna", (0, -0.01, -0.06), mao_dir, (p["giro_lanterna"], 0, 0))
        c.cone(f"{nome}LanternaCorpo", 0.022, 0.022, 0.22, (0, 0, -0.06), mt["lanterna"], lant, lados=6)
        c.cone(f"{nome}LanternaCabeca", 0.036, 0.024, 0.06, (0, 0, -0.19), mt["lanterna"], lant, lados=6)
        c.cone(f"{nome}LanternaLente", 0.033, 0.033, 0.012, (0, 0, -0.226), mt["lente"], lant, lados=6)
    else:
        # Lanterna morta pendurada no cinto, apontando para o chão.
        c.cone(f"{nome}LanternaCorpo", 0.022, 0.022, 0.20, (-r * p["barriga"] - 0.02, 0.0, -0.08),
               mt["lanterna"], tronco, lados=6, rot=(-8, 0, 0))
        c.cone(f"{nome}LanternaCabeca", 0.036, 0.024, 0.05, (-r * p["barriga"] - 0.02, -0.02, -0.19),
               mt["lanterna"], tronco, lados=6)
        c.cone(f"{nome}LanternaLente", 0.033, 0.033, 0.012, (-r * p["barriga"] - 0.02, -0.02, -0.22),
               mt["lente"], tronco, lados=6)
    if p["pedra"]:
        c.pedra(f"{nome}Pedra", 0.04, (0, -0.045, -0.11), mt["pedra"], mao_dir, (20, 30, 10))
    _ = mao_esq

    # Cabeça e quepe.
    cabeca = c.pivo(f"{nome}Cabeca", (0, 0, 0.28 + p["pescoco"]), peito, (p["giro_cabeca"], 0, 0))
    c.caixa(f"{nome}Rosto", (0.20 * p["rosto_fino"], 0.23, 0.25), (0, 0, 0.125), mt["pele"], cabeca, bisel=0.04)
    c.caixa(f"{nome}Nariz", (0.035, 0.055, 0.055), (0, -0.12, 0.10), mt["pele"], cabeca)
    ex, ey, ez = p["olho"]
    for lado in (-1, 1):
        c.caixa(f"{nome}Orelha{lado}", (0.03, 0.05, 0.06), (0.10 * p["rosto_fino"] * lado, 0.01, 0.12),
                mt["pele"], cabeca)
        c.caixa(f"{nome}Olho{lado}", (ex, 0.012, ez), (0.05 * lado, -0.113, 0.13), mt["olho"], cabeca)
        # O mesmo olho visto de lado: um pixel claro na lateral do rosto.
        c.caixa(f"{nome}OlhoLado{lado}", (0.012, ey, ez), (0.098 * p["rosto_fino"] * lado, -0.085, 0.13),
                mt["olho"], cabeca)
        if p["olheira"]:
            c.caixa(f"{nome}Olheira{lado}", (ex + 0.01, 0.01, 0.02), (0.05 * lado, -0.112, 0.10), mt["olheira"], cabeca)
    quepe = c.pivo(f"{nome}Quepe", (0, 0, 0.225), cabeca, p["giro_quepe"])
    c.cone(f"{nome}QuepeCopa", 0.125, 0.135, 0.09, (0, 0.01, 0.04), mt["quepe"], quepe, lados=8)
    c.cone(f"{nome}QuepeFaixa", 0.127, 0.127, 0.03, (0, 0.01, 0.0), mt["camisa_escura"], quepe, lados=8)
    c.caixa(f"{nome}QuepeAba", (0.19, 0.10, 0.018), (0, -0.155, -0.005), mt["aba"], quepe, (p["aba"], 0, 0))
    c.caixa(f"{nome}QuepeEmblema", (0.04, 0.012, 0.035), (0, -0.128, 0.035), mt["metal_claro"], quepe)
    if p["cabelo_comprido"]:
        # Mechas compridas e ralas escapando do quepe, dos lados e da nuca.
        import random
        rnd = random.Random(3)
        for i, (x, y) in enumerate([(-0.10, 0.02), (-0.08, 0.08), (-0.03, 0.11), (0.03, 0.11),
                                    (0.08, 0.08), (0.10, 0.02), (0.0, 0.12)]):
            L = rnd.uniform(0.14, 0.26)
            c.caixa(f"{nome}Mecha{i}", (0.035, 0.03, L), (x, y, 0.20 - L / 2), mt["cabelo"], cabeca,
                    (rnd.uniform(5, 18), rnd.uniform(-10, 10), 0))
    else:
        c.caixa(f"{nome}CabeloNuca", (0.19, 0.05, 0.07), (0, 0.095, 0.18), mt["cabelo"], cabeca, bisel=0.02)
    return raiz


# ---------------------------------------------------------------------------
# As duas versões
# ---------------------------------------------------------------------------

SONHO = {
    "cores": {
        "pele": "#8f5d40",
        "cabelo": "#3b302a",
        "camisa": "#4d6386",          # camisa do uniforme, azul
        "camisa_escura": "#34425e",
        "calca": "#2c344e",
        "quepe": "#2c344e",
        "aba": "#262a36",
        "bota": "#3a302b",
        "cinto": "#2e2e36",
        "metal_claro": ("#d2ae52", "plano"),  # distintivo, fivela: dourado
        "lanterna": "#474a52",
        "lente": ("#fff0b8", "brilho"),       # acesa
        "olho": ("#1c1822", "plano"),
        "olheira": ("#6e4432", "plano"),
        "pedra": "#bdb6a6",
    },
    "magreza": 1.0, "barriga": 1.08, "braco": 1.0, "rosto_fino": 1.0,
    "ombros": 0.245, "altura_quadril": 0.92, "pescoco": 0.08,
    "curva_baixo": 0, "curva_cima": 0, "giro_cabeca": 0,
    "coxa": -2, "joelho": 3,
    # (giro do ombro, giro do cotovelo): braço direito dobrado para a
    # frente segurando a lanterna; o esquerdo solto ao lado do corpo.
    "braco_dir": (-20, -65), "braco_esq": (3, -6),
    "lanterna_na_mao": True, "giro_lanterna": -5, "pedra": False,
    "olho": (0.035, 0.035, 0.03), "olheira": False,
    "giro_quepe": (0, 0, 0), "aba": 8,
    "cabelo_comprido": False, "rasgado": False,
}

PRESENTE = {
    "cores": {
        "pele": "#a09e94",            # pálido e acinzentado: mil anos longe do sol
        "cabelo": "#8d887c",
        "camisa": "#636d80",          # o mesmo azul, desbotado
        "camisa_escura": "#4c5362",
        "calca": "#474c5b",
        "quepe": "#474c5b",
        "aba": "#30333c",
        "bota": "#4a433d",
        "cinto": "#393a40",
        "metal_claro": ("#8e8260", "plano"),  # o dourado, fosco
        "lanterna": "#4e5056",
        "lente": ("#5d6268", "plano"),        # apagada
        "olho": ("#eef0c4", "brilho"),        # olhos que refletem a luz
        "olheira": ("#5e5a58", "plano"),
        "pedra": "#cfc9b8",                    # pedra de giz
    },
    "magreza": 0.72, "barriga": 0.92, "braco": 1.2, "rosto_fino": 0.88,
    "ombros": 0.215, "altura_quadril": 0.92, "pescoco": 0.15,
    # Curvatura: 22° na barriga + 24° no peito; a cabeça volta -52° para
    # olhar para a frente (o queixo projetado, o pescoço esticado).
    "curva_baixo": 22, "curva_cima": 24, "giro_cabeca": -52,
    "coxa": -20, "joelho": 30,
    # Braços pendurados: o ombro desfaz a curvatura (-46°) e mais um pouco,
    # para as mãos ficarem à frente do corpo.
    "braco_dir": (-58, -25), "braco_esq": (-50, -8),
    "lanterna_na_mao": False, "giro_lanterna": 0, "pedra": True,
    "olho": (0.045, 0.045, 0.04), "olheira": True,
    "giro_quepe": (-6, 10, 4), "aba": 22,     # quepe torto, aba amassada para baixo
    "cabelo_comprido": True, "rasgado": True,
}


def main():
    c.cena_vazia()
    materiais = c.Materiais()
    c.usar_colecao("VigiaPresente")
    mt_p = criar_materiais(materiais, PRESENTE["cores"], "presente")
    raiz_p = montar_vigia("VigiaPresente", PRESENTE, mt_p, 0.0)
    col_p = c.COLECAO_ATUAL
    c.usar_colecao("VigiaSonho")
    mt_s = criar_materiais(materiais, SONHO["cores"], "sonho")
    raiz_s = montar_vigia("VigiaSonho", SONHO, mt_s, 0.0)
    col_s = c.COLECAO_ATUAL
    cam = c.criar_camera()
    c.criar_luzes()
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    sprites, linhas_folha = {}, []
    for versao, raiz, col, outra in (("presente", raiz_p, col_p, col_s), ("sonho", raiz_s, col_s, col_p)):
        # Renderiza uma versão por vez (a outra fica escondida).
        col.hide_render, outra.hide_render = False, True
        sprite, indice, _ = c.renderizar_vista(cam, raiz, materiais, 90, c.QUADRO_JOGO, c.PX_POR_M_JOGO, c.PE_JOGO_PX)
        linhas = sprite[..., 3].any(axis=1).nonzero()[0]
        print(f"[vigia] {versao}: altura no sprite {linhas[-1] - linhas[0] + 1} px")
        sprites[versao] = c.contorno(sprite, indice, materiais)
        vistas = []
        for angulo in (0, 35, 90, 180):
            img, ind, _ = c.renderizar_vista(cam, raiz, materiais, angulo, c.QUADRO_REF, c.PX_POR_M_REF, c.PE_REF_PX)
            vistas.append(c.contorno(img, ind, materiais))
        linhas_folha.append(vistas)

    # Uma paleta só para o Vigia inteiro (as duas versões, sprites e folha).
    todas = [sprites["presente"], sprites["sonho"]] + linhas_folha[0] + linhas_folha[1]
    todas, paleta = c.unificar_paleta(todas, materiais, MAX_CORES)
    c.salvar_png(todas[0], os.path.join(PASTA_SAIDA, "vigia_presente_lado.png"))
    c.salvar_png(todas[1], os.path.join(PASTA_SAIDA, "vigia_sonho_lado.png"))
    c.salvar_png(c.montar_folha([todas[2:6], todas[6:10]]), os.path.join(PASTA_SAIDA, "vigia_referencia.png"))
    print("[vigia] paleta:", " ".join(c.rgb_para_hex(np.array(cor) / 255) for cor in paleta))

    # No .blend, as duas versões lado a lado (presente à esquerda).
    col_p.hide_render = col_s.hide_render = False
    raiz_p.location.x, raiz_s.location.x = -0.6, 0.6
    raiz_s.rotation_euler = (0, 0, 0.6)
    c.salvar_blend(ARQUIVO_BLEND, raiz_p)
    print("[vigia] pronto")


main()
