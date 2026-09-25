# Fases — Estrutura e Funcionamento

Este documento define como as fases e áreas do **Projeto The Game** funcionam em termos de arquitetura, fluxo de jogo e design de níveis (*level design*).

> [!NOTE]
> A divisão exata de fases (seja por áreas geográficas, prédios ou etapas da progressão) ainda está sendo definida pelo grupo. Este módulo fornece a **estrutura conceitual e o template padronizado** para a criação de qualquer fase.

---

## 🏗️ Como Funciona uma Fase no Jogo

Diferente de fases lineares isoladas com telas de carregamento tradicionais, o mundo do jogo é concebido como um **campus contínuo** modelado como um grafo de salas e corredores:

1. **Topologia e Conexões:**
   - Cada fase corresponde a um conjunto de cômodos (nós do grafo) conectados por passagens físicas (portas, vãos, janelas, buracos de desabamento).
   - Áreas exploradas anteriormente continuam acessíveis ou sofrem alterações (novas passagens abertas, caminhos bloqueados por escombros).

2. **Fluxo de Objetivos:**
   - **Objetivo Principal:** Uma meta clara que motiva o jogador a atravessar a área (ex.: encontrar uma chave, alcançar um terminal, desobstruir uma passagem).
   - **Objetivos Secundários:** Exploração opcional para coletar recursos adicionais (fungos, cápsulas de clarão, documentos ou relíquias).

3. **Dinâmica de Inimigos (Insones):**
   - Cada área possui Insones alocados que operam sob uma rotina inicial ditada pela grade horária.
   - O nível de desafio é modulado pela densidade de inimigos, pelos tipos de sentidos dominantes (audição, visão, luz) e pela disponibilidade de esconderijos na área.

4. **Puzzles e Travessia:**
   - Obstáculos mecânicos que exigem o uso das ferramentas de jogo: travessia silenciosa sobre pisos barulhentos, manipulação de luz em áreas escuras ou uso de senhas e códigos aprendidos nos sonhos.

5. **Sala Segura (*Safe Room*):**
   - Toda área deve conter pelo menos uma sala protegida com tranca funcional.
   - É nela que o jogador pode realizar o salvamento de estado e acionar a mecânica de dormir/sonhar para obter novas informações no passado.

---

## 📋 Como Criar uma Nova Fase

Para documentar uma nova fase ou área assim que o grupo fechar o escopo:
1. Copie o arquivo modelo [`template_fase.md`](template_fase.md).
2. Nomeie o novo arquivo seguindo o padrão `nome_da_area.md` (ex.: `biblioteca.md`, `blocos_aula.md`).
3. Preencha todos os campos do template.
