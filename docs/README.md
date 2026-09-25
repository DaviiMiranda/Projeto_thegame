# Documentação — Projeto The Game

Bem-vindo ao repositório de documentação do **Projeto The Game**, jogo de terror atmosférico e sobrevivência em pixel art 2.5D desenvolvido para a disciplina de Computação Gráfica (Semestre 6) na Unifor.

---

## 📌 Fonte da Verdade e Hierarquia

Para evitar contradições em um projeto em constante evolução, adotamos a seguinte regra de precedência:

1. **[`docs/decisoes.md`](decisoes.md)** — **Autoridade máxima**. Qualquer decisão recente de design, história ou técnica registrada aqui sobrepõe qualquer outro documento.
2. **Documentos Específicos de Módulos** — Detalhes aprofundados sobre mecânicas, personagens, fases, computação ou diálogos contidos em suas respectivas pastas.
3. **[`docs/gdd.md`](gdd.md)** — Sumário executivo e visão geral unificada (Game Design Document).

---

## 🗺️ Mapa de Navegação da Documentação

A documentação é dividida em módulos temáticos para facilitar o trabalho simultâneo da equipe e evitar conflitos no Git:

```
docs/
├── README.md                     # Este mapa de navegação e índice mestre
├── decisoes.md                   # Registro cronológico de decisões (ADRs)
├── equipe.md                     # Papéis da equipe e entregas acadêmicas
├── gdd.md                        # GDD resumido e visão executiva integrada
│
├── visao_geral/                  # Pilares conceituais, escopo e identidade
│   ├── conceito.md               # Premissa, público-alvo, plataforma e pilares centrais
│   └── estilo_artistico.md       # Identidade visual 2.5D, iluminação e referências
│
├── historia/                     # Universo, linha do tempo e narrativa
│   ├── README.md                 # Visão geral da trama e estrutura narrativa
│   ├── lore_e_mundo.md           # A Unifor mil anos no futuro e a tragédia do VIGÍLIA-7
│   ├── narrativa_e_finais.md     # Revelações progressivas e os dois finais
│   └── reliquias_e_lore.md       # Narrativa ambiental, marcas nas paredes e fósseis
│
├── personagens/                  # Fichas detalhadas de elenco
│   ├── README.md                 # Guia de personagens e convenções
│   ├── gabriel.md                # O protagonista: história, limitações e motivação
│   ├── rafa.md                   # Melhor amigo no passado e caçador recorrente no presente
│   └── insones.md                # Catálogo dos Insones: comportamentos, sentidos e rotinas
│
├── mecanicas/                    # Regras de jogo e jogabilidade
│   ├── README.md                 # Core loop e dinâmica de jogo
│   ├── movimentacao_e_terreno.md # Andar, correr, ruído acústico e travessia de ruínas
│   ├── furtividade_e_esconderijos.md # Esconderijos, microgames de tensão e distrações
│   ├── iluminacao_e_fungos.md    # Fungos bioluminescentes, lanterna de pote e clarão
│   └── sono_e_sonhos.md          # Ponto de salvamento e mecânica de investigação no passado
│
├── computacao/                   # Requisitos obrigatórios de Computação Gráfica / CC
│   ├── README.md                 # Mapa de aplicação dos algoritmos e estruturas
│   ├── grafos_e_navegacao.md     # Campus modelado como grafo ponderado dinâmico
│   ├── grade_e_coloracao.md      # Geração da grade de horários via coloração de grafos
│   ├── ia_e_perseguicao.md       # BFS (som), A* (perseguição), Markov e FSM
│   └── geometria_e_shaders.md    # Produto escalar para visão, raycasting e shaders
│
├── fases/                        # Progressão dos 5 dias da semana de provas
│   ├── README.md                 # Visão geral da semana e interconexão do campus
│   ├── dia_1_biblioteca.md       # Segunda-feira: O despertar e o silêncio da Bibliotecária
│   ├── dia_2_blocos_aula.md      # Terça-feira: Blocos de aula e as lições eternas do Professor
│   ├── dia_3_centro_cultural.md  # Quarta-feira: Convivência e a horda dos Calouros
│   ├── dia_4_nami.md             # Quinta-feira: NAMI, o laboratório e a Pesquisadora
│   └── dia_5_reitoria.md         # Sexta-feira: Reitoria, cofre da verdade e fuga final
│
├── dialogos/                     # Textos, falas e sistema de conversação
│   ├── README.md                 # Arquitetura técnica do sistema de diálogos
│   ├── sonhos.md                 # Diálogos do passado pré-incidente (memórias vívidas)
│   └── murmurios.md              # Falas fragmentadas dos Insones no presente
│
└── roteiro/                      # Roteirização cinematográfica e cutscenes
    ├── README.md                 # Diretrizes de roteiro e direção de cenas
    └── cutscenes/                # Documentação técnica e roteiro de cada cutscene
        ├── README.md             # Padrão de cutscenes no Godot
        └── seg_acordar.md        # Cutscene inicial do despertar de Gabriel
```

---

## ⚡ Guia Rápido para Colaboradores

- **Vai criar uma nova mecânica ou cena?** Consulte [`docs/mecanicas/`](mecanicas/) e [`docs/computacao/`](computacao/).
- **Vai escrever diálogos ou histórias?** Consulte [`docs/historia/`](historia/) e [`docs/dialogos/`](dialogos/).
- **Vai modelar ou criar sprites?** Consulte [`docs/visao_geral/estilo_artistico.md`](visao_geral/estilo_artistico.md) e [`docs/personagens/`](personagens/).
- **Tomou uma decisão que muda o design ou o escopo?** Registre imediatamente em [`docs/decisoes.md`](decisoes.md).
