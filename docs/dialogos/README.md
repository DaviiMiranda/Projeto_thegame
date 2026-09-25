# Diálogos — Arquitetura Técnica e Funcionamento

Este documento define como o sistema de diálogos é estruturado e executado no **Projeto The Game**.

---

## 1. Princípios de Funcionamento

O sistema de diálogos é projetado para ser leve, modular e totalmente desacoplado da jogabilidade através de **sinais do Godot 4.7**:

- **Desacoplamento:** O personagem ou trigger de cena apenas emite a intenção de iniciar uma conversa (`iniciar_dialogo(id)`). Uma cena de interface dedicada (`CaixaDialogo`) ou autoload (`GerenciadorDialogo`) processa os nós de texto.
- **Pausa Controlada:** Durante diálogos nos sonhos ou cutscenes, o movimento do jogador é suspenso mudando o estado do nó do jogador.
- **Suporte a Múltiplos Formatos:** Suporta diálogos sequenciais, ramificações com escolhas simples e falas rápidas de uma linha (ex.: murmúrios ou pensamentos de Gabriel).

---

## 2. Arquitetura de Sinais

```gdscript
# GerenciadorDialogo.gd (Autoload / Singleton)
signal dialogo_iniciado(id_conversa: String)
signal fala_exibida(locutor: String, texto: String, retrato: Texture2D)
signal escolhas_exibidas(opcoes: Array[String])
signal escolha_selecionada(indice: int)
signal dialogo_concluido(id_conversa: String)
```

### Ciclo de Execução:
1. Um gatilho de interação (ex.: conversar com um NPC em sonho) chama `GerenciadorDialogo.iniciar_dialogo("id_do_dialogo")`.
2. O gerenciador emite `dialogo_iniciado`. A interface de usuário (HUD) se torna visível.
3. Para cada linha de fala, emite `fala_exibida`. A UI exibe o nome do locutor, toca o som de digitação (*typewriter*) e mostra o retrato se houver.
4. Quando o jogador clica para avançar (ou seleciona uma opção), avança para a próxima linha.
5. Ao esgotar as linhas, emite `dialogo_concluido`. A UI é ocultada e o controle volta ao jogador.

---

## 3. Modelo de Criação de Diálogo

Para redigir ou incluir um novo diálogo no jogo, siga as diretrizes e os exemplos de formatação documentados em:
👉 **[`template_dialogo.md`](template_dialogo.md)**
