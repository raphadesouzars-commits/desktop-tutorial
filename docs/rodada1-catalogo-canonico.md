# Rodada 1 — Catálogo Canônico Unificado

## Objetivo

Criar uma fonte única de verdade para três vocabulários hoje espalhados (e divergentes) entre `veritas.html`, `nexo-coger.html` e `oitiva-360.html`:

1. **Papéis de pessoa** (ex.: acusado, vítima, testemunha, pessoa em situação indefinida).
2. **Tipos de prova** (documental, testemunhal, pericial, digital etc.).
3. **Normas** — conjunto canônico de 45 dispositivos da Lei nº 8.112, de 11 de dezembro de 1990, e da Lei de Acesso à Informação (LAI), Lei nº 12.527, de 18 de novembro de 2011.

Cada item passa a ter um **ID estável**, e os três sistemas passam a referenciar por ID, nunca por string livre. Esta rodada bloqueia as Rodadas 2 a 8 — nenhum contrato JSON entre sistemas deve ser fechado antes dela.

## Onde o catálogo vive (recomendação)

Como os três HTMLs são single-file, offline, sem servidor — um `catalogo.json` externo carregado via `fetch()` esbarraria em restrição de CORS ao abrir os arquivos direto do disco (`file://`). Por isso, recomendo um modelo híbrido:

- **Fonte de verdade:** `catalogo-canonico.json`, na raiz do projeto, versionado isoladamente. É o arquivo que se edita quando o vocabulário muda.
- **Cópias embutidas:** cada HTML recebe o mesmo conteúdo colado como objeto JS (`const CATALOGO_COGER = {...}`), gerado a partir do `catalogo-canonico.json`.
- **Trava de sincronismo:** cada cópia embutida carrega um comentário de cabeçalho com `schema_version` e um hash simples (ex.: soma de caracteres ou primeiros 8 caracteres de um SHA-256) do JSON de origem. O Claude Code, ao editar qualquer um dos três HTMLs, deve conferir esse hash contra o `catalogo-canonico.json` e alertar se estiverem fora de sincronia.

Isso resolve o problema de duplicação sem quebrar a arquitetura offline-first que você já usa nos outros sistemas.

## Convenção de ID (recomendação)

IDs semânticos e namespaced por categoria, **imutáveis depois de atribuídos** (registro append-only: nunca renomear ou reaproveitar um ID, apenas marcar como `deprecated` se um item sair de uso).

```
PAPEL.<slug>            → PAPEL.VITIMA, PAPEL.ACUSADO, PAPEL.PESSOA_SITUACAO_INDEFINIDA
PROVA.<slug>             → PROVA.DOCUMENTAL, PROVA.TESTEMUNHAL, PROVA.PERICIAL, PROVA.DIGITAL
NORMA.<lei>.<dispositivo> → NORMA.L8112.ART132_IV, NORMA.LAI.ART7
```

Vantagem sobre IDs sequenciais (`PAPEL_001`): legível em diffs e em logs de importação/exportação, autoexplicativo durante debug, e reduz erro de mapeamento manual entre sistemas. O risco de colisão de slug é baixo dado o volume (dezenas de itens, não milhares).

## Fonte de dados

O `nexo-coger.html` já existente é a base de partida para papéis e tipos de prova; o conjunto de normas provavelmente também já está mapeado ali. A extração deve ser feita **lendo o arquivo real** na sessão de Claude Code (não tenho acesso a ele aqui). Ao extrair, resolver diretamente os dois problemas já identificados:

- Incluir `PAPEL.PESSOA_SITUACAO_INDEFINIDA`, hoje ausente no vocabulário de prova do Nexo Coger.
- Conferir a definição de `PAPEL.VITIMA` usada na Rodada 6 do Oitiva 360 contra a definição do Nexo Coger e unificar — esse é o bug de classificação incorreta relatado.

Onde `veritas.html` e `oitiva-360.html` usarem termos próprios sem equivalente exato no Nexo Coger, registrar como item novo no catálogo (não forçar encaixe em categoria existente).

## Estrutura do `catalogo-canonico.json`

```json
{
  "schema_version": "1.0.0",
  "atualizado_em": "2026-07-11",
  "papeis_pessoa": [
    {
      "id": "PAPEL.ACUSADO",
      "label": "Acusado",
      "descricao": "Servidor submetido a processo administrativo disciplinar.",
      "status": "ativo"
    },
    {
      "id": "PAPEL.VITIMA",
      "label": "Vítima",
      "descricao": "Pessoa lesada pela conduta apurada.",
      "status": "ativo"
    },
    {
      "id": "PAPEL.PESSOA_SITUACAO_INDEFINIDA",
      "label": "Pessoa em situação indefinida",
      "descricao": "Pessoa mencionada no processo cujo papel ainda não foi determinado.",
      "status": "ativo"
    }
  ],
  "tipos_prova": [
    {
      "id": "PROVA.TESTEMUNHAL",
      "label": "Prova testemunhal",
      "descricao": "Depoimento colhido em oitiva ou interrogatório.",
      "origem_permitida": ["oitiva-360", "veritas"],
      "status": "ativo"
    }
  ],
  "normas": [
    {
      "id": "NORMA.L8112.ART132_IV",
      "lei": "Lei nº 8.112, de 1990",
      "dispositivo": "art. 132, IV",
      "descricao": "Improbidade administrativa.",
      "status": "ativo"
    }
  ]
}
```

Campos obrigatórios em todo item: `id`, `label`, `status` (`ativo` | `deprecated`). Campo `descricao` recomendado para todos; campos adicionais (`origem_permitida`, `lei`, `dispositivo`) conforme a categoria.

## Entregáveis da Rodada 1

1. `catalogo-canonico.json` na raiz do projeto, populado a partir da extração do `nexo-coger.html` real.
2. Relatório curto (pode ser um bloco de comentário no próprio JSON ou um `CHANGELOG-catalogo.md`) listando: itens migrados de cada sistema de origem, itens novos criados, e as duas correções de bug já resolvidas nesta etapa.
3. Objeto `CATALOGO_COGER` embutido nos três HTMLs, com cabeçalho de `schema_version` + hash, **sem** ainda alterar a lógica interna de cada sistema para usar os novos IDs — essa migração de uso fica para as Rodadas 2–6, para não misturar "criar o catálogo" com "consumir o catálogo" na mesma entrega.

## Critérios de aceite

- Todo papel de pessoa, tipo de prova e norma hoje usado em qualquer um dos três sistemas tem um ID correspondente no catálogo — nenhum termo solto ficou de fora.
- Nenhum ID duplicado ou ambíguo entre categorias.
- Os três HTMLs carregam exatamente o mesmo `CATALOGO_COGER` (hash idêntico).
- `PAPEL.PESSOA_SITUACAO_INDEFINIDA` presente e `PAPEL.VITIMA` com definição única, sem divergência entre Nexo Coger e Oitiva 360.
