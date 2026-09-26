# gerar_interface.py — desenha, por código, os ÍCONES DOS ITENS e as peças
# da INTERFACE (inventário e espaços de gadget), no mesmo estilo da
# Biblioteca: mesma paleta, mesmo dithering, mesmo contorno escuro.
#
# Como rodar (Python 3 + numpy, igual ao gerar_biblioteca.py):
#
#   python assets/modelagem/interface/gerar_interface.py
#
# O que sai:
#   assets/sprites/itens/<item>.png                16 x 16 px: ícone do item (inventário)
#   assets/sprites/itens/<item>_chao.png           o item caído no chão, na escala do
#                                                  cenário (1 px ≈ 3,6 cm: um pote tem ~6 px)
#   assets/sprites/interface/espaco.png            20 x 20 px: um espaço vazio da grade
#   assets/sprites/interface/espaco_selecionado.png  o mesmo, com a borda acesa
#   assets/sprites/interface/painel.png            24 x 24 px: fundo das janelas, em
#                                                  "9 fatias" (NinePatchRect no Godot)
#
# Este script IMPORTA as funções do gerar_biblioteca.py (paleta, pintar com
# dithering, contorno...), como o gerar_kit.py faz. Assim um ícone novo sai
# automaticamente com as mesmas cores do cenário.
#
# Painel em "9 fatias": a imagem é dividida em 3 x 3 pedaços. Os 4 cantos
# ficam do tamanho original, as 4 bordas esticam só num sentido e o meio
# estica nos dois. Assim uma imagem pequena vira uma janela de qualquer
# tamanho sem deformar a moldura. No Godot, o NinePatchRect faz isso: as
# margens (patch_margin) dizem onde cortar — aqui, 6 px de cada lado.

import importlib.util
import os

import numpy as np

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.normpath(os.path.join(PASTA_SCRIPT, "..", "..", ".."))
PASTA_ITENS = os.path.join(PASTA_PROJETO, "assets", "sprites", "itens")
PASTA_INTERFACE = os.path.join(PASTA_PROJETO, "assets", "sprites", "interface")

# Importa o gerar_biblioteca.py como um módulo (sem rodar o main dele).
_spec = importlib.util.spec_from_file_location(
    "gerar_biblioteca",
    os.path.join(PASTA_PROJETO, "assets", "modelagem", "salas", "biblioteca", "gerar_biblioteca.py"))
bib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bib)

Imagem, RAMPAS, CONTORNO, ruido = bib.Imagem, bib.RAMPAS, bib.CONTORNO, bib.ruido

TAMANHO_ICONE = 16
TAMANHO_ESPACO = 20
TAMANHO_PAINEL = 24
MARGEM_PAINEL = 6       # patch_margin do NinePatchRect (mude lá se mudar aqui)


# ---------------------------------------------------------------------------
# Ícones dos itens
# ---------------------------------------------------------------------------


def pote_fungos():
    """A lanterna do Gabriel: um pote de conserva de vidro com fungos
    bioluminescentes dentro (docs/mecanicas/iluminacao_e_fungos.md).
    Vidro escuro e frio, tampa de metal enferrujada, fungos ciano no fundo
    e um reflexo claro de 1 px na lateral, que é o que faz parecer vidro."""
    img = Imagem(TAMANHO_ICONE, TAMANHO_ICONE)
    X, Y = img.X, img.Y
    fino = ruido(img.w, img.h, 2, 2, 7)
    # Corpo do pote: um retângulo de cantos cortados (ombro em cima).
    corpo = img.poligono([(3, 5), (4, 4), (12, 4), (13, 5), (13, 14), (12, 15), (4, 15), (3, 14)])
    # Vidro: escuro, um pouco mais claro na esquerda (a luz vem de lá).
    img.pintar(corpo, "metal", 0.22 + 0.12 * (1 - (X - 3) / 10) + 0.06 * fino)
    # Brilho de dentro: a metade de baixo do vidro fica esverdeada/ciano,
    # iluminada pelos próprios fungos.
    brilho = corpo & (Y >= 9)
    img.pintar(brilho, "fungo", 0.05 + 0.3 * (Y - 9) / 6)
    # Fungos: três chapéus claros no fundo do pote (talo escuro, chapéu
    # claro, um ponto branco em cima: o mesmo desenho dos fungos do cenário).
    for (x, y, r) in ((5, 12, 1.5), (8, 10, 2.0), (11, 12, 1.2)):
        img.pintar(img.ret(x, y + 1, x + 1, 15), "fungo", 0.45)
        img.pintar(img.elipse(x + 0.5, y + 0.5, r + 0.5, r * 0.55 + 0.5), "fungo", 0.85)
        img.cor(img.ret(x, y, x + 1, y + 1), RAMPAS["fungo"][5])
    # Reflexo do vidro: uma linha clara vertical à esquerda.
    img.pintar(img.ret(4, 6, 5, 11), "ceu", 0.55)
    img.cor(img.ret(4, 6, 5, 7), RAMPAS["ceu"][5])
    # Tampa de metal enferrujada (mais larga que a boca do pote).
    tampa = img.ret(4, 1, 12, 4)
    img.pintar(tampa, "ferrugem", 0.35 + 0.25 * (Y == 1) + 0.1 * fino)
    img.pintar(img.ret(4, 3, 12, 4), "ferrugem", 0.2)          # borda de baixo, na sombra
    # Rótulo de papel velho, meio rasgado.
    rotulo = img.ret(6, 6, 11, 9) & ~((X == 10) & (Y == 8))
    img.pintar(rotulo, "papel", 0.45 + 0.2 * fino)
    img.contornar(CONTORNO)
    return img


def pote_fungos_chao():
    """O mesmo pote, caído no chão da sala. No cenário 1 px vale ~3,6 cm
    (o Gabriel tem 49 px), então um pote de conserva de ~25 cm tem 7 px de
    altura. Pouco detalhe: tampa, vidro, brilho ciano embaixo e o reflexo."""
    img = Imagem(9, 10)
    X, Y = img.X, img.Y
    corpo = img.poligono([(1, 3), (2, 2), (7, 2), (8, 3), (8, 8), (7, 9), (2, 9), (1, 8)])
    img.pintar(corpo, "metal", 0.3)
    img.pintar(corpo & (Y >= 5), "fungo", 0.35 + 0.35 * (Y - 5) / 4)
    img.cor(img.ret(4, 6, 5, 7), RAMPAS["fungo"][5])
    img.pintar(img.ret(2, 4, 3, 6), "ceu", 0.6)                 # reflexo do vidro
    img.pintar(img.ret(2, 1, 8, 3), "ferrugem", 0.4 + 0.2 * (Y == 1))   # tampa
    img.contornar(CONTORNO)
    return img


# Nome do arquivo -> função que desenha. Um item novo entra aqui.
ICONES = {
    "pote_fungos": pote_fungos,
    "pote_fungos_chao": pote_fungos_chao,
}


# ---------------------------------------------------------------------------
# Peças da interface
# ---------------------------------------------------------------------------


def espaco(aceso=False):
    """Um espaço da grade do inventário: um nicho escavado no concreto.
    A borda de cima e da esquerda fica escura e a de baixo e da direita
    clara (é o "chanfro para dentro": parece fundo, como uma prateleira).
    Aceso = selecionado: a borda vira a cor do sol, a mesma dos raios que
    entram pelo teto."""
    n = TAMANHO_ESPACO
    img = Imagem(n, n)
    fino = ruido(n, n, 2, 2, 3)
    tudo = img.ret(0, 0, n, n)
    img.pintar(tudo, "concreto", 0.32 + 0.08 * fino)
    dentro = img.ret(2, 2, n - 2, n - 2)
    img.cor(dentro, RAMPAS["concreto"][0])
    # Chanfro: sombra em cima/esquerda, luz embaixo/direita (1 px cada).
    img.pintar(img.ret(1, 1, n - 1, 2) | img.ret(1, 1, 2, n - 1), "concreto", 0.12)
    img.pintar(img.ret(1, n - 2, n - 1, n - 1) | img.ret(n - 2, 1, n - 1, n - 1), "concreto", 0.55)
    if aceso:
        borda = tudo & ~img.ret(1, 1, n - 1, n - 1)
        img.pintar(borda, "sol", 0.72)
        img.pintar(img.ret(1, 1, n - 1, 2) | img.ret(1, 1, 2, n - 1), "sol", 0.35)
    else:
        img.cor(tudo & ~img.ret(1, 1, n - 1, n - 1), CONTORNO)
    return img


def painel():
    """Fundo das janelas (inventário): concreto escuro e manchado, com uma
    moldura de 2 px (contorno quase preto + fio claro por dentro).
    Os cantos são cortados em diagonal, como uma placa gasta."""
    n = TAMANHO_PAINEL
    img = Imagem(n, n)
    fino = ruido(n, n, 2, 2, 5)
    manchas = ruido(n, n, 6, 6, 6)
    tudo = img.poligono([(1, 0), (n - 1, 0), (n, 1), (n, n - 1), (n - 1, n), (1, n), (0, n - 1), (0, 1)])
    img.pintar(tudo, "concreto", 0.14 + 0.08 * manchas + 0.05 * fino)
    borda = tudo & ~img.ret(1, 1, n - 1, n - 1)
    img.cor(borda, CONTORNO)
    fio = img.ret(1, 1, n - 1, n - 1) & ~img.ret(2, 2, n - 2, n - 2)
    img.pintar(fio, "concreto", 0.42 + 0.1 * fino)
    return img


def main():
    print("Gerando ícones e interface")
    for nome, funcao in ICONES.items():
        funcao().salvar(f"{nome}.png", PASTA_ITENS)
    espaco().salvar("espaco.png", PASTA_INTERFACE)
    espaco(aceso=True).salvar("espaco_selecionado.png", PASTA_INTERFACE)
    painel().salvar("painel.png", PASTA_INTERFACE)


if __name__ == "__main__":
    main()
