# Personagens — Gabriel (Funcionamento do Jogador)

Este documento descreve como o personagem controlado pelo jogador funciona em termos de mecânica, estados e sistemas.

---

## 1. Identificação Básica

- **Nome:** Gabriel *(decisão registrada em `docs/decisoes.md`)*
- **Tipo:** Protagonista / Personagem Controlável pelo Jogador
- **Papel:** Aluno que acorda mil anos depois na Biblioteca e investiga as ruínas da Unifor.

---

## 2. Estados de Movimentação (FSM do Jogador)

O script do jogador opera sob uma máquina de estados finita:

| Estado | Velocidade | Emissão de Ruído Acústico | Consumo de Estamina | Descrição |
|---|---|---|---|---|
| **PARADO** | 0 px/s | Nula | Regeneração rápida | Em repouso. |
| **ANDANDO** | Padrão (100%) | Baixo (mesma sala) | Nulo | Movimento padrão de exploração. |
| **CORRENDO** | Rápido (180%) | **Alto** (propaga no grafo) | Alto (~4s contínuos) | Fuga rápida; alerta Insones próximos. |
| **AGACHADO** | Lento (50%) | **Silencioso** | Nulo | Permite passar por vãos e não faz barulho. |
| **ESCONDIDO** | 0 px/s | Condicionado ao microgame | Nulo | Dentro de armário ou cabine. |
| **EXAUSTO** | Lento (40%) | Respiração ofegante | Nulo (bloqueio temporário) | Ocorre quando a estamina se esgota totalmente. |

---

## 3. Gestão de Inventário e Ferramentas

O jogador interage com o ambiente através de itens específicos:

- **Pote de Fungos (Lanterna):**
  - Alterna entre ligado/desligado.
  - Ilumina a escuridão mas pode ser detectado pelo Vigia.
- **Cápsulas de Clarão:**
  - Item consumível de defesa (máximo 2 unidades).
  - Atordoa temporariamente Insones próximos para permitir fuga.
- **Objetos de Arremesso (Pedras/Entulho):**
  - Geram distração acústica em salas distantes via propagação BFS.
- **Caderno de Anotações:**
  - Registra pistas, senhas e detalhes da grade horária descobertos nos sonhos.

---

## 4. Integração Técnica

- **Cena:** `cenas/personagens/gabriel.tscn`
- **Script:** `scripts/personagens/gabriel.gd`
- **Assets de Arte:** `assets/sprites/personagens/gabriel/` e `assets/modelagem/personagens/gabriel.blend`
