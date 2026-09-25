# Personagens — Funcionamento dos Insones (Inimigos de IA)

Este documento descreve como a inteligência artificial e os tipos mecânicos de Insones funcionam no sistema do jogo.

---

## 1. Arquitetura da Inteligência Artificial

Cada Insone é controlado por um script derivado de uma classe base de IA (`InsoneBase.gd`), operando sob:

1. **Máquina de Estados Finita (FSM):**
   - **ROTINA:** Segue o caminho ou tarefa padrão prevista na grade horária.
   - **INVESTIGANDO:** Alerta por som ou luz suspeita; move-se para o nó de origem da perturbação.
   - **PERSEGUINDO:** Linha de visão direta com o jogador confirmada; persegue via algoritmo $A^*$.
   - **ATORDOADO:** Estado temporário (3 a 5 segundos) após impacto de cápsula de clarão.
   - **RETORNANDO:** Retorna à sala da rotina original após perder o jogador.

2. **Sensores de Percepção:**
   - **Sensor Acústico:** Conectado aos eventos sonoros emitidos no grafo do campus via BFS.
   - **Sensor Visual:** Cone angular calculado via produto escalar ($\vec{u} \cdot \vec{v}$) e oclusão por raycasting 2D.
   - **Sensor Fotossensível:** Detecta emissão de luz do pote de fungos do jogador a distâncias maiores.

---

## 2. Tipos de Comportamento dos Insones Planejados

Os inimigos são categorizados pelo seu sentido ou padrão de comportamento predominante:

| Tipo / Inimigo | Sentido Dominante | Comportamento Principal | Ponto Fraco / Resposta do Jogador |
|---|---|---|---|
| **Acústico** (ex.: Bibliotecária) | Audição extrema | Ouve passos correndo e ruídos de entulho a múltiplas salas de distância | Mover-se agachado; distrair com arremesso de pedras |
| **Por Horário** (ex.: Professor) | Cumprimento de grade | Troca de salas conforme os horários calculados pela coloração de grafos | Consultar a grade nos sonhos para planejar rotas seguras |
| **Sentinela / Noturno** (ex.: Vigia) | Fotossensibilidade | Patrulha áreas abertas e detecta lanternas acesas a longa distância | Tampar/apagar o pote de fungos ao cruzar seu campo |
| **Enxame / Bando** (ex.: Calouros) | Proximidade em grupo | Marcham juntos, bloqueando passagens e corredores estreitos | Uso de cápsula de clarão para dispersar o grupo |
| **Persistente** (ex.: Rafa) | Perseguição contínua | Persegue o jogador por múltiplos cômodos e não desiste facilmente | Microgames de esconderijo e controle de respiração |
