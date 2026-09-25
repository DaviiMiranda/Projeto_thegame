# GDD — respostas dos itens 1 a 4

> **Título do Jogo:** Projeto The Game  
> **Hierarquia:** Para decisões recentes, consulte [`decisoes.md`](decisoes.md). Para a documentação técnica aprofundada, consulte o índice mestre em [`README.md`](README.md).

> [!TIP]
> **Documentação Modular Detalhada:**
> - 🎯 **[Visão Geral e Pilares](visao_geral/conceito.md)** | **[Estilo Artístico 2.5D](visao_geral/estilo_artistico.md)**
> - ⚙️ **[Mecânicas e Core Loop](mecanicas/README.md)** | **[Furtividade](mecanicas/furtividade_e_esconderijos.md)** | **[Iluminação](mecanicas/iluminacao_e_fungos.md)** | **[Sono e Sonhos](mecanicas/sono_e_sonhos.md)**
> - 💻 **[Conceitos de Computação](computacao/README.md)** (Grafos, Coloração, BFS, A*, Markov, Shaders)
> - 📜 **[História e Lore](historia/README.md)** | **[Os Dois Finais](historia/narrativa_e_finais.md)** | **[Relíquias](historia/reliquias_e_lore.md)**
> - 👥 **[Personagens](personagens/README.md)** ([Gabriel](personagens/gabriel.md), [Rafa](personagens/rafa.md), [Insones](personagens/insones.md))
> - 🗺️ **[Fases e Progressão](fases/README.md)** (Segunda a Sexta)
> - 💬 **[Diálogos e Murmúrios](dialogos/README.md)**

*Versão com o protagonista acordando mil anos no futuro. Os lugares da Unifor são usados apenas como cenário; pessoas, pesquisa e acontecimentos são fictícios.*

---

## 1. Visão Geral

**Gênero:** terror atmosférico e sobrevivência, com exploração, investigação e furtividade. Fugir e se esconder é a regra; defender-se é a exceção.

**Plataforma(s):** PC (Windows).

**Público-alvo:** adolescentes e adultos, a partir de 14 anos. Terror de tensão, sem violência explícita. Pensado primeiro para quem conhece a Unifor: alunos e ex-alunos reconhecem cada prédio, mesmo em ruínas.

**Resumo do Conceito:** um aluno pega no sono estudando na Biblioteca da Unifor na véspera da semana de provas e acorda **mil anos depois**. O campus virou ruína tomada pela natureza, a cidade sumiu, e ele não sabe o que aconteceu. Mas não está sozinho: as pessoas que estavam no campus naquela semana ainda estão lá, transformadas em algo que já não é humano, repetindo há mil anos a rotina daquela semana de provas. Ele investiga as ruínas para descobrir o que houve, por que só ele dormiu e por que acordou agora.

O que torna o jogo diferente:
- **Estranhamento do familiar:** o jogador reconhece a catraca, o bebedouro, o quadro, a Biblioteca. O mundo em volta não reconhece mais nada disso.
- **Os perseguidores seguem a grade horária** da semana de provas, mil anos depois. Quem descobre a grade sabe onde cada um vai estar.
- **Dormir é salvar e é voltar ao passado.** Cada sono leva o protagonista, em sonho, à última semana antes de tudo — e é só lá que ele aprende a grade, as senhas e a verdade.

**Visão Artística:** pixel art em vista lateral 2.5D, com camadas de profundidade, no estilo de *Five Nights at Freddy's: Into the Pit*. O jogo retrata a Unifor mil anos no futuro como uma ruína tomada pela natureza: concreto rachado e desabado, árvores crescendo dentro das salas, areia de dunas cobrindo corredores, e objetos do cotidiano de hoje transformados em relíquias. A atmosfera é de mistério, solidão e estranhamento — um terror silencioso, mais de tensão do que de susto, em que o maior choque é perceber quanto tempo passou. Luz natural filtrada pela vegetação contrasta com interiores escuros iluminados só pelo brilho frio de fungos bioluminescentes. Nos sonhos, o mesmo campus aparece cheio, iluminado e normal.

---

## 2. Mecânicas de Jogo

### Jogabilidade Central

O jogador explora as ruínas em vista lateral, sala por sala e prédio por prédio, procurando passagens, itens e pistas, enquanto evita os **Insones** — as pessoas que nunca mais dormiram.

**Explorar.** Andar, correr (faz barulho), se espremer por frestas, atravessar tetos desabados, vasculhar o que restou, examinar objetos e marcas nas paredes.

**Iluminar.** Nada elétrico funciona depois de mil anos. A luz vem de **fungos bioluminescentes** que cresceram nas ruínas: o protagonista os recolhe em potes e usa como lanterna. Luz ajuda a ver e ajuda a ser visto, e o brilho enfraquece com o tempo.

**Ler a grade.** Cada Insone cumpre a rotina da semana de provas: o Professor vai para a sala da aula dele no horário, a Bibliotecária arruma estantes que já não têm livros, o Vigia faz a ronda. A grade horária não existe mais em papel — o jogador a aprende nos sonhos. Fora da rotina, quando ouve ou vê o protagonista, o Insone sai do roteiro e caça.

**Esconder-se.** Armários enferrujados, buracos no piso, raízes, cabines de estudo. Com um Insone por perto, o jogador passa por um **microgame** rápido e diferente em cada esconderijo: prender a respiração no tempo certo, segurar a porta, ficar imóvel.

**Distrair.** Jogar pedras e objetos, derrubar estantes, fazer ruído num lugar para atrair os Insones para longe.

**Defender-se (limitado).** Esmagar uma **cápsula de fungo** libera um clarão forte por um instante e atordoa o Insone por alguns segundos. As cápsulas são escassas — é para escapar, não para vencer.

**Dormir.** Em salas seguras e fechadas, o jogador pode dormir. Dormir **salva o jogo** e leva a um **sonho**: o mesmo lugar na última semana antes de tudo, com as pessoas ainda normais. Nos sonhos não há perigo — há conversas, quadros de horário, senhas e detalhes que servem no presente.

### Objetivos e Progressão

**Objetivo geral:** descobrir o que aconteceu, por que ele dormiu mil anos, e sair do campus.

**Estrutura em cinco dias**, um para cada dia da semana de provas que os Insones continuam repetindo. Cada dia abre uma nova área e fica mais perigoso: mais Insones ativos, rotinas mais agressivas, menos recursos.

| Dia | Área principal | O que se descobre |
|---|---|---|
| Segunda | Biblioteca | Ele dormiu muito. As pessoas ainda estão aqui — ou o que sobrou delas. |
| Terça | Blocos de aula | Os Insones seguem a grade da semana de provas. Os tracinhos contados nas paredes indicam séculos. |
| Quarta | Centro de Convivência e Espaço Cultural | Havia uma pesquisa com voluntários naquela semana. |
| Quinta | NAMI | O estimulante, os testes, a lista de voluntários — e o nome dele nela. |
| Sexta | Reitoria e portão principal | Quanto tempo passou de verdade, e o que aconteceu com o mundo lá fora. |

A progressão entre áreas é por **passagens abertas, mecanismos e senhas**, parte encontrada nas ruínas e parte aprendida nos sonhos.

### Sistema de Recompensas

- **Acesso:** novas áreas do campus e atalhos entre elas.
- **Recursos:** fungos para luz e cápsulas de clarão, sempre escassos.
- **Verdade:** cada pista, marca na parede e sonho revela uma parte do mistério. A história é a principal recompensa.
- **Colecionáveis:** relíquias do cotidiano (um crachá, um celular fossilizado, uma caneca da cantina) com a descrição de quem eram seus donos, e páginas do diário que o protagonista vai escrevendo.
- **Final:** o que o jogador descobriu muda as opções disponíveis no final.

### OBRIGATÓRIO — recursos de Computação

Os conteúdos de computação estão **dentro das mecânicas**, não só no código:

| Conteúdo | Onde aparece no jogo |
|---|---|
| **Grafos** | O campus é um grafo: cada sala é um nó, cada porta, corredor, escada ou buraco no teto é uma aresta com peso (distância e barulho). Desabamentos removem arestas; passagens abertas pelo jogador criam novas. |
| **Coloração de grafos** | A grade horária da semana de provas é gerada por coloração de grafos: aulas que dividem professor ou sala não podem ter o mesmo horário. É essa grade que define onde cada Insone está a cada hora do jogo. |
| **Busca em largura (BFS)** | O som se propaga pelo grafo e enfraquece a cada sala. Um passo correndo é ouvido a duas salas; uma estante caindo, a cinco. |
| **A\* (caminho mínimo)** | Quando um Insone ouve ou vê o jogador, sai da rotina e o persegue pelo menor caminho no grafo. |
| **Cadeia de Markov** | Fora da rotina, cada Insone escolhe a próxima sala por probabilidade, com chances que crescem a cada dia. É o modelo de movimento dos perseguidores do FNAF, formalizado. |
| **Máquina de estados** | Cada Insone alterna entre *rotina*, *desconfiado*, *caçando*, *atordoado* e *voltando à rotina*. |
| **Estruturas de dados** | Inventário em grade (matriz), fila de eventos da rotina de cada Insone, dicionário de flags do mundo (passagens abertas, pistas encontradas, sonhos vistos). |
| **Matemática / geometria** | Campo de visão dos Insones por produto escalar e linha de visão por *ray casting*; luz dos fungos decaindo com o tempo e com a distância. |

---

## 3. Mundo e Narrativa

### Cenário

O campus da **Unifor**, em Fortaleza, **mil anos no futuro**. Os prédios que sobraram estão rachados, sem teto ou parcialmente enterrados; árvores atravessam salas de aula; dunas avançaram sobre os caminhos entre os blocos; o mato cobre o que era estacionamento. Não há cidade em volta — só vegetação até onde a vista alcança. O que resiste são as coisas duras: concreto, metal, vidro, pedra.

E, nos sonhos, o mesmo campus **na última semana antes de tudo**: cheio, iluminado, barulhento e normal.

### História e Personagens

**O começo.** Véspera da semana de provas. Gabriel estuda até tarde numa cabine da Biblioteca e pega no sono. Acorda com luz do sol entrando por um teto que não existe mais, uma árvore no meio da sala e as estantes caídas e vazias. Não há ninguém — até ele ouvir, entre as estantes, o som de alguém arrumando livros que não estão mais lá.

**O mistério, em camadas:**

1. **Onde estão todos?** Aqui. Os Insones são as pessoas que estavam no campus naquela semana.
2. **Quanto tempo passou?** Muito mais do que parece. Os tracinhos que um Insone risca na parede há séculos, os anéis de uma árvore que cresceu dentro da Biblioteca, as dunas sobre os blocos — a resposta vem aos poucos, e o número final é mil anos.
3. **Por que ninguém dorme?** Na semana de provas, um projeto de pesquisa recrutou alunos e funcionários para testar um estimulante experimental, o **VIGÍLIA-7**, que prometia dias de foco sem sono. Funcionou além do previsto: quem tomou nunca mais conseguiu desligar o corpo — nem para dormir, nem para morrer. Mil anos acordados reduziram essas pessoas ao último fio de rotina que tinham.
4. **Por que ele dormiu?** Gabriel também estava na lista de voluntários. Nele, o efeito foi o inverso: o corpo desligou e não religou. Os Insones ficaram presos acordados; ele ficou preso dormindo. É a mesma suspensão, dos dois lados. O jogador descobre isso no NAMI, vendo o próprio nome.
5. **O que aconteceu com o mundo?** O teste foi considerado um sucesso antes de os efeitos aparecerem, e o VIGÍLIA-7 saiu do campus. A Unifor não foi o único lugar abandonado — foi o primeiro.

**O final.** No último dia, Gabriel chega ao portão principal. Tudo que aprendeu nos sonhos aponta para uma coisa: o que falta aos Insones é exatamente o que só ele teve — dormir.

- **Sair sozinho:** atravessar o portão para um mundo vazio e ver o que mais sobrou.
- **Fazer o campus dormir:** com o que descobriu no NAMI, devolver o sono aos Insones, deixando que finalmente descansem — sabendo que talvez ele mesmo não acorde de novo.

As opções disponíveis dependem do que o jogador descobriu ao longo do jogo.

**Personagens:**

- **Gabriel** *(provisório)* — o protagonista. Aluno comum, cansado, que só queria passar nas provas. Não é herói nem investigador; é alguém tentando entender como a sua última lembrança é de ontem e o mundo tem mil anos a mais.
- **Rafa** *(provisório)* — o colega que estudava com ele na Biblioteca naquela noite e também tomou a dose. É o Insone que aparece em todos os dias e o coração emocional do jogo: nos sonhos, é o melhor amigo; no presente, é o que mais o caça. E às vezes parece reconhecê-lo.
- **A Bibliotecária** — arruma há mil anos estantes vazias. Ouve tudo. Barulho na Biblioteca atrai ela na hora.
- **O Professor** — dá aula para salas sem teto, trocando de sala conforme a grade. Aluno fora de sala no horário de aula é aluno que precisa ser levado de volta.
- **O Vigia** — faz a ronda noturna. É quem risca os dias nas paredes, e o mais atento à luz.
- **Os Calouros** — um grupo que anda junto, lento e numeroso. As cápsulas de clarão dão conta deles.
- **A Pesquisadora** — responsável pelo projeto VIGÍLIA-7, a Insone mais antiga e degradada do campus, no fundo do NAMI. É a única que ainda murmura palavras soltas, e o que ela diz só faz sentido depois dos sonhos.

### Elementos de Lore

- **O VIGÍLIA-7:** gravado em frascos de vidro, placas de metal e no cofre do NAMI — o que resistiu ao tempo. O slogan do recrutamento sobrevive pintado numa parede: *"Durma menos. Renda mais."*
- **Os tracinhos:** paredes inteiras cobertas de riscos contando dias, feitos por um Insone ao longo de séculos. É a primeira pista de quanto tempo passou.
- **A árvore da Biblioteca:** cresceu no lugar onde ficava a cabine vizinha à de Gabriel. Os anéis do tronco caído são uma das formas de estimar os anos.
- **A cápsula do tempo:** enterrada no campus anos antes do incidente, lacrada, com mensagens de alunos para o futuro. É um dos poucos lugares onde papel sobreviveu, e onde Gabriel encontra algo escrito por alguém que ele conhecia.
- **As relíquias:** objetos do cotidiano de hoje vistos como artefatos, cada um com a história de quem o usava.
- **Os sonhos:** a única memória viva do campus; tudo que ele sabe da última semana vem deles.

---

## 4. Níveis e Ambientes

> O detalhamento de cada fase (salas, puzzles, sonhos) fica em [`fases.md`](fases.md).

### Estrutura dos Níveis

Um campus contínuo, dividido em **cinco áreas** ligadas entre si, uma aberta a cada dia. As áreas visitadas continuam acessíveis — voltar faz parte do jogo, e cada volta encontra os Insones num horário diferente da grade.

As áreas externas entre prédios são as mais expostas: abertas, com dunas e mato alto, poucos esconderijos, e a rota do Vigia. Em vários pontos, o caminho entre dois prédios não é mais pelo chão: é por um teto desabado, uma árvore caída ou um andar enterrado.

### Design dos Ambientes

| Área | Visual | Função |
|---|---|---|
| **Biblioteca** | Estantes caídas e vazias, uma árvore no meio do salão, luz do sol por um teto aberto, poeira e pólen no ar | Tutorial e primeiro contato. Silêncio é regra: correr aqui chama a Bibliotecária. |
| **Blocos de aula** | Corredores parcialmente enterrados em areia, salas sem teto, quadros ainda presos às paredes, paredes cobertas de tracinhos | Onde a grade mais importa: o Professor muda de sala a cada horário. |
| **Centro de Convivência** | Estrutura aberta tomada pelo mato, balcões e mesas cobertos de raízes, o céu aparecendo pela cobertura | Área ampla, poucos esconderijos, os Calouros andam em grupo. |
| **Espaço Cultural** | Galeria escura e fechada, obras irreconhecíveis, fungos brilhando nas paredes | Puzzles visuais e as primeiras peças do projeto VIGÍLIA-7. |
| **NAMI** | Corredores de azulejo rachado, macas de metal, o andar de baixo alagado, a luz fria dos fungos como única iluminação | O ponto alto da tensão e das revelações. |
| **Reitoria e portão** | O prédio mais conservado, com o cofre e os arquivos; do lado de fora do portão, só vegetação | O final. |

### Desafios e Obstáculos

- **Os Insones**, cada um com rotina, sentido dominante (audição, visão, luz) e área própria.
- **Barulho:** correr, pisar em entulho e derrubar coisas se ouve pelo grafo.
- **Escuridão:** os fungos ajudam a ver e ajudam a ser visto; o brilho enfraquece.
- **Recursos escassos:** fungos para luz e cápsulas de clarão nunca sobram.
- **O próprio lugar:** pisos que cedem, passagens enterradas, andares alagados, caminhos que só existem por cima.
- **O tempo da grade:** a mesma sala é segura num horário e perigosa no seguinte, e o jogador só conhece a grade pelo que viu nos sonhos.
