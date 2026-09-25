# Personagens — Catálogo dos Insones

Os **Insones** são os habitantes perpétuos do campus da Unifor. Vítimas do teste de VIGÍLIA-7, perderam o sono e a consciência superior, tornando-se autômatos biológicos que repetem a rotina da semana de provas há dez séculos.

---

## 1. A Bibliotecária

- **Localização Principal:** Biblioteca Central (Dia 1 e conexões).
- **Sentido Dominante:** **Audição Aguda**.
- **Comportamento e Rotina:**
  - Percorre os corredores de estantes de ferro desabadas, executando o gesto mecânico de alinhar e folhear livros que se desfizeram há séculos.
  - Imune a pouca luz, mas reage violentamente a qualquer ruído acústico acima do limiar padrão.
- **Mecânica de Jogo:**
  - Correr ou pisar em entulho/cacos de vidro propaga ondas de som pelo grafo de salas via algoritmo BFS, alertando-a instantaneamente.
  - Exige que Gabriel se mova agachado ou use distrações acústicas (jogar pedras em cantos opostos).

---

## 2. O Professor

- **Localização Principal:** Blocos de Aula (Blocos C, D, E — Dia 2).
- **Sentido Dominante:** **Visão Direta e Rigor de Horário**.
- **Comportamento e Rotina:**
  - Carrega pastas desgastadas e giz esfarelado. Entra em salas sem teto, escreve fórmulas invisíveis em quadros negros quebrados e gesticula como se ministrasse uma aula magna.
  - Troca de sala de aula pontualmente ao soar do sinal da grade horária (gerada pelo algoritmo de coloração de grafos).
- **Mecânica de Jogo:**
  - O jogador precisa consultar a grade nos sonhos para saber qual sala estará ocupada e planejar rotas seguras.
  - Se avistar Gabriel em um corredor durante horário de aula, o Professor considera-o um "aluno gazeteiro" e dispara em perseguição para capturá-lo e arrastá-lo à carteira.

---

## 3. O Vigia

- **Localização Principal:** Pátios externos, passarelas, estacionamentos e áreas abertas (Dia 2, Dia 3 e Dia 5).
- **Sentido Dominante:** **Detecção de Luz (Fotossensibilidade)**.
- **Comportamento e Rotina:**
  - Faz a ronda perimetral histórica do campus com uma lanterna de metal sem pilhas, apontando-a mecanicamente para janelas e cantos.
  - Em cada pausa de ronda, aproxima-se de uma parede de concreto e faz mais um risco vertical com um prego enferrujado — o autor dos milhares de tracinhos espalhados pela universidade.
- **Mecânica de Jogo:**
  - Detecta feixes de luz a longas distâncias nas áreas abertas. O jogador precisa desligar/tampar o pote de fungos ao notar a silhueta do Vigia.
  - Assets técnicos: [`assets/sprites/personagens/vigia/visual.md`](../../assets/sprites/personagens/vigia/visual.md) e modelagem 3D em [`assets/modelagem/personagens/vigia.blend`](../../assets/modelagem/personagens/vigia.blend).

---

## 4. Os Calouros

- **Localização Principal:** Centro de Convivência e Espaço Cultural (Dia 3).
- **Sentido Dominante:** **Proximidade e Aglomeração em Bando**.
- **Comportamento e Rotina:**
  - Grupo denso de jovens insones que se deslocam juntos em marcha lenta e errática, arrastando mochilas apodrecidas.
  - Simbolizam o pânico coletivo dos alunos recém-ingressos na primeira semana de exames finais.
- **Mecânica de Jogo:**
  - Individualmente são lentos e previsíveis, mas em grupo bloqueiam corredores largos e passagens vitais.
  - Não são despistados com facilidade em áreas abertas, mas entram em pânico e se dispersam quando confrontados com o clarão de uma **cápsula de fungo** esmagada.

---

## 5. A Pesquisadora

- **Localização Principal:** NAMI — Laboratório Subterrâneo de Pesquisa Clínica (Dia 4).
- **Sentido Dominante:** **Máquina de Estados Complexa e Hipersensibilidade Territorial**.
- **Comportamento e Rotina:**
  - A pesquisadora-chefe que sintetizou o VIGÍLIA-7 e acompanhou os primeiros testes no campus.
  - É a mais desgastada fisicamente entre todos os Insones, mas a única cujo cérebro ainda emite vocalizações linguísticas: balbucia sequências numéricas, termos farmacológicos e fragmentos do termo de consentimento dos voluntários.
- **Mecânica de Jogo:**
  - Patrulha o laboratório alagado e a área de arquivos. Seus murmúrios servem como pista auditiva para a posição dela no cenário e fornecem charadas para decifrar os códigos do cofre da Reitoria.
