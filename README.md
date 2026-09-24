# Projeto The Game

Jogo de terror em pixel art 2.5D, feito em Godot 4.7 para a disciplina de Computação Gráfica — Unifor, Semestre 6.

> Gabriel pega no sono estudando na Biblioteca da Unifor na véspera da semana de provas e acorda mil anos depois. O campus virou ruína, e as pessoas que estavam lá ainda estão — sem nunca terem dormido.

## Documentos

| Arquivo | O que tem |
|---|---|
| [`docs/gdd.md`](docs/gdd.md) | Game Design Document (itens 1 a 4) |
| [`docs/decisoes.md`](docs/decisoes.md) | Registro das decisões de design e de história, com data |
| [`docs/equipe.md`](docs/equipe.md) | Papéis e divisão de tarefas |
| [`docs/roteiro/`](docs/roteiro/) | História, personagens, diálogos |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Regras de git e de trabalho em equipe — leia antes de começar** |
| [`CLAUDE.md`](CLAUDE.md) | Contexto do projeto para o Claude |

## Primeira vez neste repositório

### 1. Instale

- **Git:** https://git-scm.com/download/win (pode aceitar as opções padrão da instalação)
- **Godot 4.7.x** (todos na mesma versão)

### 2. Configure seu nome no git (só uma vez por computador)

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email-do-github@exemplo.com"
```

### 3. Clone o repositório

**Não clone dentro do OneDrive, Google Drive ou Dropbox.** A sincronização dessas pastas briga com o git e corrompe o repositório. Use uma pasta local, como `C:\dev`.

```bash
cd C:\dev
git clone https://github.com/DaviiMiranda/Projeto_thegame.git
cd Projeto_thegame
```

### 4. Abra no Godot

No Godot, *Importar* → selecione o arquivo `project.godot` desta pasta.

### 5. Leia o `CONTRIBUTING.md` e comece sua primeira tarefa numa branch.

## Estrutura

```
cenas/          cenas do Godot (.tscn)
scripts/        GDScript (.gd)
shaders/        shaders
assets/         sprites, tiles, audio, fontes
docs/           documentação do projeto
.claude/        agentes do Claude para este projeto
.github/        modelo de PR e dono do código
```

## Equipe

[preencher]
