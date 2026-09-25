# Visão Geral — Estilo Artístico e Atmosfera

## 1. Direção Visual

- **Estilo:** Pixel art em vista lateral com sensação de profundidade 2.5D (estilo consagrado por *Five Nights at Freddy's: Into the Pit*).
- **Resolução Nativa:** 320×180 pixels, com escala inteira (*pixel perfect*) na viewport do Godot 4.7.
- **Filtragem de Texturas:** *Nearest* (sem interpolação linear, preservando a nitidez de cada pixel).
- **Camadas de Profundidade:**
  - **Fundo (Background):** Paredes distantes, janelas com luz exterior filtrada, silhuetas de prédios ao longe.
  - **Plano de Ação (Midground):** Gabriel, Insones, portas, móveis interativos e obstáculos navegáveis.
  - **Primeiro Plano (Foreground):** Raízes caídas, colunas em primeiro plano, folhas e poeira em suspensão que geram sensação claustrofóbica e tridimensional.

---

## 2. O Contraste entre os Dois Mundos

A direção de arte estabelece um contraste visceral e imediato entre as duas temporalidades do jogo:

### O Presente (Ruína Milenar)
- **Cores Predominantes:** Cinzas de concreto desgastado, marrons terrosos, verde-musgo profundo, tons de areia de dunas e o ciano/esmeralda gélido dos fungos bioluminescentes.
- **Iluminação:** Fortemente contrastada. A luz do sol entra em feixes poeirentos por buracos de lajes e tetos desabados (via `shaders/raios_de_sol.gdshader`). Os interiores são escuros, dependentes do brilho frágil da lanterna de fungos.
- **Sensação:** Silêncio melancólico, poeira, pólen, degradação natural e abandono cósmico.

### O Passado / Sonhos (Véspera de Provas)
- **Cores Predominantes:** Branco clínico e tons quentes de luz fluorescente, amarelo suave, mesas de fórmica limpas, corredores movimentados, telas de computadores acesas.
- **Iluminação:** Plana, acolhedora e uniforme, sem sombras assustadoras.
- **Sensação:** Ansiedade acadêmica palpável, murmúrios de corredores, normalidade urbana do século XXI.

---

## 3. Pipeline de Arte

Para manter a consistência de proporção e iluminação sem depender de pacotes pagos de terceiros, o projeto utiliza um fluxo híbrido inovador:

1. **Modelagem 3D (Blender):**
   - Criação de modelos geométricos simplificados de personagens e cenários em Blender (`assets/modelagem/personagens/`).
   - Configuração de câmera ortogonal e luzes pontuais consistentes.
2. **Renderização Automatizada:**
   - Scripts Python no Blender (`gerar_gabriel.py`, `gerar_vigia.py`, `gerar_seg_acordar.py`) geram projeções das poses e ângulos necessários.
3. **Pós-processamento em Pixel Art:**
   - Imagens são reduzidas à resolução alvo e tratadas com paletas harmonizadas.
4. **Integração no Godot:**
   - Importação direta com suporte aos arquivos `.import` correspondentes em `assets/sprites/`.
