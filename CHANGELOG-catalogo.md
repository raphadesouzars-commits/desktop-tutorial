# Changelog — Catálogo Canônico

`catalogo-canonico.json` — `schema_version: 1.0.0`, `atualizado_em: 2026-07-11`, hash8 (SHA-256, 8 primeiros caracteres): `5906e98f`.

## Rodada 3 — Contrato Veritas → Nexo Coger (fechada)

### 3.1 — Padronização do nome `nexo-coger`

Ocorrências de `nexus-coger` encontradas e corrigidas, todas em `nexo-coger.html` (nenhuma em `veritas.html`):
- `LS_KEY_LEGADO='nexus-coger:draft'` e `FERRAMENTA_LEGADO='nexus-coger'` — removidos por inteiro. A spec desta rodada autoriza explicitamente redesenhar sem camada de retrocompatibilidade ("não há arquivos em produção a preservar"), então a checagem de leitura/importação (`loadDraft()`, handler de `#fileInput`) passou a aceitar só `FERRAMENTA==='nexo-coger'`.
- Nome de arquivo de download em `exportJson()`: prefixo `nexus-` (não continha `-coger`, mas era a mesma raiz do nome legado) trocado para `nexo-coger-`, alinhando com a decisão "nome de arquivo sugerido no download" da spec.
- Confirmado por busca (case-insensitive) zero ocorrências remanescentes de `nexus-coger`/`nexuscoger`/`NEXUS_COGER` em ambos os arquivos.

### 3.2 — Estruturas originais encontradas (antes do redesenho)

**Exportação do Veritas (diagnóstico):** não existia nenhuma função de exportação dedicada ao Nexo Coger. `App.exportarDossie()` (a única exportação existente) baixa o `DB.dossie` inteiro — processo, comissão, todos os itens com todos os campos internos — no próprio formato de rascunho do Veritas (`versaoEsquema`, `hashDoDossie`). Não há conceito de "provas" isoladas nem de contrato com outro sistema.

**Importação no Nexo Coger (diagnóstico):** também não existia importação específica do Veritas. O único elo entre os dois sistemas era o campo `hashVeritas` no formulário de prova (`abrirFormProva`), texto livre preenchido manualmente pelo usuário, explicitamente documentado no próprio rótulo como "sem integração automática". O import existente de arquivo (`#fileInput`) só aceita o formato interno do próprio Nexo Coger (`d.ferramenta==='nexo-coger'`); e a "Importação de prova de retorno" (`importarProva`/`#fileInputProva`, Rodada 4) é um contrato à parte, do Oitiva 360, com `tipo` em slug interno do Nexo (`documental`, `testemunhal` etc.) e `fatoIds` — não tem relação com o Veritas.

Conclusão do diagnóstico: a Rodada 3 não estava ajustando um contrato desalinhado — estava criando o contrato Veritas → Nexo do zero, como a própria spec previa como possibilidade.

### Contrato redesenhado e implementado

Novo formato de exportação (`veritas.html`, `App.exportarProvasParaNexo()`, botão "Exportar provas → Nexo Coger"):
```json
{
  "schema_version": "1.0",
  "catalogo_schema_version": "1.0.0",
  "exportado_em": "2026-07-11T22:18:21.354Z",
  "origem": "veritas",
  "origem_instancia": "<processo.id do dossiê Veritas>",
  "provas": [{
    "id_prova": "...", "titulo": "...", "tipo_prova": "PROVA.PRINT_SISTEMA",
    "descricao": "...", "sigilo": "...", "status": "...",
    "proveniencia": { /* exatamente os mesmos campos já existentes no item do Veritas */ },
    "arquivos": [{ "nomeArquivo": "...", "descricao": "...", "hashLocal": "...", "hashDeclarado": "..." }],
    "cadeia_custodia": [ /* linhaDoTempoItem do Veritas, sem alteração de formato */ ]
  }]
}
```
- `tipo_prova` resolvido via novo mapa fixo `CATEGORIA_VERITAS_PARA_PROVA_ID` (uma entrada por chave de `CATEGORIAS`) — nunca texto livre.
- Campos de cadeia de custódia (`proveniencia`, `arquivos`, `cadeia_custodia`) preservados tal como já existiam no Veritas, conforme escopo da rodada.
- Nome de arquivo de download: `nexo-coger-provas-<numero-do-processo>.json`.

Nova importação (`nexo-coger.html`, `importarProvasVeritas()`, botão "Importar provas do Veritas", modal de revisão — nada é importado silenciosamente, mesmo padrão já usado na importação de retorno do Oitiva):
- `tipo_prova` (id do catálogo) resolvido para rótulo em português via `CATALOGO_COGER.tipos_prova` — a tela mostra "Print de sistema", nunca `PROVA.PRINT_SISTEMA` cru.
- `tipo_prova` também mapeado para um dos 8 `TIPOS_PROVA_VALIDOS` internos do Nexo via novo `PROVA_ID_PARA_TIPO_NEXO` (as 9 subcategorias exclusivas do Veritas caem em `documental`, a mais próxima; os 8 tipos nativos mapeiam 1:1); o rótulo de origem mais específico fica preservado em `p.origemVeritas.tipoProvaOrigemLabel` e aparece como badge 🌐 no card da prova no mapa.
- `catalogo_schema_version` do arquivo comparado com `CATALOGO_COGER.schema_version` do Nexo: se diferente, um banner de aviso visível (não bloqueante, mas impossível de não ver) é exibido no topo do modal de revisão antes de qualquer importação — nunca falha silenciosa.
- Proveniência e cadeia de custódia completas do Veritas ficam guardadas em `p.origemVeritas` para rastreabilidade, sem alterar o restante da lógica interna do Nexo Coger.

### Teste de ponta a ponta (Playwright, os dois HTMLs reais no navegador)

1. Item criado no Veritas (categoria `print_sistema`) → exportado → arquivo real gerado com `tipo_prova: "PROVA.PRINT_SISTEMA"`, `catalogo_schema_version: "1.0.0"`, proveniência e 1 evento de cadeia de custódia preservados.
2. Arquivo importado no Nexo Coger → modal mostra "Print de sistema" (não o id cru) → após confirmar, `doc.provas` recebe a prova com `tipo: "documental"` e `origemVeritas.tipoProvaOrigemLabel === "Print de sistema"`.
3. Mesmo arquivo com `catalogo_schema_version` alterada para `"0.9.0"` → modal exibe aviso visível: *"Este arquivo foi exportado com catalogo_schema_version 0.9.0, diferente da versão do catálogo em uso neste Nexo Coger (1.0.0)."*

Os três critérios de aceite da Rodada 3 foram confirmados nesse teste real (não apenas leitura de código).

## Rodada 2 — Correção dos bugs conhecidos (fechada)

Os dois bugs registrados na Rodada 1 foram diagnosticados e corrigidos, consumindo o catálogo canônico por ID nos dois pontos afetados.

### Bug 1 — Classificação incorreta do papel de vítima (Oitiva 360, Rodada 6)

**Diagnóstico:** três camadas foram inspecionadas. A entrada (radio de papel, Etapa 1) e a saída de termo (`gerarTermoTexto()`) já liam `compromisso` dinamicamente de `CATALOGO.papeis` e estavam corretas. A falha estava isolada na lógica de sugestão de exportação de prova para o Nexo — `tipoSugeridoParaItem()` (Rodada 6, seção 6.3), chamada só em `abrirDialogoExportarProva()` (nenhuma outra rodada reutiliza essa função, então o bug não se repetia em outro lugar): retornava `{ tipo: "testemunhal", compromissada: true }` para o papel `vitima`, hardcoded, contradizendo `PAPEL.VITIMA.compromisso === false` já fixado no catálogo canônico desde a Rodada 1.

**Correção:** `oitiva-360.html` — `tipoSugeridoParaItem()` agora resolve o slug interno (`d.papel`) para o ID do catálogo via novo mapa `PAPEL_SLUG_PARA_ID_CATALOGO` e lê `compromisso` de `CATALOGO_COGER.papeis_pessoa` em vez de um booleano fixo. Teste manual (Node, fora do DOM): `tipoSugeridoParaItem({papel:'vitima'})` agora retorna `compromissada:false`; os demais papéis (`acusado`, `declarante_informante`, `testemunha`, `situacao_indefinida`) mantiveram o comportamento anterior — sem regressão.

### Bug 2 — Ausência de "pessoa em situação indefinida" no vocabulário de prova do Nexo Coger

**Diagnóstico:** o Nexo Coger não tem, em lugar nenhum do arquivo, um conceito genérico de "papel de pessoa" — a única entidade de pessoa é `doc.acusados[]`. O único ponto onde um depoente é referenciado ao vincular prova a um fato é o formulário de detalhe de prova testemunhal/declaração de informante (`abrirFormProva()`), que capturava o depoente apenas como nome livre + um booleano `compromissada`, sem nenhum campo de papel — por isso `PAPEL.PESSOA_SITUACAO_INDEFINIDA` (e qualquer outro papel) não podia aparecer em lugar nenhum: não faltava uma opção em uma lista, faltava a lista em si. Não existem "seletor de papel ao vincular fato-prova" separado, "filtros do mapa fático-probatório" por papel, nem tela de exportação/relatório listando papéis — o mapa SVG e a matriz de força probatória do Nexo não segmentam por papel de pessoa.

**Correção:** `nexo-coger.html` — o formulário de detalhe de prova testemunhal/declaração de informante ganhou o campo "Papel do depoente" (`d.papelId`), populado dinamicamente a partir de `CATALOGO_COGER.papeis_pessoa.filter(status==='ativo')` (não hardcoded), com "Compromissada?" pré-preenchido a partir do `compromisso` do papel escolhido (ainda editável pela comissão, no mesmo padrão de outros campos "sugestão, nunca aplicação automática" do sistema). Teste (Node, fora do DOM): a lista de opções gerada contém os 5 papéis do catálogo, incluindo `PAPEL.PESSOA_SITUACAO_INDEFINIDA` — confirmado programaticamente. Como esse era o único ponto do arquivo relacionado a papel de pessoa, a correção cobre a totalidade dos "seletores/formulários de papel" do critério de aceite (conjunto de um único ponto).

**Nota:** o critério de aceite geral pedia ausência de string livre "vítima"/"pessoa em situação indefinida" nos dois pontos corrigidos — confirmado: ambos os pontos agora referenciam apenas os IDs `PAPEL.VITIMA`/`PAPEL.PESSOA_SITUACAO_INDEFINIDA` do catálogo, nunca a string solta.

## Rodada 1 — Itens migrados por sistema de origem

### Nexo Coger (base de partida)
- **Papéis de pessoa:** apenas `PAPEL.ACUSADO` existia (array `doc.acusados[]`). O Nexo Coger não tinha vocabulário próprio de vítima, testemunha, declarante/informante ou pessoa em situação indefinida.
- **Tipos de prova:** `PROVA.DOCUMENTAL`, `PROVA.PERICIAL`, `PROVA.TESTEMUNHAL`, `PROVA.DECLARACAO_INFORMANTE`, `PROVA.INTERROGATORIO`, `PROVA.DILIGENCIA`, `PROVA.EMPRESTADA`, `PROVA.INDICIARIA` — migrados de `TIPOS_PROVA_VALIDOS`.
- **Normas:** todas as 52 entradas de `NORMAS_BASE` migradas — 45 dispositivos da Lei nº 8.112/1990 (arts. 116, 117, 130 §1º e 132) e 7 do art. 32 da Lei nº 12.527/2011 (LAI).

### Oitiva 360
- **Papéis de pessoa:** `PAPEL.VITIMA`, `PAPEL.TESTEMUNHA`, `PAPEL.DECLARANTE_INFORMANTE` e `PAPEL.PESSOA_SITUACAO_INDEFINIDA` migrados de `CATALOGO.papeis`, com descrições literais preservadas. A definição de `PAPEL.ACUSADO` do catálogo canônico usa o texto mais completo do Oitiva 360 (direito ao silêncio, Lei 13.869/2019, Súmula Vinculante nº 5/STF, art. 159), unificando com o `PAPEL.ACUSADO` mínimo do Nexo Coger.

### Veritas Digital
- **Tipos de prova:** nenhum papel de pessoa (Veritas não lida com depoentes, só com cadeia de custódia de evidência). As categorias de evidência digital/física (`CATEGORIAS`) foram registradas como novos itens de `tipos_prova`, pois são subcategorias mais finas que não colidem 1:1 com o vocabulário do Nexo: `PROVA.PRINT_SISTEMA`, `PROVA.DOCUMENTO_FINANCEIRO`, `PROVA.COMUNICACAO`, `PROVA.FOTO_VIDEO`, `PROVA.OFICIO`, `PROVA.DECISAO_JUDICIAL`, `PROVA.DOCUMENTO_FISICO`, `PROVA.DISPOSITIVO_FISICO`, `PROVA.OUTRO`. A categoria `laudo_pericia` do Veritas foi tratada como equivalente a `PROVA.PERICIAL` (já existente), sem duplicação.
- Vocabulário interno de rastreabilidade forense do Veritas (`PROVENIENCIA_TIPOS`, `ELEMENTO_FISICO_TIPOS`, `CONDICAO_LACRE`, `SIGILO`, `STATUS_ITEM`, `RESULTADO`, `EVENTO_TIPOS`) **não** entrou no catálogo — não é papel de pessoa, tipo de prova ou norma; é metadado de cadeia de custódia, fora do escopo desta rodada.
- Normas: Veritas cita apenas art. 158-A a 158-F do CPP (Lei nº 13.964/2019), por analogia, e explicitamente declara não vincular-se ao CPP. Não há referência real a Lei 8.112/1990 ou LAI no arquivo — nenhuma norma nova migrada dessa fonte.

## Itens novos criados (sem equivalente exato em nenhuma fonte)

- Nenhum item foi criado do zero fora do que já existia em algum dos três sistemas. Todos os itens "novos" no catálogo (papéis do Oitiva, categorias de prova do Veritas) já existiam em pelo menos uma das três ferramentas — a novidade é que passam a ter ID estável compartilhado, o que antes não existia.

## Correções de bug resolvidas nesta rodada

1. **`PAPEL.PESSOA_SITUACAO_INDEFINIDA` ausente no vocabulário do Nexo Coger** — o Nexo não tinha nenhum papel equivalente a "pessoa em situação indefinida" (confirmado por busca exaustiva, zero ocorrências). O catálogo agora inclui `PAPEL.PESSOA_SITUACAO_INDEFINIDA`, usando a definição do Oitiva 360 como fonte única (não havia versão do Nexo para conciliar).
2. **Divergência/bug na classificação de `PAPEL.VITIMA`** — o Nexo Coger não tinha nenhum conceito de vítima (zero ocorrências de "vítima" no arquivo); o Oitiva 360 define `vitima` com `compromisso: false`, mas a função `tipoSugeridoParaItem()` (usada ao exportar prova de retorno para o Nexo) marcava incorretamente `{ tipo: "testemunhal", compromissada: true }` para o papel `vitima`, contradizendo a própria definição do papel no mesmo arquivo. O catálogo agora fixa `PAPEL.VITIMA` com `compromisso: false` como definição única e documenta a nota do bug. **A correção da lógica interna (`tipoSugeridoParaItem()` no Oitiva 360 e o reconhecimento do papel vítima no Nexo) fica para as Rodadas 2–6**, conforme escopo desta entrega (criar o catálogo, não ainda consumi-lo).

## Observação sobre a meta de "45 dispositivos"

A especificação da Rodada 1 menciona um "conjunto canônico de 45 dispositivos da Lei nº 8.112 e da LAI". A extração real do Nexo Coger mostra que **os 45 dispositivos correspondem exatamente à Lei nº 8.112/1990 isolada** (12 do art. 116 + 19 do art. 117 + 1 do art. 130 §1º + 13 do art. 132 = 45); a LAI contribui mais 7 dispositivos próprios (art. 32, I a VII), totalizando **52 normas** no catálogo. Nenhum dispositivo foi omitido — os 52 refletem o universo completo já mapeado no Nexo Coger.

## Critérios de aceite — status

- [x] Todo papel de pessoa, tipo de prova e norma hoje usado em qualquer um dos três sistemas tem um ID correspondente no catálogo.
- [x] Nenhum ID duplicado ou ambíguo entre categorias (validado programaticamente — 74 IDs, 74 únicos).
- [x] Os três HTMLs carregam exatamente o mesmo `CATALOGO_COGER` (mesmo hash8 `5906e98f`).
- [x] `PAPEL.PESSOA_SITUACAO_INDEFINIDA` presente e `PAPEL.VITIMA` com definição única, sem divergência entre Nexo Coger e Oitiva 360.
