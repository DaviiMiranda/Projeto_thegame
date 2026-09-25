# Documentação — Projeto The Game

Bem-vindo ao repositório de documentação do **Projeto The Game**, jogo de terror atmosférico e sobrevivência em pixel art 2.5D desenvolvido para a disciplina de Computação Gráfica (Semestre 6) na Unifor.

---

## 📌 Fonte da Verdade e Hierarquia

Para manter a consistência entre o código, o design e o roteiro, adotamos a seguinte regra de precedência:

1. **[`docs/decisoes.md`](decisoes.md)** — **Autoridade máxima**. Toda decisão recente de design, história ou técnica registrada aqui sobrepõe qualquer outro documento.
2. **Documentos Específicos de Módulos** — Estruturações técnicas e mecânicas detalhadas em suas respectivas pastas.
3. **[`docs/gdd.md`](gdd.md)** — Sumário executivo e visão geral unificada (Game Design Document).

---

## 🗺️ Mapa de Navegação da Documentação

A documentação é organizada de forma modular, servindo como guia de funcionamento de cada sistema e fornecendo templates padronizados para preenchimento:

```
docs/
├── README.md                      # Este mapa de navegação e índice mestre
├── decisoes.md                    # Registro cronológico de decisões (ADRs)
├── equipe.md                      # Papéis da equipe e entregas acadêmicas
├── fases.md                       # Ponto de entrada para o design de fases
├── gdd.md                         # GDD executivo integrado
├── guia_montar_salas.md           # Como montar uma sala com o kit de cenário (passo a passo)
│
├── visao_geral/                   # Pilares conceituais, escopo e identidade
│   ├── conceito.md                # Premissa, público-alvo, escopo e pilares de design
│   └── estilo_artistico.md        # Identidade visual 2.5D, iluminação e pipeline Blender->Sprites
│
├── mecanicas/                     # Regras de jogo e funcionamento dos sistemas
│   ├── README.md                  # Diagrama do Core Loop de gameplay
│   ├── movimentacao_e_terreno.md  # Andar, correr, estamina, ruído e tipos de superfícies
│   ├── furtividade_e_esconderijos.md # Esconderijos, microgames de tensão e distrações
│   ├── iluminacao_e_fungos.md     # Pote de fungos, dilema luz/perigo e cápsulas de clarão
│   └── sono_e_sonhos.md           # Salas seguras, mecânica de save e investigação no passado
│
├── computacao/                    # Requisitos da disciplina de Computação Gráfica / CC
│   ├── README.md                  # Matriz de algoritmos aplicados ao jogo
│   ├── grafos_e_navegacao.md      # Campus modelado como grafo ponderado dinâmico
│   ├── grade_e_coloracao.md       # Algoritmo de coloração de grafos para horários de patrulha
│   ├── ia_e_perseguicao.md        # BFS (som), A* (perseguição), Cadeia de Markov e FSM
│   └── geometria_e_shaders.md     # Visão 2D por produto escalar, raycasting e shaders
│
├── fases/                         # Design de fases e áreas
│   ├── README.md                  # Estrutura e funcionamento do level design no campus
│   └── template_fase.md           # Modelo padronizado para documentação de novas fases/áreas
│
├── personagens/                   # Fichas técnicas e mecânica de personagens
│   ├── README.md                  # Arquitetura de personagens no Godot (Jogador vs Insones)
│   ├── gabriel.md                 # Funcionamento mecânico do jogador (estados, estamina, inventário)
│   ├── insones.md                 # Funcionamento dos inimigos de IA (sensores, FSM e sentidos)
│   └── template_personagem.md     # Modelo padronizado para novas fichas de personagens
│
├── dialogos/                      # Sistema de conversação e falas
│   ├── README.md                  # Arquitetura técnica desacoplada via sinais no Godot 4.7
│   └── template_dialogo.md        # Modelo estrutural (JSON / GDScript) para criação de diálogos
│
├── historia/                      # Estrutura narrativa e narrativa ambiental
│   ├── README.md                  # Funcionamento das camadas narrativas (presente vs sonhos)
│   └── template_documento.md      # Modelo padronizado para documentos, bilhetes e relíquias
│
└── roteiro/                       # Roteirização cinematográfica e cutscenes
    ├── README.md                  # Diretrizes gerais de roteiro
    └── cutscenes/                 # Estrutura técnica e documentação de cutscenes
        ├── README.md              # Padrão de implementação de cutscenes no Godot
        └── seg_acordar.md         # Cutscene inicial do despertar de Gabriel
```

---

## ⚡ Guia Rápido para a Equipe

- **Vai criar ou alterar uma mecânica?** Consulte [`docs/mecanicas/`](mecanicas/) e [`docs/computacao/`](computacao/).
- **Vai planejar uma sala ou área?** Utilize [`docs/fases/template_fase.md`](fases/template_fase.md).
- **Vai criar uma nova fala ou diálogo?** Utilize [`docs/dialogos/template_dialogo.md`](dialogos/template_dialogo.md).
- **Vai adicionar um documento ou relíquia de lore?** Utilize [`docs/historia/template_documento.md`](historia/template_documento.md).
- **Vai adicionar um novo personagem ou inimigo?** Utilize [`docs/personagens/template_personagem.md`](personagens/template_personagem.md).
- **Tomou uma decisão que muda o design ou escopo?** Registre imediatamente em [`docs/decisoes.md`](decisoes.md).
