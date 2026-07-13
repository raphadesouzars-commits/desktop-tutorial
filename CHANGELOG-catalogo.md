# Changelog — Catálogo Canônico

`catalogo-canonico.json` — `schema_version: 1.2.0` (inalterada; estendida na Rodada PAR-1, era `1.1.0`), `atualizado_em: 2026-07-12`, hash8 (SHA-256, 8 primeiros caracteres): `0955151a` (era `958dfd97`).

## Rodada 12 — COGER Print Standard no Oitiva 360 (Termo de Oitiva)

Implementação do **COGER Print Standard** em `ferramentas/oitiva-360.html` — renderização do termo de oitiva (redução de depoimento) com cabeçalho fixo, rodapé, 3 seções numeradas com barra lateral gold (Identificação, Perguntas e Respostas, Encerramento), formatação Q&A (pergunta em negrito, resposta normal), e referência única (INT-YYYYMMDD-XXXX). **Nenhuma alteração no catálogo canônico** — impressão isolada em `@media print`, UI interativa preservada. **Mais simples que Rodada 11** — estrutura linear Q&A, sem tabelas complexas.

### Diagnóstico D1–D4 (Oitiva 360)

1. **D1 — Função de impressão:** existe `montarAreaImpressaoTermo(d)` (linha 7389) que constrói HTML e preenche `#area-impressao`; chamada pelo handler de `btn-imprimir-termo` seguida por `prepararAreaImpressaoParaImpressao()` e `window.print()`.
2. **D2 — Estrutura HTML atual:** termo renderizado em estrutura simples (header + refs + impresso-termo como pré-formatado + rodapé); será refatorado para `#printPage` com 3 seções estruturadas (header fixo, main, footer fixo).
3. **D3 — CSS @media print:** sim, ~200 linhas com estilos `#area-impressao` (básico); será estendido com Print Standard completo (header/footer fixos, seções gold, Q&A items com page-break).
4. **D4 — Metadados:** acessíveis via `d` (depoent object) com campos `d.papel`, `d.identificacao`, `d.ato.numero`, `d.ato.data`, `d.ato.hora`, `d.termoTexto` (texto completo gerado por `gerarTermoTexto()`).

### Implementação 12.1–12.7

**12.1 CSS Print Standard:** integração das variáveis de tema (26 variáveis: navy/gold/cinza/fontes/dimensões) + @media print bloco completo (320+ linhas, copy de Rodada 11) com header/footer fixos, seções gold, tabelas thead replicado, infobox, blocos legais, **novo: seções Q&A** (`.coger-print-qa-item` com `page-break-inside: avoid`, `.coger-print-qa-question`/`response` formatação).

**12.2 JavaScript utility module:** integração de `window.CogerPrint` IIFE (5 funções puras idênticas a Rodadas 10–11) — `generatePrintReference()`, `formatDatePtBr()`, `formatTimePtBr()`, `fillPrintMetadata()`, `prepareForPrint()`.

**12.3 Refatoração montarAreaImpressaoTermo():** HTML refatorado para `<div id="printPage">` com (a) header com logos data URI + metadados; (b) main com 3 seções; (c) footer com paginação. Seções: 1. **IDENTIFICAÇÃO** (infobox com processo/depoente/papel/data); 2. **PERGUNTAS E RESPOSTAS** (items coger-print-qa-item parseados de d.termoTexto); 3. **ENCERRAMENTO** (fecho + bloco de assinatura 3 colunas).

**12.4 Parsing Q&A:** nova função `extrairQADoTermo(termoTexto)` com regex pattern para detectar pares "N. P: [pergunta]\n   R: [resposta]" — retorna array de {pergunta, resposta}; cada item renderizado como coger-print-qa-item com pergunta em `<strong>`, resposta normal.

**12.5 Formatação Q&A:** pergunta em negrito (P[N]. [pergunta]); resposta normal com prefixo "R:" em negrito; espaçamento 10pt entre items; `page-break-inside: avoid` em cada item (vs. seção em Rodada 11).

**12.6 Classe no-print aplicada:** botões interativos (`btn-imprimir-termo`, etc.) herdam `no-print` existente ou recebem classe explícita — ocultos em impressão via `display: none !important`.

**12.7 Referência única e metadados:** `montarAreaImpressaoTermo()` agora chama `window.CogerPrint.prepareForPrint()` logo antes de `prepararAreaImpressaoParaImpressao()` — preenche header/footer com INT-YYYYMMDD-XXXX, data/hora, page count estimado.

### Resultado esperado

Ao imprimir termo de oitiva (Oitiva 360, Ctrl+P → Salvar como PDF):

- ✅ Header fixo (logos + "TERMO DE OITIVA" + referência/data/hora)
- ✅ Footer fixo (referência + "Página X de Y" + "USO INTERNO")
- ✅ 3 seções numeradas com barra lateral gold 3px
- ✅ Identificação em infobox (background cinza/borda navy)
- ✅ Q&A com pergunta negrito, resposta normal
- ✅ Cada P/R fica junto (page-break-inside: avoid)
- ✅ Nenhuma seção-title fica órfã no pé de página
- ✅ Referência única gerada (INT-YYYYMMDD-XXXX)
- ✅ Nenhum botão/input interativo na impressão
- ✅ UI interativa funciona normalmente
- ✅ Tipografia consistente (Barlow Condensed, Inter, JetBrains Mono)
- ✅ Paleta navy/gold conforme padrão COGER

**Validação:** ~450 insertions (CSS Print Standard + window.CogerPrint) + ~80 insertions (refatoração montarAreaImpressaoTermo) + nova função `extrairQADoTermo`; braces balanceadas; nenhuma quebra de funcionalidade interativa.

---

## Rodada 11 — COGER Print Standard no Nexo Coger (Minuta de Indiciação)

Implementação do **COGER Print Standard** em `ferramentas/nexo-coger.html` — renderização da minuta de indiciação (termo de indiciação formal) com cabeçalho fixo, rodapé, 7 seções numeradas com barra lateral gold, tabelas com header replicado em quebras de página, e referência única (INT-YYYYMMDD-XXXX). **Nenhuma alteração no catálogo canônico** — impressão isolada em `@media print`, UI interativa preservada.

### Diagnóstico D1–D4 (Nexo Coger)

1. **D1 — Função de impressão:** existe `renderIndiciacao(id, dataDoc)` (linha 4652) que constrói a minuta como array de strings HTML e chama `openPrint()` com o resultado.
2. **D2 — Estrutura HTML atual:** minuta é renderizada como concatenação de divs/tabelas sem estrutura padronizada; seções incluem qualificação (table.qual), fatos, provas, enquadramento, síntese fato-prova-norma, defesa, encerramento; típico 20–50+ páginas.
3. **D3 — CSS @media print:** sim, ~8 linhas básicas (ocultar topbar/main/panel, remover toolbar), sem header/footer fixos, sem classes de componente.
4. **D4 — Metadados:** acessáveis via `doc.processo`, `doc.acusados`, `doc.fatos`, `doc.provas`; função `renderIndiciacao()` tem acesso direto a `doc` (global) e funções helper (`acusadoById`, `fatosOrdenados`, `tabelaFatoProvaEnquadramento`, etc.).

### Implementação 11.1–11.7

**11.1 CSS Print Standard:** integração completa das variáveis de tema (navy `#0B2F5F`, gold `#C9A35C`, cinza `#F5F8FC`/`#DCE6F4`, tipografia) + @media print bloco completo (400+ linhas) com header/footer fixos (`position: fixed`, `z-index: 1000`), seções (barra lateral gold 3px), tabelas (thead replicado via `display: table-header-group`, tbody tr `page-break-inside: avoid`), infobox (background cinza/borda navy), blocos legais (citações com barra esquerda navy).

**11.2 JavaScript utility module:** integração de `window.CogerPrint` IIFE (funções puras) — `generatePrintReference()`, `formatDatePtBr()`, `formatTimePtBr()`, `fillPrintMetadata()`, `prepareForPrint()` — idênticas a Rodada 10, reutilizadas no Nexo Coger.

**11.3 Refatoração renderIndiciacao():** HTML refatorado para estrutura COGER Print Standard com `<div id="printPage">` contendo (a) header com logos data URI + metadados; (b) main com 7 seções; (c) footer com paginação. Seções: 1. **QUALIFICAÇÃO DO ACUSADO** (infobox com nome/matrícula/cargo/lotação); 2. **DOS FATOS E DAS CONDUTAS** (parágrafos numerados); 3. **DAS PROVAS** (descrição e trechos significativos); 4. **DO ENQUADRAMENTO LEGAL** (normas com fundamentação); 5. **SÍNTESE FATO-PROVA-NORMA** (tabela coger-print-table); 6. **DAS ALEGAÇÕES DA DEFESA NÃO ACATADAS** (editable-block com classe no-print); 7. **DO ENCERRAMENTO** (fecho + bloco de assinatura 3 colunas).

**11.4 Tabelas com thead replicado:** síntese fato-prova-norma (resultado de `tabelaFatoProvaEnquadramento()`) tem classe `coger-print-table` com `display: table-header-group` em thead — garante que cabeçalho se repita em cada página de quebra (crítico para tabelas 50+ linhas).

**11.5 Classe no-print aplicada:** editable-block de defesa tem classe `no-print` — oculto na impressão, preservado interativamente.

**11.6 Referência única e metadados:** `renderIndiciacao()` agora chama `window.CogerPrint.prepareForPrint()` logo antes de `openPrint()` — preenche header/footer, calcula página count, gera INT-YYYYMMDD-XXXX aleatória.

**11.7 Logos e estrutura offline:** logos MF e RFB como data URIs SVG (mesmos de Rodada 10); nenhuma dependência externa; estrutura isolada em @media print — nenhuma mudança no modo tela.

### Resultado esperado

Ao imprimir minuta de indiciação (Nexo Coger, Ctrl+P → Salvar como PDF):

- ✅ Header fixo (logos + título "TERMO DE INDICIAÇÃO" + referência/data/hora)
- ✅ Footer fixo (referência + "Página X de Y" + "USO INTERNO")
- ✅ 7 seções numeradas com barra lateral gold 3px
- ✅ Tabela de síntese com cabeçalho replicado em cada página de quebra
- ✅ Nenhuma linha de tabela cortada no meio (page-break-inside: avoid nas rows)
- ✅ Seções nunca começam orfã no pé de página (page-break-after: avoid em títulos)
- ✅ Infobox (qualificação) com fundo cinza/borda navy, labels em negrito
- ✅ Nenhum botão/input/editable-block na impressão (no-print oculto)
- ✅ Múltiplas páginas: tipicamente 20–50+; paginação automática
- ✅ Tipografia consistente (Barlow Condensed, Inter, JetBrains Mono)
- ✅ UI interativa funciona normalmente (botões "Gerar minuta", edição de defesa, etc.)

**Validação:** 547 insertions/60 deletions em nexo-coger.html; braces balanceadas; nenhuma quebra de funcionalidade interativa; `git push` para branch `claude/tool-integration-setup-7wxech` bem-sucedido.

---

## Rodada 10 — COGER Print Standard completo no Veritas (redo com especificação de referência)

Implementação da **Rodada 9** no Veritas (`ferramentas/veritas.html`) — Rodada 9 criou a especificação de design unificado (`padroes/coger-print-standard.css`, `padroes/coger-print-utility.js`, `padroes/coger-print-template.html`), redo de Rodada 10 aplica o padrão completo ao Veritas com fidelidade à especificação. **Nenhuma alteração no catálogo canônico** (`schema_version`/hash8 inalterados). Impressão exclusiva — nenhuma mudança no `@media screen` (UI interativa preservada).

### Diagnóstico D1–D4 (Veritas)

1. **D1 — Função de impressão:** existe `window.print()` chamado no botão "Imprimir / Salvar PDF" da tela `viewRelatorio()` (linha anterior 3255), sem validação de conteúdo.
2. **D2 — Elemento printPage:** não existia `#printPage`; conteúdo de impressão era renderizado como `.vdc-relatorio` dentro do fluxo normal da UI.
3. **D3 — CSS @media print:** sim, ~300 linhas com variáveis de tema (navy/gold) e regras básicas de header/footer/seções, mas sem infobox styles completos.
4. **D4 — Metadados:** armazenados em `DB.dossie.processo` (objeto com `numero`, `comissao`, `secaoResponsavel`, `tipoProcesso`, etc.); acesso via `p = d.processo` em `viewRelatorio()`.

### Implementação 10.1–10.10

**10.1 CSS Print Standard:** integração completa das variáveis (navy `#0B2F5F`, gold `#C9A35C`, cinza `#F5F8FC`, tipografia inter/Barlow Condensed/JetBrains Mono) + `page-break` rules (seções `page-break-inside: avoid`, títulos `page-break-after: avoid`, orphans/widows 3) + novo: estilos `.coger-print-infobox`, `.coger-print-infobox-row`, `.coger-print-infobox-label`, `.coger-print-infobox-value`, `.coger-print-legal-block` (blocos de legislação com barra lateral navy).

**10.2 Refatoração HTML para COGER Print Standard:** `viewRelatorio()` gerava `.vdc-relatorio` (tabelas, antigo padrão de impressão); refatorado para gerar `<div id="printPage">` com estrutura exata da especificação — (a) `<header class="coger-print-header">` com logos data URI SVG (MF + RFB placeholders, 100x40px) + título + metadados em `<span id="coger-print-ref">`, `#coger-print-date`, `#coger-print-time`; (b) `<main>` com seções numeradas; (c) `<footer class="coger-print-footer">` com referência (id `coger-print-footer-ref`), paginação (`.page-number` de/`.page-count` de), nota "USO INTERNO · FERRAMENTAS COGER".

**10.3 Seções numeradas com barra lateral gold:** 1. **DADOS DO PROCESSO** — blocos `coger-print-infobox` para número/portaria/seção/tipo/presidente/secretário/vogais; 2. **ELEMENTOS DE PROVA** — cada item renderizado como `coger-print-infobox` com título/categoria/proveniência/folhas/status/arquivos; 3. **LINHA DO TEMPO DETALHADA** (condicional — só se itens tiverem eventos) — blocos com eventos mesclados por prova (data + título + observações). Cada seção tem `<h2 class="coger-print-section-title">` com número e barra esquerda de 3px solid `--coger-print-gold-500`, `page-break-after: avoid` e espaçamento 16pt (12pt + 4pt).

**10.4 Referência única:** novo módulo `window.CogerPrint` (IIFE) expondo 5 funções puras: (a) `generatePrintReference()` → `INT-YYYYMMDD-XXXX` (ex: `INT-20260713-2305`), onde YYYY/MM/DD é data/hora atual e XXXX é aleatório 0000–9999; (b) `formatDatePtBr(date)` → "13 de julho de 2026"; (c) `formatTimePtBr(date)` → "18:35"; (d) `fillPrintMetadata(options)` → preenche `#coger-print-ref`, `#coger-print-footer-ref`, `#coger-print-date`, `#coger-print-time`, calcula `.page-count`; (e) `prepareForPrint(options)` → função principal, retorna referência gerada.

**10.5 Botão imprimir:** chamada antes de `window.print()` é `window.CogerPrint.prepareForPrint()` — já aplicado (linha 3422, antes da mudança), sem spinner ou confirmação — tão logo o usuário clica, o diálogo de impressão do navegador abre com metadados preenchidos.

**10.6 Ocultar UI interativa:** classe `.no-print` já presente no botão de ações (`.vdc-actions.no-print`); CSS em `@media print` continua com `display: none !important` para `.no-print`; adicionado explícito `display: none !important` para `.vdc-relatorio` (antiga renderização, substituída por `#printPage`).

**10.7 Page-break rules e compatibilidade:** header/footer com `position: fixed` + `z-index: 1000`; `#printPage` + `.vdc-main` + `[role="main"]` com padding = header + margin top + footer + margin bottom (total ~100mm de reserva); seções, tabelas, blocos de info com `page-break-inside: avoid`; títulos com `page-break-after: avoid` + `orphans: 3` + `widows: 3` para evitar órfãos.

**10.8 Logos como data URIs:** sem dependência externa; SVG mínimos (navy + RFB branco) codificados inline em `data:image/svg+xml,%3Csvg...%3C/svg%3E` (URL encoding aplicado na string).

### Resultado esperado

Ao imprimir Veritas para PDF (Ctrl+P → Salvar como PDF):

- ✅ Header fixo em **todas** as páginas (50mm altura visual, 60px em pixels)
- ✅ Footer fixo em **todas** as páginas (como header)
- ✅ Título centrado "DOSSIÊ DE PROVAS"
- ✅ Referência INT-YYYYMMDD-XXXX preenchida dinamicamente
- ✅ Data e hora em português
- ✅ Seções numeradas com barra lateral 3px gold
- ✅ Blocos de dados (infobox) com borda navy-100 / background gray-100
- ✅ Tipografia consistente (Barlow Condensed títulos, Inter corpo, JetBrains Mono hashes)
- ✅ Sem botões, inputs, ou elementos interativos na página impressa
- ✅ Múltiplas páginas: nenhuma title fica órfã no rodapé
- ✅ Paginação automática no footer ("Página 1 de N")

**Validação:** braces balanceadas (`node -e` check); componentes presentes (7 referências `window.CogerPrint`, 18 `coger-print-header`, 48 `coger-print-infobox`); `git push` para `claude/tool-integration-setup-7wxech` bem-sucedido.

**Próximo:** Rodada 11 — replicar padrão em **Nexo Coger** (Minuta de Indiciação PAD/PAR); Rodada 12 — replicar em **Oitiva 360** (Termo de Oitiva PAD/PAR).

## Atualização do Manual da Suíte COGER para o domínio PAR (rodada de documentação, 3 etapas — fechada)

Atualização do `manual/Manual_Suite_COGER.docx` (gerado por `manual/build_manual.py` via python-docx) para cobrir o domínio **PAR** por completo, fechando a lacuna entre o manual publicado — que só documentava o PAD com 3 ferramentas — e o sistema real pós-série PAR-1..PAR-6. **Catálogo canônico intocado** (`schema_version`/hash8 inalterados) — a rodada é só de documentação; nenhum HTML de ferramenta foi alterado. O manual não tem esquema/versão formal; registra-se aqui apenas a atualização de conteúdo.

Executada em três etapas (diagnóstico → seções 1-4 → seções 5-8 + auditoria), das quais esta entrada fecha a rodada. Principais mudanças estruturais:

- **Suíte passou de 3 para 4 ferramentas** — Capa, Introdução Geral e todas as contagens ("três ferramentas") atualizadas; introduzido o contraste **modo dual** (Veritas, Oitiva 360) × **modo fork** (Nexo Coger / Nexo PAR).
- **Renumeração de seções** — Nexo PAR inserido como **nova Seção 4**; Oitiva 360 → **Seção 5**; Integração → **Seção 6**. Todas as referências cruzadas internas conferidas contra a nova numeração (busca global por "Seção 4/5/6"); nenhuma aponta para o número antigo.
- **Nova Seção 4 (Nexo PAR)** — documentada campo a campo no rigor da Seção 3: cadastro de ente privado (razão social, CNPJ, representantes, estruturas societárias, desconsideração art. 14), fato PAR sem elemento subjetivo (benefício/interesse + nexo de causalidade), 11 normas LAC em 2 optgroups, catálogo de pendências (P8 removida, P8-PAR e P-ENTE novas), Nota de Indiciação (art. 17 da IN CGU 13/2019 + 4 textos complementares), prazos do rito PAR (com a ressalva de fonte não fornecida para o prazo de conclusão).
- **Reescrita da Seção 5 (Oitiva 360)** — modo dual em cada subseção: 5º campo Domínio na Matriz com a cascata manual → pauta → trava → confirmação de conflito; categoria de infração e papéis de depoente por domínio (ACUSADO ausente no PAR; 3 papéis PAR); 3 blocos PAR do banco de perguntas; matriz do checklist condicional PAR; chip de domínio; exportações com campo `dominio`.
- **Reescrita da Seção 6 (Integração)** — 4 contratos com campo `dominio` e validação na importação; diagrama do ciclo bifurcado por domínio; nova subseção com a tabela da Política de validação cruzada (PAR-5); subseção de mensagens de recusa padronizadas (formato domínio encontrado/esperado/ferramenta correta/nada alterado) e garantia de importação atômica; badges + chip de domínio do Oitiva 360.
- **Glossário e FAQ** — novas entradas (Domínio, Ente privado, Ato lesivo, papéis PAR, Programa de integridade, Nota de Indiciação, Modo dual, Modo fork) com desambiguação explícita dos três sentidos de "nexo" (nexo fático-probatório × nexo de causalidade × nomes próprios Nexo Coger/Nexo PAR); FAQ do Veritas (Tipo de processo opcional/agnóstico), split Nexo Coger ↔ nova subseção Nexo PAR, e novas perguntas do Oitiva 360 (definição de domínio sem pauta; troca de domínio com dados preenchidos).
- **Convenção de citação normativa** aplicada em todo o texto novo (primeira menção por extenso com data completa; seguintes abreviadas com o ano). **Marcadores `[CAPTURA PENDENTE]`** inseridos onde caberia captura nova (cadastro de ente, seletor de domínio da Matriz, Nota de Indiciação PAR, recusa por domínio).

Verificação: `python3 build_manual.py` gera sem erro; docx é zip válido; 69 headings, 17 imagens, nenhuma imagem com altura > 20 cm; extração de texto via python-docx confirma ausência de "Seção 4" referindo-se à Oitiva 360 ou "Seção 5" referindo-se à Integração. Diagnóstico da etapa 1 em `manual/diagnostico-atualizacao-par.md`.

## Multa_PAR: desempacotamento do bundler + tela inicial padrão

**Fase 1 — Desempacotamento.** `Multa_PAR.html` era o único arquivo da suíte empacotado por um bundler: a aplicação real (React + Babel standalone) ficava serializada como string JSON dentro de `<script type="__bundler/template">`, com imagens em base64 (por vezes gzip) num `<script type="__bundler/manifest">` à parte; um loader desempacotava tudo em `DOMContentLoaded`, gerando blob URLs e substituindo `document.documentElement` inteiro. Isso impedia edição direta de texto, diferente das outras 6 ferramentas.

Executado, uma única vez, exatamente o que o loader fazia em runtime: decodificar o manifesto (com gunzip quando `compressed:true`), gerar **data URIs** (em vez de blob URLs, que não sobrevivem em disco) para cada asset, substituir os placeholders UUID no texto do template, remover `integrity`/`crossorigin` (sem sentido num arquivo local), injetar `window.__resources` logo após `<head>`, e salvar o HTML resultante como o novo `Multa_PAR.html` — sem nenhum vestígio de bundler (`__bundler_thumbnail`, loader, as três tags `__bundler/*`). Verificado via Playwright: zero erros de carregamento, calculadora renderiza e interage normalmente, mesma UI do arquivo original (comparação visual). A partir de agora é um HTML estático comum, mesma arquitetura do `Dosimetria_TAC.html` (React via `text/babel`), editável diretamente.

**Fase 2 — Tela inicial padrão.** A ferramenta já tinha rascunho automático em localStorage e exportação (.json com `_meta`/`dados`, incluindo hash SHA-256 do conteúdo para detectar arquivo adulterado) — só faltava a tela de entrada uniforme. Implementada: identificador do caso (nº do PAR) ou estado vazio, com "▶ Continuar caso" (necessário aqui pelo mesmo motivo do Nexo/Dosimetria — a tela é bloqueante a cada carregamento), "+ Novo caso" (modal com o mesmo texto/estrutura do `renderModalReiniciar` do Veritas: aviso de dado salvo, sugestão de exportar antes, alerta "não pode ser desfeita", botões Cancelar/Exportar antes/Iniciar novo mesmo assim) e "📂 Importar caso (.json)" (reaproveita `importarEstado`, que já valida `_meta.aplicacao`, versão de schema e hash de conteúdo antes de aplicar, com confirmação extra se já há dado preenchido).

Testado via Playwright (com tratamento dos diálogos nativos `confirm`/`alert` que a ferramenta já usa): fluxo completo exportar → recarregar → tela mostra o processo → "Novo" pede confirmação → cancelar preserva o rascunho → confirmar limpa; importar restaura o estado corretamente; JSON inválido é rejeitado com mensagem clara sem alterar nada. Nenhum campo/cálculo do wizard foi alterado.

## Correção de bugs — Nexo Coger e Nexo PAR (reportados pelo usuário)

Dois bugs relatados no Nexo PAR, diagnosticados e corrigidos (um deles também no Nexo Coger, por ser o mesmo código herdado):

**1. Radios permitindo marcar mais de uma opção ao mesmo tempo (nexo-coger.html e nexo-par.html).**
A função `radio(name,cur,val,label,onset)` (usada por todo grupo de rádio construído manualmente na ferramenta — ex.: "Contraditório — acusado intimado da produção?", com as 3 opções Intimado/Não intimado/Não avaliado) gerava um sufixo aleatório por CHAMADA: `name+Math.random().toString(36).slice(2,6)`. Como cada opção do mesmo grupo lógico é uma chamada separada de `radio()`, cada uma nascia com um `name` diferente — quebrando o agrupamento nativo de exclusão mútua do navegador. Resultado: era possível marcar as 3 opções simultaneamente. Bug idêntico, linha a linha, em `nexo-coger.html` (herdado pelo fork na Rodada PAR-3, não introduzido por ela). Corrigido nos dois arquivos: `name` fixo (sem sufixo), preservando o agrupamento. Confirmado por grep que nenhum grupo de rádio na mesma tela reutiliza o mesmo `name` para campos diferentes (sem risco de colisão). `veritas.html`/`oitiva-360.html` não usam esse helper (radios com `name` fixo desde sempre) — não afetados.

**2. Descrição truncada no meio da frase para as normas LAC (nexo-par.html).**
`buildCatalogo()` gerava o rótulo de cada norma LAC truncando `descricao` (o texto integral do inciso, único campo disponível no catálogo canônico para essas normas — diferente das normas da Lei 8.112, que têm um `rotulo` curto autoral separado) em 78 caracteres, cortando no meio da frase (ex.: "...vantagem indevida a…", sem "agente público"). Esse rótulo truncado aparecia tanto no `<select>` de enquadramento quanto embutido na Nota de Indiciação gerada — nos dois casos, uma frase jurídica incompleta. Corrigido: `rotuloCurto` não trunca mais, usa o texto integral (só remove o ponto final, para caber melhor entre parênteses no documento gerado). O navegador acomoda a opção mais larga no `<select>` sem problema.

Testes: `test-fluxo-integrado.js` — 127/127, sem regressão. Verificação visual via Playwright: nenhuma opção de norma termina em "…"; os 3 radios do campo "Contraditório" agora são mutuamente exclusivos nos dois arquivos.

## Importação + tela inicial padrão — Dosimetria_TAC

Ferramenta **standalone** `ferramentas/Dosimetria_TAC.html` (React via `text/babel`, fora da suíte `test-fluxo-integrado.js`). Duas capacidades novas, alinhadas ao padrão Veritas mas adaptadas à arquitetura React (estado em `useState` no componente `App`, não `DB`/`render()` global). **Catálogo canônico intocado.**

### Formato do JSON exportado/importado

`exportarJSON` (Tela 11) e o novo `exportarCaso` (nível `App`, usado na tela inicial) produzem o **mesmo esquema**: o objeto `state` **achatado** (todas as chaves de `initState()` — `processo`, `regime`, `enquadramento`, `reincidencia`, `pontuacao`, `tac50`, campos TAC/LINDB, `schemaVersion:'3.0'`, etc.) acrescido dos campos calculados `somaTotal`, `penal`, `tacViavel`, `geradoEm` e — **novidade** — dos identificadores `ferramenta:'dosimetria_tac'` e `esquemaExport:'1.0'` no topo. Não há campo `step` no export (a exportação só ocorre no resultado final, então a importação sempre recai na Tela 11). Adicionar os dois campos de identificação é seguro: nada no arquivo lia esse JSON de volta antes (não havia importação).

### Importação (`importarArquivo`) e validação

Novo handler `App.importarArquivo(evt)`: lê o arquivo com `FileReader`, faz `JSON.parse` e valida em três camadas — (1) JSON malformado → `alert` "não é um JSON válido"; (2) `ferramenta !== 'dosimetria_tac'` → `alert` de ferramenta incorreta; (3) ausência de `processo` **ou** `pontuacao` → `alert` de campos essenciais faltando. Em qualquer falha o estado atual **não** é tocado. Se há caso em andamento com conteúdo (`temConteudoCaso(state)`: nº/servidor/matrícula, regime, enquadramento ou infrações), pede `window.confirm("A importação nunca mescla — o caso atual será substituído. Deseja continuar?")` antes de prosseguir. Ao confirmar, `reconstruirCasoImportado` descarta os campos calculados/identificadores e reidrata sobre `initState()` (defaults para chaves ausentes), navega à Tela 11 (`step=11`, `maxDone=11`) e passa a persistir no localStorage. Botão de importar disponível na Tela 11 (ao lado de "Exportar JSON") e na tela inicial. Feedback de erro por `alert`/`confirm` — não havia `toast` nesta ferramenta.

### Tela inicial padrão (`TelaInicio` + `ModalNovoCaso`)

Substitui o antigo `ModalSessaoSalva` (retomar/descartar silencioso). Exibida **antes** do wizard (`iniciado=false` por padrão). Ao montar, `carregarSessao()` é lido para `sessaoSalva` **sem** sobrescrever o localStorage (o efeito de salvar automático agora é condicionado a `iniciado`, evitando clobber do rascunho enquanto na tela inicial). Mostra o nº do processo do caso salvo (ou estado vazio) e os botões **"Continuar caso"** (só quando há rascunho com conteúdo — desvio justificado abaixo), **"+ Novo caso"** e **"Importar caso (.json)"**. "Novo caso" com rascunho salvo abre `ModalNovoCaso` (3 parágrafos: caso salvo no navegador / apagar localStorage e exportar antes / alerta de ação irreversível; botões Cancelar / Exportar .json antes / Iniciar novo mesmo assim). Sem rascunho, "Novo caso" entra direto no wizard sem aviso. **Desvio do padrão Veritas:** o Veritas mostra a tela inicial só quando não há dossiê e entra direto na tela de trabalho quando há; aqui, como o "trabalho" é um wizard, adicionei um botão explícito **"Continuar caso"** para retomar o rascunho (o Veritas não precisa dele). Justificado por não haver outra forma de retomar um caso em andamento a partir da tela inicial.

### Testes (Playwright, Chromium, sem suíte integrada)

Todos com `page.on('pageerror')` como verificação de sintaxe Babel — **zero erros** em todos os cenários. Tarefa 1: seed de estado válido → Tela 11 → exportar → JSON confere (`ferramenta`/`esquemaExport` presentes, sem `step`, `somaTotal=18`); importar arquivo diferente com caso em andamento → `confirm` de substituição → estado restaurado; JSON malformado → `alert`, estado intacto; ferramenta errada → recusado. Tarefa 2: tela inicial vazia (sem "Continuar"); com rascunho → mostra nº + "Continuar" → Tela 11; import a partir da tela vazia → restaura na Tela 11; "Novo caso" → modal com os 3 parágrafos + 3 botões; "Exportar .json antes" baixa o caso salvo; "Iniciar novo mesmo assim" limpa o localStorage e entra no wizard fresco; reload volta à tela inicial vazia; "Novo caso" sem rascunho entra direto na Tela 0.

## Rodada PAR-6 — Teste integrado do fluxo PAR + fixture completo (fechada)

Equivalente PAR da Rodada 7 original: prova executável, sem browser e sem interação manual, de que o ciclo PAR funciona ponta a ponta. **Nenhuma funcionalidade de ferramenta mudou** (6.6) — só fixture, testes e extração pontual de funções puras sem mudança de comportamento observável. **Catálogo canônico intocado** (`schema_version`/hash8 inalterados). Um único `node test-fluxo-integrado.js` exercita os dois domínios e a validação cruzada.

### 6.1 — `fixtures/par-ficticio-001.json` expandido (mesmo arquivo, não um segundo)

A versão mínima da PAR-5 foi expandida para o conteúdo completo, espelho estrutural do `pad-ficticio-001.json`: **um ente privado** (*Construtora Fictícia Alfa Ltda.*, CNPJ `11.222.333/0001-81` fictício, faturamento bruto preenchido) com **um representante legal** de vínculo `PAPEL.REPRESENTANTE_LEGAL` (valor exato que o gate **P-ENTE** exige); **dois fatos** apurados, `FP1`→`NORMA.LAC.ART5_IV_A` (frustração do caráter competitivo) e `FP2`→`NORMA.LAC.ART5_IV_D` (fraude a contrato), **ambos** com `beneficioInteresse` + `nexoCausalidade` preenchidos (satisfaz o gate **P8-PAR**) e `descricao` (exigida por `validaMinuta`); **uma prova documental** inicial no Veritas vinculada a `FP1`; **uma lacuna** (`FP2` sem prova → `tipo_lacuna: sem_prova`) que gera a pauta; **um depoente representante legal** (papel `representante_legal`, um dos 3 vínculos PAR) com resposta fictícia e sem "acusado alternativo" (→ `acusado_vinculo:"padrao"`, vínculo ao ente privado). Campos dos fatos usam os **nomes reais lidos pelo Nexo PAR** (`beneficioInteresse`/`nexoCausalidade`), evitando remapeamento no teste. Blocos `_descricao`/`_comoReexecutar` documentam a reexecução.

### 6.2 — Ciclo PAR de 8 etapas (grupos `par_passo1..par_passo8`)

`test-fluxo-integrado.js` estendido (não um script paralelo) com o ciclo espelhando as 7 etapas do PAD + o 8º passo próprio do PAR: (1) Veritas exporta a prova inicial → contrato válido com `dominio:"par"`; (2) Nexo PAR monta o doc (ente + 2 fatos), confirma gates P-ENTE/P8-PAR satisfeitos, valida o domínio (`validarDominioEnvelope` ok) e importa a prova resolvendo tipo/rótulo do catálogo; (3) gera a pauta da lacuna `FP2` com `pauta_id` único, norma LAC nos `pontos_instrucao` e `dominio:"par"` no envelope (emissão corrigida na PAR-5 Parte B); (4) Oitiva 360 importa a pauta e **deriva o domínio PAR pela cascata** (`derivarDominioDaPauta`), confirmando que `PAPEL.ACUSADO` some e os 3 papéis PAR aparecem, e que ≥1 pergunta vem de um dos 3 blocos PAR (`par_atos_licitacoes`/`par_terceiro_interposto`/`par_programa_integridade`); (5) gera o termo com as respostas → hash sha256 conferido → `dominio:"par"`; (6) Veritas importa no dossiê PAR (domínio compatível + hash) → novo `id_prova` `termo_oitiva`; (7) Oitiva exporta o retorno → Nexo PAR importa e vincula ao **ente privado padrão** (`doc.acusados[0]`), **sem** disparar Nota de Indiciação (pendências/provas/`_minutaGerada` inalterados); (8) com os gates ok, gera a **Nota de Indiciação** via a função pura `construirTextoIndiciacao` e afirma por **busca de marcadores** (não igualdade literal) a presença de: título, cabeçalho PAR + Lei 12.846/2013, razão social/CNPJ/representante legal, conduta lesiva, provas, enquadramento art. 5º IV, benefício/nexo, multa + faturamento bruto, inciso IV do art. 22 do Decreto 11.129/2022, prazo de 30 dias, programa de integridade, resolução negociada (Termo de Compromisso/Acordo de Leniência) e art. 17 da IN CGU 13/2019.

### 6.3 — Idempotência e falha controlada no ciclo PAR (`par_idempotencia`, `par_falha_controlada`)

Réplica dos testes 7.4/7.5 para o PAR: reimportação dos passos 2/4/6/7 com o mesmo payload → recusa explícita por duplicidade (sem duplicar prova, item de pauta, item de dossiê ou contexto); termo PAR com 1 caractere alterado antes do passo 6 → rejeição por `hash_divergente`; `catalogo_schema_version` divergente no contrato de prova e no termo PAR → aviso (`catalogoDivergente:true`) sem bloquear, mesmo comportamento do PAD.

### 6.4 — Recusa cruzada PAD↔PAR com os DOIS fixtures reais (`cruzada`, com atomicidade)

Migrado dos payloads sintéticos da PAR-5 para os fixtures reais: (1) prova PAR → Nexo Coger **recusada**; (2) prova PAD (marcada) → Nexo PAR **recusada**; (3) pauta PAR → Oitiva 360 já em domínio PAD **sem confirmação** (`confirm()=>false`) → importação **inteira recusada** via `aplicarImportacaoPauta` (nada em `estado.pautaImportada`, domínio manual `pad` preservado); (4) termo PAR → dossiê Veritas PAD **recusado** (`dominio_incompativel`); (5) envelope PAD legado (sem `dominio`) → Nexo Coger **aceito**, → Nexo PAR **recusado** com mensagem de legado. **Toda** recusa afirma a **atomicidade**: snapshot da contagem de provas/itens/domínio do receptor antes e depois — idênticos. O grupo `validacao_dominio` (14) da PAR-5 permanece como cobertura das funções puras com entradas sintéticas; o grupo `cruzada` (12) adiciona os 6 casos com fixtures reais + atomicidade. Sem duplicação de casos idênticos.

### 6.5 — Relatório unificado em três seções

Saída de console reorganizada (sem framework, mesmos `checar`/`registrar`) em **Fluxo PAD**, **Fluxo PAR** e **Validação cruzada** via `secaoDoGrupo(grupo)`, cada seção listando seus grupos e placar. `process.exitCode = 1` quando qualquer verificação falha (comportamento já existente, mantido). O guard "caso 7" foi ajustado para contar explicitamente os grupos da seção PAD (43), robusto às novas seções.

### Extração de função pura no Nexo PAR (e exposições no Oitiva 360)

- **`ferramentas/nexo-par.html`:** `renderIndiciacao` estava acoplado ao DOM (chamava `openPrint` com a string montada). O **corpo** foi extraído para a função pura `construirTextoIndiciacao(id, dataDoc)` (lê o `doc` via `setDoc`, devolve a STRING HTML, sem tocar em `document`/print); `renderIndiciacao` virou wrapper fino que só envia o resultado ao `openPrint` — **comportamento idêntico**. Foi a única extração necessária: os gates **P-ENTE** e **P8-PAR** já eram puros em `computePendencias`, e o cadastro de ente já era construível direto no `doc` (como o acusado do fixture PAD).
- **`ferramentas/oitiva-360.html`:** por ser um IIFE, quatro funções já existentes foram **expostas** em `window.OitivaPuro` para o teste (`derivarDominioDaPauta`, `dominioProcesso`, `itemVisivelNoDominio`, `papelEhPAR`) e `aplicarImportacaoPauta` (recusa atômica de pauta em conflito) — apenas exposição, nenhuma mudança de comportamento (mesmo padrão dos setters da Rodada 7). `veritas.html` e `nexo-coger.html` **não** foram tocados.

### Placar final

`node test-fluxo-integrado.js` → **127/127**, exit 0. Seções: **Fluxo PAD 43/43** (inalterado — 6.6 confirmada), **Fluxo PAR 58/58** (`par_passo1 3`, `par_passo2 6`, `par_passo3 5`, `par_passo4 6`, `par_passo5 4`, `par_passo6 3`, `par_passo7 5`, `par_passo8 18`, `par_idempotencia 5`, `par_falha_controlada 3`), **Validação cruzada 26/26** (`validacao_dominio 14` + `cruzada 12`). `node --check` (via `new Function`) no `<script>` de `nexo-par.html` e `oitiva-360.html`: OK.

## Rodada PAR-5 — Validação cruzada de domínio nos contratos (em andamento)

Fechamento e consistência: cada receptor passa a validar o `dominio` do envelope contra o seu próprio domínio; nenhum campo novo de negócio, nenhuma tela nova além dos avisos de recusa. **Nenhuma alteração no catálogo canônico** (`schema_version`/hash8 inalterados). Tabela da "Política única de validação" registrada como comentário-referência no código de cada rotina de importação dos dois arquivos, com texto idêntico (não divergir em manutenção futura).

### Parte C — Teste de regressão estendido e fixture PAR (`test-fluxo-integrado.js`, `fixtures/par-ficticio-001.json`)

Etapa de fechamento (seção 5.6): estende o teste integrado programático (Node `vm`, sem browser) com os 7 casos de validação de domínio e cria o fixture PAR reutilizável, sem tocar nas implementações das Partes A/B.

- **`fixtures/par-ficticio-001.json` (novo):** no mesmo espírito descritivo do `pad-ficticio-001.json` (campos `_descricao`/`_comoReexecutar`). Um ente privado fictício (razão social *Construtora Fictícia Alfa Ltda.*, CNPJ `11.222.333/0001-81` — fictício, só em formato válido —, representante legal com CPF fictício e vínculo `representante_legal`); um fato com enquadramento LAC `NORMA.LAC.ART5_IV_A` (art. 5º, IV, "a" — grupo Licitações e contratos) com os dois campos materiais do PAR preenchidos (`beneficioInteresse` + `nexoCausal`, para não disparar a P8-PAR); uma prova documental fictícia; um depoente `preposto` (vínculo PAR); e um bloco de pauta com `dominio:"par"`. Reutilizável nas próximas rodadas PAR.

- **`test-fluxo-integrado.js` estendido:** passou a carregar também `nexo-par.html` via `vm`, no mesmo padrão de stub/contexto do Nexo Coger (fork estruturalmente idêntico — PAR-3). Novo grupo de verificações `validacao_dominio` com os 7 casos da spec, todos chamando as **funções reais** já expostas por cada ferramenta (nenhuma exposição nova foi necessária):
  1. Envelope `{dominio:"par"}` no Nexo Coger → `validarDominioEnvelope` retorna `ok:false`; mensagem cita "encontrado: PAR" e sugere o Nexo PAR. **RECUSADO.**
  2. Envelope `{dominio:"pad"}` no Nexo PAR → `ok:false`; mensagem cita "encontrado: PAD" e sugere o Nexo Coger. **RECUSADO.**
  3. Envelope `{}` (sem `dominio`) no Nexo Coger → `ok:true`. **ACEITO como legado.**
  4. Envelope `{}` no Nexo PAR → `ok:false`; confirmado que a mensagem é a **específica de arquivo legado** ("anterior às Rodadas PAR"/"acervo legado") e **distinta** da mensagem do caso 2 (recusa de `"pad"`). **RECUSADO.**
  5. Termo PAR (`dominio:"par"`, hash coerente) em dossiê Veritas **sem tipo** → `avaliarImportacaoTermo` retorna `ok:true` (`dominioDoProcesso("")===undefined`). **ACEITO** (agnosticismo preservado).
  6. Mesmo termo PAR em dossiê Veritas com `tipoProcesso:"PAD"` (`dominioDoProcesso→"pad"`) → `ok:false, motivo:"dominio_incompativel"`. **RECUSADO.**
  7. Fluxo PAD original (7 etapas) → verificado explicitamente que todas as verificações fora do grupo `validacao_dominio` somam **43/43 com 0 falhas** (inalterado).

- **Exposição de funções:** **nenhuma** exposição nova em `VeritasPuro`/`OitivaPuro` foi necessária. `validarDominioEnvelope` está no escopo de topo do `<script>` dos dois Nexos (sem IIFE) → visível no contexto `vm`; `avaliarImportacaoTermo` e `dominioDoProcesso` já estavam em `window.VeritasPuro` desde a PAR-2. O Oitiva não precisou ser exercitado por função nova (os casos 5.6 cobrem Nexos e Veritas).

- **Placar final:** `node test-fluxo-integrado.js` → **57/57**, exit 0. Grupos: `setup 3/3`, `validacao_dominio 14/14` (13 asserções dos 7 casos + carregamento do Nexo PAR), `fixture 1/1`, `passo1 3/3`, `passo2 3/3`, `passo3 6/6`, `passo4 3/3`, `passo5 4/4`, `passo6 4/4`, `passo7 5/5`, `idempotencia 8/8`, `falha_controlada 3/3`. As 43 verificações originais permanecem intactas (subiu de 43 para 57 só pelo novo grupo).

- **Critérios de aceite (reconfirmação programática):** cada linha da tabela de política é demonstrável por teste (recusa por domínio divergente nos Nexos, aceite de legado só no PAD, recusa de legado no PAR com mensagem própria, agnosticismo do Veritas sem tipo, recusa cruzada com tipo definido); o fluxo PAD original segue intacto (43/43); e a atomicidade da recusa (nenhum estado parcial) — já testada por Playwright nas Partes A/B — é reconfirmada aqui no nível puro: as funções de validação retornam o veredito **antes** de qualquer mutação (o teste chama `validarDominioEnvelope`/`avaliarImportacaoTermo` de forma isolada, sem que nada seja gravado no `doc`/`dossiê` na recusa).

### Parte B — Nexo Coger e Nexo PAR (`nexo-coger.html`, `nexo-par.html`)

Ambos ganharam, junto à seção de importação, uma constante `DOMINIO_FERRAMENTA` (`'pad'` no Nexo Coger, `'par'` no Nexo PAR), a tabela-comentário da política e o par de funções puras `validarDominioEnvelope(env)` + `mensagemRecusaDominio(encontrado)`. A validação roda no **início** de cada rotina de revisão de importação, **antes** de montar o modal — recusa **atômica**: o `alert()` com a mensagem dispara e a função retorna, então nenhum item chega à tela de revisão nem ao estado (confirmado por teste: `modalOpen===false` e contagem de `doc.provas` inalterada na recusa).

- **5.1 — Receptor de provas do Veritas** (`revisarImportacaoVeritas`): Nexo Coger aceita `dominio:"pad"` ou ausente (legado), recusa `"par"`. Nexo PAR aceita apenas `"par"`, recusa `"pad"` e recusa ausente (mensagem de legado).
- **5.2 — Emissor de pauta para o Oitiva 360** (`construirContratoPauta`, usada por `gerarPautaPorDepoente`): **descoberta** — a PAR-3 (item 3.1) marcou `dominio` só no `exportJson()` do processo; o envelope da **pauta** NÃO emitia `dominio` em nenhum dos dois arquivos. Adicionado `dominio:DOMINIO_FERRAMENTA` ao envelope da pauta: `"pad"` no Nexo Coger, `"par"` no Nexo PAR.
- **5.4 — Receptor de retorno de prova do Oitiva 360** (`revisarImportacaoRetornoOitiva`): mesma política do 5.1. **Vínculo padrão confirmado correto no Nexo PAR**: `doc.acusados[0]` (usado como vínculo automático quando há 1 sujeito) É o **ente privado** do processo — a PAR-3 manteve deliberadamente o array `doc.acusados[]`/`acusadoId` como identificador estável, com `a.nome` espelhando a razão social. Nenhum resquício incoerente; só documentado com comentário no código, sem alteração estrutural.
- **5.5 — Mensagem de recusa padronizada**, mesma estrutura de frase nos dois arquivos: explicação em linguagem clara (origem do arquivo + ferramenta correta a usar) seguida de `"Domínio encontrado: <X>. Domínio esperado: <Y>. Nenhum dado foi alterado."`. Exemplos reais adotados — Nexo Coger recusando `par`: *"Este arquivo foi exportado de um processo PAR (Lei nº 12.846/2013 — LAC). Este é o Nexo Coger, que trabalha com processos PAD (Lei nº 8.112/1990) — importe-o no Nexo PAR. Domínio encontrado: par. Domínio esperado: pad. Nenhum dado foi alterado."*; Nexo PAR recusando ausente (legado): *"Este arquivo não indica domínio (formato anterior às Rodadas PAR) e não pode ser importado no Nexo PAR, que trabalha exclusivamente com processos PAR (Lei nº 12.846/2013 — LAC). No PAR não existe acervo legado a preservar. Domínio encontrado: (ausente). Domínio esperado: par. Nenhum dado foi alterado."*

`veritas.html` e `oitiva-360.html` (Parte A) e o `test-fluxo-integrado.js`/`fixtures/par-ficticio-001.json` (5.6) **não foram tocados** por esta parte.

### Testes (Parte B)

- `node --check` (via `new Function()`) no `<script>` de ambos os arquivos: OK.
- `node test-fluxo-integrado.js`: **43/43**, exit 0 — sem regressão (o fluxo PAD original e a validação de hash/idempotência seguem intactos).
- Playwright (Chromium, os dois HTMLs reais): **16/16** asserções — envelope de prova `par` recusado no Nexo Coger (sem modal, estado inalterado); `pad` recusado no Nexo PAR; ausente aceito como legado no Nexo Coger (modal abre); ausente recusado no Nexo PAR com mensagem de legado; `par` aceito no Nexo PAR; `validarDominioEnvelope` com as três entradas em cada arquivo; pauta emitindo `dominio` correto; e a recusa por domínio também no contrato de retorno de oitiva (`revisarImportacaoRetornoOitiva`) nos dois arquivos.

### Parte A — Veritas e Oitiva 360 (`veritas.html`, `oitiva-360.html`)

Adiciona validação de domínio na importação de termo (Veritas) e a recusa atômica de pauta em conflito não confirmado (Oitiva), e confere a emissão nos dois emissores. Catálogo canônico intocado; sem campo/tela novos além dos avisos. Importação **atômica** em todos os pontos: recusa não altera nenhum dado do estado.

- **5.5 — Mensagem-base única de recusa.** Helper `mensagemRecusaDominio(encontrado, esperado, acaoCorreta)` + `rotuloDominioExtenso(d)` embutidos nos dois arquivos, mesma estrutura de frase: **`"Domínio encontrado: <X>. Domínio esperado: <Y>. <ação/ferramenta correta>. Nenhum dado foi alterado."`** — `<X>`/`<Y>` renderizados por extenso (`"PAD (Lei 8.112/1990)"` / `"PAR (Lei 12.846/2013)"` / `"não indicado (arquivo legado, anterior às rodadas PAR)"`), seguindo o exemplo textual da spec 5.3. Usado em todos os pontos de recusa por domínio desta metade.
- **5.1 — Emissão no Veritas (conferência).** Confirmado sem correção necessária: `App.exportarDossie` (via `persistir()` que sincroniza `processo.dominio` — PAR-2.3) **e** `App.exportarProvasParaNexo`/`construirContratoProvasNexo` já emitem `dominio` (padrão "ausente, nunca null"). Os dois contratos estavam cobertos desde a PAR-2.
- **5.3 — Veritas como RECEPTOR de termo (novo).** Validação de domínio adicionada em `avaliarImportacaoTermo()` (núcleo puro `VeritasPuro`), **após o check de formato e ANTES do hash** (recusar cedo). Domínio do dossiê = `processo.dominio || dominioDoProcesso(processo.tipoProcesso)`. Dossiê **sem tipo** (agnóstico) → aceita qualquer termo (Veritas genérico preservado). Definido → mesmo domínio prossegue; diferente → `motivo:"dominio_incompativel"`; envelope legado (sem `dominio`) → aceito em dossiê PAD, recusado (`motivo:"dominio_legado_par"`) em dossiê PAR. `App.importarTermoOitiva` ganhou dois ramos de `alert()` com a mensagem-base. Verificação de hash (Rodada 5) intocada, só passou a rodar após a validação de domínio. Tabela da política comentada no código.
- **5.4 — Emissão no Oitiva 360 (conferência).** Confirmado sem correção: `construirEnvelopeTermo` (→ Veritas) e `construirEnvelopeRetorno` (→ Nexo) já emitem `dominio` via `dominioProcessoDefinido()` (omitido quando indefinido).
- **5.2 — Oitiva 360 como RECEPTOR de pauta (fecha caso da PAR-4).** `aplicarImportacaoPauta()` reordenada: o conflito de domínio (pauta com `dominio` divergente de um domínio manual já definido) é detectado por `confirm()` **antes de qualquer mutação de estado** (antes de `mesclarPautaImportada`). **Não confirmar → importação inteira recusada** (`return` precoce; `estado.pautaImportada`/`estado.matriz` intactos) com `alert()` padronizado — antes a PAR-4 só alertava e importava mesmo assim. O `alert()` de conflito redundante em `derivarDominioDaPauta()` foi removido. Sem conflito → deriva/trava o domínio pela pauta como na PAR-4, sem diálogo.

### Testes (Parte A)

- `new Function` sobre o `<script>` de cada arquivo: OK nos dois.
- `node test-fluxo-integrado.js`: **43/43**, exit 0, sem regressão (o teste usa os núcleos puros; dossies do teste são agnósticos/PAD, aceitos pela nova validação).
- Playwright (Chromium real, `veritas.html` + `oitiva-360.html`): **11/11** — termo PAR recusado em dossiê PAD (atômico); termo PAR aceito em dossiê sem tipo; termo legado recusado em PAR e aceito em PAD; validação antes do hash; pauta PAR conflitante **recusada inteiramente** quando não confirmada (nada importado, domínio PAD preservado, alert padronizado); pauta importada + domínio trocado quando confirmada; derivação sem diálogo sem domínio manual.

> **Nota de reconciliação (Partes A × B):** a estrutura da frase-base de recusa é a mesma nas quatro ferramentas. A Parte A renderiza o rótulo do domínio por extenso (`"PAR (Lei 12.846/2013)"`, seguindo o exemplo da spec 5.3); a Parte B usa o token cru (`"par"`/`"pad"`) na string `Domínio encontrado:`/`Domínio esperado:`. Recomenda-se unificar num único formato na reconciliação final (sugestão: o por extenso, mais informativo). Nenhuma diferença funcional — só apresentação do rótulo.

## Rodada PAR-4 — Ajuste do Oitiva 360 (modo dual PAD/PAR) (fechada)

Modo dual (não fork), como decidido na spec: `ferramentas/oitiva-360.html` permanece um único arquivo. **Nenhuma alteração no catálogo canônico** (`schema_version`/hash8 inalterados) — a rodada é só de UI/lógica embutida no HTML, com o mesmo `CATALOGO_COGER` já compartilhado. Disciplina do modo dual respeitada: **nenhum condicional por domínio tocou a mecânica central** (rodadas de oitiva, geração/estrutura do termo, cálculo de hash). Tudo o que muda é filtragem de lista (papéis, infrações, blocos, checklist) e vocabulário. Confirmação objetiva: o termo gerado em modo PAD é **byte-idêntico** ao anterior (a neutralização do texto de abertura usa um placeholder que resolve para exatamente a string antiga em PAD) e `test-fluxo-integrado.js` segue **43/43** sem tocar em `sha256HexOitiva`/`gerarTermoTexto`.

### 4.1 — Seletor de domínio na Matriz de Apuração
5º campo da matriz (`estado.matriz.dominio`, `pad`|`par`). `processoVazio()` nasce `"pad"`; **JSONs antigos não são backfilled** em `migrarEstadoCarregado()` (confirmado) — assim a exportação só emite `dominio` quando explicitamente definido. Select editável enquanto `!dominioTravadoPorPauta()`; travado (exibido, não editável, com aviso "🔒 derivado da pauta") quando a pauta importada trouxe `dominio`. Troca manual com dados incompatíveis já cadastrados → `confirm()` que lista, ANTES de aplicar, as infrações que serão LIMPAS e os papéis que serão MANTIDOS mas sinalizados "fora do domínio"; recusa reverte o select. Derivação por pauta em `aplicarImportacaoPauta()` via novo `derivarDominioDaPauta()` (grava `pautaImportada.dominio`, alinha `estado.matriz.dominio`, avisa em conflito com domínio manual divergente). Pauta sem o campo não trava nada.

### 4.2 — Categoria de infração sensível a domínio
`popularSelectInfracao()` desvia para `popularSelectInfracaoLAC()` em modo PAR: 11 normas `NORMA.LAC.*` (derivadas de `CATALOGO_COGER.normas` em `INFRACOES_LAC`) em 2 optgroups. `renderInfracaoDetalhe()` mostra a `nota_aplicacao` da norma LAC como hint (📌), reaproveitando o padrão visual existente. `buscarInfracao()` unifica o lookup PAD+LAC (usado na lista de depoentes). Modo PAD inalterado (53 normas da Lei 8.112/LAI).

### 4.3 — Papéis de depoente sensíveis a domínio
`renderEtapa2()` filtra `CATALOGO.papeis` por `itemVisivelNoDominio(p.dominio, dominioProcesso())`. PAR: entram `representante_legal`/`preposto`/`socio_administrador` (3 entradas completas criadas no catálogo embutido, com `descricaoRegime` coerente com o regime PAR) + papéis `"comum"`; sai `acusado` (marcado `dominio:"pad"`). Papel já cadastrado fora do domínio novo é preservado no estado e ainda aparece no rádio (marcado), sinalizado "fora do domínio" — na lista de depoentes e na própria opção.

### 4.4 — Banco de perguntas: 3 blocos PAR
`par_atos_licitacoes` (7 perguntas, art. 5º, IV), `par_terceiro_interposto` (6, art. 5º, III/II), `par_programa_integridade` (7, art. 7º, VIII), todos `dominio:"par"` com `normasRelacionadas`. Blocos existentes classificados: `elemento_subjetivo` e `circunstancias_art128` → `"pad"` (institutos exclusivos do PAD; LAC é de responsabilidade objetiva, art. 2º); os demais → `"comum"`. Filtragem em `blocoForaDoDominio()`, consumida por `blocoDeveSerOmitido()` e `gerarRoteiroInicial()` (só a LISTA de blocos é filtrada; a geração/concatenação é idêntica).

### 4.5 — Checklist condicional PAR
6 itens novos com condições simbólicas resolvidas em `itensChecklistAplicaveis()`, no mesmo padrão de parsing dos casos existentes: `dominio == par` (transversal benefício/nexo causal, art. 2º LAC — aparece em toda combinação PAR), `papel_par`, `socio_par`, `representante_par`, `grupo == licitacoes` (via `grupoDaInfracaoLAC()`), `infracao == NORMA.LAC.ART5_III`. Nenhum ativa em PAD.

### 4.6 — Propagação do domínio nas exportações
`construirEnvelopeTermo()` (→ Veritas) e `construirEnvelopeRetorno()` (→ Nexo) emitem `dominio` a partir de `dominioProcessoDefinido()`, com o padrão da PAR-2 (`if (dom) envelope.dominio = dom;`) — omitido, nunca `null`, quando indefinido. Sem validação de importação por domínio (reservada à PAR-5).

### 4.7 — Textos neutros e identidade
Chip `PAD`/`PAR` no `topbar` (paleta navy/gold), atualizado por `renderChipDominio()`. Texto fixo compartilhado da abertura formal ("Processo Administrativo Disciplinar") neutralizado via placeholder `{{tipo_processo_extenso}}` (resolve para "Processo Administrativo Disciplinar" em PAD — string idêntica — e "Processo Administrativo de Responsabilização" em PAR). Grep de "servidor"/"acusado" revisado: as demais ocorrências são citações literais da Lei 8.112 ou perguntas atadas a normas `N-*` (só visíveis em PAD) — não são texto compartilhado, deixadas intactas por serem PAD por natureza.

### Testes
`node test-fluxo-integrado.js`: **43/43**, sem regressão (fluxo PAD intacto). Teste manual via Playwright (Chromium headless): **27/27** cobrindo os 5 critérios de aceite — modo PAR lista as 11 normas LAC (2 optgroups) + hint, papéis PAR e exclusão de `acusado`, 3 blocos de pergunta no roteiro e ausência dos blocos PAD; modo PAD idêntico (53 normas 8.112, `acusado` presente); troca de domínio com dados incompatíveis dispara `confirm()`; checklist PAR ativa os itens corretos incluindo o transversal benefício/nexo; ambos os envelopes de exportação carregam `dominio:"par"` (e omitem quando indefinido).

## Rodada PAR-3 — Fork do Nexo Coger → Nexo PAR (fechada)

Fork (não modo dual): `ferramentas/nexo-par.html` criado como cópia byte-a-byte do `nexo-coger.html` estabilizado e transformado para o domínio PAR (Lei nº 12.846/2013 — LAC). **Nenhuma alteração no catálogo canônico** (`schema_version`/hash8 inalterados) — a rodada é só de UI/lógica do novo arquivo. `nexo-coger.html` permaneceu **byte a byte idêntico** (md5 `c7ee92022bbcedc0ec335002799f99ad` antes e depois; `git diff --stat` vazio). `CATALOGO_COGER` embutido no fork **não foi tocado** (é o catálogo compartilhado; suas `descricao`/`origem_permitida` que citam "nexo-coger" foram deliberadamente preservadas).

### 3.1 — Identidade e dados do processo
`<title>`, `hero__title`, `gate-hero__title`, rodapé (`Nexo PAR v1.0`), cabeçalho de impressão do mapa e subtítulos → **Nexo PAR**. Constantes internas: `FERRAMENTA='nexo-par'` (identidade de exportação/import) e `LS_KEY='nexo-par:draft'` (rascunho separado, não colide com o Nexo Coger no mesmo navegador). `docVazio().processo` nasce com `tipo:'PAR'` e `dominio:'par'`; `migra()` força `dominio='par'` sempre. Exportação (`exportJson`) grava `processo.dominio='par'` no envelope e o nome do arquivo virou `nexo-par-<numero>-<data>.json` (idem `nexo-par-pauta-…`). Tela "Dados do Processo" (gate): tipo **pré-selecionado PAR**, mantido **editável** (bom senso — reaproveita o mesmo `<select>` `TIPOS_PROCESSO` já validado, sem travar o campo; a criticidade P-ENTE e o domínio fixo garantem o rito).

### 3.2 — Cadastro do polo passivo: ente privado
`abrirFormAcusado` **substituído** pelo formulário de ente privado (Razão social obrigatória, CNPJ com validação de formato — 14 dígitos com/sem máscara, sem DV —, Nome fantasia, Endereço, Faturamento bruto opcional). **Representantes**: lista repetível (padrão "Vogal(is)" do gate) com Nome/CPF/Vínculo (select dos 3 papéis PAR do catálogo, com labels reais). **Estruturas societárias** (registro, sem cálculo): Solidariedade (lista CNPJ/razão/vínculo), Sucessão (tipo fusão/incorporação/cisão + descrição + data), Desconsideração art. 14 (checkbox + fundamentação + checkbox "atingido" por representante). **Decisão estrutural de bom senso**: o array interno permanece `doc.acusados[]` e o campo de conduta `acusadoId` (identificadores estáveis) — preserva mapa, vínculo fato-conduta, Nota de Indiciação, selo de oitiva e import de retorno sem reescrever dezenas de call-sites; `a.nome` espelha a razão social (lido por avatares/rótulos). Primeiro ente = padrão de vínculo automático. `migra()` faz backfill dos campos de ente.

### 3.3 — Remoção do elemento subjetivo (remoção real)
Removidos do form de fato: bloco de rádio (dolo direto/eventual, negligência, imprudência, imperícia), campo `elementoSubjetivo`, aviso `⚠` de conflito norma × elemento subjetivo, e a exigência na validação de salvamento. **Pendência P8** (alternatividade dolo/culpa) removida de `computePendencias()`. Comentário de justificativa no código (LAC objetiva, art. 2º). Texto do princípio "alternatividade" no wizard de multiplicidade neutralizado (não cita mais "dolo × culpa").

### 3.4 — Benefício + nexo causal
Dois `textarea` obrigatórios no fato (campos do **fato**, não do enquadramento — descrevem a relação ato-proveito da PJ): "Interesse ou benefício da pessoa jurídica" e "Nexo de causalidade", no lugar conceitual do elemento subjetivo. Nova **P8-PAR** — "Fato com enquadramento LAC sem descrição de benefício/interesse ou nexo causal", **CRÍTICA** (bom senso: substitui a P8 que era crítica; requisito material de imputação). Dispara quando há enquadramento ativo e qualquer um dos dois campos está em branco.

### 3.5 — Seletor de enquadramento: só LAC
`buildCatalogo()` reescrito para montar `doc.catalogoNormas` **apenas** das 11 `NORMA.LAC.*` (`dominio:"par"`, `status:"ativo"`) do `CATALOGO_COGER` — `NORMAS_BASE`/`RELACOES_DECL` (Lei 8.112/LAI) deixaram de ser usados (ficaram como código morto no fonte, **não renderizado**; mantidos para minimizar diff/risco). `GRUPOS` e `grupoDaNorma()` reescritos para 2 optgroups ("Atos de corrupção em geral" / "Licitações e contratos", lidos do campo `grupo` do item) + grupo residual "Criadas pelo usuário". A `nota_aplicacao` (entendimentos SIPRI/CGU) aparece como hint (📌) ao selecionar a norma. Pílula de norma no mapa e no form troca gravidade/pena (inexistentes na LAC) pelo rótulo do grupo. `normaInternaParaCanonica()` ganhou passagem direta para ids já canônicos (`NORMA.*`), preservando a exportação de pauta. Selects de papel (prova testemunhal, revisão de pauta) — filtro por `status:'ativo'` já exclui naturalmente os papéis; os 3 vínculos PAR são expostos no cadastro de ente.

### 3.6 — Nota de Indiciação do PAR
`renderIndiciacao` adaptado: título "**Nota de Indiciação**", cabeçalho "Processo Administrativo de Responsabilização (PAR) nº … / Lei nº 12.846/2013", linha "Pessoa jurídica: razão social, CNPJ" (no lugar de "Servidor: nome, cargo, matrícula"). Qualificação: Razão social/CNPJ/Nome fantasia/Endereço/Representante legal. Seção "Da conduta lesiva imputada ao ente privado" (com benefício/interesse e nexo causal por fato). Enquadramento sem "a título de <elemento subjetivo>". **4 textos complementares fixos** adicionados: (1) faculdade de apresentar informações/provas sobre parâmetros de cálculo da multa e faturamento bruto; (2) solicitação de documentos para o inciso IV do art. 22 do Decreto nº 11.129/2022; (3) prazo de 30 dias para defesa + evidências de programa de integridade (Portaria CGU nº 909/2025); (4) resolução negociada (Termo de Compromisso / Acordo de Leniência). Encerramento com intimação de 30 dias (art. 17, IN CGU nº 13/2019), sem art. 161 da Lei 8.112. `validaMinuta` exige razão social + representante legal (não mais cargo). Labels do fluxo ("Gerar Nota de Indiciação", "Notas de Indiciação geradas") renomeados.

### 3.7 — Catálogo de pendências revisado
Mantidas com texto adaptado: P1, P2, P3, P5, P4, P6a, P7; **P6b** reescrita para "Ente privado não intimado da produção desta prova". **Removida**: P8. **Novas**: P8-PAR (3.4) e **P-ENTE** — "Processo sem ente privado cadastrado" (alvo processo) ou "Ente privado sem representante legal cadastrado" (alvo ente), **CRÍTICA**, bloqueia geração. Painel de pendências e `focarNo()` ganharam tratamento do `alvoTipo:'processo'`. **P6c** (antecedência de interrogatório, art. 41 Lei 9.784) permanece no código mas fica dormente (o ente não tem campos de interrogatório) — sem UI PAD. Checklist de encerramento adaptado: C1 → "Ente com representante legal" (sem P-ENTE), C2 → "Benefício/nexo descritos" (sem P8-PAR), C3 → "Zero críticas (P1, P2, P5, P8-PAR, P-ENTE)". **Painel de Prazos**: bloco de defesa passou a "Intimação da Nota de Indiciação e defesa escrita — 30 dias (art. 17, IN CGU nº 13/2019)", sem a lógica pessoal/edital 10/15 da Lei 8.112. Prazo de **conclusão do processo**: **não fornecido pela spec** para o PAR → mantido o mesmo cálculo do PAD (instauração + `prazoConclusaoDias`), com comentário no código declarando explicitamente a ausência de fonte normativa (não se inventou prazo).

### 3.8 — Preparação para Multa_PAR (sem UI)
Comentário-âncora `// FUTURO: exportação Multa_PAR` em `exportJson()`, documentando que o estado já reúne de forma coesa e diretamente exportável o ente (com `faturamentoBruto`), os enquadramentos LAC confirmados por fato (+ benefício/nexo) e as referências de prova. Campo `faturamentoBruto` adicionado ao ente. **Nenhum botão/tela/contrato novo.**

### 3.9 — Não tocados
Mapa fato-prova-norma (mecânica/SVG), import de provas do Veritas, import de retorno do Oitiva, exportação de pauta, selo 🎙 de oitiva, design system COGER — preservados. **Decisão de escopo (bom senso)**: como PAD-exclusivos e não citados em 3.1–3.8, foram retirados/ocultados da UI do fork para não exibir Lei 8.112: item de menu "Gerar termo de intimação" (`gerarIntimacaoFlow`, dormente no código) removido; tag de prescrição do cabeçalho (art. 142, Lei 8.112) ocultada (`display:none` — a prescrição do PAR é outra: Lei 12.846, art. 25, fora do escopo desta rodada). Hints do gate/edição do processo e do form de "nova norma residual" tiveram menções à Lei 8.112 neutralizadas.

### Melhorias genéricas descobertas (aplicáveis futuramente ao Nexo Coger)
Anotadas, **não aplicadas** ao `nexo-coger.html` (disciplina de fork):
1. **`normaInternaParaCanonica()` — passagem direta de ids já canônicos**: no Nexo Coger a função só converte o formato interno `N-…`; se algum dia o catálogo do Nexo passar a conter ids `NORMA.*` diretos, o mesmo guard `if(id.startsWith('NORMA.'))` seria útil lá.
2. **Bug de inicialização `compromissada:true` fixo** em prova nova de "declaração de informante" (documentado na auditoria §3/§5 do `audit-nexo-coger.md`) — existe idêntico no Nexo Coger; não corrigido aqui.
3. **`grupoDaNorma()` por dado do item, não por prefixo de id**: o fork passou a ler o grupo do próprio item (mais robusto que deduzir por `N-116-`/`N-117-`); o Nexo Coger ainda deduz por prefixo — refino aproveitável se o catálogo do Nexo ganhar um campo `grupo`.

### Testes
- `node test-fluxo-integrado.js` — **43/43**, exit 0 (roda contra veritas/nexo-coger/oitiva-360; nenhum regrediu).
- `nexo-coger.html` — **byte a byte idêntico** (md5 `c7ee92022bbcedc0ec335002799f99ad` antes/depois; `git diff --stat` vazio).
- `node --check` no `<script>` do `nexo-par.html` — sem erro de sintaxe.
- **Playwright (Chromium, `nexo-par.html` real)** — 37/38 asserções ok (a única falha foi um artefato do próprio teste: o `<select>` de vínculo só existe após adicionar um representante; `vinculosEnteOpts()` confirmado correto por chamada direta). Cobertos os 6 pontos do critério de aceite: (1) gate com PAR pré-selecionado; (2) form de ente com representante e vínculos do catálogo, sem matrícula/cargo; (3) fato com enquadramento LAC + benefício/nexo; (4) prova vinculada citada; (5) Nota de Indiciação com razão social/CNPJ, representante legal, conduta lesiva, prova, art. 5º I LAC, benefício/nexo e os 4 textos complementares (multa/faturamento, art. 22 IV do Decreto 11.129/2022, 30 dias + integridade Portaria 909/2025, Compromisso/Leniência); (6) ausência de "Nexo Coger", Lei 8.112, elemento subjetivo e art. 161 no HTML da Nota; e o gate de bloqueio (P8-PAR e P-ENTE impedem a geração, P8 confirmada inexistente). Export confirmado: `ferramenta:"nexo-par"`, `processo.dominio:"par"`, arquivo `nexo-par-<numero>-<data>.json`.

### Correção pontual pós-PAR-2 — `origem_permitida` das categorias de prova PAR

A implementação da PAR-2 (2.2, abaixo) expõe `PROVA.PROGRAMA_INTEGRIDADE` e `PROVA.INFORMACOES_COAF` como categorias selecionáveis no Veritas — mas o agente que executou a PAR-2 encontrou e sinalizou (sem corrigir, por estar fora do escopo da sua tarefa) que o `origem_permitida` desses dois itens no catálogo, criado na Rodada PAR-1, listava só `["nexo-coger"]`, sem `"veritas"`. Isso contradizia o comportamento que a própria PAR-2 já implementa. Corrigido para `["nexo-coger","veritas"]` nos dois itens, `CATALOGO_COGER` reembutido nos três HTMLs (hash8 `958dfd97` → `0955151a`) e reconfirmado idêntico nos três arquivos e no JSON fonte. `test-fluxo-integrado.js`: 43/43, sem regressão. `schema_version` não muda (correção de dado, não mudança estrutural).

## Rodada PAR-2 — Ajuste do Veritas (modo dual PAD/PAR) (fechada)

Segunda rodada da trilha PAR, depende da PAR-1 concluída (catálogo com `dominio`, `TIPOS_PROCESSO` com PAR/IPS). Princípio explícito da rodada, respeitado à risca: o Veritas é quase agnóstico de domínio (cadeia de custódia, hash, proveniência, lacre e linha do tempo funcionam identicamente para PAD e PAR) — só vocabulário e propagação de domínio, **nenhuma mudança na lógica de custódia**. Nenhum arquivo além de `ferramentas/veritas.html` foi tocado.

### PAR-2.1 — Campo "Tipo de processo" nos Dados do processo

- `TIPOS_PROCESSO` (mesmo array `[valor, rótulo]`, mesmo agrupamento Investigativos/Acusatórios, com PAR e IPS já incluídos pela PAR-1) foi **copiado** de `nexo-coger.html` para `veritas.html` — não existia lá antes desta rodada. Novo select "Tipo de processo" (com hint "opcional") na seção "Dados do processo" da tela de Processo, ao lado dos campos já existentes (Nº do processo, Portaria, Seção/unidade responsável). Campo opcional: não bloqueia `_validarStep` nem qualquer outro fluxo; dossiês sem esse campo continuam funcionando exatamente como hoje.
- Novo campo `processo.tipoProcesso` (default `""`) em `novoDossie()`, migrado em `migrarDossie()` para dossiês antigos (`if (d.processo.tipoProcesso === undefined) d.processo.tipoProcesso = ""`, mesmo padrão já usado por `secaoResponsavel`).
- Nova função pura `dominioDoProcesso(tipoProcesso)`: `"PAR"` → `"par"`; `TIPOS_QUE_LEVAM_A_PAD` (`PAD`, `investigacao_preliminar`, `sindicancia_investigativa`, `sindicancia_patrimonial`, `sindicancia_acusatoria`) → `"pad"` — mesma lógica implícita de "tipos que levam a PAD" já usada no Nexo Coger (o Nexo trata IP/SINVE/SINPA como investigativos que alimentam a mesma matriz fato-prova-norma do PAD, e SINAC/PAD como os acusatórios correspondentes); qualquer outro valor (incluindo tipo não informado) devolve `undefined`.
- **Decisão sobre IPS (Investigação Preliminar Sumária):** deliberadamente **fora** de `TIPOS_QUE_LEVAM_A_PAD`, então `dominioDoProcesso('investigacao_preliminar_sumaria')` devolve `undefined` — o campo `dominio` fica **ausente**, não `"pad"`. A spec desta rodada só lista IP/SINVE/SINPA/SINAC (não IPS) como "tipos investigativos correlatos" ao PAD, e o texto da spec já reconhece que IPS é ambíguo. Presumir `"pad"` para IPS esconderia as categorias de prova PAR (2.2) e o campo `dominio` na exportação (2.3) exatamente do processo que mais precisa ficar neutro até a comissão decidir o rito — na prática, um processo de IPS que vier a virar PAR perderia sem necessidade a sinalização de domínio se o padrão fosse "pad por omissão". A alternativa descartada (`dominio: "pad"` fixo para IPS) foi considerada e rejeitada por esse motivo; a ausência do campo é o comportamento mais conservador e reversível (a comissão pode reclassificar o tipo de processo a qualquer momento, sem precisar desfazer nenhuma marcação anterior).
- Retrocompatibilidade testada explicitamente (Playwright): dossiê `.json` construído manualmente sem `tipoProcesso`/`dominio` (simulando exportação pré-PAR-2) importa sem erro, mostra o item já existente normalmente e o select "Tipo de processo" aparece vazio.

### PAR-2.2 — Categorias de prova sensíveis a domínio

- Nova função pura `categoriasDisponiveis(dominio)`: `dominio !== "par"` (ausente, `"pad"`, ou qualquer outro) → devolve o objeto `CATEGORIAS` estático, sem cópia nem alteração — comportamento de hoje, byte a byte; `dominio === "par"` → devolve `Object.assign({}, CATEGORIAS, CATEGORIAS_ADICIONAIS_PAR)`, uma cópia nova a cada chamada (o array/objeto `CATEGORIAS` original nunca é mutado). Usada nos dois selects de categoria que existiam (Etapa 1 do wizard de criação e o campo "Categoria" editável na tela de detalhe do item) — as duas passaram a montar as opções dinamicamente a partir do `dominio` do processo atual (`dominioDoProcesso(DB.dossie.processo.tipoProcesso)`), em vez de `Object.keys(CATEGORIAS)` fixo.
- `CATEGORIAS_ADICIONAIS_PAR = { programa_integridade: "Programa de integridade", informacoes_coaf: "Informações do COAF" }` — rótulos reproduzidos literalmente do `catalogo-canonico.json` (`PROVA.PROGRAMA_INTEGRIDADE`, `PROVA.INFORMACOES_COAF`). `PROVA.EMPRESTADA` **não foi adicionada**: confirmado por leitura de `CATEGORIAS` que ela não existe como categoria própria selecionável no Veritas hoje (o Veritas não tem um conceito de "prova emprestada" na Etapa 1 — isso é vocabulário do Nexo Coger), então não havia o que estender, exatamente como a spec previa ("se implementada").
- **Discrepância encontrada e não corrigida nesta rodada** (fora de escopo, documentada para rodada futura de consistência do catálogo): `catalogo-canonico.json` define `origem_permitida: ["nexo-coger"]` para os dois tipos de prova PAR (`PROVA.PROGRAMA_INTEGRIDADE`, `PROVA.INFORMACOES_COAF"`), sem incluir `"veritas"` — mas a spec desta rodada instrui explicitamente expor essas duas categorias no Veritas quando `dominio: "par"`. Segui a instrução explícita da spec (aprovada) em vez do campo `origem_permitida` do catálogo (que não previu esse uso quando foi escrito na PAR-1) — nenhuma validação automática lê `origem_permitida` hoje em nenhuma das três ferramentas, então não há quebra de comportamento, só uma inconsistência de metadado a ser resolvida quando o catálogo for revisado.
- `CATEGORIAS_TODAS = Object.assign({}, CATEGORIAS, CATEGORIAS_ADICIONAIS_PAR)`: lookup de rótulo (não de opções selecionáveis) usado na listagem de itens e no relatório, para que um item já salvo com categoria PAR continue exibindo o rótulo certo mesmo que o processo seja reaberto sem `tipoProcesso` definido.
- "Termo de oitiva" mantém seu comportamento especial (atribuída só via `App.importarTermoOitiva`, não oferecida como opção de criação manual no fluxo normal) nos dois domínios — nenhuma mudança nesse ponto; ela continua presente como `<option>` no HTML do select em ambos os casos (comportamento herdado, não alterado por esta rodada).
- Testado via Playwright: sem tipo de processo definido e com tipo `PAD`, as duas categorias PAR não aparecem no select da Etapa 1; com tipo `PAR`, ambas aparecem, junto com todas as categorias originais (incluindo "Termo de oitiva", inalterada).

### PAR-2.3 — Propagação do domínio na exportação

- `persistir()` (chamada antes de toda exportação e a cada alteração salva) agora sincroniza `DB.dossie.processo.dominio` com `dominioDoProcesso(DB.dossie.processo.tipoProcesso)` a cada chamada — `dominio` recebe `"pad"`/`"par"` quando derivável, ou é **removido do objeto** (`delete`, não `= null`) quando não derivável. Decisão de arquitetura: em vez de deixar `dominio` como um valor puramente computado só em memória (o que exigiria `exportarDossie` reconstruir o objeto exportado campo a campo, arriscando divergir do `hashDoDossie`, calculado sobre o mesmo `DB.dossie` que é serializado), o campo é escrito no próprio objeto que `persistir()` já hasheia e serializa — assim o hash cobre exatamente o que sai no arquivo, e o campo nunca fica dessincronizado do `tipoProcesso` (recalculado a cada persistência, nunca editado à mão), no mesmo espírito de "computado, não digitado" já usado pelos badges de status da Rodada 8.
- `App.exportarDossie()` não precisou de nenhuma mudança de código — como já serializa `DB.dossie` inteiro após `persistir()`, o campo `processo.dominio` passa a vir de graça quando presente, e simplesmente não existe no objeto quando ausente (confirmado inspecionando o JSON bruto exportado — a string `"dominio"` não aparece no arquivo quando o tipo de processo não foi informado).
- `construirContratoProvasNexo()` (núcleo puro do contrato Veritas → Nexo Coger, `App.exportarProvasParaNexo`) ganhou `var dominio = dossie.processo.dominio || dominioDoProcesso(dossie.processo.tipoProcesso);` e só atribui `contrato.dominio = dominio` quando o valor existe — mesma regra "ausente, não `null` inventado" do dossiê completo. Testado nos dois sentidos: `dominio: "par"` presente no envelope quando o processo é PAR; chave `dominio` completamente ausente (`Object.prototype.hasOwnProperty` retorna `false`, string `"dominio"` ausente do JSON bruto) quando o tipo de processo não foi definido.
- **Nenhuma validação de importação por domínio foi implementada** — nem no Veritas (que não faz nenhuma checagem de `dominio` ao importar dossiê ou termo de oitiva), nem em nenhum outro arquivo (`nexo-coger.html`, `oitiva-360.html` não foram tocados nesta rodada). Só a emissão do campo, exatamente como a spec pediu, reservando a validação cruzada para a Rodada PAR-5.
- `dominioDoProcesso`, `categoriasDisponiveis`, `TIPOS_PROCESSO`, `CATEGORIAS`, `CATEGORIAS_ADICIONAIS_PAR` e `migrarDossie` foram adicionados a `window.VeritasPuro` (mesmo padrão de núcleos puros estabelecido na Rodada 7), para serem exercitados diretamente via Node em testes automatizados, sem depender de browser.

### PAR-2.4 — Ajustes de texto neutro

Busca case-insensitive por "servidor" no arquivo inteiro encontrou só **3 ocorrências**, todas dentro do `CATALOGO_COGER` embutido (dados do catálogo canônico, não texto de interface do Veritas em si):
- `PAPEL.ACUSADO.descricao` ("Servidor submetido a apuração disciplinar...") — descreve literalmente o papel de acusado num PAD, `dominio: "pad"` desde a PAR-1; o PAR já tem seu próprio papel equivalente (`PAPEL.ENTE_PRIVADO`, com descrição própria, não tocado). **Mantido como está** — reescrever a descrição de um papel `dominio: "pad"` para linguagem neutra apagaria a distinção que a própria PAR-1 criou entre os dois domínios.
- Duas normas da Lei nº 8.112/1990 (`NORMA.L8112.ART117_XVII` — "Cometer a outro servidor atribuições estranhas ao cargo..." — e `NORMA.L8112.ART322` — "Ofensa física, em serviço, a servidor ou particular...") — texto legal reproduzido literalmente do dispositivo, `dominio: "pad"`. **Mantidas como estão** — são o texto de um artigo de lei que só se aplica a servidor por natureza jurídica do próprio dispositivo; "neutralizar" a redação seria parafrasear a lei incorretamente, o que a PAR-1 já havia decidido não fazer para nenhuma norma do catálogo.

Fora do catálogo embutido, duas ocorrências de texto de interface presumiam escopo só-PAD e foram ajustadas para incluir PAR:
- `CATALOGO.disclaimerLongo` (exibido na tela inicial e no rodapé do relatório impresso): "...investigação, parecer técnico e comissões de **PAD/sindicância**." → "...investigação, parecer técnico e comissões de **PAD/sindicância/PAR**."
- Parágrafo descritivo fixo da tela de Processo (`viewProcesso`, logo abaixo do cabeçalho "Dados do processo"): mesmo trecho "comissões de PAD/sindicância." → "comissões de PAD/sindicância/PAR.", mesma razão.

**Explicitamente NÃO tocado, por instrução direta da spec:** `CATALOGO.fundamentacao` (a fundamentação doutrinária da cadeia de custódia por analogia ao CPP) — vale para os dois domínios tal como já estava escrita e permanece byte a byte idêntica. Também não tocados: qualquer rótulo de campo do wizard (Título/descrição, Proveniência, Sigilo etc. já eram neutros), os textos dos 6 tipos de evento e das dicas contextuais (`CATALOGO.dicas`) — nenhuma delas menciona "servidor" nem qualquer termo PAD-específico, revisão confirmou que já eram neutras.

### Teste de regressão

`node test-fluxo-integrado.js` — **43/43 verificações passaram, exit code 0**, mesmo placar de antes da mudança (conferido antes de editar). Nenhum teste do domínio PAD foi afetado.

### Teste manual (Playwright, `ferramentas/veritas.html` real, Chromium)

20 verificações, todas ok, cobrindo os 3 critérios de aceite da spec:
1. **Retrocompatibilidade:** dossiê `.json` construído manualmente sem `tipoProcesso`/`dominio` (simulando um dossiê exportado antes desta rodada) importado sem erro — tela de Processo carrega, o único item pré-existente aparece normalmente, e o select "Tipo de processo" aparece vazio (não quebra, não força um valor).
2. **Categorias por domínio:** sem tipo de processo e com tipo `PAD`, "Programa de integridade" e "Informações do COAF" não aparecem no select "Categoria" da Etapa 1; com tipo `PAR`, ambas aparecem, junto com todas as categorias originais (incluindo "Termo de oitiva", intacta).
3. **Exportação:** com tipo `PAR`, `Exportar .json` gera `processo.dominio === "par"` e `Exportar provas → Nexo Coger` gera `dominio === "par"` no envelope (inspecionado no JSON bruto salvo em disco, não só na tela); com tipo de processo revertido para vazio na mesma sessão, os dois exports não têm a chave `dominio` (confirmado por `hasOwnProperty` e por ausência da string `"dominio"` no arquivo bruto — não veio como `null`).

## Rodada PAR-1 — Extensão do catálogo para o domínio PAR (fechada)

Primeira rodada da trilha PAR (responsabilização de entes privados, Lei nº 12.846/2013 — LAC), bloqueando as Rodadas PAR-2 a PAR-6. Escopo estritamente de dados: só o catálogo cresce; nenhuma interface das três ferramentas passou a expor os itens novos nesta rodada (exceção única e explícita: PAR/IPS em `TIPOS_PROCESSO`, ver PAR-1.3).

### PAR-1.1 — Campo `dominio` em todos os itens existentes

Todo item de `papeis_pessoa[]`, `tipos_prova[]` e `normas[]` ganhou o campo `dominio` (`"pad"` | `"par"` | `"comum"`). Nenhum item existente mudou de `id` ou de qualquer outro campo — validado programaticamente (script Python comparando, item a item por `id`, todos os campos exceto `dominio` entre o JSON original salvo antes da edição e o JSON final; zero divergências).

- **Normas:** as 45 da Lei nº 8.112/1990 e as 7 do art. 32 da LAI (Lei nº 12.527/2011) → `"pad"`. A spec já indicava explicitamente a LAI como `"pad"` (é usada apenas no contexto de apuração PAD, conforme a auditoria original da Rodada 1 — o Veritas nem chega a referenciá-la); confirmado por leitura de cada item `NORMA.LAI.*` antes da migração, nenhum sinal de uso fora do contexto disciplinar.
- **Papéis de pessoa:** `PAPEL.ACUSADO` → `"pad"` (é o servidor investigado; no PAR o polo passivo é o ente privado, um conceito à parte — `PAPEL.ENTE_PRIVADO`, novo). `PAPEL.VITIMA`, `PAPEL.TESTEMUNHA`, `PAPEL.DECLARANTE_INFORMANTE`, `PAPEL.PESSOA_SITUACAO_INDEFINIDA` → `"comum"`, exatamente como a spec instruiu.
- **Tipos de prova (decisão de bom senso — não estavam listados item a item na spec):** os 8 tipos nativos do Nexo Coger (`PROVA.DOCUMENTAL`, `PROVA.PERICIAL`, `PROVA.TESTEMUNHAL`, `PROVA.DECLARACAO_INFORMANTE`, `PROVA.INTERROGATORIO`, `PROVA.DILIGENCIA`, `PROVA.EMPRESTADA`, `PROVA.INDICIARIA`) e as 9 subcategorias de evidência do Veritas (`PROVA.PRINT_SISTEMA`, `PROVA.DOCUMENTO_FINANCEIRO`, `PROVA.COMUNICACAO`, `PROVA.FOTO_VIDEO`, `PROVA.OFICIO`, `PROVA.DECISAO_JUDICIAL`, `PROVA.DOCUMENTO_FISICO`, `PROVA.DISPOSITIVO_FISICO`, `PROVA.OUTRO`) foram classificados `"comum"`: são vocabulário de tipo de mídia/meio de prova (um documento, uma perícia, uma comunicação eletrônica, um depoimento) e nada neles é exclusivo de um rito — tanto um PAD quanto um PAR podem ter prova documental, pericial, testemunhal ou uma comunicação eletrônica como evidência. `PROVA.TERMO_OITIVA` (Rodada 5) também foi classificada `"comum"` pelo mesmo raciocínio: é o veículo estruturado de pergunta-resposta de uma oitiva, e nada na Lei nº 12.846/2013 restringe a oitiva de preposto ou sócio-administrador a um formato diferente do já usado para testemunha/acusado no PAD.

### PAR-1.2 — Itens novos

- **11 normas `NORMA.LAC.*`** (art. 5º da Lei nº 12.846/2013), com `descricao` reproduzindo o texto legal do inciso tal como fornecido pela spec (sem paráfrase) e `nota_aplicacao` com o entendimento da CGU — grupo `"Atos de corrupção em geral"` (incisos I, II, III, V) e `"Licitações e contratos"` (inciso IV, alíneas a–g), exatamente a divisão doutrinária do manual CGU indicada na spec.
- **4 papéis PAR:** `PAPEL.ENTE_PRIVADO`, `PAPEL.REPRESENTANTE_LEGAL`, `PAPEL.PREPOSTO`, `PAPEL.SOCIO_ADMINISTRADOR`, todos `dominio:"par"`.
- **2 tipos de prova PAR novos:** `PROVA.PROGRAMA_INTEGRIDADE`, `PROVA.INFORMACOES_COAF`. `PROVA.EMPRESTADA` **não foi duplicada** — já existia desde a Rodada 1 (migrada do Nexo Coger); só recebeu `dominio:"comum"`, conforme a spec ("prova produzida em outro processo, transportada com contraditório" já era exatamente a definição existente).
- **Contagem final:** 92 itens no catálogo (eram 74 na Rodada 1), 53 `"pad"`, 22 `"comum"`, 17 `"par"`.

### PAR-1.3 — `TIPOS_PROCESSO` do `nexo-coger.html`

Único ponto de UI tocado nesta rodada, por instrução explícita da spec (correção de lacuna preexistente, não feature nova do domínio PAR): adicionado `investigacao_preliminar_sumaria` ("Investigação Preliminar Sumária (IPS)") ao grupo Investigativos e `PAR` ("Processo Administrativo de Responsabilização (PAR)") ao grupo Acusatórios, em `TIPOS_PROCESSO`, `TIPO_SIGLA` e `TIPOS_INVESTIGATIVOS` (IPS somado ao `Set` de tipos investigativos, junto de IP/SINVE/SINPA, para preservar a lógica existente de `mostraRito` que já depende desse `Set`).

### PAR-1.4 — Re-sincronização de `CATALOGO_COGER`

Reembutido nos três `ferramentas/*.html` a partir do `catalogo-canonico.json` atualizado, comentário de cabeçalho atualizado (`schema_version: 1.2.0`, hash8 `958dfd97`). Script Python extraiu `CATALOGO_COGER` de cada um dos três arquivos via regex e comparou (`==` estrutural, via `json.loads`) contra o JSON fonte e entre si: **os quatro batem exatamente**. Verificação adicional: `node -c` (via `new Function()`) em cada `<script>` embutido dos três HTMLs, sem erro de sintaxe após a substituição.

### Teste de regressão

`node test-fluxo-integrado.js` — **43/43 verificações passaram, exit code 0** (mesmo placar de antes da mudança; conferido a contagem antes de editar, já era 43/43 desde a Rodada 7/8). Nenhum teste do domínio PAD foi afetado pela extensão. Teste adicional descartável (script Python, não versionado) confirmou: todo item tem `dominio` válido (`pad`/`par`/`comum`); as 11 normas LAC presentes com os IDs exatos da spec; os 4 papéis PAR e os 2 tipos de prova PAR presentes; `PROVA.EMPRESTADA` existe uma única vez com `dominio:"comum"`; os três HTMLs e o JSON fonte são estruturalmente idênticos.

## Rodada 8 — Sinalização visual de pendências (fechada)

### 8.1 — Diagnóstico

Confirmado: as três ferramentas já usam exclusivamente exportação/importação de JSON local (`exportJson`/`importJson` no Nexo, `App.exportarDossie`/`App.importarArquivo` no Veritas, botões de exportar/importar processo no Oitiva) — nenhuma usa `localStorage` como fonte de verdade entre sessões de trabalho compartilhadas (`localStorage` só existe como rascunho automático dentro do mesmo navegador). A Rodada 8 não introduziu nenhum mecanismo novo — os campos de status desta rodada viajam dentro do mesmo JSON já exportado/importado.

### Decisão de arquitetura: status computado vs. persistido

A introdução do escopo já avisa: "a detecção é sempre local, e recalculada a partir do estado atualmente carregado". Segui isso à risca — só usei um campo `status` **persistido e mutável** onde o estado realmente não é derivável de outro dado (é uma decisão humana, tipo "eu já li isso"). Onde o status já podia ser deduzido de uma relação que já existe no JSON, optei por **computar ao vivo a cada render**, para eliminar qualquer risco de desincronização entre o campo e a relação real:

| Ferramenta | Entidade | Mecanismo |
|---|---|---|
| Nexo Coger | Prova importada do Veritas (`pendente`/`vinculada`) | **Computado**: pendente se `p.origemVeritas` existe e nenhum `f.provaIds` contém `p.id`; vinculada caso contrário. Mesma lógica já usada pela pendência P3 ("prova órfã"), sem campo novo — a vinculação em si já é a ação natural (checkbox no formulário do fato, Rodada existente). |
| Oitiva 360 | Pauta importada do Nexo Coger (`pendente`/`em_andamento`/`concluida`) | **Computado**: concluída se `statusChecklist` é `abordado`/`sem_resposta`; em_andamento se algum depoente tem o `fatoId` em `pautaSelecionada`; pendente caso contrário. |
| Nexo Coger | Retorno de prova de oitiva (`pendente_revisao`/`revisado`) | **Persistido**: `provasContexto[].status`, porque "revisado" é puramente uma confirmação humana — nenhum outro dado do JSON indica isso. Transição pela ação natural de abrir o cadastro do acusado, conferir o item e salvar (não é um botão isolado). |
| Veritas (extensão além da tabela da spec) | Termo de oitiva importado (`pendente_revisao`/`revisado`) | **Persistido**: `item.termoOitiva.status`, mesmo raciocínio do retorno de oitiva. A tabela do escopo (8.2) lista só 3 entidades, mas o texto geral diz "cada entidade que chega por importação (Rodadas 3-6) ganha um campo de status" — e o Veritas recebe o termo (Rodada 5), então essa 4ª entidade foi coberta para os três badges baterem com o entregável 3 ("badge... nas três ferramentas"). Transição pela ação natural de abrir o item e clicar "Marcar como revisado" (mostrado só quando o item tem `termoOitiva`, junto com o próprio texto do termo — antes desta rodada não havia nenhuma tela mostrando esse conteúdo).

### Badges

Os três seguem a paleta navy/gold já usada pelo design system COGER: fundo navy do próprio cabeçalho de cada ferramenta (hero do Nexo/Oitiva, topbar do Veritas) com o badge em dourado sólido (`--rfb-gold-500`), texto navy escuro para contraste — nenhuma cor nova introduzida. Cada um só aparece quando a contagem é maior que zero (`display:none` em zero, evita ruído visual permanente). Clicar no badge do Nexo abre um modal listando os itens pendentes com atalho para abrir cada um; no Oitiva rola até o resumo da pauta; no Veritas abre diretamente o primeiro termo pendente.

### Teste (Playwright, os três HTMLs reais)

- Nexo: importar uma prova do Veritas sem vincular mantém o badge em 1; vincular a um fato reduz para 0 **sem recarregar a página**; simular salvar+recarregar o JSON com uma prova ainda pendente preserva o status (não some, não vira "vinculada" sozinho).
- Nexo: um retorno de oitiva pendente conta no badge; abrir o formulário do acusado, marcar "Revisado" e salvar zera o badge e persiste `status:"revisado"` no objeto.
- Confirmado que os elementos `#badgePautaPendente` (Oitiva) e `#badgeTermoPendente` (Veritas) existem no cabeçalho de cada ferramenta.
- Reexecutado o teste de ponta a ponta da Rodada 6 (Playwright) e o `test-fluxo-integrado.js` da Rodada 7 (43/43) depois de todas as mudanças — nenhuma regressão.
- Nenhuma das três ferramentas ganhou código de rede/`fetch`/leitura de arquivo de outra ferramenta — os badges só reagem a mudanças no próprio estado já carregado, conforme 8.4.

## Rodada 7 — Teste de fluxo integrado ponta a ponta (fechada)

### 7.1 — Diagnóstico de separabilidade

- **`nexo-coger.html`** não tem IIFE — tudo (funções e variáveis de topo) já é escopo de script. A maior parte da lógica de contrato já era pura (`analisarLacunasPauta`, `normaInternaParaCanonica`, `retornoJaExiste`); o que faltava era **extrair** a construção de envelopes/objetos de dentro de funções que também baixavam arquivo/re-renderizavam (`gerarPautaPorDepoente`, `aplicarImportacaoVeritas`, `aplicarImportacaoRetornoOitiva`). Como `doc`/`CATALOGO_COGER`/`PROVA_ID_PARA_TIPO_NEXO` são `let`/`const` de topo de script, não viram propriedades do objeto global mesmo fora de IIFE (só `function` declarada vira) — foram criados accessors mínimos (`getDoc`/`setDoc`/`getCatalogoCoger`/`tipoNexoParaProvaId`) só para isso.
- **`veritas.html`** e **`oitiva-360.html`** são IIFEs — só o que é explicitamente atribuído a `window` é visível de fora. Cada um ganhou um namespace novo (`window.VeritasPuro`, `window.OitivaPuro`) reunindo as funções centrais de cada contrato, todas reescritas/extraídas para receber dados e devolver dados (inclusive as assíncronas de hash), sem tocar `document`/`localStorage`. As funções de UI (`App.exportarProvasParaNexo`, `App.importarTermoOitiva`, `exportarTermoParaVeritas`, `exportarRetornoContextoAcusado`, `aplicarImportacaoPauta`) viraram wrappers finos em torno dessas — **mesmo comportamento de interface, lógica testável isolada**. Confirmado sem regressão reexecutando o teste Playwright da Rodada 6 (browser real) depois do refactor: passou integralmente.
- Duas lacunas de idempotência foram descobertas só ao planejar os testes de 7.4 e corrigidas nesta rodada (iam além do que as Rodadas 3 e 5 tinham exigido originalmente): a importação de prova do Veritas no Nexo (Rodada 3) não tinha nenhum dedup — reimportar o mesmo `id_prova` criava uma segunda prova; e a importação de termo no Veritas (Rodada 5) também não tinha dedup — reimportar o mesmo `hash_origem` gerava um novo `id_prova` a cada vez. Ambas ganharam checagem de duplicidade com mensagem clara (`provaVeritasJaImportada`/`avaliarImportacaoTermo` com `motivo:"duplicado"`), no mesmo padrão já usado pela Rodada 6 para o retorno de contexto.

### 7.2/7.3 — Fixture e script de teste

- `fixtures/pad-ficticio-001.json`: 1 acusado, 3 fatos (1 com prova inicial do Veritas, 2 gerando lacuna — o teste usa a lacuna de `F2`, tipo `sem_prova`), depoente testemunha com uma `respostaPadrao` fictícia aplicada a todo o roteiro gerado, sem acusado alternativo (exercita o vínculo automático da Rodada 6).
- `test-fluxo-integrado.js`: carrega os três `ferramentas/*.html` **reais** via `vm.createContext`/`vm.runInContext` do Node, com um stub mínimo de `document`/`localStorage`/`URL`/`Blob`/`crypto` só para os scripts terminarem de carregar sem lançar (nenhuma asserção depende do stub — toda a lógica exercitada é pura). Roda as 7 etapas do fluxo (Veritas exporta prova → Nexo importa → Nexo gera pauta → Oitiva importa pauta e monta roteiro → Oitiva responde e gera termo com hash → Veritas importa termo e gera `id_prova` → Oitiva exporta retorno e Nexo importa vinculando ao acusado padrão), depois repete os passos 2, 4, 6 e 7 com o mesmo payload (7.4) e testa hash adulterado + `catalogo_schema_version` divergente (7.5). Relatório por grupo no console, `console.assert`-style, sem framework.

### Resultado

`node test-fluxo-integrado.js` — **43/43 verificações passaram**, exit code 0: as 7 etapas, as 4 reimportações (nenhuma duplicidade, todas sinalizadas explicitamente — reimportar pauta agora dispara um aviso, reimportar prova/termo/retorno são recusados com motivo claro) e os 2 testes de falha controlada (hash divergente rejeitado; `catalogo_schema_version` divergente sinalizada sem bloquear quando o hash confere).

## Rodada 6 — Contrato Oitiva 360 → Nexo Coger: retorno da prova / contexto do acusado (fechada)

### 6.2 — Diagnóstico

Confirmado por busca: **nenhuma estrutura de "contexto do acusado" existia** no `nexo-coger.html` — criada do zero (`acusado.provasContexto[]`).

Achado mais importante da rodada: o Oitiva 360 **já tinha** um mecanismo de "prova de retorno" para o Nexo (botão "Exportar prova(s) para o Nexo" / `abrirDialogoExportarProva`, consumido por `aplicarImportacaoProva` no Nexo) — mas esse mecanismo empurra a prova para `doc.provas[]` e `f.provaIds`, que **alimentam diretamente** `computePendencias()` (P1 "sem prova", P7 "sustentação frágil") e, por consequência, a força probatória e o caminho até a indiciação. Isso conflita frontalmente com o critério 6.4 desta rodada ("nenhum caminho de código que dispare indiciação automaticamente" / "sem qualquer campo que participe do cálculo/fluxo de indiciação"). Conclusão: o mecanismo existente serve a um propósito legítimo diferente (prova evidenciária formal) e **não foi reaproveitado nem alterado** — o contrato desta rodada é novo, paralelo, e deliberadamente isolado de `doc.provas`/`doc.fatos`, para que nenhuma função de pendência ou indiciação possa lê-lo, nem por acidente.

### Contrato implementado

`oitiva-360.html`:
- O bloco já existente "Pauta do Nexo — itens abordados nesta sessão" (Etapa 4) ganhou, por item abordado, um campo "Resumo da resposta" e um campo opcional "Acusado alternativo" — vazio (o caso comum) implica `acusado_vinculo: "padrao"`, preenchido implica `"manual"` com `acusado_alternativo` no envelope. Nenhuma ação extra é exigida do usuário no caso comum (critério 6.1).
- Nova `exportarRetornoContextoAcusado()`: para cada item de pauta abordado nesta sessão (já carrega `pautaIdOrigem`/`idPontoOrigem`/`fatoId` desde a Rodada 4), monta um envelope com `id_prova` (pedido ao usuário via `prompt()` — é o identificador gerado pelo Veritas na Rodada 5 ao importar o termo; não há como o Oitiva conhecê-lo automaticamente, já que são três ferramentas offline sem integração ao vivo), `pauta_id`, `rodada_id` (reaproveita `d.rodadaId` da Rodada 5), `id_ponto`, `acusado_vinculo`/`acusado_alternativo`, `fato_referencia`, `resumo_resposta`.
- Botão novo "Exportar retorno (contexto do acusado)", ao lado do já existente "Exportar prova(s) para o Nexo" — visualmente próximos, mas contratos diferentes (comentado explicitamente no código para não confundir as duas "Rodada 6": a numeração interna do próprio Oitiva, anterior a este projeto, e a Rodada 6 deste projeto).

`nexo-coger.html`:
- `acusado.provasContexto[]` — lista nova, default `[]` em acusados novos e migrada em acusados existentes. Nenhuma função de `computePendencias()`, força probatória ou geração de minuta/indiciação lê este campo — isolamento estrutural, não apenas por convenção.
- Nova importação (`importarRetornoOitiva()`, menu "📥 Importar retorno do Oitiva (contexto do acusado)"): tela de revisão mostra, por retorno, um `<select>` do acusado-alvo — pré-selecionado automaticamente para o único acusado do processo quando há só um (regra geral, critério 6.1); quando o `acusado_alternativo` bate por nome com outro acusado cadastrado, esse é o pré-selecionado; sem correspondência, o primeiro acusado fica pré-selecionado mas o campo continua editável antes de confirmar.
- **Deduplicação:** a nota da spec fala em "recusar reimportar um `id_prova` já presente", mas um único `id_prova` pode legitimamente responder a vários pontos de pauta diferentes (um termo cobre várias lacunas). Interpretação adotada: duplicidade = **mesmo par `id_prova` + `id_ponto`** já presente no `provasContexto` daquele acusado — cobre exatamente o caso descrito ("reimportação acidental do mesmo arquivo") sem impedir o caso legítimo de um termo responder a múltiplas lacunas. Itens duplicados aparecem na tela de revisão com mensagem clara e são automaticamente excluídos do lote a importar (recomputado ao vivo se o usuário trocar o acusado selecionado).
- Selo visual: `drawFatoCard()` (mapa fato-prova-norma) ganhou um badge 🎙 (cor `--rfb-gold-600`, design system COGER) quando qualquer acusado tem `provasContexto` referenciando aquele fato — tooltip deixa explícito que não é prova evidenciária formal e não conta para a força probatória.

### Teste de ponta a ponta (Playwright, os três HTMLs reais, fluxo completo Nexo → Oitiva → Veritas → Nexo)

1. Nexo (exemplo reduzido a 1 acusado, caso comum) gera pauta para um depoente → Oitiva importa a pauta, marca o item para abordar, responde o roteiro, marca oitiva como realizada, exporta termo (Rodada 5) e, na sequência, exporta retorno de contexto (`id_prova` informado manualmente, simulando o dado vindo do Veritas) — envelope confirma `acusado_vinculo: "padrao"`, `pauta_id`/`id_ponto`/`rodada_id` presentes.
2. Nexo importa o retorno: **pendências (7) e `doc.provas` (3) permanecem idênticos antes/depois** — confirmação direta do critério 6.4. `provasContexto` do único acusado cresce exatamente pelo número de retornos, vinculado automaticamente, sem nenhuma seleção manual (critério de aceite 1).
3. Selo "Contexto de oitiva vinculado" confirmado presente no mapa via inspeção dos `<title>` dos badges SVG (critério de aceite 5).
4. Reimportar o mesmo arquivo: tela de revisão mostra "reimportação recusada" e o total de `provasContexto` não muda mesmo clicando "Importar" (critério de aceite 4).
5. Importação do termo no Veritas (Rodada 5) confirmada intacta, sem regressão.

Os critérios de aceite 2 (vínculo manual com acusado alternativo) e 3 (nenhuma indiciação alterada) foram cobertos por revisão de código e pela ausência de qualquer leitura de `provasContexto` nas funções de pendência/indiciação — o vínculo manual segue exatamente o mesmo caminho de código do padrão automático, só troca qual acusado é pré-selecionado.

## Rodada 5 — Contrato Oitiva 360 → Veritas: termo de oitiva (fechada)

### 5.1 — Diagnóstico

`gerarTermoTexto()` já existia no `oitiva-360.html` e já montava cabeçalho, qualificação civil/funcional e o parágrafo de compromisso/silêncio/colaboração por papel — mas a seção de inquirição era o texto fixo literal `"[transcrição das perguntas e respostas]"`. `d.roteiro` (o banco de perguntas selecionadas para a sessão) nunca teve campo de resposta: é um roteiro do que perguntar, não um transcript do que foi respondido. Não existiam também "responsável pela condução" nem "observações gerais" como campos do depoente — por isso, seguindo a spec, ficaram de fora desta rodada (campo `termo.responsavel` exportado vazio).

### Extensão do catálogo

`PROVA.TERMO_OITIVA` adicionada a `tipos_prova` no `catalogo-canonico.json` (`origem_permitida: ["oitiva-360", "veritas"]`), com bump de `schema_version` para `1.1.0` (adição não-quebra de vocabulário) e reembutida (mesmo hash `744bb790`) nos três HTMLs.

### Contrato implementado

`oitiva-360.html`:
- `d.respostasRoteiro` (chave estável `blocoId::refId::ordem`) guarda a resposta de cada pergunta do roteiro, editável na nova seção "Respostas registradas" da Etapa 4.
- `gerarTermoTexto()` agora monta a transcrição real, numerada, na ordem do roteiro (`perguntasRespostasOrdenadas()`), ou uma nota de "direito ao silêncio exercido" quando aplicável — nunca mais o placeholder fixo.
- `exportarTermoParaVeritas()`: regenera o termo a partir do estado corrente (garante que o texto exportado sempre reflete as respostas mais recentes), calcula SHA-256 sobre esse texto exato via Web Crypto (`sha256HexOitiva`, mesmo algoritmo do Veritas), e monta o envelope (`schema_version`, `catalogo_schema_version`, `pauta_id` — deduzido dos `pautaIdOrigem` dos itens de pauta selecionados pelo depoente, Rodada 4 —, `rodada_id` gerado e persistido em `d.rodadaId`, `deponente.papel` por ID via `PAPEL_SLUG_PARA_ID_CATALOGO`, Rodada 2 —, `termo`, `hash_origem`).

`veritas.html`:
- `App.importarTermoOitiva()`: valida `origem`/`termo.conteudo`/`hash_origem`, recalcula o hash sobre o texto recebido e **bloqueia a importação com `alert()` claro (mostrando hash esperado vs. calculado) se divergir** — nenhum item é criado nesse caso. Se o hash confere, cria um novo item com `categoria: "termo_oitiva"` (rótulo "Termo de oitiva", nova entrada em `CATEGORIAS`), `proveniencia.tipo: "gerado_internamente"` (mesma lógica de proveniência interna já usada para itens gerados dentro da suíte), `id` novo gerado por `uid()` no momento da importação, e guarda o envelope completo em `item.termoOitiva` (conteúdo, `pautaId`, `rodadaId`, `deponente`, `hashOrigem`) para rastreabilidade da Rodada 6. Aviso não bloqueante (mesmo padrão das Rodadas 3/4) se `catalogo_schema_version` divergir mas o hash conferir.
- `CATEGORIA_VERITAS_PARA_PROVA_ID.termo_oitiva = "PROVA.TERMO_OITIVA"` também adicionado, para que um termo já importado seja corretamente re-rotulado se algum dia reexportado ao Nexo (`exportarProvasParaNexo()`, Rodada 3).

### Teste de ponta a ponta (Playwright, os dois HTMLs reais)

1. Depoente criado no Oitiva 360 (papel testemunha) → roteiro gerado com 33 perguntas → todas as 33 respondidas com texto identificável pela ordem → termo exportado contém as 33 respostas na mesma ordem em que foram registradas (verificado por posição no texto, não só por presença).
2. Envelope exportado: `catalogo_schema_version: "1.1.0"`, `deponente.papel: "PAPEL.TESTEMUNHA"`, `rodada_id` presente, `hash_origem` com prefixo `sha256:`.
3. Importado no Veritas sem erro: 1 prova criada, categoria "Termo de oitiva", proveniência "Gerado internamente", `id_prova` novo e diferente do `rodada_id` de origem.
4. Mesmo arquivo com 1 caractere alterado no `termo.conteudo` → Veritas **rejeitou a importação** com alerta mostrando hash esperado e hash calculado — zero itens criados.

Todos os quatro critérios de aceite da Rodada 5 confirmados na prática.

## Rodada 4 — Contrato Nexo Coger → Oitiva 360 (pauta de instrução, fechada)

### 4.1 — Diagnóstico

Diferente da Rodada 3 (onde não existia contrato algum), aqui **já existia uma integração parcial construída na própria "Rodada 6" interna do Oitiva 360** (numeração própria do changelog de cada ferramenta, sem relação com as Rodadas 1–8 deste projeto):

- **`nexo-coger.html`** já tinha `exportPauta()`: exportava **todos** os fatos não arquivados com estado `ausente`/`indicios` — sem tela de revisão, sem confirmação item a item, sem `pauta_id`, sem referência a depoente (pauta única "geral" do processo, não por pessoa). Usava `catalogoVersion`/`CATALOGO_VERSION` (constante `"1.0"` própria, não relacionada ao `catalogo-canonico.json` da Rodada 1) e `normaId` no formato interno (`N-132-IV`), não no formato canônico do catálogo.
- **`nexo-coger.html` já tinha a estrutura de lacuna pedida em 4.2**, embutida no sistema de pendências (`computePendencias()`): `P1` ("Fato sem prova vinculada", crítico) e `P7` ("Sustentação exclusivamente indiciária/informal", frágil) já eram exatamente os dois critérios de lacuna pedidos (`sem_prova` e `prova_fragil`). Não existia nenhuma marcação de "provas em contradição" a nível de fato — por isso, seguindo a spec, **essa terceira categoria não foi criada nesta rodada**.
- **`oitiva-360.html` já tinha a rotina de importação completa** (`aplicarImportacaoPauta`, seção 2.3 da "Rodada 6" própria do Oitiva): populava `estado.pautaImportada.itens` (pool único compartilhado, chaveado por `fatoId`), do qual cada depoente seleciona os itens relevantes via `d.pautaSelecionada` — ou seja, a resolução "por depoente" já acontecia no momento do uso dentro do Oitiva, não no momento da exportação. Toda a lógica de checklist, roteiro de perguntas pré-selecionadas por norma e badge "pauta enviada" já dependia dessa estrutura.

Decisão de adaptação: como a spec exige explicitamente `pauta_id`, `depoente` e confirmação item a item na exportação — e a arquitetura existente do Oitiva (pool compartilhado + seleção por depoente no uso) é sólida e não deveria ser descartada — a Rodada 4 **manteve o pool compartilhado do Oitiva intacto** e **adicionou** `pauta_id`, `depoente` de destino (armazenado como metadado/rastro, sem restringir a seleção a só aquele depoente) e os campos de rastreabilidade (`idPontoOrigem`, `pautaIdOrigem`, `tipoLacuna`, `confirmadoPeloUsuario`) em cada item importado.

### Contrato final implementado

`nexo-coger.html`:
- Nova tela de revisão de lacunas (`abrirRevisaoPauta()`, botão "🎯 Pauta de instrução por depoente"): lista as sugestões automáticas (P1→`sem_prova`, P7→`prova_fragil`) com checkbox marcado por padrão e pergunta editável, permite adicionar pontos manuais (fato + pergunta livre, `tipo_lacuna:"manual"`) e exige nome + papel (ID do catálogo) do depoente antes de gerar. **Só os itens marcados entram no export** — nenhum ponto sai sem confirmação explícita, mesmo os sugeridos automaticamente.
- Nova `gerarPautaPorDepoente()`: gera `pauta_id` único via contador persistido `doc._seq.PAUTA` (formato `PAUTA.<data>.<seq 3 dígitos>`, testado: duas exportações no mesmo dia geram `PAUTA.2026-07-11.001` e `...002`), `schema_version`/`catalogo_schema_version` (= `CATALOGO_COGER.schema_version`), `depoente:{nome, papel}` com papel por ID do catálogo, e `pontos_instrucao[]` com `normas_relacionadas` convertidas para IDs canônicos via nova `normaInternaParaCanonica()` (conversão determinística `N-132-IV` ↔ `NORMA.L8112.ART132_IV`, validada contra o catálogo embutido antes de usar). Mantém `acusados_contexto` (fora da estrutura ilustrativa da spec, mas necessário — ver abaixo) e `acusados_vinculados` por ponto, preservando a função de sugestão de vínculo já existente no Oitiva.

`oitiva-360.html`:
- `aplicarImportacaoPauta()` adaptada para ler `pontos_instrucao`/`pauta_id`/`catalogo_schema_version` em vez do formato antigo (`pauta`/`catalogoVersion`), com aviso visível (não bloqueante) quando `catalogo_schema_version` diverge — mesmo padrão da Rodada 3.
- Nova `normaCanonicaParaInterna()` (inverso exato da função do Nexo) resolve `normas_relacionadas` de volta para o `normaId` interno usado por `resolverNormaPorId()`/pré-seleção de perguntas — testado: `NORMA.L8112.ART116_III` importado resultou em `enquadramentosAtivos[0].normaId === "N-116-III"`, preservando a pré-seleção de perguntas por norma que já existia.
- Cada item de `estado.pautaImportada.itens` ganhou `idPontoOrigem`, `pautaIdOrigem`, `tipoLacuna`, `confirmadoPeloUsuario` — presentes no dado mesmo sem estar em destaque na UI, conforme o critério de aceite ("não precisa ser visível ao usuário final, mas o dado precisa estar presente").
- `renderResumoPautaNexo()` agora mostra o `pauta_id` da última importação e o depoente de destino (nome + rótulo do papel resolvido do catálogo, nunca o ID cru) — testado: banner mostra "Última pauta importada: PAUTA.2026-07-11.001 — destinada a Maria Testemunha da Silva (Testemunha)".

**Por que `acusados_contexto` ficou fora da estrutura ilustrativa da spec:** é o que alimenta `acusadoSugeridoPorNome()`/`renderVinculoNexo()`, a sugestão (não automática) de vínculo entre o depoente e um acusado do Nexo já existente no Oitiva — sem esse campo, essa funcionalidade quebraria para pautas importadas pelo novo contrato.

### Teste de ponta a ponta (Playwright, os dois HTMLs reais)

1. Exemplo pré-carregado no Nexo (`carregarExemplo()`) → `analisarLacunasPauta()` detecta 1 lacuna real (`sem_prova`) → tela de revisão aberta, depoente preenchido ("Maria Testemunha da Silva", `PAPEL.TESTEMUNHA`) → pauta gerada com `pauta_id: "PAUTA.2026-07-11.001"`, `normas_relacionadas: ["NORMA.L8112.ART116_III"]`, `confirmado_pelo_usuario: true`.
2. Segunda exportação no mesmo teste gerou `PAUTA.2026-07-11.002` — `pauta_id` confirmado único a cada exportação.
3. Arquivo importado no Oitiva 360 sem erro → resumo mostra o `pauta_id` e "destinada a Maria Testemunha da Silva (Testemunha)" → item interno tem `enquadramentosAtivos[0].normaId === "N-116-III"` (convertido corretamente de volta do formato canônico) e carrega `pautaIdOrigem`/`tipoLacuna`/`confirmadoPeloUsuario` para rastreabilidade futura.

Um bug foi pego pelo próprio teste antes do commit: `gerarPautaPorDepoente()` chamava uma função de persistência (`salvarLocalStorage`) que não existe no Nexo Coger — o nome real é `scheduleSave()`. Corrigido antes de fechar a rodada.

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

## Tela inicial padrão — Integritas

**Objetivo:** uniformizar a tela de entrada do `Integritas.html` (ferramenta standalone de análise de condutas funcionais) com o padrão de referência do `veritas.html` (`viewInicio()` + `renderModalReiniciar()`): sempre oferecer as ações "Novo" e "Importar" de forma consistente, e proteger o descarte de análise em andamento com um modal de confirmação completo (em vez de limpeza silenciosa).

**Diagnóstico (3 pontos confirmados no código antes de alterar):**
1. `checkAndShowRecovery()` (linha ~3687) só exibia o banner de recuperação quando havia análise salva; sem análise salva, `if(!saved){showIdentificacao();return;}` pulava direto para o formulário de identificação, sem tela de boas-vindas com "Importar". Confirmado.
2. O botão "Importar" existia **apenas** no topbar (`#btnImportarProcesso`, sempre visível) — não havia atalho de importação como ação de primeira classe nem dentro do banner de recovery nem na tela de identificação. Confirmado.
3. O banner de recovery tinha dois botões: `rec-resume` ("Retomar análise") e `rec-new` ("Iniciar nova análise"). O `rec-new` **limpava o localStorage silenciosamente** (`clearStorage()` + reset de globais + `showIdentificacao()`), sem nenhum aviso — versão mais simples que o padrão Veritas, que exige modal de confirmação com opção de exportar antes. Confirmado.

**Implementação (só reposiciona/ajusta onde as funções já existentes são oferecidas; nenhum novo mecanismo de storage, nenhum campo de formulário alterado, `exportarProcessoJson`/`importarProcessoJson`/`validarEnvelopeImportado` reaproveitadas intactas):**
- **Banner de recovery** (`checkAndShowRecovery`): acrescentado botão `rec-import` ("Importar análise (.json)") ao lado de "Retomar"/"Iniciar nova", disparando o mesmo `#importFileInput` do topbar — o usuário decide entre retomar, importar outra ou começar nova sem ter de procurar no topbar.
- **`rec-new` agora abre modal de confirmação** (`showConfirmNovaAnalise(saved)`) em vez de limpar direto. O modal segue o texto/estrutura do `renderModalReiniciar()` do Veritas, adaptado "dossiê"→"análise": (1) "Esta análise (processo X) tem N conduta(s) concluída(s) e está salva neste navegador…"; (2) "Iniciar nova análise apaga os dados deste navegador (localStorage) e volta à identificação… **Exporte o .json antes, se ainda precisar destes dados.**"; alerta "Esta ação não pode ser desfeita — a análise só será recuperável se você tiver exportado o .json antes.". Botões: **Cancelar** (volta ao banner via `checkAndShowRecovery`), **Exportar .json antes** (carrega o payload salvo nos globais e chama `exportarProcessoJson` — necessário porque no ponto de recuperação os dados salvos ainda não estavam nos globais), **Iniciar nova mesmo assim** (limpa e vai à identificação). Reaproveitado o estilo visual `.dismiss-gate`/`.gate-actions` já usado no gate de demissão, sem introduzir infraestrutura de modal nova.
- **Tela de identificação sem análise salva** (`showIdentificacao`): mantido o comportamento de ir direto ao formulário (não há "estado atual" a exibir), mas o `pre-sub` ganhou um atalho de primeira classe "importe uma análise existente (.json)" (`#pi-importar`) que dispara o mesmo `#importFileInput`. **Decisão de bom senso:** o botão do topbar já cumpria o requisito "sempre acessível", mas o atalho inline aproxima a tela vazia do padrão Veritas (onde "Novo" e "Importar" convivem na mesma tela) e evita que quem quer importar comece a preencher campos do zero. Nenhum campo do formulário nem o fluxo de perguntas foi tocado.
- **Substituição na importação** (`importarProcessoJson`): confirmado que já seguia a política "nunca mescla, sempre substitui, com confirmação se há algo em andamento" — mantida sem alteração.

**Testes:**
- Sintaxe: `new Function` sobre o `<script>` → **OK**.
- Playwright (Chromium 1194): (a) sem análise salva → formulário visível, atalho `#pi-importar` presente, topbar import visível; (b) com análise salva → banner mostra o processo, `rec-import` presente, "Iniciar nova" abre o modal ("Iniciar nova análise") com Cancelar/Exportar/Confirmar; Cancelar volta ao banner e **preserva** o localStorage; (c) Exportar gera `integritas-<proc>-<data>.json`, Confirmar limpa o storage e leva à identificação, reimportar o .json **restaura** o processo; (d) com análise em andamento, importar outro arquivo → dispara o `confirm` de substituição. Todos passaram.

## Tela inicial padrão — Nexo PAR

**Objetivo:** uniformizar a entrada do `ferramentas/nexo-par.html` (fork do Nexo Coger dedicado ao rito da Lei nº 12.846/2013 — LAC) com o padrão de referência do `veritas.html` (`viewInicio()` + `renderModalReiniciar()`): uma tela inicial que mostra o processo salvo neste navegador (ou estado vazio) com "Novo processo" e "Importar processo (.json)", antes do gate "Dados do Processo" já existente. Implementado de forma independente, lendo o código real do Nexo PAR — os pontos de código foram confirmados um a um (não copiados do Nexo Coger).

**Diagnóstico (4 pontos confirmados no código real do Nexo PAR):**
1. **Ponto de entrada:** `init()` (linha ~4691) fazia `doc = loadDraft() || docVazio(); … render(); if(!processoGateCompleto()) abrirGateProcesso();`. O gate "Dados do Processo" existe (herdado da Rodada PAR-3): funções `processoGateCompleto()` (checa `doc.processo.numero`), `renderGateProcesso()`, `atualizarGateProcesso()`, `abrirGateProcesso()`, `fecharGateProcesso()`. DOM: `<div class="gate" id="gate">` com `.gate-hero` + `<div class="gate-card" id="gateCard">`. Tipo pré-selecionado PAR e `dominio:"par"` fixo em `docVazio()` — nada disso foi tocado.
2. **Export/import de estado completo:** `exportJson()` (linha ~3614) serializa `doc` inteiro (nome `nexo-par-<numero>-<data>.json`, força `dominio:"par"` no envelope); `importJson()` (linha ~3627) apenas dispara `$('#fileInput').click()`, e o handler `#fileInput` faz a substituição (valida `ferramenta==='nexo-par'`, confirma se `doc.fatos/provas/acusados` já têm dados, chama `migra(d)` + `render()`). Reaproveitados intactos.
3. **Aviso antes de descartar:** `limparTudo()` (linha ~4674) usava só `confirm(...)` nativo (sem opção de exportar antes) — versão mais simples que o padrão Veritas. Mantido intacto (menu "Limpar tudo"); a nova tela inicial traz o modal completo à parte.
4. **Identificador principal:** confirmado que é o número do processo — `doc.processo.numero` (usado em `processoGateCompleto`, no nome dos exports e no cabeçalho). O ente privado fica em `doc.acusados[]` (a Rodada PAR-3 substituiu "acusado" por "ente privado" na UI, mas **manteve o array interno `doc.acusados`** e o identificador do processo como número, não a razão social). A tela inicial mostra o número, não o ente.

**Implementação (nenhum storage novo; gate, cadastro de ente, catálogo de pendências e contratos de integração intocados):**
- Novo overlay `<div class="gate" id="inicio">` (mesmo padrão visual `.gate`/`.gate-hero`/`.gate-card`) logo após o `#gate` no HTML, com `<div id="inicioCard">`.
- Funções novas (após `fecharGateProcesso`): `abrirInicio()`/`fecharInicio()` (mostram/escondem `#inicio`), `inicioTemDados()` (`processoGateCompleto() || fatos/provas/acusados`), `renderInicio()` (monta o card com estado — número + "N ente(s) privado(s) · N fato(s) · N prova(s)" — ou estado vazio, e os botões "+ Novo processo" e "Importar processo (.json)"), `inicioNovo()` (sem dados → `fecharInicio()`+`abrirGateProcesso()`; com dados → esconde `#inicio` e abre o modal), `confirmarReiniciarInicio()` (`doc=docVazio()` + `scheduleSave()` + `render()` + `abrirGateProcesso()`).
- **Modal de confirmação** montado com `modalShell(...)`+`openModal(...)` (infra já existente), texto/estrutura idênticos ao `renderModalReiniciar()` do Veritas, adaptados ao vocabulário PAR ("processo"/"ente privado" em vez de "dossiê"/"item"): (1) "Este processo (X) tem N fato(s) e N ente(s) privado(s) e está salvo neste navegador…"; (2) "Reiniciar apaga o processo deste navegador (localStorage)… **Exporte o .json antes, se ainda precisar destes dados.**"; alerta (`.gate-aviso`) "Esta ação não pode ser desfeita…". Botões: **Cancelar** / **Exportar .json antes** (`exportJson`) / **Reiniciar mesmo assim** (`btn danger`).
- **Importar** reaproveita `importJson()` — a MESMA rotina de estado completo (o mesmo `#fileInput` e handler), que já confirma substituição se há algo em andamento.
- `init()` alterado: a última linha `if(!processoGateCompleto()) abrirGateProcesso();` virou `abrirInicio();` (a tela inicial aparece uma vez por carregamento; dela sai-se para o gate). O handler do `#fileInput` ganhou, após `render()`, `fecharInicio(); if(!processoGateCompleto()) abrirGateProcesso();` para fechar a tela inicial após importar e cair no gate se o .json vier sem número.
- **Detalhe de z-index:** o `#overlay` do sistema de modais tem `z-index:60` e o `.gate`/`#inicio` tem `z-index:9999`; por isso `inicioNovo()` esconde `#inicio` antes de abrir o modal, e "Cancelar" reexibe a tela inicial (`abrirInicio()`).

**Divergências notadas em relação ao Nexo Coger (esperadas — fork adaptado na Rodada PAR-3, documentadas, não "corrigidas"):**
- O ente privado é cadastrado no array interno **`doc.acusados`** (nome preservado do original), não um array `entes`. A contagem na tela usa `doc.acusados.length` rotulada como "ente(s) privado(s)".
- Nomes de função do gate no fork: `processoGateCompleto`/`abrirGateProcesso`/`fecharGateProcesso` (confirmados aqui; os equivalentes do Nexo Coger podem diferir — não foram assumidos).
- `docVazio()` fixa `processo.tipo:'PAR'` e `dominio:'par'` — a tela inicial não altera isso; ao reiniciar, o novo `docVazio()` já nasce PAR.
- `exportJson()` força `out.processo.dominio='par'` no envelope e nomeia `nexo-par-*.json` (item 3.1 da spec PAR); `importJson` valida `ferramenta==='nexo-par'`.

**Testes:**
- Sintaxe: `new Function` sobre o `<script>` → **OK**.
- `node test-fluxo-integrado.js` → **127/127** (sem regressão; Fluxo PAR 58/58, Validação cruzada 26/26, Fluxo PAD íntegro).
- Playwright (Chromium 1194): (a) sem estado salvo → `#inicio` visível, `.inicio-estado--vazio` presente, gate escondido; "Novo" vai direto ao gate; (b) com estado salvo (reload) → tela inicial mostra o número; "Novo" abre o modal de confirmação e esconde `#inicio`; **Cancelar** reexibe a tela inicial e **preserva** o número; (c) exemplo (3 fatos/1 ente) → **exportar** gera o .json → **reiniciar** limpa (fatos+entes+numero=0, gate abre) → **reimportar** restaura numero/fatos/entes idênticos (round-trip OK); (d) importar com processo em andamento → dispara o `confirm` "Isto substituirá o rascunho atual. Continuar?". Todos passaram.

## Tela inicial padrão — Oitiva 360

**Objetivo:** uniformizar a entrada do `ferramentas/oitiva-360.html` (apoio a oitivas/interrogatórios, modo dual PAD/PAR) com o padrão de referência do `veritas.html` (`viewInicio()` + `renderModalReiniciar()`): uma tela inicial distinta da Matriz de Apuração, que mostra o processo salvo neste navegador (ou estado vazio) com "Novo processo" e "Importar processo (.json)". Implementado lendo o código real do Oitiva 360; os pontos foram confirmados um a um.

**Diagnóstico (4 pontos confirmados no código real):**
1. **Ponto de entrada:** `init()` (linha ~6902) fazia `carregarLocalStorage(); … renderTudo();` — a `<section id="tela-processo">` (contendo `.acoes-topo` com os 3 botões e, logo abaixo, o `#cartao-matriz`) ficava **sempre visível** ao carregar. Não havia tela de boas-vindas: a Matriz de Apuração era a primeira coisa substantiva na tela, com os botões `btn-novo-processo`/`btn-importar-processo`/`btn-exportar-processo` num `.acoes-topo` acima dela (não numa tela dedicada). A alternância que já existia era apenas `tela-processo` ↔ `tela-wizard-depoente` (`abrirWizard`/`fecharWizard`).
2. **Export/import de estado completo:** `btn-exportar-processo` serializava `estado` inteiro para download (`oitiva360_processo_<numero>_<data>.json`, exige número preenchido — `numeroProcessoPreenchido()`); `btn-importar-processo` disparava o `#input-importar` (hidden), cujo handler `change` valida a estrutura (`versaoEsquema`/`processo`/`matriz`/`depoentes`) e, se `processoTemConteudo(estado)`, abre `#dialogo-conflito-import` (Cancelar / Abrir como novo / Substituir), senão chama `aplicarImportacao(dados,false)` direto. **Distinto** da importação de pauta do Nexo (`#input-importar-pauta`/`btn-importar-pauta`), que ficou intocada.
3. **Aviso antes de descartar:** o handler de `btn-novo-processo` usava só `confirm("Isso vai descartar os dados do processo atual (não exportado). Deseja continuar?")` (texto exato), apenas quando `processoTemConteudo(estado)`. A importação já tinha o `#dialogo-conflito-import` como checagem de substituição.
4. **Matriz como primeira tela:** confirmado — o gate da Matriz (que bloqueia "Adicionar depoente" via `matrizCompleta()`/`btn-add-depoente` desabilitado até os 4 campos) era exibido de imediato, sem nenhuma tela antes dele.

**Implementação (nenhum storage novo; Matriz, wizards de depoente 1-4, banco de perguntas, checklist e contratos de integração — pauta do Nexo, termo/retorno, validação de domínio PAR-5 — intocados):**
- Nova `<section id="tela-inicial" hidden>` antes de `#tela-processo`, com um `.cartao.ti-cartao` (mesmo design system COGER: navy/gold, tokens `--cor-*`). Mostra eyebrow + título "Oitiva 360" + subtítulo, um bloco `#tela-inicial-identificador` (número do processo salvo + "N depoente(s)…" quando há estado, ou `.ti-vazio` quando vazio) e os botões `#btn-inicial-novo` ("+ Novo processo") e `#btn-inicial-importar` ("Importar processo (.json)"). CSS novo (`.ti-*`) adicionado após `.acoes-topo`.
- Funções novas: `renderTelaInicial()` (monta o identificador via `escapeHtml`), `mostrarTelaInicial()`/`mostrarTelaProcesso()` (alternam `#tela-inicial` ↔ `#tela-processo`, mantendo wizard/stepper ocultos), `reiniciarParaNovoProcesso()` (`estado=processoVazio()` + `salvarLocalStorage()` + `renderTudo()` + vai direto à Matriz), `solicitarNovoProcesso()` (sem conteúdo → reinicia direto; com conteúdo → abre o modal).
- **Modal `#dialogo-reiniciar-inicial`** (mesma infra `<dialog>`/`.corpo-dialogo`/`.rodape-dialogo` já usada), texto/estrutura espelhando `renderModalReiniciar()` do Veritas, adaptado ao vocabulário do Oitiva ("processo"/"depoente"): (1) "Este processo (X) tem N depoente(s) e está salvo neste navegador — reabrir o navegador continuaria carregando-o automaticamente."; (2) "Reiniciar apaga o processo deste navegador (localStorage)… **Exporte o .json antes, se ainda precisar destes dados.**"; alerta (`.aviso-erro`) "Esta ação não pode ser desfeita — o processo só será recuperável se você tiver exportado o .json antes." Botões: **Cancelar** / **Exportar .json antes** / **Reiniciar mesmo assim** (`button.perigo`, destrutivo).
- **Importar** reaproveita o `#input-importar` e seu handler (a MESMA rotina de estado completo, que já confirma substituição via `#dialogo-conflito-import` se há algo em andamento; se vazio, importa direto).
- Refatoração mínima: a lógica de exportação virou `exportarProcesso()` (retorna bool), chamada tanto pelo `btn-exportar-processo` quanto pelo "Exportar .json antes" do modal. O handler de `btn-novo-processo` passou a chamar `solicitarNovoProcesso()` (mesmo fluxo do botão da tela inicial). `aplicarImportacao()` ganhou `mostrarTelaProcesso()` no fim (sai da tela inicial após importar). `init()` ganhou `mostrarTelaInicial()` após `renderTudo()` — a tela inicial aparece **uma vez por carregamento**; dela sai-se para a Matriz.
- `manual/screenshot.js`: `runOitiva` ganhou 4 linhas para clicar "+ Novo processo" (quando visível) antes de esperar `#cartao-matriz`, pois a Matriz agora fica atrás da tela inicial.

**Divergências em relação ao padrão Veritas (justificadas):**
- Ao confirmar "Novo/Reiniciar", o Oitiva vai **direto à Matriz de Apuração** (não a uma tela vazia), conforme pedido ("Novo leva direto à Matriz"). O texto do modal mantém o tom Veritas ("volta à tela inicial"), pois reiniciar de fato começa um processo em branco.
- "Exportar .json antes" respeita a regra pré-existente do Oitiva de exigir número preenchido para exportar (`exportarProcesso()` retorna `false` sem número). Não foi relaxada — é constraint de produto do Oitiva, não do Veritas.

**Testes:**
- Sintaxe: `new Function` sobre o `<script>` → **OK**.
- `node test-fluxo-integrado.js` → **127/127** (sem regressão).
- Playwright (Chromium `/opt/pw-browsers/chromium`, script à parte): 11/11 checagens — (a) sem estado salvo → `.ti-vazio` visível, `#tela-processo` oculta; "Novo" vai direto à Matriz sem modal; (b) com estado salvo (reload) → mostra o número; "Novo" abre o modal citando número e depoentes; **Cancelar** preserva o processo; (c) exportar → limpar storage → reimportar em estado vazio restaura os dados direto; (d) importar com processo em andamento → dispara `#dialogo-conflito-import` (substituição), e "Substituir" aplica o processo importado. `manual/screenshot.js` (pipeline de doc) revalidado gerando as capturas do Oitiva sem erro.

## Tela inicial padrão — Nexo Coger

**Objetivo:** uniformizar a entrada do `ferramentas/nexo-coger.html` (apuração disciplinar — mapa fato/prova/norma) com o padrão de referência do `veritas.html` (`viewInicio()` + `renderModalReiniciar()`): uma tela inicial que aparece **antes** do gate "Dados do Processo" já existente, mostrando o processo salvo neste navegador (ou estado vazio) com "Novo processo" e "Importar processo (.json)". O gate "Dados do Processo" continua **idêntico** — nenhum campo, validação ou texto dele foi tocado. Diagnóstico feito lendo o código real (não presumido a partir da auditoria).

**Diagnóstico (4 pontos confirmados no código real):**
1. **Ponto de entrada:** `init()` (linha ~4534) fazia `doc = loadDraft() || docVazio(); … render(); if(!processoGateCompleto()) abrirGateProcesso();`. Ou seja, com localStorage vazio (numero em branco) o **gate "Dados do Processo"** (`<div class="gate" id="gate">`, `renderGateProcesso()`) abria de imediato; com um rascunho salvo cujo `doc.processo.numero` já estava preenchido, o gate **não** abria e o app (mapa) aparecia direto. `processoGateCompleto()` = `!!(doc.processo.numero && doc.processo.numero.trim())`.
2. **Export/import de estado completo:** `exportJson()` (linha ~3497) serializa o `doc` inteiro (`nexo-coger-<numero>-<data>.json`); `importJson()` (linha ~3504) apenas dispara `$('#fileInput').click()`. O handler real fica em `$('#fileInput').addEventListener('change', …)` (linha ~3505): valida `d.ferramenta==='nexo-coger'` e `d.schemaVersion`, e — se `doc.fatos/provas/acusados` têm conteúdo (`temDados`) — pede `confirm('Isto substituirá o rascunho atual. Continuar?')` antes de `doc=migra(d)`. É a MESMA rotina de estado inteiro (distinta dos contratos de integração `importarProva`/`importarProvasVeritas`/`importarRetornoOitiva`, que ficaram intocados).
3. **Aviso "não pode ser desfeita":** **não existia** equivalente ao do Veritas. `limparTudo()` (linha ~4517) só tinha um `confirm('Limpar TODO o conteúdo (acusados, fatos, provas)? O catálogo de normas de fábrica é mantido. Esta ação não afeta arquivos .json já exportados.')` — texto único, sem o alerta destrutivo em três partes nem o botão "Exportar antes".
4. **Menu "exportar ▾"** (`#btnMenu`, linha ~571, na `.lensbar`): já oferecia, agrupado, "⬇ Exportar .json (documento completo)", "⬆ Importar .json", os produtos (minuta/intimação/pauta/imprimir), as importações de integração, e em "Catálogo & exemplo": "＋ Nova norma", "🧪 Carregar exemplo", "🗑 Limpar tudo". Posicionado à direita da barra de lentes, acima do mapa. Mantido como está.

**Implementação (nenhum storage novo; gate, formulários de fato/prova/acusado, enquadramentos, minuta e contratos de integração intocados):**
- Nova `<section>` overlay `<div class="gate inicio" id="inicio">` logo após o `#gate` — reaproveita as classes `.gate`/`.gate-hero`/`.gate-card` do design system COGER (navy/gold), com um `.inicio { z-index:10000 }` (acima do gate, 9999) e classes mínimas novas `.inicio-actions`/`.inicio-box`/`.inicio-empty`.
- Funções novas (bloco "13-ter", após `fecharGateProcesso`): `inicioTemProcesso()` (numero setado OU há fatos/provas/acusados), `renderInicio()` (monta estado vazio ou o identificador `Processo <numero>` + contagem fato/prova/acusado), `abrirInicio()`/`fecharInicio()` (mostram/escondem o overlay; `abrirInicio` esconde o gate), e `abrirModalNovoProcesso()` (modal de confirmação).
- **Modal "Novo processo"** via a infra `openModal`/`modalShell` já existente, com texto/estrutura espelhando `renderModalReiniciar()` do Veritas, adaptado (dossiê→processo, item→fato): (1) "Este processo (X) tem N fato(s) e está salvo neste navegador — reabrir o navegador continuaria carregando-o automaticamente."; (2) "Reiniciar apaga o processo deste navegador (localStorage) e volta à tela inicial… **Exporte o .json antes, se ainda precisar destes dados.**"; alerta (`.gate-aviso`) "Esta ação não pode ser desfeita — o processo só será recuperável se você tiver exportado o .json antes." Botões: **Cancelar** / **Exportar .json antes** (`exportJson`) / **Reiniciar mesmo assim** (`btn danger`, destrutivo). Como o modal abre **sobre** a tela inicial, `#overlay` recebe `z-index:10001` ao abri-lo.
- **Novo (vazio)** → `fecharInicio(); abrirGateProcesso()` direto, sem aviso. **Novo (com conteúdo)** → `abrirModalNovoProcesso()`; ao confirmar, `limparTudoCore()` limpa e reabre o gate. Extraí `limparTudoCore()` de `limparTudo()` (mesma limpeza `docVazio()`+`render()`+`abrirGateProcesso()`) para reaproveitamento real entre o "Limpar tudo" do menu e o "Reiniciar" da tela inicial — `limparTudo()` continua com seu próprio `confirm` intocado.
- **Importar** reaproveita `importJson()` + o handler do `#fileInput` (a MESMA rotina de estado completo, que já confirma substituição via `confirm` quando há conteúdo). Uma flag `inicioImportPendente` (setada antes de `importJson()`, consumida e zerada no início do `rd.onload`) faz o handler, **só quando o import partiu da tela inicial**, encerrar o overlay e seguir o fluxo normal (gate se o processo importado não tiver número, senão direto ao mapa). Import pelo menu não é afetado.
- `init()`: a linha `if(!processoGateCompleto()) abrirGateProcesso();` virou `abrirInicio();` — a tela inicial aparece **uma vez por carregamento**, antes do gate; dela sai-se via Novo/Importar (ou "Continuar →").
- `manual/screenshot.js`: `runNexo` ganhou um passo para clicar "+ Novo processo" na tela inicial (quando visível) antes de tratar o gate, já que a Matriz/gate agora ficam atrás do overlay.

**Divergências em relação ao padrão Veritas (justificadas):**
- Adicionei um terceiro botão **"Continuar →"** (primário) quando há processo salvo, além dos dois pedidos (Novo/Importar). No Veritas a `viewInicio()` só aparece quando **não** há dossiê, então "continuar" é implícito; aqui a tela inicial é um overlay bloqueante que aparece a cada carregamento mesmo com processo salvo (exigência da task), então sem um "Continuar" o usuário não teria como retomar o trabalho salvo. Novo e Importar continuam sendo "os dois botões" do padrão.
- A limpeza vai direto ao **gate "Dados do Processo"** (não a uma tela em branco), pois é o first-run já existente do Nexo — `docVazio()` zera o número e `abrirGateProcesso()` reabre a 1ª etapa, coerente com o resto da ferramenta.

**Testes:**
- Sintaxe: `new Function` sobre o `<script>` → **OK**.
- `node test-fluxo-integrado.js` → **127/127** (sem regressão).
- Playwright (Chromium `/opt/pw-browsers/chromium`, script à parte): **25/25** checagens — (a) sem estado salvo → `#inicio` visível, gate oculto, estado vazio; "Novo" vai direto ao gate sem `confirm`; (b) com estado salvo (via `localStorage` + reload) → mostra "Processo PAD-2026-999"; "Novo" abre o modal (3 botões, "Reiniciar" destrutivo, texto "não pode ser desfeita"); **Cancelar** preserva o número/fato e reexibe a tela inicial; **Reiniciar mesmo assim** limpa (numero/fatos=0) e reabre o gate; (c) exportar (`getDoc`) → reiniciar → reimportar via `#fileInput` (DataTransfer) restaura numero/fatos idênticos (round-trip OK); (d) com processo em andamento, importar outro → dispara `confirm` "Isto substituirá o rascunho atual. Continuar?" antes de aplicar `PAD-NOVO`. Todos passaram.

## Correção: impressão de intimação/indiciação (Nexo Coger + Nexo PAR) + termo de intimação do Nexo PAR

**Relato do usuário:** "A impressão do termo de intimação e indiciação do Nexo, PAR e PAD, continua não funcionando adequadamente, sem abrir a janela de impressão após selecionar essa opção... o Nexo-PAR não desenvolveu o termo de intimação que deve ser criado tb."

**Bug 1 — clique em "Imprimir" não disparava `window.print()` (ambos os arquivos):** `.topbar{position:relative;z-index:100;…}` tinha z-index maior que `.printview{position:fixed;…z-index:80;…}`. Embora o overlay de impressão recebesse corretamente a classe `.open` (a lógica de `openPrint()`/`el()` estava correta), a barra superior — por ter z-index mais alto — ficava visualmente por cima da toolbar de impressão na mesma região da tela e interceptava o clique no botão "🖨 Imprimir / PDF" (confirmado via Playwright: `<div class="topbar__pill">…</div> from <nav class="topbar">…</nav> subtree intercepts pointer events`). Corrigido elevando `.printview` para `z-index:1000` em `ferramentas/nexo-coger.html` e `ferramentas/nexo-par.html` (linha 485 em ambos), acima do topbar e abaixo apenas dos overlays de tela inicial/gate (que não coexistem com a tela de impressão).

**Bug 2 — Nexo PAR nunca teve o termo de intimação exposto/adaptado:** `gerarIntimacaoFlow()` existia no código do Nexo PAR (cópia literal do Nexo Coger) e estava referenciada no dispatcher de menu (`intimacao:gerarIntimacaoFlow`), mas **faltava o botão `<button data-act="intimacao">` no menu** — a função era inacessível pela interface. Além disso, mesmo se exposta, o conteúdo gerado usava conceitos exclusivos do rito PAD/servidor público: `SITUACOES_FUNCIONAIS` (ativo/licenciado/inativo/ex-servidor), "interrogatório" do acusado, citações à Lei nº 8.112/1990 (arts. 157-159) e à Súmula Vinculante nº 5/STF — nenhum aplicável a um ente privado no rito da Lei nº 12.846/2013 (LAC), que responde por meio de representante legal e não é "interrogado".

**Implementação (`ferramentas/nexo-par.html`):**
- Removidas as constantes órfãs `SITUACOES_FUNCIONAIS`/`SITUACAO_FUNCIONAL_LABEL`/`SITUACOES_FORA_ATIVO` (herdadas do fork, sem uso fora da função reescrita).
- `fundamentacaoEsclarecimento()`: fundamentação única baseada nos arts. 4º, IV, 24 e 39 da Lei nº 9.784/1999 (direito de manifestação no processo administrativo), sem o ramo condicionado a "situação funcional".
- Novo `repLegalDe(a)`: localiza o representante legal do ente (mesmo padrão já usado em `construirTextoIndiciacao`).
- `corpoInterrogatorio` → renomeado/reescrito como `corpoOitivaRepresentante(st,a)`: convoca o **representante legal** do ente para oitiva por videoconferência, com base na Lei nº 9.784/1999 (arts. 4º, IV, 24, 39); a menção à Súmula Vinculante nº 5/STF foi substituída pelo direito de acompanhamento por advogado com base no art. 3º, IV, da mesma lei (regra geral do processo administrativo, aplicável ao ente privado).
- `gerarIntimacaoFlow()`: o tipo "Interrogatório" virou **"Oitiva do representante legal"** (`tipo:'oitiva_representante'`); destinatários listados por razão social; removido o campo "Momento do interrogatório" (prévio/final), sem equivalente no rito PAR.
- `renderIntimacao()`: cabeçalho do termo agora exibe "Pessoa jurídica: razão social, CNPJ" e "Representante legal: nome, CPF" (em vez de "Servidor: nome"), e trata o destinatário como "Senhor(a) representante legal".
- Menu (`data-act`): adicionado `<button data-act="intimacao">📨 Gerar termo de intimação</button>` entre "Gerar Nota de Indiciação" e "Pauta de instrução por depoente" — a funcionalidade agora é alcançável pela UI.

**Testes:**
- Sintaxe: `new Function` sobre o `<script>` de `nexo-par.html` → **OK**.
- `node test-fluxo-integrado.js` → **127/127** (sem regressão).
- Playwright (Chromium): (a) confirmado por `getComputedStyle` que `.printview` tem z-index 1000 > `.topbar` (100) em ambos os arquivos; (b) chamada direta de `openPrint()` em ambos os arquivos → clique no botão "Imprimir / PDF" não é mais interceptado e `window.print()` é efetivamente chamado; (c) fluxo completo do Nexo PAR: botão "Gerar termo de intimação" presente no menu → modal com os 3 tipos ("Esclarecimento de fato", "Manifestação sobre prova", "Oitiva do representante legal") → destinatário listado pela razão social do ente → termo gerado exibe corretamente pessoa jurídica/CNPJ/representante legal, sem nenhum resquício de linguagem PAD (servidor/interrogatório/Lei 8.112/SV5) → impressão abre e `window.print()` é chamado.

## Correção: PDF de impressão trazia o mapa fato-prova-norma por cima do documento (Nexo Coger + Nexo PAR)

**Relato do usuário (com captura de tela):** ao gerar o PDF de intimação/indiciação, o topo da página mostrava os nós e conexões do mapa (ex.: "Oferecimento de vantagens indev...", "Frustração de caráter compet...") sobrepostos ao documento, diferente do resultado limpo já obtido em `Integritas.html`, `Dosimetria_TAC.html` e `Multa_PAR.html`.

**Causa:** a regra `@media print` de `nexo-coger.html`/`nexo-par.html` (linha ~516-523) escondia `.topbar,.hero,.lensbar,.panel,.footer,.fab,.col-headers`, mas **não** escondia `.main` — o container que envolve o SVG do mapa (`#map`, dentro de `.canvas-wrap`). Como `.printview` passa a `position:static` na impressão (para fluir como documento normal), o mapa (ainda visível, por não estar na lista de elementos ocultos) aparecia antes do conteúdo do `.pv-doc` na mesma página. O padrão usado em `Integritas.html`, por comparação, esconde tudo que não é o conteúdo de impressão (`body>*:not(#printPage){display:none!important}`) — mais abrangente do que a lista extensa e incompleta usada no Nexo.

**Correção:** adicionado `.main` à lista de seletores ocultos na regra `@media print` de ambos os arquivos (`.topbar,.hero,.lensbar,.main,.panel,.footer,.fab,.col-headers{display:none!important}`), linha 518 em `nexo-coger.html` e `nexo-par.html`. `.main` engloba tanto `.canvas-wrap` (mapa + cabeçalhos de coluna) quanto `.panel` (pendências), sem afetar `#printview`, que é irmão de `.main` no DOM (não descendente) — nenhum conteúdo de impressão é ocultado por engano.

**Testes:**
- `node test-fluxo-integrado.js` → **127/127** (sem regressão).
- Sintaxe: `new Function` sobre o `<script>` de ambos os arquivos → **OK**.
- Playwright com `page.emulateMedia({media:'print'})`: `getBoundingClientRect()` do `#map` retorna `width:0, height:0` (elemento efetivamente sem renderização sob mídia de impressão) em ambos os arquivos.
- PDF real gerado via `page.pdf()` (Chromium) para o termo de intimação (Nexo PAR, tipo "Oitiva do representante legal") renderizado e inspecionado visualmente: documento limpo, sem o mapa, no mesmo padrão de `Integritas.html`/`Multa_PAR.html`/`Dosimetria_TAC.html`.

## Correção: barra de rolagem horizontal no termo de intimação/indiciação (Nexo Coger + Nexo PAR)

**Relato do usuário (com captura de tela e o modelo do Integritas como referência):** mesmo após a correção do mapa sobreposto, o documento gerado continuava exibindo uma barra de rolagem horizontal, diferente do padrão limpo do `Integritas.html`.

**Causa:** o bloco de assinatura (`blocoAssinatura3`, compartilhado entre indiciação e intimação) desenhava a linha de assinatura como texto literal (`___________________________________`, ~35 caracteres). A tabela `table.sig3` usava `table-layout` padrão (`auto`), então o navegador dimensionava as colunas pelo conteúdo: essa sequência de sublinhados, por ser um token não quebrável, forçava a coluna — e a tabela inteira — a ultrapassar a largura disponível de `.pv-doc` (measurement confirmado via Playwright: `scrollWidth` de `.pv-doc` de 843px contra um `width` de 820px antes da correção, chegando a exceder em ~63px a área útil de 740px). Esse é exatamente o tipo de problema que `Integritas.html` evita: lá o "documento" é montado como página HTML própria (`#printPage`), sem depender de texto sublinhado para desenhar linhas.

**Correção (`ferramentas/nexo-coger.html` e `ferramentas/nexo-par.html`):**
- `table.sig3{table-layout:fixed}` — força as 3 colunas a respeitarem `width:33%` cada, independentemente do conteúdo.
- `table.sig3 td{overflow-wrap:break-word}` — rede de segurança para qualquer texto inesperadamente longo (sem `word-break:break-all`, que quebrava até números curtos como "1234567" no meio do dígito).
- `blocoAssinatura3()`: a linha de assinatura deixou de ser o texto `___________________________________` e passou a ser um `<div style="border-bottom:1px solid #333;width:90%;margin:0 auto 4px"></div>` — uma linha desenhada por CSS, do mesmo jeito visual mas sem forçar largura de coluna (mesmo princípio usado no Integritas, que também não depende de caracteres de sublinhado para desenhar linhas).

**Testes:**
- `node test-fluxo-integrado.js` → **127/127** (sem regressão).
- Sintaxe: `new Function` sobre o `<script>` de ambos os arquivos → **OK**.
- Playwright: `.pv-doc.scrollWidth` (820px) agora é **idêntico** a `.pv-doc.getBoundingClientRect().width` (820px) — sem overflow horizontal — tanto na tela quanto no PDF gerado via `page.pdf()` (Chromium), inspecionado visualmente: bloco de assinatura com linha contínua, sem quebra de dígitos, sem barra de rolagem.

## Rodada 9 — Guia de Estilo de Impressão Unificado (COGER Print Standard)

**Entrega de especificação:** "Rodada 9 — Guia de Estilo de Impressão Unificado (COGER Print Standard)" — documento especificativo que harmoniza a aparência impressa de todas as três ferramentas (Veritas, Nexo Coger, Oitiva 360) com o padrão visual consolidado do Integritas, sem quebrar a funcionalidade interativa. **Nenhuma alteração em ferramentas ou catálogo canônico nesta rodada**; é a criação de padrões reutilizáveis (CSS, HTML, JavaScript, documentação) que serão aplicados sequencialmente nas Rodadas 10–12.

**Arquivo especificativo fornecido pelo usuário:** `/root/.claude/uploads/175ecdf8-5887-57b7-9696-2a2c1672751d/e7b88c01-rodada9guiaestiloimpressao.md` (documentação completa com definições de variáveis CSS, estrutura de página, header/footer fixos, seções com barras laterais, info boxes, blocos legais, tabelas padronizadas, quebras de página e utilitários JavaScript).

**Entregáveis criados (`padroes/` — novo diretório):**

1. **`coger-print-standard.css`** — Arquivo CSS unificado com:
   - Definição de variáveis CSS COGER (paleta navy/gold, tipografia Inter/Barlow Condensed/JetBrains Mono, espaçamento A4/mm)
   - Estilos de header fixo (60px, com logos, título, metadata — referência INT-YYYYMMDD-XXXX, data, hora)
   - Estilos de footer fixo (40px, com referência, página X de Y, "USO INTERNO")
   - Seções numeradas com barra lateral ouro (3px)
   - Info boxes (dados estruturados com fundo cinza e borda)
   - Blocos legais (citações de lei com barra lateral navy)
   - Tabelas (cabeçalho navy com texto branco, linhas alternadas, bordas consistentes)
   - Página-breaks automáticos (orphans/widows, page-break-inside:avoid em seções/tabelas/boxes)
   - Classes utilitárias (.no-print, .coger-print-page-break-before, etc.)
   - Tudo encapsulado em `@media print { … }` — zero impacto na UI interativa

2. **`coger-print-template.html`** — Exemplo de markup HTML mostrando a estrutura esperada quando uma ferramenta adota o padrão:
   - Header com logos (SVG embutido), título, metadata
   - Main com ID `#printPage`
   - Seções com `.coger-print-section`, `.coger-print-section-title`, `.coger-print-section-body`
   - Info boxes com `.coger-print-infobox` + `.coger-print-infobox-row`
   - Tabelas com `.coger-print-table` + `.coger-print-table-head`
   - Blocos legais com `.coger-print-legal-block` + `.coger-print-legal-quote`
   - Footer com referência, paginação, nota institucional
   - Anotações comentadas para orientar integração

3. **`coger-print-utility.js`** — Funções JavaScript reutilizáveis:
   - `generatePrintReference()` — gera `INT-YYYYMMDD-XXXX` único
   - `formatDatePT(date)`, `formatTimePT(date)` — localização para português
   - `prepareForPrint(options)` — preenchimento de metadata no header/footer, zero de margens do body, disparo de evento `beforeprint`
   - `validatePrintStructure()` — validação de presença de elementos críticos
   - `estimatePrintPages()`, `updatePageCount(count)` — suporte a numeração
   - `onPrintButtonClick(event)` — listener pronto para plugar em botão `[data-act="print"]`
   - `initPrintSupport()` — inicialização completa (listeners, validação)
   - Exportável como módulo CommonJS (quando necessário)

4. **`GUIA-COGER-PRINT-STANDARD.md`** — Documentação de implementação:
   - Explicação de princípios (offline-first, CSS puro, sem regressão)
   - Passo a passo de integração (copiar CSS, adicionar header/footer HTML, copiar JS utility)
   - Descrição visual de cada elemento (seções, info boxes, blocos legais, tabelas)
   - Referência de paleta de cores (9 variáveis)
   - Referência de tipografia (3 fontes, usos específicos)
   - Referência de espaçamento e margens
   - Explicação de quebras de página (automáticas e forçadas)
   - Guia de funções JavaScript disponíveis
   - Exemplo de fluxo completo (click → prepareForPrint → window.print)
   - Seção de testes (navegador, headless)
   - Troubleshooting (header não aparece, conteúdo cortado, etc.)
   - Tabela de referência rápida de classes/IDs

**Diretório criado:** `/home/user/desktop-tutorial/padroes/` — novo diretório centralizado para padrões reutilizáveis da suíte.

## Rodada 10 — Implementação do COGER Print Standard no Veritas

Integração completa do padrão unificado de impressão criado na Rodada 9 no arquivo `ferramentas/veritas.html`.

**Implementação:**
- **CSS COGER Print Standard:** integrado em bloco `@media print { … }` com:
  - Definição de variáveis CSS (9 cores navy/gold, 3 fontes, espaçamento A4)
  - Header fixo 60px com logos SVG, título "DOSSIÊ DE ANÁLISE...", metadata (ref, data, hora)
  - Footer fixo 40px com referência, paginação "Página X de Y", nota "USO INTERNO"
  - Page-break rules (orphans/widows, avoid para títulos/seções/tabelas/imagens)
  - Estilos de tabelas (cabeçalho navy, alternância cinza, bordas consistentes)
  - Utilidades (.no-print, .coger-print-page-break-before, etc.)
- **HTML Elements:**
  - `<header class="coger-print-header">` com logos, título, metadata (IDs: coger-print-ref, coger-print-date, coger-print-time)
  - `<footer class="coger-print-footer">` com referência (ID: coger-print-footer-ref), paginação, nota institucional
  - Ambos `display:none` por padrão, exibidos apenas em `@media print`
- **JavaScript Utilities:** (embutido no `<script>` principal)
  - `generatePrintReference()` — `INT-YYYYMMDD-XXXX` único
  - `formatDatePT(date)`, `formatTimePT(date)` — localização português
  - `prepareForPrint(options)` — preenche metadata header/footer, limpa margens, dispara `beforeprint`

**Validação:**
- Sintaxe verificada: 105 ocorrências de "coger-print", função `prepareForPrint` presente
- Estrutura HTML balanceada (closing tags corretos)
- CSS restrito a `@media print` — **zero impacto na UI interativa** (Veritas continua 100% funcional em tela)
- Alinhamento com Rodada 9: mesmas variáveis, classes, estrutura header/footer

**Próximas rodadas (dependentes):**
- **Rodada 11 — Implementação no Nexo Coger:** Integrar `coger-print-standard.css` no `ferramentas/nexo-coger.html`, adaptar markup de impressão existente às classes do padrão.
- **Rodada 12 — Implementação no Oitiva 360:** Idem para `ferramentas/oitiva-360.html` (termo de oitiva).
