# CLAUDE.md — contexto do Projeto The Game

Este arquivo dá contexto a qualquer sessão do Claude que trabalhe neste repositório. Leia antes de mexer em qualquer coisa.

## O projeto

**Projeto The Game** é o jogo do trabalho de Computação Gráfica (Semestre 6) de um grupo de 4 alunos da Unifor.

- **Premissa:** Gabriel, um aluno, pega no sono estudando na Biblioteca da Unifor na véspera da semana de provas e acorda **mil anos depois**. O campus virou ruína tomada pela natureza. As pessoas que estavam lá naquela semana ainda estão — transformadas nos **Insones**, que repetem há mil anos a rotina da semana de provas. Gabriel investiga para descobrir o que aconteceu.
- **Estilo:** pixel art em vista lateral 2.5D, inspirado em *Five Nights at Freddy's: Into the Pit*. Terror atmosférico, fuga e esconderijo, defesa limitada.
- **O roteiro e parte das mecânicas ainda estão sendo definidos** ao longo do projeto. A fonte da verdade é `docs/gdd.md` + `docs/decisoes.md`. Se algo aqui contradizer `docs/decisoes.md`, vale o registro de decisões (é o mais recente).

**Requisito obrigatório da disciplina:** o jogo precisa usar conteúdos de computação — grafos, estruturas de dados avançadas, matemática. Planejado: campus como grafo, BFS para propagação de som, A\* para perseguição, cadeia de Markov no movimento dos Insones, coloração de grafos na grade horária, máquina de estados, campo de visão por produto escalar. Detalhes em `docs/gdd.md`, item 2.4.

## Stack

- **Godot 4.7.x**, **GDScript**, 2D.
- Resolução base 320×180, escala inteira, filtro de textura *Nearest* (pixel art).
- Sem assets pagos. Placeholders gerados no próprio Godot até a arte ficar pronta.

## Estrutura

```
cenas/          cenas do Godot (.tscn) — uma cena por sistema/sala/personagem
scripts/        GDScript (.gd)
shaders/        shaders (.gdshader)
assets/         sprites, tiles, audio, fontes
docs/           gdd.md, equipe.md, decisoes.md
docs/roteiro/   história, personagens, diálogos
.claude/agents/ agentes especializados deste projeto
```

## Convenções

- Arquivos, pastas, variáveis e funções em `snake_case`; `class_name` em `PascalCase`. Nomes em português, sem acento em nome de arquivo.
- Código comentado em português, simples e didático: o grupo está aprendendo.
- Cada sistema, personagem e sala é uma **cena separada**. Não coloque vários sistemas numa cena só.
- Comunicação entre sistemas por **sinais** do Godot (ex.: `jogador_detectado`, `jogador_perdido`), não por referências diretas entre cenas de pessoas diferentes.
- Commite os arquivos `.import` e `.uid`. Nunca commite `.godot/`.

## Regras de git para o Claude

As regras completas estão em `CONTRIBUTING.md`. O essencial:

- **Nunca faça commit nem push na `main`.** Sempre trabalhe numa branch `tipo/descricao-curta`.
- **Nunca use `git push --force`.**
- Commits pequenos, mensagem no formato `tipo: o que mudou`, em português.
- Ao terminar uma tarefa, **prepare o PR** (título e descrição no modelo de `.github/pull_request_template.md`), mas quem abre e quem aprova são as pessoas. O revisor principal é o Davi.
- Não edite cenas (`.tscn`) ou arquivos de arte de outra pessoa sem que o usuário confirme que pode.

## Como ajudar este grupo

- O grupo nunca trabalhou com git em equipe. Quando um comando git for necessário, **explique o que ele faz** antes de sugerir.
- Prefira **o menor passo que funciona**. Escopo de trabalho de faculdade: uma sala perfeita vale mais que cinco pela metade.
- Mecânicas e história ainda mudam. Antes de implementar algo grande baseado no GDD, confira `docs/decisoes.md`.
- Se uma mudança de design ou de história for decidida numa conversa, sugira registrá-la em `docs/decisoes.md`.

## Agentes do projeto

Em `.claude/agents/`:

| Agente | Use para |
|---|---|
| `revisor` | revisar uma branch ou PR antes de pedir revisão humana: regras do `CONTRIBUTING.md`, bugs, cenas misturadas, arquivos que não deviam estar no commit |
| `roteirista` | escrever e revisar história, diálogos e textos, checando consistência com o que já foi decidido |
| `sistemas` | grafos, IA dos Insones, algoritmos — e explicar a matemática para a apresentação da disciplina |
| `artista` | guia de estilo, shaders, iluminação 2D, placeholders e listas de assets por sala; conferir se a arte conta o que o roteiro pede |
