# Rodada 6 — Contrato Oitiva 360 → Nexo Coger (Retorno da Prova)

## Pré-requisito

Depende das Rodadas 1–5 concluídas. A prova retornada aqui é a mesma criada no Veritas na Rodada 5 (`id_prova`), agora entrando no Nexo Coger como contexto do acusado — sem gerar indiciação automática, conforme decidido no início do planejamento.

## Escopo

### 6.1 — Vínculo com acusado(s): padrão simples, com exceção manual

Como a regra geral é um único acusado por processo, o vínculo padrão é automático: toda prova retornada de uma oitiva se associa, por padrão, ao acusado do processo em curso no Nexo Coger — sem exigir nenhuma marcação manual do usuário no caso comum.

Para o caso raro em que uma resposta da oitiva menciona ou implica outro acusado (mesmo processo com mais de um acusado, ou fato que cruza com outro processo), o Oitiva 360 permite, campo opcional por resposta, marcar um acusado adicional/alternativo. Se não marcado, assume-se o padrão (acusado do processo corrente). Isso evita adicionar trabalho manual ao fluxo comum e ainda cobre a exceção.

### 6.2 — Diagnóstico: "contexto do acusado" no Nexo Coger

Antes de implementar, verificar no `nexo-coger.html` real se já existe alguma estrutura de dados que agregue informação por acusado (ex.: um objeto por acusado no mapa fato-prova-norma, ou histórico de provas vinculadas). Se existir, a prova retornada passa a ser mais um item dessa estrutura. Se não existir, criar uma estrutura mínima: lista de provas associadas a cada acusado, cada uma com referência ao fato relacionado, sem qualquer campo que participe do cálculo/fluxo de indiciação.

### 6.3 — Rastreabilidade do retorno

Cada prova retornada carrega, além do `id_prova` do Veritas:
- `pauta_id` e `rodada_id` de origem (Rodada 4/5), para reconstruir de qual pauta e rodada de oitiva a prova veio.
- `id_ponto` do ponto de instrução original que gerou aquela resposta (Rodada 4) — permite ao Nexo Coger, futuramente, mostrar "esta lacuna foi respondida por esta prova".
- `schema_version` / `catalogo_schema_version`, no mesmo padrão das rodadas anteriores.

### 6.4 — Não geração de indiciação

A importação desta prova no Nexo Coger **não** aciona nenhuma rotina de indiciação, nem altera o status do processo. Ela apenas populariza o contexto do acusado. A indiciação continua sendo um ato explícito, separado, ao final do processo — este contrato não deve ter nenhum caminho de código que a dispare automaticamente.

### 6.5 — Apresentação visual (proposta)

A prova retornada aparece junto ao fato correspondente no mapa fato-prova-norma do Nexo Coger, com uma marca visual distinta (ex.: um selo ou ícone "origem: oitiva") para diferenciá-la de provas importadas diretamente do Veritas sem passar por oitiva. Isso mantém tudo num único lugar de trabalho (o mapa, que já é a ferramenta central do Nexo Coger) em vez de criar uma tela separada que o usuário precisaria lembrar de checar. Segue o design system COGER (cores navy/gold já usadas para diferenciação de status).

**Estrutura de referência:**

```json
{
  "schema_version": "1.0.0",
  "catalogo_schema_version": "1.0.0",
  "origem": "oitiva-360",
  "id_prova": "...",
  "pauta_id": "PAUTA.2026-07-11.001",
  "rodada_id": "...",
  "id_ponto": "...",
  "acusado_vinculo": "padrao",
  "acusado_alternativo": null,
  "fato_referencia": "...",
  "resumo_resposta": "..."
}
```

`acusado_vinculo: "padrao"` indica uso da regra automática (acusado do processo corrente); quando houver marcação manual, `acusado_vinculo: "manual"` e `acusado_alternativo` preenchido com o identificador do outro acusado.

## Nota sobre duplicidade

Esta rodada não implementa verificação completa de idempotência (isso é objeto da Rodada 7), mas a importação deve, no mínimo, recusar reimportar um `id_prova` já presente no contexto do acusado, evitando duplicação trivial no caso mais óbvio (reimportação acidental do mesmo arquivo).

## Entregáveis da Rodada 6

1. Campo opcional de vínculo com acusado alternativo no Oitiva 360, com padrão automático.
2. Estrutura de "contexto do acusado" no Nexo Coger (existente ajustada, ou criada do zero).
3. Importação da prova retornada, sem disparo de indiciação.
4. Apresentação visual da prova no mapa fato-prova-norma, com selo de origem.
5. Registro no `CHANGELOG-catalogo.md`.

## Critérios de aceite

- Uma prova retornada de oitiva sem marcação manual aparece vinculada ao acusado correto do processo, sem nenhuma ação extra do usuário.
- Uma prova marcada com acusado alternativo aparece vinculada ao acusado indicado, não ao padrão.
- Nenhuma indiciação é criada ou alterada como efeito colateral da importação.
- Reimportar o mesmo `id_prova` é recusado com mensagem clara.
- A prova retornada é visualmente distinguível de uma prova importada diretamente do Veritas.
