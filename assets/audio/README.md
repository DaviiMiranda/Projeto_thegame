# Áudio

Todo som do jogo fica aqui. **Dono:** papel 4 (Roteiro e fases, que inclui o áudio). Qualquer um pode adicionar som por PR.

## Pastas

```
audio/
├── musica/              trilhas que tocam em loop
│   ├── menu/            menu principal
│   ├── sonho/           o campus na última semana antes de tudo
│   ├── perseguicao/     quando um Insone sai da rotina e caça
│   └── final/           o final no portão
├── ambiente/            som de fundo contínuo de cada área, presente e sonho
│   ├── biblioteca/
│   ├── blocos_aula/
│   ├── centro_convivencia/
│   ├── espaco_cultural/
│   ├── nami/
│   ├── reitoria/
│   └── areas_externas/  dunas e mato entre os prédios, rota do Vigia
├── efeitos/             sons curtos, tocados uma vez
│   ├── gabriel/         passos, corrida, respiração, esconder, dormir
│   ├── insones/         sons de cada Insone
│   ├── objetos/         portas, entulho, estantes, objetos jogados, fungos, cápsula de clarão
│   └── interface/       botões do menu, inventário, avisos
└── vozes/               falas e murmúrios (ex.: a Pesquisadora)
```

## Nomes de arquivo

Formato: `onde_o_que_variacao.ext`, em `snake_case`, português, sem acento.

- Com variações, numere com dois dígitos: `gabriel_passo_areia_01.wav`, `gabriel_passo_areia_02.wav`.
- Em `ambiente/`, diga se é presente ou sonho: `biblioteca_presente.ogg`, `biblioteca_sonho.ogg`.
- Em `efeitos/insones/`, comece pelo nome do Insone: `vigia_passos_01.wav`, `bibliotecaria_livro_01.wav`.
- Em `vozes/`, comece pelo personagem: `pesquisadora_murmurio_01.ogg`.

## Formato

| Tipo | Formato | Por quê |
|---|---|---|
| Música e ambiente | `.ogg` ou `.mp3` | arquivo pequeno, bom para sons longos em loop |
| Efeitos e interface | `.wav` | toca sem atraso, bom para sons curtos |
| Vozes | `.ogg` | falas longas ficam pequenas |

- Loop de música e ambiente se liga no Godot: selecione o arquivo, aba **Import**, marque **Loop** e clique em **Reimport**.
- Commite os arquivos `.import` que o Godot cria ao lado de cada som.
- Só sons livres (CC0 ou com licença que permita uso) ou gravados pelo grupo. Anote a origem de cada som de fora em `creditos.md`, nesta pasta.
