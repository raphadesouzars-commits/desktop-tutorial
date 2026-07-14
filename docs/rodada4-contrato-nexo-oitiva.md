# Rodada 4 — Contrato Nexo Coger → Oitiva 360 (Pauta de Instrução)

## Pré-requisito

Depende das Rodadas 1–3 concluídas: catálogo canônico em uso, bugs corrigidos, contrato Veritas → Nexo Coger já usando IDs canônicos. A pauta gerada nesta rodada deve seguir o mesmo padrão de `schema_version` + `catalogo_schema_version` adotado na Rodada 3.

## Escopo

### 4.1 — Diagnóstico inicial (Claude Code)

Antes de desenhar o contrato, verificar no `nexo-coger.html` real:
1. Se já existe alguma função de geração de pauta ou exportação de perguntas — mesmo que incompleta ou não usada atualmente.
2. Se já existe alguma estrutura de dados que represente "lacuna" no mapeamento fato-prova (ex.: fato sem prova vinculada, prova vinculada mas de força insuficiente, contradição não resolvida) — mesmo que hoje só sirva para exibição visual, sem exportação.
3. Se o `oitiva-360.html` já tem uma rotina de importação de pauta pronta para receber esse contrato, ou se essa também precisa ser criada.

Se nada disso existir, a Rodada 4 cria os dois lados do zero; se existir parcialmente, a Rodada 4 adapta o que já existe ao catálogo canônico e ao formato abaixo.

### 4.2 — Identificação de lacunas (modelo híbrido)

O Nexo Coger deve **sugerir automaticamente** pontos de lacuna a partir do mapeamento fato-prova-norma:

- Fato apurado sem nenhuma prova vinculada.
- Fato com prova vinculada, mas de tipo frágil (ex.: só indício, sem prova documental ou testemunhal direta) — critério de "força" pode ser simples nesta primeira versão (ex.: contagem de provas por fato), refinamento fica para rodadas futuras.
- Fato com duas ou mais provas vinculadas em contradição (se essa marcação já existir na estrutura de dados do Nexo Coger; caso não exista, não é criada nesta rodada só para viabilizar isso).

O sistema apresenta essas sugestões numa tela de revisão, onde o usuário:
- Confirma quais entram na pauta,
- Remove sugestões irrelevantes,
- Adiciona pontos manuais que o sistema não detectou.

Só o conjunto final confirmado pelo usuário é exportado.

### 4.3 — Organização da pauta: por depoente

Cada pauta exportada corresponde a **um depoente**. Se o mesmo fato gera perguntas para múltiplos depoentes, o fato aparece replicado (com a mesma referência de fato) em cada pauta individual correspondente — não há uma pauta "geral" nesta rodada.

Cada pauta carrega:
- Identificador único da pauta (`pauta_id`) — necessário desde já, mesmo sem uso imediato, porque a Rodada 6 (retorno da oitiva) vai referenciar esse ID para rastreabilidade.
- Identificador do depoente (nome + papel, usando ID do catálogo).
- Lista de pontos de instrução, cada um com: referência ao fato apurado, referência às normas envolvidas (IDs canônicos), e a pergunta ou tópico sugerido/confirmado.

**Estrutura de referência (a validar/ajustar contra o diagnóstico 4.1):**

```json
{
  "schema_version": "1.0.0",
  "catalogo_schema_version": "1.0.0",
  "pauta_id": "PAUTA.2026-07-11.001",
  "exportado_em": "2026-07-11T00:00:00Z",
  "origem": "nexo-coger",
  "depoente": {
    "nome": "...",
    "papel": "PAPEL.TESTEMUNHA"
  },
  "pontos_instrucao": [
    {
      "id_ponto": "...",
      "fato_referencia": "...",
      "normas_relacionadas": ["NORMA.L8112.ART132_IV"],
      "tipo_lacuna": "sem_prova | prova_fragil | contradicao | manual",
      "pergunta_sugerida": "...",
      "confirmado_pelo_usuario": true
    }
  ]
}
```

`tipo_lacuna: "manual"` identifica pontos adicionados pelo usuário sem sugestão automática do sistema — importante manter essa distinção para calibrar a qualidade da sugestão automática ao longo do uso real.

## Entregáveis da Rodada 4

1. Relato do diagnóstico 4.1 (o que já existia, o que foi criado do zero).
2. Tela de revisão de lacunas no Nexo Coger (sugestão automática + confirmação/edição manual).
3. Exportação da pauta por depoente, no formato acima, usando IDs do catálogo canônico.
4. Importação da pauta no Oitiva 360, populando a rodada de oitiva correspondente com os pontos de instrução recebidos.
5. Registro no `CHANGELOG-catalogo.md`.

## Critérios de aceite

- Uma pauta exportada do Nexo Coger é importada sem erro no Oitiva 360, com pontos de instrução visíveis e associados ao depoente correto.
- O `pauta_id` está presente e é único a cada exportação.
- Nenhum ponto de instrução entra na pauta exportada sem confirmação explícita do usuário (mesmo os sugeridos automaticamente).
- Pontos marcados como `manual` são distinguíveis dos sugeridos automaticamente na interface do Oitiva 360 (não precisa ser visível ao usuário final, mas o dado precisa estar presente para uso futuro).
