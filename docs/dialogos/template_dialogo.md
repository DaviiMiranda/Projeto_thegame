# Modelo de Diálogo (Template)

Este documento apresenta a estrutura padrão que qualquer diálogo ou fala do jogo deve seguir, seja armazenado em arquivo JSON ou em dicionários GDScript.

---

## 1. Estrutura Padrão em JSON

```json
{
  "dialogo_id": "identificador_unico_snake_case",
  "bloquear_movimento": true,
  "linhas": [
    {
      "locutor": "Nome do Personagem",
      "texto": "Texto da fala a ser exibido na caixa de diálogo.",
      "retrato_id": "nome_do_sprite_de_rosto",
      "audio_voz": "caminho_ou_id_do_bip_de_voz",
      "velocidade_texto": 0.03
    },
    {
      "locutor": "Nome do Segundo Personagem",
      "texto": "Resposta do segundo personagem.",
      "retrato_id": "retrato_segundo_personagem",
      "audio_voz": "",
      "velocidade_texto": 0.03
    }
  ],
  "escolhas": [
    {
      "texto_opcao": "Opção A",
      "proximo_dialogo_id": "id_dialogo_ramo_a"
    },
    {
      "texto_opcao": "Opção B",
      "proximo_dialogo_id": "id_dialogo_ramo_b"
    }
  ]
}
```

---

## 2. Estrutura para Falas Rápidas / Murmúrios (GDScript)

Para falas curtas emitidas por inimigos no presente ou pensamentos de Gabriel (sem bloquear a tela com caixa de diálogo completa):

```gdscript
const MURMURIOS_EXEMPLO: Array[String] = [
    "Texto do murmúrio 1...",
    "Texto do murmúrio 2...",
    "Texto do murmúrio 3..."
]
```

---

## 3. Checklist para Novos Diálogos

- [ ] O `dialogo_id` é único e segue o padrão `snake_case`?
- [ ] O locutor possui cena ou retrato correspondente?
- [ ] A duração do texto é adequada para a resolução 320×180 sem cortar na tela?
- [ ] Caso haja escolhas, todos os `proximo_dialogo_id` existem?
