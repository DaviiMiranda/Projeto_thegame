# Computação — Grade Horária e Coloração de Grafos

## 1. O Problema da Grade Acadêmica (*Timetabling*)

Na semana de provas da universidade, dezenas de turmas e exames precisam ser distribuídos em horários e salas sem que ocorram conflitos:
- Um mesmo professor não pode aplicar duas provas simultaneamente em locais distintos.
- Uma mesma sala física não pode abrigar duas turmas no mesmo horário.
- Alunos matriculados em disciplinas afins não podem ter exames no mesmo período.

Esse desafio clássico de alocação de recursos é modelado no jogo através do **Problema de Coloração de Vértices de Grafos**.

---

## 2. Modelagem Matemática do Grafo de Conflito

Constrói-se um grafo de interferência $G_{conflito} = (T, C)$:
- **Vértices ($T$):** Cada prova ou aula $t_i$.
- **Arestas ($C$):** Existe uma aresta $(t_i, t_j)$ se $t_i$ e $t_j$ compartilham o mesmo professor, a mesma sala ou o mesmo grupo de estudantes.
- **Cores ($\mathcal{K}$):** Cada cor $k \in \{1, 2, \dots, K\}$ representa um intervalo de horário específico da semana de provas (ex.: Manhã 1, Manhã 2, Noite).

O objetivo é encontrar uma função de coloração $c: T \to \mathcal{K}$ tal que:
$$(t_i, t_j) \in C \implies c(t_i) \neq c(t_j)$$

---

## 3. Aplicação Direta na Experiência do Jogador

A coloração de grafos não é apenas um gerador de dados estáticos; ela controla dinamicamente a jogabilidade:

1. **A Agenda dos Insones:** O algoritmo de coloração define a matriz de horários dos professores e monitores.
2. **Previsibilidade Estratégica:**
   - Nos **sonhos**, Gabriel examina o mural de provas e memoriza a alocação (ex.: *"O professor de Cálculo está na sala D-104 no primeiro horário e vai para a sala D-208 no segundo"*).
   - Nas **ruínas**, um alarme periódico ressoa nos alto-falantes carcomidos do campus marcando a troca de horário. O Professor interrompe o que está fazendo e caminha para a próxima sala ditada pela cor da grade horária.
3. **Puzzles de Evitamento:** O jogador planeja sua travessia pelos blocos de aula sabendo exatamente quais salas estarão ocupadas ou vazias em cada bloco de tempo.
