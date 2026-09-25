# Diálogos — Arquitetura Técnica e Convenções

Este documento define o padrão técnico e de roteirização para todos os textos, conversas e interações faladas de *Projeto The Game*.

---

## 1. Princípios de Design dos Diálogos

- **Minimalismo nas Ruínas (O Presente):** Os Insones não conversam nem explicam nada. O presente é marcado pelo silêncio, passos no entulho e murmúrios desconexos de autômatos. Informação em excesso no presente quebra o suspense.
- **Riqueza e Familiaridade nos Sonhos (O Passado):** Nos sonhos, o diálogo é natural, rápido, recheado de gírias universitárias locais ("valei-me", "arretado", "matar aula", "café requentado", "virar a noite") e ansiedade com exames.
- **Diálogo com Função de Gameplay:** Toda conversa nos sonhos fornece ao menos uma informação prática utilizável no presente (um código de armário, a grade horária de um professor, a localização de uma chave ou uma pista sobre o composto).

---

## 2. Arquitetura Técnica no Godot 4.7

O sistema de diálogos é implementado de forma modular e desacoplada, utilizando sinais do Godot para não amarrar cenas de personagens à interface gráfica:

### Sinais Canônicos (`GerenciadorDialogo`)
```gdscript
signal dialogo_iniciado(id_conversa: String)
signal fala_exibida(locutor: String, texto: String, retrato: Texture2D)
signal escolhas_exibidas(opcoes: Array[String])
signal escolha_selecionada(indice: int)
signal dialogo_concluido(id_conversa: String)
```

### Formato de Dados dos Diálogos (JSON / Dicionário GDScript)
Os diálogos são armazenados em arquivos estruturados em `dialogos/` ou recursos GDScript:

```json
{
  "conversa_id": "sonho_segunda_cabine",
  "linhas": [
    {
      "locutor": "Rafa",
      "texto": "Gabriel, acorda cara... Se o fiscal passar e ver você roncando em cima do resumo de Cálculo, já era.",
      "retrato": "rafa_sonho_sorrindo",
      "velocidade_texto": 0.03
    },
    {
      "locutor": "Gabriel",
      "texto": "Que horas são...? Minha cabeça tá parecendo um bloco de cimento.",
      "retrato": "gabriel_cansado",
      "velocidade_texto": 0.03
    },
    {
      "locutor": "Rafa",
      "texto": "Passou das duas da manhã. Toma um gole desse troço que peguei no NAMI. Chama VIGÍLIA-7. O sono zera na hora.",
      "retrato": "rafa_sonho_oferecendo",
      "velocidade_texto": 0.03
    }
  ]
}
```

---

## 3. Módulos de Roteiro de Diálogos

- **[`sonhos.md`](sonhos.md):** Diálogos completos de cada noite de sonho (Segunda a Sexta).
- **[`murmurios.md`](murmurios.md):** Murmúrios audíveis, ecos e frases em loop dos Insones no presente.
