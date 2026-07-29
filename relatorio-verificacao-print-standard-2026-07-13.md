# Relatório de Verificação — COGER Print Standard (Rodada 13)

**Data/hora da execução:** 2026-07-13
**Navegador:** Chromium (via Playwright, `/opt/pw-browsers/chromium`)
**Firefox:** ❌ não disponível neste ambiente de execução — item 3 (paridade Chrome/Firefox) **não pôde ser testado**. Recomenda-se repetir a Camada 3 em Firefox antes do aceite final em produção.
**Ambiente:** todos os testes executados via `file://` (sem servidor), replicando o uso real.
**Fixtures usados:** `fixtures/pad-ficticio-001.json`, `fixtures/par-ficticio-001.json` (via `test-fluxo-integrado.js`).
**Metodologia:** Playwright dirigindo os 4 arquivos reais (`ferramentas/*.html`), sem mocks; `test-fluxo-integrado.js` executado sem modificação.
**Scripts produzidos nesta rodada** (reutilizáveis, em `scripts/`): `verify-camada1.js`, `verify-camada1b.js`, `verify-camada2-3.js`, `verify-camada3-nexo2.js`, `verify-camada3-oitiva2.js`, `verify-camada3-veritas.js`, `verify-camada4-terminologia.sh`.

---

## Sumário Executivo

| Ferramenta | Camada 1 | Camada 2 | Camada 3 | Camada 4 |
|---|---|---|---|---|
| **Veritas** | ✅ Passou | ✅ Passou | ✅ Passou (2/3 seções — 3ª condicional, correto) | N/A (não gera minuta formal) |
| **Nexo Coger** | ✅ Passou | ✅ Passou | ⚠️ **Passou com ressalvas críticas** (ver 3.2) | ⚠️ Nota de Indiciação: conteúdo OK; Termo de Intimação: **não avaliável** (sem Print Standard) |
| **Nexo PAR** | ❌ **Falhou** (zero Print Standard) | ✅ Passou (lógica de negócio intacta) | ⛔ Bloqueado pela Camada 1 | ⛔ Bloqueado pela Camada 1 (conteúdo textual correto via função pura, mas wrapper visual é 100% legado) |
| **Oitiva 360** | ⚠️ Passou com nota (ver 1.2) | ✅ Passou | ✅ Passou | ✅ Passou |

**Conclusão preliminar:** **Aprovado com ressalvas para Veritas e Oitiva 360. Reprovado para Nexo PAR (Camada 1 bloqueante). Nexo Coger aprovado com ressalva crítica em duas peças específicas** — a tabela de síntese fato-prova-norma da Nota de Indiciação e a totalidade do Termo de Intimação não seguem o Print Standard, apesar de descritos como concluídos na documentação da Rodada 11 e no apêndice produzido nesta sessão.

---

## CAMADA 1 — Integridade Estrutural

### 1.1 Resultado por ferramenta

| Item | Veritas | Nexo Coger | Nexo PAR | Oitiva 360 |
|---|---|---|---|---|
| Abre sem erro (file://) | ✅ | ✅ | ✅ | ✅ |
| Console sem erros JS | ✅ (0 erros) | ✅ (0 erros) | ✅ (0 erros) | ✅ (0 erros) |
| Console sem erros de CSS | ✅ | ✅ | ✅ | ✅ |
| Screenshot inicial não-branco | ✅ (458 KB) | ✅ (331 KB) | ✅ (339 KB) | ✅ (479 KB) |
| Zero requisições de rede (http/https) | ✅ (0) | ✅ (0) | ✅ (0) | ✅ (0) |
| Single-file via `file://` | ✅ | ✅ | ✅ | ✅ |

### 1.2 Variáveis CSS (`--coger-print-navy-900`, `--coger-print-gold-500`)

| Ferramenta | `--coger-print-navy-900` | `--coger-print-gold-500` | `window.CogerPrint` presente ao carregar |
|---|---|---|---|
| Veritas | `#0B2F5F` ✅ | `#C9A35C` ✅ | ✅ sim |
| Nexo Coger | `#0B2F5F` ✅ | `#C9A35C` ✅ | ✅ sim |
| **Nexo PAR** | **`` (vazio) ❌** | **`` (vazio) ❌** | **❌ não** |
| Oitiva 360 | `#0B2F5F` ✅ | `#C9A35C` ✅ | ⚠️ **não ao carregar** — só após renderizar a Etapa 4 do wizard (ver nota) |

**FALHA CRÍTICA — Nexo PAR:** nenhuma variável do Print Standard existe no arquivo. Confirmado por grep: `ferramentas/nexo-par.html` tem **zero** ocorrências de `coger-print-navy-900`, `coger-print-header`, `CogerPrint`, contra 31 ocorrências em `nexo-coger.html`. O `@media print` de `nexo-par.html` continua sendo o mesmo bloco mínimo de ~8 linhas anterior à Rodada 9 (linha 518), sem header/footer fixo, sem seções com barra gold, sem nada do padrão. **Isso indica que a Rodada 11-PAR (mencionada como opção no Apêndice de formatos) nunca foi executada** — o fork `nexo-par.html` foi feito antes da Rodada 9/10/11 e nunca recebeu o Print Standard.

**Nota (Oitiva 360, não bloqueante):** diferente de Veritas e Nexo Coger — onde `window.CogerPrint` é definido no escopo top-level do `<script>` e existe desde o carregamento da página —, em `oitiva-360.html` o módulo `window.CogerPrint` foi colocado dentro da função `ligarEventosEtapa4()` (Rodada 12, linha ~6986), que só executa quando o wizard chega à Etapa 4 de um depoente específico. Funcionalmente isso não quebra nada (confirmado na Camada 3 — o fluxo completo funciona), mas é uma inconsistência arquitetural em relação ao padrão estabelecido nas Rodadas 10-11, e tecnicamente falha o item "nenhuma variável CSS retorna undefined" se testado antes de se alcançar a Etapa 4.

### Critério de saída da Camada 1

- **Veritas: ✅ aprovado**
- **Nexo Coger: ✅ aprovado**
- **Nexo PAR: ❌ reprovado** — bloqueia Camadas 3 e 4 para esta ferramenta.
- **Oitiva 360: ✅ aprovado com nota** (arquitetura do `window.CogerPrint` deveria ser movida para escopo top-level, alinhando com Rodadas 10-11 — recomendado para rodada de correção, não implementado nesta verificação).

---

## CAMADA 2 — Não Regressão Funcional

### 2.1 `test-fluxo-integrado.js` (execução literal, não apenas leitura de código)

```
Total: 127 passaram, 0 falharam, de 127 verificações.
▓▓▓ Fluxo PAD: 43/43 ✅
▓▓▓ Fluxo PAR: 58/58 ✅
▓▓▓ Validação cruzada: 26/26 ✅
```

Cobre: wizard de prova do Veritas (hash, proveniência, campos travados), pendências P1-P8/P8-PAR/P-ENTE, geração de Nota de Indiciação PAR com todos os marcadores de conteúdo, contratos de integração (Veritas↔Nexo Coger↔Oitiva 360↔Nexo PAR), idempotência de reimportação, validação cruzada de domínio (5 casos, incluindo rejeição de prova PAR em Nexo Coger e vice-versa). **Nenhuma regressão detectada nesta suíte.**

**Observação (não regressão, pré-existente):** a saída de `validarCatalogo()` no console do Oitiva 360 mostra `blocos: 16 (esperado: 13)` e `perguntasGerais: 48 (esperado: 28)` — os números reais do catálogo divergem dos comentários "esperado" hardcoded na função. Confirmado via `git show HEAD~1` que essa divergência **já existia antes da Rodada 12** (não foi introduzida pelo Print Standard) — é um comentário desatualizado de rodadas anteriores (provavelmente Rodada 5/6), fora do escopo desta verificação, mas registrado para rodada de limpeza futura.

### 2.2–2.6 Checklist por ferramenta (smoke test dirigido)

| Verificação | Resultado |
|---|---|
| Veritas: wizard 4 etapas, hash, campos travados | ✅ coberto por `test-fluxo-integrado.js` (fluxo PAD/PAR completo) |
| Nexo Coger: gate "Dados do Processo", pendências P1/P2/P5/P8 bloqueando minuta | ✅ **confirmado visualmente** — no cenário de exemplo (3 pendências críticas ativas: P1, P8, P5), o botão "Gerar minuta do termo de indiciação" aparece **desabilitado** (cinza), exatamente como documentado |
| Nexo PAR: isolamento do fork, ausência de dolo/culpa, P8-PAR/P-ENTE | ✅ coberto por `test-fluxo-integrado.js` (par_passo1-8) |
| Oitiva 360: matriz de apuração, wizard 4 etapas, geração automática de termo | ✅ **fluxo completo dirigido via Playwright** até a Etapa 4 (34 perguntas no roteiro carregadas corretamente), botão "Imprimir termo" funcional |
| Integração entre ferramentas (4 contratos) | ✅ coberto por `test-fluxo-integrado.js` (passo5-7, par_passo5-7) |

### Critério de saída da Camada 2

**✅ Aprovado nas 4 ferramentas** — nenhuma regressão de lógica de negócio detectada. O trabalho de Print Standard (Rodadas 10-12) não alterou nenhum comportamento funcional pré-existente.

---

## CAMADA 3 — Conformidade Visual (Print Standard)

> Bloqueada para **Nexo PAR** pela falha da Camada 1 (nenhum elemento do Print Standard existe no arquivo). Avaliada para as outras 3.

### 3.1 Checklist por ferramenta

| Item | Veritas | Nexo Coger (Nota de Indiciação) | Nexo Coger (Termo de Intimação) | Oitiva 360 |
|---|---|---|---|---|
| Header idêntico em todas as páginas | ✅ `.coger-print-header` presente, `position:fixed` | ✅ presente | ❌ **inexistente** — usa `openPrint()`/`.pv-doc` (renderer legado, pré-Print Standard) | ✅ presente |
| Logos MF+RFB, ~40px | ✅ (data URI SVG) | ✅ (data URI SVG) | ❌ N/A | ✅ (reutiliza `obterLogoRFBDataUri()`) |
| Referência `INT-YYYYMMDD-XXXX` no header | ✅ (placeholder verificado; preenchimento real ocorre em `prepareForPrint()`) | ✅ (`INT-20260713-0993` gerado ao vivo) | ❌ N/A | ✅ (`INT-20260713-6832` gerado ao vivo) |
| Mesma referência no footer | ✅ | ✅ | ❌ N/A | ✅ |
| Data por extenso em português | ✅ (`formatDatePtBr`) | ✅ | ❌ N/A | ✅ |
| Footer idêntico em todas as páginas | ✅ | ✅ | ❌ N/A | ✅ |
| Paginação "Página X de Y" | ✅ (`.page-number`/`.page-count`) | ✅ | ❌ N/A | ✅ |
| Nota "USO INTERNO" | ✅ | ✅ | ❌ N/A | ✅ |
| Seções numeradas com barra gold | ✅ (2 seções na amostra testada — 3ª "Linha do Tempo" é condicional, correto) | ✅ (7 seções: Qualificação, Fatos, Provas, Enquadramento, Síntese, Defesa, Encerramento) | ❌ N/A | ✅ (3 seções: Identificação, Perguntas e Respostas, Encerramento) |
| Nenhum elemento interativo na impressão | ✅ | ✅ (seção 6 usa `.no-print` no bloco editável de defesa) | ❌ N/A | ✅ |
| Tipografia Barlow Condensed/Inter | ✅ (variáveis aplicadas) | ✅ | ❌ N/A | ✅ |
| Paleta exclusivamente COGER | ✅ | ✅ | ❌ N/A | ✅ |

### 3.2 Tabelas (Nexo Coger) — **FALHA CRÍTICA**

Item do checklist: *"`<thead>` da tabela é replicado em cada página onde a tabela continua"*.

**Resultado: ❌ REPROVADO.**

Inspecionando o HTML real gerado por `renderIndiciacao()` (seção 5 — Síntese Fato-Prova-Norma):

```html
<table class="qual fp"><tbody><tr><td><b>Fatos de que se acusa</b></td>...
```

A tabela **não tem `<thead>`** — a primeira linha é um `<tr>` comum dentro do `<tbody>` implícito. A classe aplicada é `qual fp` (classe legada, pré-Rodada 11), não `coger-print-table`.

**Causa raiz identificada** — `ferramentas/nexo-coger.html`, linha 4779:

```js
tabelaFatoProvaEnquadramento(fatos).replace(/class="fact-proof-table"/g, 'class="coger-print-table"')
```

A função `tabelaFatoProvaEnquadramento()` (linha 4633-4647) gera a tabela com `class="qual fp"` — **nunca** `class="fact-proof-table"`. O `.replace()` procura uma classe que a função nunca produziu; a substituição é um no-op silencioso. Resultado prático:

- A tabela nunca recebe a classe `coger-print-table`.
- Nunca recebe o CSS de header navy/replicação de thead (`.coger-print-table thead { display: table-header-group }`) — porque nem sequer existe um elemento `<thead>` no HTML gerado.
- Em um documento de produção com 15+ fatos (múltiplas páginas), o cabeçalho da tabela **não se repete** — cada página de continuação mostra linhas de dados sem saber a que coluna pertencem.

Isso **contradiz diretamente** a entrada da Rodada 11 no `CHANGELOG-catalogo.md` ("✅ Tabela de síntese com cabeçalho replicado em cada página de quebra") — a implementação documentada como concluída nunca funcionou.

**Severidade: CRÍTICA.** Bloqueia o uso em produção de qualquer Nota de Indiciação com mais de ~1 página de tabela (típico em processos com múltiplos fatos).

### 3.3 Q&A (Oitiva 360)

| Item | Resultado |
|---|---|
| Pergunta em negrito, resposta normal | ✅ confirmado (`<strong>P1. ...</strong>` / `<strong>R:</strong> ...`) |
| Cada P/R na mesma página | ✅ CSS `.coger-print-qa-item { page-break-inside: avoid }` presente |
| Espaçamento consistente | ✅ `margin-bottom: 10pt` uniforme em todos os 34 itens testados |
| Contagem de itens | ✅ 34 perguntas do roteiro → 34 `.coger-print-qa-item` gerados (1:1, nenhuma perda no parsing) |

### 3.4 Consistência cruzada (Veritas / Nexo Coger / Oitiva 360)

| Item | Resultado |
|---|---|
| Mesmo navy/gold nas 3 ferramentas | ✅ `#0B2F5F` / `#C9A35C` idêntico nas 3 (Nexo PAR excluído — não aplicável) |
| Mesma tipografia título/corpo | ✅ mesmas variáveis `--coger-print-font-display`/`--coger-print-font-sans` |
| Layout de header idêntico | ✅ mesma estrutura `coger-print-header-logos` / `-title` / `-meta` |
| Layout de footer idêntico | ✅ mesma estrutura `-left`/`-center`/`-right` |
| `coger-print-infobox` visualmente idêntico | ✅ mesmas classes/CSS nas 3 |
| "Mesma suíte" à primeira vista (teste qualitativo) | ✅ **sim** — as 3 impressões (Nota de Indiciação, dossiê Veritas, termo de Oitiva) compartilham header/footer/paleta indistinguíveis; a única peça destoante é o **Termo de Intimação do Nexo Coger**, que continua com o layout legado pré-Rodada 9 e destoa visivelmente das demais |

### Critério de saída da Camada 3

- **Veritas: ✅ aprovado**
- **Oitiva 360: ✅ aprovado**
- **Nexo Coger: ⚠️ aprovado com ressalva crítica** — Nota de Indiciação aprovada exceto a tabela de síntese (falha crítica, 3.2); Termo de Intimação **reprovado** (nunca migrado ao Print Standard).
- **Nexo PAR: ⛔ bloqueado** (Camada 1 falhou).

---

## CAMADA 4 — Conformidade Documental (Formatos Jurídicos)

### 4.1 FORMATO 1 — Termo de Intimação (Nexo Coger, PAD)

**Não avaliável quanto ao Print Standard** (Camada 3 reprovada — sem header/footer/seções). Quanto ao **conteúdo textual** (função `renderIntimacao()`, formato legado `openPrint()`/`.pv-doc`):

- ✅ Identifica servidor (nome, matrícula via `acusadoById`), cargo, unidade.
- ✅ Referencia processo, comissão (via `blocoAssinatura3(c)`).
- ✅ Três tipos de intimação suportados: esclarecimento de fato, manifestação sobre prova, interrogatório — mais amplo que o único formato descrito no Apêndice (7 seções fixas), sugerindo que o Apêndice descreveu um formato idealizado que diverge da implementação real, ou que a implementação real é mais flexível e não segue a estrutura de 7 seções fixas do Apêndice.
- ⚠️ **Estrutura não corresponde ao Apêndice**: o Apêndice descreve 7 `<section class="coger-print-section">` fixas; a implementação real gera um documento de parágrafos corridos (`<p class="center">`), sem seções numeradas, sem `coger-print-section-title`. **O Apêndice (`CLAUDE-CODE-RODADA-11-APENDICE.md`, produzido nesta mesma sessão) descreve incorretamente o Termo de Intimação como já implementado com Print Standard — isso deve ser corrigido no próprio apêndice.**

### 4.2 FORMATO 2 — Termo de Intimação (Nexo PAR)

**Não avaliável** — Nexo PAR não possui nenhuma função equivalente identificada para "Termo de Intimação" dedicado (apenas `renderIndiciacao` para a Nota). Se este formato existe, está fora do escopo desta verificação por não ter sido localizado; recomenda-se diagnóstico D1-D4 específico numa rodada de correção.

### 4.3 FORMATO 3 — Nota de Indiciação (Nexo Coger, PAD)

Verificado via renderização real (`renderIndiciacao('A1', doc)` com fixture de exemplo):

- ✅ Identificação do acusado consistente (nome, matrícula, cargo, lotação).
- ✅ Fatos apurados numerados ("Fato 1", "Fato 2" na tabela de síntese).
- ⚠️ **Não verificado**: se a ordem reflete o painel "Ordem dos Fatos" da Toolbar — teste não realizado por restrição de tempo; a função usa `fatosOrdenados()`, cujo critério de ordenação não foi auditado nesta rodada.
- ✅ Tabela lista apenas fatos ativos do acusado selecionado (`!fatoArquivado(x)`).
- ✅ Enquadramento legal presente (`art. 117, IX, Lei nº 8.112/90`, `art. 116, III, Lei nº 8.112/90`).
- ❌ **Ver 3.2** — tabela sem `<thead>` replicado (falha crítica de apresentação, não de conteúdo).

### 4.4 FORMATO 4 — Nota de Indiciação (Nexo PAR)

Verificado via `test-fluxo-integrado.js` (`par_passo8`, 18 marcadores, todos ✅):

- ✅ Identificação do investigado com CNPJ (não matrícula).
- ✅ "Conduta lesiva"/"ato lesivo" (terminologia correta, não "infração funcional").
- ✅ Enquadramento exclusivo Lei nº 12.846/2013, art. 5º, IV.
- ✅ Estimativa de danos e faturamento bruto presentes.
- ✅ Prazo de 30 dias, programa de integridade, Termo de Compromisso/Acordo de Leniência.
- ⚠️ **Ressalva de escopo**: estes marcadores foram verificados na função de **texto puro** `NexoPar.construirTextoIndiciacao()`, não na função de renderização DOM `renderIndiciacao()` do arquivo `nexo-par.html` (que carece de Print Standard — Camada 1). Não foi confirmado nesta rodada se as duas funções produzem exatamente o mesmo texto, ou se a função DOM tem uma implementação de conteúdo divergente da função pura testada.

### 4.5 Verificação cruzada de terminologia (script reutilizável)

Script produzido: `scripts/verify-camada4-terminologia.sh`. Escopo: apenas as funções de geração de documento (`renderIndiciacao`, `renderIntimacao`), não o arquivo inteiro — o catálogo canônico embutido referencia normas de ambos os domínios por design (validação cruzada), o que não constitui contaminação.

```
=== Nexo Coger — renderIndiciacao/renderIntimacao não devem conter termos PAR ===
   (nenhuma ocorrência) — ambas as funções
=== Nexo PAR — renderIndiciacao não deve conter termos PAD ===
   (nenhuma ocorrência)
```

**✅ Aprovado.** Nenhuma contaminação terminológica cruzada nas funções de geração de documento.

### Critério de saída da Camada 4

- **Nexo Coger (Nota de Indiciação): ✅ conteúdo aprovado / ❌ apresentação reprovada (3.2)**
- **Nexo Coger (Termo de Intimação): ⚠️ conteúdo funcional mas estrutura diverge do Apêndice; apresentação reprovada**
- **Nexo PAR: ⛔ bloqueado pela Camada 1** (conteúdo textual correto via função pura, mas não confirmado na função DOM real)
- **Terminologia cruzada: ✅ aprovado**

---

## Lista Consolidada de Não Conformidades

| # | Severidade | Ferramenta | Descrição | Camada |
|---|---|---|---|---|
| 1 | **Crítica** | Nexo Coger | Tabela de síntese fato-prova-norma (Nota de Indiciação) nunca recebe a classe `coger-print-table` — o `.replace()` na linha 4779 procura `class="fact-proof-table"`, mas `tabelaFatoProvaEnquadramento()` gera `class="qual fp"`. Sem `<thead>`, sem replicação de cabeçalho em quebras de página. Bloqueia uso em produção para processos com múltiplos fatos. | 3.2 |
| 2 | **Crítica** | Nexo Coger | `renderIntimacao()` (Termo de Intimação) nunca foi migrado ao Print Standard — usa o renderer legado `openPrint()`/`.pv-doc`, sem header/footer fixo, sem seções, sem paleta/tipografia COGER. Destoa visivelmente das demais peças da suíte. | 3.1, 3.4, 4.1 |
| 3 | **Crítica** | Nexo PAR | Nenhum elemento do Print Standard existe no arquivo (`nexo-par.html`) — zero variáveis CSS, zero classes `coger-print-*`, `@media print` ainda no formato pré-Rodada 9. A Rodada 11-PAR mencionada como opção no Apêndice nunca foi executada. | 1.2 |
| 4 | Documental | — | `CLAUDE-CODE-RODADA-11-APENDICE.md` (produzido nesta sessão) descreve o Termo de Intimação como implementado com estrutura de 7 seções Print Standard — isso não corresponde à implementação real (não conformidade nº 2). O apêndice precisa de correção. | 4.1 |
| 5 | Visual/cosmética | Oitiva 360 | `window.CogerPrint` é definido dentro de `ligarEventosEtapa4()` em vez de escopo top-level (padrão das Rodadas 10-11) — funcionalmente inofensivo (fluxo completo testado e aprovado), mas inconsistente arquiteturalmente. | 1.2 |
| 6 | Cosmética (pré-existente, não é regressão) | Oitiva 360 | Comentários "esperado" em `validarCatalogo()` desatualizados em relação ao catálogo real (`blocos: 16 vs. esperado 13`, etc.) — confirmado pré-existente antes da Rodada 12, fora do escopo do Print Standard. | 2.1 |
| 7 | Escopo não testado | Nexo Coger / Nexo PAR | Item 4.3 (ordem dos fatos na minuta vs. painel "Ordem dos Fatos") e item 4.4 (paridade função pura vs. função DOM no Nexo PAR) não foram auditados nesta rodada por restrição de tempo. | 4.3, 4.4 |
| 8 | Ambiente de teste | Todas | Testes de paridade Firefox não puderam ser executados — Firefox não está instalado neste ambiente (apenas Chromium via Playwright). | 3 |

---

## Conclusão e Critérios de Aceite Geral

| Camada | Critério (100% exigido) | Resultado |
|---|---|---|
| Camada 1 | 4 ferramentas aprovadas | **❌ 3/4** — Nexo PAR reprovado |
| Camada 2 | 4 ferramentas + test-fluxo-integrado.js | **✅ 4/4 + 127/127** |
| Camada 3 | 4 ferramentas aprovadas | **❌ 2/4 aprovadas sem ressalva** (Veritas, Oitiva 360); Nexo Coger com ressalva crítica; Nexo PAR bloqueado |
| Camada 4 | 4 formatos aprovados | **❌ 1/4 aprovado sem ressalva** (Nota de Indiciação PAR); demais com ressalva ou bloqueados |

### Veredito final: **REPROVADO** para uso em produção sem correções.

**Aprovado para uso imediato:**
- ✅ **Veritas** — Print Standard completo e funcional.
- ✅ **Oitiva 360** — Print Standard completo e funcional (com nota cosmética não bloqueante, item 5).

**Aprovado com ressalva — usar com cautela até correção:**
- ⚠️ **Nexo Coger — Nota de Indiciação**: usável para processos de fato único ou tabela cabendo em 1 página; **não usar em produção para processos com múltiplos fatos** até a não conformidade nº 1 ser corrigida.

**Bloqueado — não usar em produção:**
- ⛔ **Nexo Coger — Termo de Intimação**: sem Print Standard; destoa da suíte.
- ⛔ **Nexo PAR — ambas as minutas**: sem nenhum elemento do Print Standard.

### Itens que bloqueiam a aprovação plena (correção necessária antes de nova homologação)

1. Corrigir a linha 4779 de `nexo-coger.html` para que a tabela de síntese realmente receba `class="coger-print-table"` **e** estrutura `<thead>`/`<tbody>` — refatorar `tabelaFatoProvaEnquadramento()` para gerar HTML com `<thead>` explícito.
2. Migrar `renderIntimacao()` (Termo de Intimação, Nexo Coger) ao Print Standard — mesma estrutura `#printPage`/header/footer/seções usada em `renderIndiciacao()`.
3. Executar uma Rodada 11-PAR (ou equivalente) para levar o Print Standard completo a `nexo-par.html` — ambas as minutas (Termo de Intimação, se existir, e Nota de Indiciação).
4. Corrigir `CLAUDE-CODE-RODADA-11-APENDICE.md` para não afirmar que o Termo de Intimação já segue o Print Standard.
5. (Não bloqueante) Mover `window.CogerPrint` em `oitiva-360.html` para escopo top-level.
6. (Não bloqueante) Auditar ordem dos fatos na minuta vs. painel "Ordem dos Fatos" (item 7 da lista de não conformidades).
7. (Não bloqueante) Repetir Camada 3 em Firefox antes do aceite final.

Conforme instrução da Rodada 13, **nenhuma correção foi aplicada nesta verificação** — este relatório é fiel ao estado atual do código, e as correções pertencem a uma rodada subsequente.
