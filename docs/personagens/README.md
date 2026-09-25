# Personagens — Estrutura e Funcionamento

Este documento define como os personagens são arquitetados e funcionam mecanicamente no **Projeto The Game**.

---

## 🎭 Arquitetura de Personagens no Godot 4.7

Conforme as regras do projeto, cada personagem é uma **cena isolada** (`.tscn`) com seu respectivo script (`.gd`):

1. **O Jogador (Gabriel):**
   - Controlado pelo usuário através de inputs (`CharacterBody2D`).
   - Possui máquina de estados de locomoção (Parado, Andando, Correndo, Agachado, Escondido, Exausto).
   - Detalhes mecânicos em [`gabriel.md`](gabriel.md).

2. **Os Insones (Inimigos de IA):**
   - Controlados por inteligência artificial autônoma (`CharacterBody2D`).
   - Operam sob uma Máquina de Estados Finita (Rotina, Investigando, Caçando, Atordoado, Retornando).
   - Possuem sensores de percepção (visão por produto escalar e raycast, audição conectada ao grafo BFS, fotossensibilidade).
   - Detalhes de funcionamento em [`insones.md`](insones.md).

3. **NPCs dos Sonhos (Interações Passivas):**
   - Cenas leves focadas em interação de diálogo e passagem de informações investigativas.

---

## 📋 Como Criar uma Nova Ficha de Personagem

Para documentar um novo personagem quando o grupo decidir seu papel narrativo e mecânico:
👉 Utilize o modelo padronizado em **[`template_personagem.md`](template_personagem.md)**.
