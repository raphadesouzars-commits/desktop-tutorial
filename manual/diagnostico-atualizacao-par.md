# Diagnóstico — Atualização do Manual da Suíte COGER para o Domínio PAR

Relatório de diagnóstico (item 0 da spec `2033b568-orientacaoatualizacaomanualpar.md`). **Somente leitura + este relatório.** Não edita `build_manual.py`, não gera `.docx`, não faz commit. As duas próximas rodadas (outros agentes) usarão este documento como guia.

Fontes cruzadas: 6 specs PAR (`rodadapar1..6`), `CHANGELOG-catalogo.md` (histórico real, mais confiável que as specs — item 0 da spec: "onde spec e código divergirem, o código manda"), e o código real de `veritas.html`, `nexo-coger.html`, `nexo-par.html`, `oitiva-360.html`. Onde cito código, uso arquivo + linha confirmados na leitura de julho/2026.

> **Convenção de numeração deste relatório:** "Seção N atual" = numeração do manual publicado hoje (Veritas 2, Nexo Coger 3, Oitiva 360 4, Integração 5). "Seção N nova" = numeração-alvo pós-renumeração (Nexo PAR entra como 4, Oitiva 360 → 5, Integração → 6).

---

## 1. Checklist de cobertura: rodada PAR × manual atual

Legenda: ✅ já coberto corretamente · ⚠️ precisa de ajuste pontual · ❌ não coberto, exige conteúdo novo.

### Rodada PAR-1 — Extensão do catálogo canônico (LAC)

| # | Entregável / critério de aceite | Status | Onde / o que falta |
|---|---|---|---|
| 1.1 | Campo `dominio` (`pad`/`par`/`comum`) em todos os itens do catálogo; PAD preservado | ❌ | Manual atual não menciona a existência do campo `dominio` em lugar nenhum. É conceito estruturante de tudo que segue. Deve entrar na Introdução (Seção 1 nova) e no Glossário (entrada "Domínio"). |
| 1.2 | 11 normas `NORMA.LAC.*` (art. 5º LAC), 2 optgroups | ❌ | Nenhuma menção. Entra na nova Seção 4 (Nexo PAR, seletor de enquadramento) e na Seção 5 nova (Oitiva 360, categoria de infração PAR). Inventário completo no item 4 deste relatório. |
| 1.3 | 4 papéis PAR (ENTE_PRIVADO, REPRESENTANTE_LEGAL, PREPOSTO, SOCIO_ADMINISTRADOR) | ❌ | Não coberto. A Seção 3.4/3.3 atual lista só os 5 papéis PAD. Entra na nova Seção 4 (cadastro de ente) e Seção 5 nova (papéis de depoente PAR) + Glossário. |
| 1.4 | 2 tipos de prova PAR (PROGRAMA_INTEGRIDADE, INFORMACOES_COAF); EMPRESTADA=comum | ⚠️ | A Seção 2.1 atual lista as categorias de prova do Veritas sem as duas PAR. Precisa da nota "quando `dominio: par`, surgem as categorias Programa de integridade e Informações do COAF" (escopo item 2 da spec, Veritas). |
| 1.5 | `TIPOS_PROCESSO` completado com PAR e IPS (PN CGU 27) | ⚠️ | A Seção 3.1 atual descreve o campo "Tipo (PN CGU 27)" com **só os 5 tipos PAD** (IP, SINVE, SINPA, SINAC, PAD). Após PAR-1 o catálogo tem IPS (investigativos) e PAR (acusatórios). A lista da Seção 3.1 está desatualizada — ver Divergência D-8. |

### Rodada PAR-2 — Veritas modo dual

| # | Entregável / critério de aceite | Status | Onde / o que falta |
|---|---|---|---|
| 2.1 | Campo "Tipo de processo" (opcional) nos Dados do processo + derivação de `dominio` | ❌ | A Seção 2 atual não descreve esse campo. Escopo item 2 da spec: inserir em 2.1/Dados do processo, com nota de que é opcional e que sem ele o Veritas fica agnóstico de domínio. |
| 2.2 | Categorias de prova sensíveis a domínio (fallback ao atual) | ⚠️ | Ver 1.4. Nota na Seção 2.1: categorias PAR extras só aparecem com tipo=PAR. |
| 2.3 | Campo `dominio` emitido nos dois contratos de exportação ("Exportar .json" e "Exportar provas → Nexo Coger") | ❌ | A Seção 2.3 e a Seção 5.1 atual não mencionam `dominio` no envelope. Entra na Seção 2.3 e na Seção 6 nova (integração). |
| 2.4 | Textos neutros (disclaimer/tela de processo passaram a "PAD/sindicância/PAR") | ⚠️ | Baixa prioridade; o manual não cita esses textos literais. Mencionar na Introdução que a suíte cobre PAD, PAR e sindicância. |
| 2.5 | Retrocompatibilidade (dossiê antigo importa sem `tipoProcesso`) | ⚠️ | Vale uma FAQ no Veritas (spec item 8). |

### Rodada PAR-3 — Fork Nexo PAR

| # | Entregável / critério de aceite | Status | Onde / o que falta |
|---|---|---|---|
| 3.1 | Identidade Nexo PAR; tipo pré-selecionado PAR; `dominio:'par'`; nome de arquivo `nexo-par-*` | ❌ | Ferramenta inteira ausente do manual. Nova Seção 4. |
| 3.2 | Cadastro de ente privado (razão social, CNPJ, representantes, solidariedade, sucessão, desconsideração art. 14) | ❌ | Nova Seção 4, campo a campo (inventário no item 4). |
| 3.3 | Remoção do elemento subjetivo e da pendência P8 (LAC objetiva, art. 2º) | ❌ | Nova Seção 4 + nota "o que NÃO existe no PAR". A Seção 3 atual descreve elemento subjetivo/P8 como PAD — correto lá, mas precisa contraste na Seção 4. |
| 3.4 | Benefício/interesse + nexo causal obrigatórios; nova pendência P8-PAR (crítica) | ❌ | Nova Seção 4 (campos do fato + tabela de pendências). |
| 3.5 | Seletor de enquadramento só LAC (11 normas, 2 optgroups, `nota_aplicacao` como hint) | ❌ | Nova Seção 4. |
| 3.6 | Nota de Indiciação PAR (art. 17 IN CGU 13/2019 + 4 textos complementares) | ❌ | Nova Seção 4 (estrutura completa no item 4). |
| 3.7 | Catálogo de pendências revisado (P8 removida, P8-PAR e P-ENTE novas, P6b reescrita, prazos) | ❌ | Nova Seção 4 (tabela de pendências no formato da Seção 3.5). |
| 3.8 | Preparação Multa_PAR (só comentário-âncora, sem UI) | ✅ | Nada a documentar no manual (não há UI/contrato). Mencionável de passagem. |
| 3.9 | O que NÃO muda (mapa, toolbar, import de provas, exportação de pauta) | ❌ | Nova Seção 4, nota final "o que não muda vs. Nexo Coger". |
| CA | `nexo-coger.html` byte a byte inalterado | ✅ | Seção 3 atual permanece factualmente válida; precisa só da nota de abertura "esta seção é o domínio PAD". |

### Rodada PAR-4 — Oitiva 360 modo dual

| # | Entregável / critério de aceite | Status | Onde / o que falta |
|---|---|---|---|
| 4.1 | Seletor de domínio na Matriz de Apuração (cascata manual→pauta→trava→confirmação de conflito) | ❌ | Seção 5 nova (ex-4.1). A Matriz atual tem 4 campos; agora são 5 (Domínio). |
| 4.2 | Categoria de infração sensível a domínio (52/53 normas PAD vs. 11 LAC + hint) | ⚠️ | A Seção 4.4 atual descreve "52 normas" agrupadas — precisa do ramo PAR (11 LAC, 2 optgroups). |
| 4.3 | Papéis de depoente por domínio (3 PAR entram, ACUSADO sai no PAR) | ⚠️ | A Seção 4.4 atual lista 5 papéis PAD. Precisa da tabela PAD-lado × PAR-lado. |
| 4.4 | Banco de perguntas: 3 blocos PAR novos | ❌ | Seção 5 nova. Descrever finalidade dos 3 blocos (não reproduzir perguntas). |
| 4.5 | Checklist condicional PAR (matriz papel×grupo + item transversal benefício/nexo) | ❌ | Seção 5 nova (a 4.7 atual descreve só o checklist PAD). |
| 4.6 | `dominio` emitido nos dois contratos de exportação | ❌ | Seção 6 nova. |
| 4.7 | Chip de domínio PAD/PAR no cabeçalho | ❌ | Seção 5 nova + Seção 6 nova (badges). |
| CA | Estado antigo carrega como PAD puro | ⚠️ | FAQ Oitiva (spec item 8). |

### Rodada PAR-5 — Validação cruzada de domínio

| # | Entregável / critério de aceite | Status | Onde / o que falta |
|---|---|---|---|
| 5.1 | Política única de validação nas 4 ferramentas + tabela-comentário | ❌ | Seção 6 nova, subseção com a tabela de política reproduzida (crítico — critério de aceite explícito da spec). |
| 5.2 | Emissão de `dominio` conferida em todos os emissores (incl. pauta — corrigido) | ❌ | Ver "achado" abaixo (D-9). Seção 6 nova. |
| 5.3 | Mensagens de recusa padronizadas + importação atômica | ❌ | Seção 6 nova, subseção de mensagens de recusa, com textos literais (item 2/D-1..D-5). |
| 5.4 | Casos de teste (Veritas receptor, Nexo receptor, legado) | ✅(código) / ❌(manual) | Comportamento existe e testado; ausente do manual. |
| CA | Achado registrado: pauta não emitia `dominio` até a PAR-5 | ✅ | Confirmado no estado FINAL (pós-correção) — ver D-9. O manual deve documentar apenas o comportamento atual (pauta emite `dominio`), não o defeito histórico. |

### Rodada PAR-6 — Teste integrado PAR

| # | Entregável / critério de aceite | Status | Onde / o que falta |
|---|---|---|---|
| 6.1 | `fixtures/par-ficticio-001.json` completo | ✅ | Artefato de teste, não vai ao manual. |
| 6.2 | Ciclo PAR de 8 etapas no `test-fluxo-integrado.js` | n/a | Não documentado no manual (o manual não descreve testes). Pode informar o diagrama do ciclo PAR espelhado na Seção 6 nova. |
| 6.3–6.4 | Idempotência/falha e recusa cruzada com fixtures reais | n/a→⚠️ | O comportamento de recusa cruzada é o que a Seção 6 nova deve descrever (mensagens + atomicidade). |
| 6.5 | Relatório em 3 seções (PAD/PAR/cruzada) | n/a | Artefato de teste. |
| CA | 127/127, exit 0, PAD intacto | ✅ | Confirma que documentar PAD sem mudança é seguro (spec: "PAR preservou o comportamento PAD"). |

**Placar do checklist:** ✅ **7** · ⚠️ **9** · ❌ **20** (mais alguns itens marcados n/a por serem artefatos de teste sem reflexo no manual). A esmagadora maioria dos ❌ concentra-se na ferramenta inteiramente nova (Nexo PAR, nova Seção 4) e na reescrita da Integração (Seção 6 nova) — coerente com a decisão de escopo da spec ("reescrita estrutural das seções 3–5, ferramenta nova para o Nexo PAR").

---

## 2. Divergências spec × código real

Cada item cita o trecho literal do código para o Raphael revisar. Prioridade nas mensagens exatas.

### D-1 · Mensagem de recusa P-domínio no Nexo PAR — envelope PAD explícito
`nexo-par.html:3881-3883` (`mensagemRecusaDominio`, ramo `encontrado='pad'`), texto literal:
> "Este arquivo foi exportado de um processo PAD (Lei nº 8.112/1990). Este é o Nexo PAR, que trabalha com processos PAR (Lei nº 12.846/2013 — LAC) — importe-o no Nexo Coger. Domínio encontrado: PAD (Lei 8.112/1990). Domínio esperado: PAR (Lei 12.846/2013). Nenhum dado foi alterado."

Nota: o rótulo por extenso vem de `rotuloDominioExtenso` (`nexo-par.html:3868-3872`): `par`→`"PAR (Lei 12.846/2013)"`, `pad`→`"PAD (Lei 8.112/1990)"`, ausente→`"não indicado (arquivo legado, anterior às rodadas PAR)"`.

### D-2 · Mensagem de recusa P-domínio no Nexo PAR — envelope legado (sem `dominio`)
`nexo-par.html:3876-3878`, texto literal:
> "Este arquivo não indica domínio (formato anterior às Rodadas PAR) e não pode ser importado no Nexo PAR, que trabalha exclusivamente com processos PAR (Lei nº 12.846/2013 — LAC). No PAR não existe acervo legado a preservar. Domínio encontrado: não indicado (arquivo legado, anterior às rodadas PAR). Domínio esperado: PAR (Lei 12.846/2013). Nenhum dado foi alterado."

Regra do receptor: `validarDominioEnvelope` (`nexo-par.html:3885-3890`) — aceita **apenas** `enc==='par'`; recusa `'pad'` **e** recusa ausente (legado). Constante `DOMINIO_FERRAMENTA='par'` (`:3865`).

### D-3 · Mensagens de recusa das outras 3 ferramentas — dois formatos de rótulo coexistem
**Divergência de apresentação já registrada pelos próprios implementadores** (CHANGELOG, "Nota de reconciliação (Partes A × B)" da PAR-5): a estrutura da frase-base é idêntica nas 4 ferramentas, mas o rótulo do domínio aparece em **dois formatos**:
- **Parte A (Veritas, Oitiva 360):** rótulo por extenso — ex.: `"PAR (Lei 12.846/2013)"` — via `mensagemRecusaDominio(encontrado, esperado, acaoCorreta)` + `rotuloDominioExtenso`.
- **Parte B (Nexo Coger, Nexo PAR):** o Nexo Coger usava o **token cru** (`"par"`/`"pad"`) na string `Domínio encontrado:`; o Nexo PAR (D-1/D-2) já usa o por extenso.

O CHANGELOG recomenda **unificar no formato por extenso** na reconciliação final, mas **não confirma que foi feito**. **Ação para o Raphael:** confirmar qual formato o Nexo Coger emite hoje antes de citar a mensagem literal do Nexo Coger no manual (Seção 6 nova). No Nexo PAR o formato por extenso está confirmado (D-1/D-2).

### D-4 · Exemplo de mensagem do Nexo Coger (recusando `par`) — citar da fonte, confirmar no código
O CHANGELOG (PAR-5 Parte B, 5.5) dá como exemplo real do Nexo Coger recusando `par`:
> "Este arquivo foi exportado de um processo PAR (Lei nº 12.846/2013 — LAC). Este é o Nexo Coger, que trabalha com processos PAD (Lei nº 8.112/1990) — importe-o no Nexo PAR. Domínio encontrado: par. Domínio esperado: pad. Nenhum dado foi alterado."

Repare no `Domínio encontrado: par` (token cru) — coerente com D-3. **Não citei isto do `nexo-coger.html` diretamente** (fora do meu conjunto de leitura foco; a spec pediu foco em nexo-par/veritas/oitiva/nexo-coger, mas prioriza nexo-par). Antes de publicar, ler `nexo-coger.html` (`mensagemRecusaDominio`) e confirmar o texto literal + formato do rótulo.

### D-5 · Mensagem de recusa de termo no Veritas (importação por domínio) — bloqueio PAR-5
O manual atual (Seção 5.3 / `build_manual.py:1663-1686`) documenta 4 verificações do Veritas ao importar termo (formato / hash / duplicado / catálogo). A PAR-5 (5.3) **acrescentou uma validação de domínio ANTES do hash** (`avaliarImportacaoTermo`, motivos `dominio_incompativel` e `dominio_legado_par`). Essa 5ª verificação **não está no manual**. **Ação:** ler `veritas.html` (`App.importarTermoOitiva` / `VeritasPuro.avaliarImportacaoTermo`) e capturar os dois novos textos de `alert()` para inserir na Seção 6 nova. O CHANGELOG confirma a existência mas não transcreve o texto literal.

### D-6 · Campos do fato PAR: nome interno é `nexoCausalidade`, não `nexoCausal`
A spec PAR-3/PAR-5 e o CHANGELOG PAR-5 mencionam o campo como `nexoCausal`; o **código real usa `nexoCausalidade`** (`nexo-par.html:3146,3148,4418,4733`; label de UI `nexo-par.html:3258` = "Nexo de causalidade"). O CHANGELOG PAR-6 6.1 já corrige para `beneficioInteresse`/`nexoCausalidade` (nomes reais). Documentar o **rótulo de UI**, não o nome interno; registrar a divergência só para não confundir quem cruzar spec × código.

### D-7 · Rótulo das normas LAC: não é mais truncado (bug corrigido)
Bug corrigido registrado no CHANGELOG ("Correção de bugs — Nexo Coger e Nexo PAR"): `buildCatalogo()` truncava a `descricao` da norma LAC em 78 caracteres, cortando a frase no `<select>` e na Nota de Indiciação. **Estado final:** `rotuloCurto` não trunca mais — usa o texto integral, removendo só o ponto final (`nexo-par.html:1729` `const rotuloCurto=s=>(s||'').trim().replace(/\.$/, '')`). Ao documentar o seletor de enquadramento na Seção 4 nova, descrever o rótulo **completo**, não truncado.

### D-8 · Seção 3.1 do manual (Tipo PN CGU 27) está desatualizada pós-PAR-1
`build_manual.py:642` afirma "os 5 tipos reais da Portaria Normativa CGU nº 27/2022 (Investigativos: IP, SINVE, SINPA, SINAC; Acusatórios: PAD)". Após PAR-1.3, `TIPOS_PROCESSO` inclui **IPS** (investigativos) e **PAR** (acusatórios). Como o Nexo Coger continua sendo domínio PAD, a lista visível pode ainda exibir esses tipos — **confirmar no `nexo-coger.html` real** se a Seção 3.1 precisa passar a "7 tipos". Este é um trecho PAD que pode ter mudado; a spec exige justificar cada trecho PAD tocado (critério de aceite).

### D-9 · Achado "pauta não emitia `dominio`" — confirmado corrigido no estado FINAL
Solicitado explicitamente pela spec. Histórico: PAR-3 (item 3.1) marcou `dominio` só no `exportJson()` do processo; o envelope da **pauta** NÃO emitia `dominio` em nenhum dos dois Nexos (descoberta registrada no CHANGELOG PAR-5 Parte B, 5.2). **Estado final (corrigido na PAR-5):** confirmado no código — `construirContratoPauta` inclui `dominio:DOMINIO_FERRAMENTA` (`nexo-par.html:3898`, valor `'par'`). O manual deve documentar **apenas o comportamento atual** (a pauta emite `dominio`), sem narrar o defeito histórico — o "a spec dizia X, o código fazia Y até ser corrigido" está capturado aqui e resolvido no estado pós-PAR-5.

### D-10 · Estrutura interna preserva `doc.acusados[]` para o ente privado
O ente privado é armazenado no array **`doc.acusados[]`** (nome preservado do fork), com `a.nome` espelhando a razão social (`nexo-par.html:2864-2868,2984`). O vínculo padrão de retorno de oitiva é `doc.acusados[0]` = o ente privado (CHANGELOG PAR-5 5.4, confirmado). Não é divergência funcional, mas o manual **não deve** expor `doc.acusados` ao leitor — descrever como "cadastro de ente privado". Registrado para o redator não se confundir.

---

## 3. Plano de renumeração (`build_manual.py`)

Renumeração-alvo: **Nexo PAR = nova Seção 4** (inserida antes do capítulo Oitiva); **Oitiva 360 → Seção 5**; **Integração → Seção 6**. Seções 1 (Introdução), 2 (Veritas) e 3 (Nexo Coger) **mantêm o número**.

### 3a. Cabeçalhos de capítulo (`add_chapter`) — 2 alterações + 1 inserção
| Linha | Atual | Novo |
|---|---|---|
| ~1214 | `add_chapter(doc, "Seção 4", "Oitiva 360 (uso isolado)")` | `"Seção 5"` |
| ~1607 | `add_chapter(doc, "Seção 5", "Integração entre as três ferramentas")` | `"Seção 6"` — e o título muda para "quatro ferramentas" |
| (antes de 1211/1214) | — | **Inserir** novo capítulo `add_chapter(doc, "Seção 4", "Nexo PAR (uso isolado)")` |

### 3b. Referências cruzadas no corpo do texto que MUDAM (13)
Toda referência a **Seção 5.x** (Integração atual) → **Seção 6.x**; a **Seção 4.x** (Oitiva atual) → **Seção 5.x**; frases "Seções 2 a 4" precisam virar "Seções 2 a 5" (4 ferramentas em uso isolado + nova Seção 4).

| Linha | Contexto (1 linha) | Antigo → Novo |
|---|---|---|
| 93 | "As **Seções 2, 3 e 4** deste manual documentam cada ferramenta em uso isolado" | → "Seções 2 a 5" (inclui Nexo PAR) |
| 184 | Categoria "Termo de oitiva" reservada "(ver **Seção 5**)" | → Seção 6 |
| 465 | Alerta: exportação p/ Nexo Coger "está documentada na **Seção 5**" | → Seção 6 |
| 535 | "importação de termo de oitiva (**Seção 5.3**)" | → Seção 6.3 |
| 749 | Estado probatório "alimenta diretamente o Oitiva 360 (ver **Seção 5**)" | → Seção 6 |
| 816 | "Revisão de pauta (…ver **Seção 5**)" | → Seção 6 |
| 961 | Bloco Contexto de oitiva "(**Seção 5.4**)" | → Seção 6.4 |
| 1016 | Hash Veritas "ver **Seção 5** para a integração real" | → Seção 6 |
| 1068 | Selo de prova "Exportar prova(s) para o Nexo (**Seção 5.1**)" | → Seção 6.1 |
| 1105 | Selo de fato "Exportar retorno (**Seção 5.4**)" | → Seção 6.4 |
| 1465 | Status do depoente ≠ "status de item de pauta (**Seção 4.11** abaixo)" | → Seção 5.11 |
| 1612 | "independente (**Seções 2 a 4** comprovam isso)" | → Seções 2 a 5 |
| 1767 | "como demonstrado nas **Seções 2, 3 e 4**" | → Seções 2 a 5 |

### 3c. Referências que NÃO mudam (apontam para Seções 2 ou 3, que mantêm número) — 21
Confirmadas como estáveis (não editar): linhas **482** (2.3), **563** (2.2), **685** (3.2), **903** (3.6), **942** (3.4), **952** (3.5), **971** (3.9), **985** (3.5), **994** (3.9), **1003** (3.4), **1021** (3.3), **1031** (3.4), **1045** (3.6), **1125** (3.5), **1141** (3.5), **1170** (3.5), **1179** (3.1), **1297** (3.3), **1630** (2.3), **1724** (3.8), **1731** (3.8), **1819** (3.3). *(Também os cabeçalhos 119/605 e as subseções internas 2.x/3.x via `add_h2`.)*

### 3d. Renumeração de subseções internas (`add_h2`/`add_h3`) — bulk, ~16
Não são "cross-refs", mas rótulos de heading que precisam acompanhar o novo número do capítulo:
- **Capítulo Oitiva (atual Seção 4 → nova Seção 5):** headings `4.1`…`4.11` → `5.1`…`5.11` (11 headings `add_h2`, linhas ~1224–1572, mais os `add_h3` que não têm número).
- **Capítulo Integração (atual Seção 5 → nova Seção 6):** headings `5.1`…`5.5` → `6.1`…`6.6` (5 headings `add_h2`, linhas ~1622–1744; a reescrita da spec item 6 acrescenta subseções novas — validação cruzada, mensagens de recusa —, então a contagem final sobe).
- **Novo capítulo Nexo PAR (Seção 4):** headings `4.1`…`4.n` a criar do zero, espelhando a Seção 3.

**Resumo renumeração:** **13** cross-refs de corpo + **2** cabeçalhos de capítulo a editar + **1** capítulo a inserir + **~16** headings de subseção a renumerar. **21** cross-refs confirmadas estáveis.

> ⚠️ Recomendação: rodar uma busca global final por `"Seção 4"`, `"Seção 5"`, `"Seções 2 a 4"`, `"4.1"…"4.11"`, `"5.1"…"5.5"` **após** a reescrita, pois a reescrita da Seção 6 (Integração) e a nova Seção 4/5 introduzirão novas referências. Critério de aceite da spec: "nenhuma referência cruzada aponta para o número antigo".

---

## 4. Inventário para a nova Seção 4 (Nexo PAR) — campos e textos exatos do código

Dados extraídos de `nexo-par.html`, citados por linha. A nova Seção 4 é paralela à Seção 3 (Nexo Coger), campo a campo.

### 4.1 Cadastro do ente privado (`abrirFormAcusado`, `nexo-par.html:2869-2985`)
Ordem e rótulos exatos renderizados:
| Campo | Rótulo exato | Obrigatoriedade |
|---|---|---|
| Razão social | `Razão social` (`:2950`) | **Obrigatória** — bloqueio: `"Informe a razão social do ente."` (`:2982`) |
| CNPJ | `CNPJ`, hint `"14 dígitos, com ou sem máscara."` (`:2951`) | Opcional, mas se preenchido valida formato: `cnpjValido` = 14 dígitos sem DV (`:2863`); bloqueio `"CNPJ inválido: informe 14 dígitos (com ou sem máscara)."` (`:2983`) |
| Nome fantasia | `Nome fantasia (opcional)` (`:2953`) | Opcional |
| Faturamento bruto | `Faturamento bruto (opcional)`, hint "Base para a futura dosimetria da multa (Multa_PAR)." (`:2954`) | Opcional |
| Endereço da sede | `Endereço da sede (opcional)` (`:2955`) | Opcional |
| **Representantes** (bloco repetível) | título `Representantes` (`:2956`); por linha: `Nome`, `CPF (opcional)`, `Vínculo` (select). Botão `+ Adicionar representante` (`:2904`). Vínculo default `PAPEL.REPRESENTANTE_LEGAL`. Hint quando vazio: `"Nenhum representante. Cadastre ao menos um representante legal (exigência P-ENTE)."` (`:2893`) | Ao menos 1 representante **legal** exigido pelo gate P-ENTE (não bloqueia salvar o ente, bloqueia a Nota de Indiciação) |
| **Estruturas societárias** | bloco `Estruturas societárias (registro, sem cálculo)` (`:2957`) | Opcional, registro puro |
| — Solidariedade | `Solidariedade — entes do mesmo grupo econômico` (`:2910`); por linha `CNPJ`, `Razão social`, `Descrição do vínculo`; botão `+ Adicionar ente relacionado` (`:2921`) | Opcional |
| — Sucessão empresarial | `Sucessão empresarial — tipo` (select: —/Fusão/Incorporação/Cisão), `Descrição`, `Data` (`:2960-2962`) | Opcional |
| — Desconsideração | bloco `Desconsideração da personalidade jurídica (art. 14 da LAC)` (`:2928`); checkbox `Aplicar desconsideração da personalidade jurídica`; se ativa, `Fundamentação` + checkboxes por representante "atingido" (`:2926-2943`) | Opcional |

Vínculos disponíveis no select (`vinculosEnteOpts`, `:2858-2862`): os 3 papéis PAR do catálogo — `PAPEL.REPRESENTANTE_LEGAL`, `PAPEL.PREPOSTO`, `PAPEL.SOCIO_ADMINISTRADOR` (labels do catálogo). Confirmação de exclusão: `"Excluir este ente? As condutas vinculadas a ele nos fatos serão removidas."` (`:2978`).

### 4.2 Campos de fato/enquadramento PAR (`:3245-3259`)
Substituem o "Elemento subjetivo" do PAD (removido — LAC objetiva, art. 2º):
- Bloco `Interesse/benefício da PJ e nexo causal` (com `*` quando há enquadramento LAC), hint: `"Obrigatórios quando há enquadramento LAC (pendência crítica P8-PAR se em branco)."` (`:3254-3255`)
- Campo `Interesse ou benefício da pessoa jurídica` (`:3256`) — textarea
- Campo `Nexo de causalidade`, hint "Correlação entre o ato lesivo e o benefício/interesse apontado." (`:3258-3259`)
- Internamente `f.beneficioInteresse` / `f.nexoCausalidade` (ver D-6). **Não** bloqueiam o salvamento do fato — são cobrados via P8-PAR na geração (`:3334-3335`).

### 4.3 As 11 normas LAC e os 2 optgroups (`:1512-1620`, `buildCatalogo :1716`, `GRUPOS :1801`)
Optgroups renderizados (`GRUPOS`, `:1801-1805`): **"Atos de corrupção em geral"**, **"Licitações e contratos"**, e residual **"Criadas pelo usuário"**. Grupo lido do campo `grupo` do item (`grupoDaNorma :1795-1799`).

| ID | Dispositivo | Grupo |
|---|---|---|
| NORMA.LAC.ART5_I | art. 5º, I | Atos de corrupção em geral |
| NORMA.LAC.ART5_II | art. 5º, II | Atos de corrupção em geral |
| NORMA.LAC.ART5_III | art. 5º, III | Atos de corrupção em geral |
| NORMA.LAC.ART5_IV_A | art. 5º, IV, a | Licitações e contratos |
| NORMA.LAC.ART5_IV_B | art. 5º, IV, b | Licitações e contratos |
| NORMA.LAC.ART5_IV_C | art. 5º, IV, c | Licitações e contratos |
| NORMA.LAC.ART5_IV_D | art. 5º, IV, d | Licitações e contratos |
| NORMA.LAC.ART5_IV_E | art. 5º, IV, e | Licitações e contratos |
| NORMA.LAC.ART5_IV_F | art. 5º, IV, f | Licitações e contratos |
| NORMA.LAC.ART5_IV_G | art. 5º, IV, g | Licitações e contratos |
| NORMA.LAC.ART5_V | art. 5º, V | Atos de corrupção em geral |

`nota_aplicacao` de cada norma exibida como hint (📌) ao selecionar (`:1741`). Rótulo da norma = `descricao` integral sem ponto final (não truncado — D-7).

### 4.4 Catálogo de pendências do fork (`computePendencias :2067-2128`)
| Código | Nível | Texto exato | Observação |
|---|---|---|---|
| P1 | crítico | `"Fato sem prova vinculada — alegação sem evidência"` (`:2081`) | mantida (salvo override justificado) |
| P2 | crítico/frágil | `"Fato sem enquadramento legal"` (`:2085`) | crítico só da indiciação em diante |
| P3 | frágil | `"Prova órfã — não sustenta nenhum fato do mapa"` (`:2110`) | mantida |
| P4 | pendente | `"Multiplicidade de enquadramentos não classificada: concurso formal ou conflito aparente?"` (`:2093`) | mantida |
| P5 | crítico | `"Conduta não individualizada — risco de indiciação genérica (nulidade)"` (`:2090`) | mantida |
| P6a | frágil | `"Prova emprestada com pendência formal (certidão/autorização)"` (`:2113`) | mantida |
| P6b | frágil | `"Ente privado não intimado da produção desta prova (contraditório)"` (`:2116`) | **reescrita** (era "acusado") |
| P6c | (dormente) | antecedência de intimação p/ interrogatório (art. 41, Lei 9.784/99) — `:2130` | permanece no código, **sem UI PAR** (ente não tem interrogatório) |
| P7 | frágil | `"Sustentação exclusivamente indiciária/informal — explicitar raciocínio indutivo"` (`:2097`) | mantida |
| **P8** | — | **REMOVIDA** (`:2098`) | LAC objetiva — não há dolo/culpa |
| **P8-PAR** | **crítico** | `"Fato com enquadramento LAC sem descrição de benefício/interesse ou nexo causal"` (`:2103`) | **nova** — dispara com enquadramento ativo e benefício OU nexo em branco |
| **P-ENTE** | **crítico** | `"Processo sem ente privado cadastrado"` (alvo processo, `:2122`) **ou** `"Ente privado sem representante legal cadastrado"` (alvo ente, `:2126`) | **nova** — bloqueia geração |

Checklist de encerramento adaptado (`:2805-2807`): C1 `"Ente privado cadastrado com representante legal"`, C2 `"Benefício/interesse e nexo causal descritos em todo fato com enquadramento LAC"`, C3 `"Zero pendências críticas (P1, P2, P5, P8-PAR, P-ENTE)"`.

### 4.5 Estrutura da Nota de Indiciação (`construirTextoIndiciacao :4385-4489`)
Ordem exata das seções do documento gerado:
1. Cabeçalho institucional: "MINISTÉRIO DA FAZENDA — RECEITA FEDERAL DO BRASIL" / "CORREGEDORIA…" / título **"Nota de Indiciação"** / "Processo Administrativo de Responsabilização (PAR) nº …" / "Lei nº 12.846, de 1º de agosto de 2013 (Lei Anticorrupção — LAC)" / Portaria / "Pessoa jurídica: <razão social>, CNPJ <…>" (`:4392-4398`).
2. Tabela de qualificação do ente: Razão social, CNPJ, Nome fantasia (se houver), Endereço da sede (se houver), Representante legal (`:4400-4406`). Se desconsideração ativa, parágrafo em itálico art. 14 (`:4407-4409`).
3. **"Da conduta lesiva imputada ao ente privado"** — por fato: descrição, conduta individualizada comissiva/omissiva, e (se preenchidos) "Interesse ou benefício da pessoa jurídica:" e "Nexo de causalidade:" (`:4411-4420`).
4. **"Das provas"** — por fato, com índice numerado e trechos significativos (`:4431-4446`).
5. **"Do enquadramento legal"** — por fato, "a conduta amolda-se ao <dispositivo> (<rótulo>)", **sem** elemento subjetivo; trata concurso formal / conflito aparente (`:4448-4463`).
6. **"Síntese dos fatos, provas e enquadramentos"** — tabela (`:4464-4466`).
7. **"Das alegações da defesa não acatadas"** — bloco editável (`:4467-4472`).
8. **"Da multa, do faturamento bruto e do programa de integridade"** — os **4 textos fixos complementares** (`:4474-4478`), literais:
   - "Faculta-se expressamente à pessoa jurídica indiciada apresentar informações e provas relativas aos parâmetros de cálculo da multa e ao seu faturamento bruto no exercício anterior ao da instauração do processo."
   - "Solicitam-se, ainda, informações e documentos necessários à análise do parâmetro previsto no inciso IV do art. 22 do Decreto nº 11.129, de 11 de julho de 2022."
   - "Fica assegurado o prazo de 30 (trinta) dias para apresentação de defesa escrita, contado da intimação desta Nota de Indiciação, podendo a pessoa jurídica apresentar, em conjunto com a defesa, evidências da existência e do funcionamento de programa de integridade, nos termos da Portaria CGU nº 909, de 7 de abril de 2025."
   - "Registra-se, por fim, a possibilidade de resolução negociada do processo, por meio de Termo de Compromisso ou de Acordo de Leniência, na forma da legislação de regência."
9. **"Do encerramento"** — ressalva de adequação do enquadramento; "Intime-se… no prazo de 30 (trinta) dias… (art. 17 da IN CGU nº 13/2019)"; cidade/data; bloco de assinatura em 3 colunas (`:4482-4486`).

Validação pré-geração (`validaMinuta`, `:4328-4332`): exige razão social do ente, representante legal, e ao menos um fato ativo imputado. Caixa de destaque a criar: adaptar a caixa "ATO FINAL — USE COM CAUTELA" da Seção 3.5 para a Nota de Indiciação do PAR.

### 4.6 Painel de Prazos (`prazoConclusaoInfo :2731-2736`, `renderPrazos :2745-2773`, form `:3648-3650`)
- **Prazo confirmado (mudou):** defesa escrita **30 dias** a contar da intimação da Nota de Indiciação (art. 17, IN CGU nº 13/2019). Bloco: `"Intimação da Nota de Indiciação e defesa escrita"` (`:2772`), hint `"Prazo de 30 dias para defesa escrita a contar da intimação da Nota de Indiciação (art. 17, IN CGU nº 13/2019). Fonte: item 3.6 da spec."` (`:2773`). Substitui a lógica PAD pessoal/edital 10/15 da Lei 8.112.
- **Prazo SEM fonte confirmada (ressalva a reproduzir literalmente no manual):** o prazo de **conclusão do processo** manteve o cálculo do PAD por ausência de fonte normativa PAR. Comentário no código (`:2731-2734`): *"…mantido o mesmo cálculo do PAD (data de instauração + prazoConclusaoDias) por ausência de fonte normativa fornecida — não se inventa prazo. O único prazo PAR confirmado (30 dias de defesa) está no bloco de intimação abaixo."* Hint do form (`:3650`): `"Prazo de conclusão do processo em dias (editável). Fonte do prazo do PAR não fornecida nesta rodada."` — o manual deve reproduzir a mesma ressalva.

### 4.7 O que NÃO muda vs. Nexo Coger (nota final da Seção 4)
Mecânica do mapa fato-prova-norma, import de provas do Veritas, import de retorno do Oitiva, exportação de pauta, selo 🎙 de oitiva, toolbar (exceto textos/prazos), design system — todos herdados byte-idênticos do fork (CHANGELOG PAR-3 3.9). Manter a disciplina "o que não muda" para o leitor que já conhece a Seção 3.

---

## Notas finais para os próximos agentes
- **Marcadores de captura:** inserir `[CAPTURA PENDENTE — …]` em: cadastro de ente privado, seletor de domínio da Matriz (Oitiva), Nota de Indiciação PAR, tabela de validação cruzada. Não descrever capturas inexistentes.
- **Desambiguação de "Nexo":** o Glossário/texto deve separar sempre os 3 sentidos — *Nexo fático-probatório* (ligação fato-prova), *nexo de causalidade* (conceito LAC, campo do fato PAR), e os nomes próprios *Nexo Coger* / *Nexo PAR*.
- **Confirmar no `nexo-coger.html`** antes de publicar: D-4 (mensagem literal de recusa e formato do rótulo) e D-8 (lista de tipos PN CGU 27 na Seção 3.1). Estes dois pontos ficaram fora do meu foco de leitura profunda (o foco pedido foi `nexo-par.html`).
- **Convenção normativa:** primeira menção por extenso com data completa; seguintes abreviadas só com o ano; vírgulas separando elementos.
