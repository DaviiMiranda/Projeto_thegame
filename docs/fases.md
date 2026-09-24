# Fases e puzzles

Tudo que é **específico de cada fase** do Projeto The Game fica aqui: salas, Insones, puzzles, sonho e o que o jogador descobre. O GDD (`gdd.md`, item 4) descreve o campus em geral; este arquivo detalha uma fase de cada vez.

- **Dono:** papel 4 (Roteiro e fases). Qualquer um pode propor mudança por PR.
- Aqui só entra o que já foi decidido (no GDD ou em `decisoes.md`). O que ainda não foi decidido fica como _a definir_.
- Se algo aqui contradizer `decisoes.md`, vale `decisoes.md`.

---

## Como organizar os puzzles

### 1. Todo puzzle é uma passagem do grafo

No GDD, o campus é um grafo (salas = nós, passagens = arestas) e a progressão é "por passagens abertas, mecanismos e senhas". Então cada puzzle é uma **passagem fechada**: resolver o puzzle liga uma **flag** no dicionário de flags do mundo, e a flag abre a aresta.

Assim os puzzles usam o grafo e as flags que já estão no GDD (item 2.4), sem código especial para cada um.

### 2. De onde vem a pista

O GDD diz que as passagens se abrem "parte com o que se encontra nas ruínas e parte com o que se aprende nos sonhos". Cada ficha de puzzle registra de qual dos dois vem a pista.

### 3. Tipos de puzzle

Os tipos saem das mecânicas do GDD. Servem para variar e não repetir o mesmo puzzle em todas as fases.

| Tipo | Mecânica do GDD que usa |
|---|---|
| **Senha** | senhas aprendidas nos sonhos |
| **Horário** | ler a grade: saber onde cada Insone está a cada hora |
| **Distração** | jogar objetos e fazer barulho (som por BFS) |
| **Ambiente** | tetos desabados, frestas, árvores caídas, andares enterrados |
| **Luz** | fungos bioluminescentes |
| **Observação** | examinar objetos e marcas nas paredes |

### 4. Ficha de cada puzzle

Cada puzzle recebe um ID `FASE-NN` (ex.: `SEG-01`, `TER-01`) e uma ficha na seção da fase:

```
### SEG-01 — Nome do puzzle
- Tipo:
- Onde: sala do obstáculo
- Obstáculo: o que impede o jogador
- Pista: onde está (sonho ou ruínas, e em que sala)
- Solução: o que o jogador faz
- Libera: nome da flag + passagem/sala/item que abre
- Depende de: IDs ou flags que precisam vir antes
- Perigo: qual Insone ameaça durante o puzzle
- Status: ideia / aprovado / implementado
```

O campo **Libera** usa o mesmo nome de flag que vai para o código (`snake_case`), para que roteiro e programação usem a mesma lista.

### 5. Mapa de dependências

Cada fase pode ter um diagrama `mermaid` (o GitHub desenha sozinho) mostrando o que precisa vir antes do quê. Serve para ver se algum puzzle ficou sem pista ou se a fase pode travar.

Esse mapa é um grafo dirigido: a ordem possível de resolução é uma ordenação topológica, e um ciclo nele significa que a fase trava.

---

## Resumo das fases

Conforme a tabela de progressão do GDD (item 2).

| Dia | Área | O que se descobre |
|---|---|---|
| Segunda | Biblioteca | Ele dormiu muito. As pessoas ainda estão aqui — ou o que sobrou delas. |
| Terça | Blocos de aula | Os Insones seguem a grade da semana de provas. Os tracinhos contados nas paredes indicam séculos. |
| Quarta | Centro de Convivência e Espaço Cultural | Havia uma pesquisa com voluntários naquela semana. |
| Quinta | NAMI | O estimulante, os testes, a lista de voluntários — e o nome dele nela. |
| Sexta | Reitoria e portão principal | Quanto tempo passou de verdade, e o que aconteceu com o mundo lá fora. |

Em todas as fases: Rafa "é o Insone que aparece em todos os dias" (GDD, item 3).

---

## Segunda — Biblioteca

- **O que o GDD já diz:** tutorial e primeiro contato. Silêncio é regra: correr aqui chama a Bibliotecária. Estantes caídas e vazias, uma árvore no meio do salão, luz do sol por um teto aberto.
- **Insones:** Bibliotecária, Rafa.
- **Marco do Sprint 4** (`equipe.md`): a Biblioteca jogável do começo ao fim.
- **Objetivo:** _a definir_

### Salas
_A definir._

### Puzzles
_A definir._

### Sonho
_A definir._

---

## Terça — Blocos de aula

- **O que o GDD já diz:** corredores parcialmente enterrados em areia, salas sem teto, quadros nas paredes, paredes cobertas de tracinhos. Onde a grade mais importa: o Professor muda de sala a cada horário.
- **Insones:** Professor, Rafa.
- **Objetivo:** _a definir_

### Salas
_A definir._

### Puzzles
_A definir._

### Sonho
_A definir._

---

## Quarta — Centro de Convivência e Espaço Cultural

- **O que o GDD já diz:**
  - Centro de Convivência: área ampla, poucos esconderijos, os Calouros andam em grupo.
  - Espaço Cultural: galeria escura, fungos nas paredes, puzzles visuais e as primeiras peças do projeto VIGÍLIA-7.
- **Insones:** Calouros, Rafa.
- **Objetivo:** _a definir_

### Salas
_A definir._

### Puzzles
_A definir._

### Sonho
_A definir._

---

## Quinta — NAMI

- **O que o GDD já diz:** corredores de azulejo rachado, macas, andar de baixo alagado, só a luz dos fungos. O ponto alto da tensão e das revelações. A Pesquisadora fica no fundo do NAMI.
- **Insones:** Pesquisadora, Rafa.
- **Objetivo:** _a definir_

### Salas
_A definir._

### Puzzles
_A definir._

### Sonho
_A definir._

---

## Sexta — Reitoria e portão

- **O que o GDD já diz:** o prédio mais conservado, com o cofre e os arquivos; do lado de fora do portão, só vegetação. É o final: sair sozinho ou fazer o campus dormir, e as opções dependem do que o jogador descobriu.
- **Insones:** Rafa. Demais _a definir_.
- **Objetivo:** chegar ao portão principal.

### Salas
_A definir._

### Puzzles
_A definir._

### Sonho
_A definir._
