# Regras de trabalho do time

Este arquivo é o combinado do grupo. Se alguma regra atrapalhar, a gente muda — mas muda aqui, por PR, e não cada um do seu jeito.

---

## A regra de ouro

**Ninguém envia nada direto para a `main`.** Toda mudança passa por uma branch, vira um Pull Request (PR) e só entra na `main` depois de revisada.

A `main` é sempre a versão que funciona. Se o jogo abre e roda na `main`, qualquer um pode puxar e trabalhar em cima dela sem medo.

---

## O fluxo de cada tarefa

Sempre o mesmo ciclo, do começo ao fim:

```bash
# 1. Atualize a main antes de começar
git checkout main
git pull

# 2. Crie uma branch para a tarefa
git checkout -b feat/movimento-gabriel

# 3. Trabalhe, e salve o progresso em commits pequenos
git add .
git commit -m "feat: movimento lateral do Gabriel"

# 4. Envie a branch para o GitHub
git push -u origin feat/movimento-gabriel

# 5. No site do GitHub, abra um Pull Request para a main
# 6. Espere a revisão. Se pedirem ajustes, faça na mesma branch e dê push de novo
# 7. Depois de aprovado, o PR é mesclado ("Squash and merge") e a branch é apagada
```

Uma branch = uma tarefa. Terminou a tarefa, a branch morre. A próxima tarefa começa de novo no passo 1.

---

## Nomes de branch

Formato: `tipo/descricao-curta`, tudo minúsculo, com hífen, sem acento.

| Tipo | Quando usar | Exemplo |
|---|---|---|
| `feat/` | mecânica ou sistema novo | `feat/esconderijo-armario` |
| `fix/` | correção de bug | `fix/gabriel-atravessa-parede` |
| `arte/` | sprites, tiles, animações | `arte/tiles-biblioteca` |
| `fase/` | montagem de sala ou área | `fase/biblioteca-andar-1` |
| `roteiro/` | história, diálogos, textos do jogo | `roteiro/sonho-segunda` |
| `docs/` | documentação, GDD, estas regras | `docs/atualiza-gdd-item-5` |

---

## Mensagens de commit

Formato: `tipo: o que mudou`, em português, no presente.

```
feat: Insone persegue o jogador pelo grafo
fix: microgame do armário não fechava
arte: animação de corrida do Gabriel
roteiro: diálogo da Bibliotecária no sonho
docs: adiciona item 5 do GDD
```

**Faça commits pequenos.** "Mudei tudo" é impossível de revisar. Um commit por coisa que faz sentido sozinha.

---

## Pull Requests

- **Um PR por tarefa**, pequeno. Um PR que mexe em 3 arquivos é revisado em 10 minutos; um que mexe em 40 fica parado uma semana.
- **Preencha o modelo** que aparece ao abrir o PR: o que mudou, como testar, print ou vídeo se for visual.
- **Teste antes de abrir.** O jogo precisa abrir e rodar na sua branch.
- **Mantenha a branch atualizada.** Se a `main` andou enquanto você trabalhava:

```bash
git checkout main
git pull
git checkout sua-branch
git merge main
```

### Revisão

- O **Davi é o revisor principal** e dono do repositório: todo PR precisa da aprovação dele para entrar na `main`.
- Os PRs do próprio Davi são aprovados por **outro integrante** — o GitHub não deixa ninguém aprovar o próprio PR, e é bom que não deixe.
- Meta de tempo: **revisar em até 48 horas.** Se o revisor não conseguir, avisa no grupo.
- Revisão é sobre o código, não sobre a pessoa. Comentário bom diz o problema e sugere o caminho.
- Quem abriu o PR responde todos os comentários, mesmo que seja com "feito".

---

## Regras específicas do Godot

O Godot guarda cenas (`.tscn`) em texto, mas **mesclar duas edições da mesma cena quase sempre dá errado**. Por isso:

1. **Cada sistema é uma cena separada.** O Gabriel é uma cena, cada Insone é uma cena, cada sala é uma cena. A cena principal só junta as outras.
2. **Uma pessoa por cena de cada vez.** Vai mexer numa cena que é de outra pessoa? Avise no grupo antes.
3. **Nunca edite a mesma cena em duas branches ao mesmo tempo.**
4. **Commite os arquivos `.import` e `.uid`** que o Godot cria ao lado dos assets e scripts. Eles fazem parte do projeto.
5. **Não commite a pasta `.godot/`.** Ela é cache e já está no `.gitignore`.
6. **Todos usam a mesma versão do Godot:** 4.7.x.

### Arquivos binários (imagens, sons, `.blend`)

Git não consegue mesclar binário. Se duas pessoas editarem o mesmo PNG, uma das duas perde o trabalho.

- **Cada arquivo de arte tem um dono.** Só ele edita.
- Arquivos-fonte grandes (`.blend`, `.psd`, `.aseprite`) vão em `assets/fonte/` e só se forem necessários para o grupo.
- **Nada acima de 50 MB** no repositório.

---

## Onde ficam as coisas

| Pasta | Conteúdo |
|---|---|
| `cenas/` | cenas do Godot (`.tscn`) |
| `scripts/` | scripts GDScript (`.gd`) |
| `shaders/` | shaders (`.gdshader`) |
| `assets/sprites/` | personagens e objetos |
| `assets/tiles/` | tilesets dos cenários |
| `assets/audio/` | música e efeitos |
| `assets/fontes/` | fontes de texto |
| `docs/` | GDD, divisão de tarefas, registro de decisões |
| `docs/roteiro/` | história, personagens, diálogos |

### Nomes de arquivo

- Arquivos e pastas: `snake_case`, sem acento → `insone_bibliotecaria.tscn`, `grafo_campus.gd`
- Classes (`class_name`): `PascalCase` → `GrafoCampus`
- Variáveis e funções: `snake_case` → `velocidade_corrida`, `func calcular_caminho()`
- Pode escrever em português. Só não misture: se a função é `calcular_caminho`, a próxima não vira `get_path`.

---

## Tarefas e decisões

- **Tarefas** ficam nas *Issues* do GitHub, organizadas num quadro do *GitHub Projects* (A fazer → Fazendo → Em revisão → Feito). Toda branch deve estar ligada a uma issue.
- **Decisões de design e de história** que mudam o jogo ("o protagonista agora se chama Gabriel", "tiramos o combate") vão para `docs/decisoes.md`, com data. Como mecânicas e roteiro vão sendo definidos durante o projeto, esse registro é o que evita a mesma discussão duas vezes.

---

## Quando der problema

- **Conflito ao fazer merge:** não entre em pânico e não apague nada. Pare, avise no grupo, e resolvam juntos. Na dúvida, `git merge --abort` desfaz a tentativa.
- **Commitou na `main` sem querer (antes de dar push):** peça ajuda antes de tentar desfazer.
- **Nunca use `git push --force`** na `main`. Em qualquer branch compartilhada, também não.
