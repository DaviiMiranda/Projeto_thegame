# Computação — Grafos e Navegação no Campus

## 1. O Campus como Grafo Ponderado

A topologia do campus da Unifor em *Projeto The Game* é formalmente estruturada como um grafo não direcionado ponderado $G = (V, E, W)$:

- **Vértices ($V$):** Cada sala de aula, corredor, saguão da biblioteca, cabine de estudo, pátio externo e laboratório do NAMI é representado por um nó no grafo com coordenadas espaciais e propriedades ambientais.
- **Arestas ($E$):** As conexões físicas transitáveis entre dois nós vizinhos — portas, arcos de corredor, vãos em tetos desabados, escadas e frestas de passagem.
- **Pesos das Arestas ($W$):** O custo de travessia entre dois nós adjacentes, ponderado pela fórmula:
  $$W(u, v) = \text{Distância}(u, v) \times \text{FatorPiso}(u, v)$$
  onde $\text{FatorPiso}$ penaliza pisos de areia pesada ou entulho ruidoso.

---

## 2. Modificação Dinâmica da Topologia

O grafo não é estático; ele sofre mutações conforme o jogador progride e os dias avançam:

### A. Remoção de Arestas (Desabamentos e Bloqueios)
- Eventos climáticos ou abalos estruturais causam novos desabamentos entre um dia e outro.
- Se uma laje desaba bloqueando o corredor entre o Bloco D e o Bloco E, a aresta $(D_1, E_1)$ é removida do grafo ou seu peso é ajustado para $\infty$.
- Isso força Gabriel (e os Insones) a recalcularem rotas por caminhos alternativos.

### B. Inserção de Arestas (Atalhos e Chaves)
- Ao encontrar uma chave enferrujada ou desobstruir uma porta escorada por raízes, o jogador adiciona uma nova aresta $(u, v)$ ao conjunto $E$.
- Esses atalhos reduzem o caminho mínimo entre as áreas seguras e os objetivos, diminuindo o tempo de exposição aos Insones.

---

## 3. Estrutura de Dados em GDScript

```gdscript
class_name GrafoCampus
extends Node

# Dicionário de adjacência: { id_no: { vizinho_id: peso } }
var adjacencias: Dictionary = {}

func adicionar_no(id: String, dados: Dictionary = {}) -> void:
    if not adjacencias.has(id):
        adjacencias[id] = {}

func conectar(id_origem: String, id_destino: String, peso: float = 1.0, bidirecional: bool = true) -> void:
    adjacencias[id_origem][id_destino] = peso
    if bidirecional:
        adjacencias[id_destino][id_origem] = peso

func desconectar(id_origem: String, id_destino: String) -> void:
    adjacencias[id_origem].erase(id_destino)
    adjacencias[id_destino].erase(id_origem)
```
