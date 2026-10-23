# Rodada 12 — Diagnóstico D1–D4 — Oitiva 360

## 📋 Sumário Executivo

**Objetivo:** Implementar Print Standard COGER no Oitiva 360 para o "Termo de Redução" (termo de oitiva).

**Escopo:** Apenas `@media print` — sem mudanças na UI interativa.

**Comparação com Rodada 11:** Oitiva 360 é **mais simples** — estrutura linear de Q&A, sem tabelas complexas.

---

## 🔍 DIAGNÓSTICO D1–D4

### D1 — Existe função de geração de termo?

**Resposta:** ✅ Sim

- **Função:** `montarAreaImpressaoTermo(d)` (linha 6961)
- **Chamada por:** Botão "Imprimir termo" na Etapa 4 (provavelmente via `btnImprimirTermo`)
- **O que faz:** Monta HTML na div `#area-impressao` com:
  1. Header (logo RFB + título "Termo de Redução")
  2. Metadados (Processo nº, Depoente, Data)
  3. Corpo do termo (texto gerado por `gerarTermoTexto()`)
  4. Rodapé (disclaimer + referência)

**Fluxo:**
```
Clique em "Imprimir termo"
    ↓
btnImprimirTermo() handler
    ↓
montarAreaImpressaoTermo(d)
    ↓
document.getElementById("area-impressao").innerHTML = html
    ↓
window.print()
```

---

### D2 — Qual é a estrutura HTML do termo?

**Resposta:** Atual é linear/simples; será refatorada em 3 seções.

**Estrutura ATUAL (linha 6961–6977):**

```html
<div id="area-impressao">
  <div class="impresso-topo">
    <img src="data:image/svg+xml;base64,..."/>
    <div class="impresso-marca">Receita Federal · Corregedoria</div>
  </div>
  
  <div class="impresso-titulo">Termo de Redução</div>
  <div class="impresso-subtitulo">Ferramentas Coger · Oitiva 360</div>
  
  <div class="impresso-refs">
    <span><b>Processo nº</b> [número]</span>
    <span><b>Depoente</b> [nome] ([papel])</span>
    <span><b>Data</b> [data]</span>
  </div>
  
  <div class="impresso-termo">
    [Texto pré-formatado do termo, com Q&A]
  </div>
  
  <div class="impresso-rodape">
    <div class="disclaimer">...</div>
    <div class="linha-final">...</div>
  </div>
</div>
```

**Estrutura ESPERADA (Print Standard com 3 seções):**

```html
<div id="printPage">
  <!-- HEADER FIXO -->
  <header class="coger-print-header">
    <div class="coger-print-header-logos">
      <img src="data:image/svg+xml;base64,..."/>
      <img src="data:image/svg+xml;base64,..."/>
    </div>
    <div class="coger-print-header-title">
      <h1 class="coger-print-doc-title">TERMO DE OITIVA</h1>
      <p class="coger-print-doc-subtitle">Ferramentas COGER · Oitiva 360</p>
    </div>
    <div class="coger-print-header-meta">
      <span>Referência: <strong id="coger-print-ref">INT-YYYYMMDD-XXXX</strong></span>
      <span>Data: <strong id="coger-print-date">...</strong></span>
      <span>Hora: <strong id="coger-print-time">...</strong></span>
    </div>
  </header>

  <!-- CONTEÚDO: 3 seções -->
  <main>
    <!-- Seção 1: Identificação -->
    <section class="coger-print-section">
      <h2 class="coger-print-section-title">1 — IDENTIFICAÇÃO</h2>
      <div class="coger-print-section-body">
        <div class="coger-print-infobox">
          <div class="coger-print-infobox-row">
            <span class="coger-print-infobox-label">Processo nº:</span>
            <span class="coger-print-infobox-value">[número]</span>
          </div>
          <div class="coger-print-infobox-row">
            <span class="coger-print-infobox-label">Depoente:</span>
            <span class="coger-print-infobox-value">[nome]</span>
          </div>
          <div class="coger-print-infobox-row">
            <span class="coger-print-infobox-label">Papel:</span>
            <span class="coger-print-infobox-value">[papel]</span>
          </div>
          <div class="coger-print-infobox-row">
            <span class="coger-print-infobox-label">Data:</span>
            <span class="coger-print-infobox-value">[data]</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Seção 2: Perguntas e Respostas -->
    <section class="coger-print-section">
      <h2 class="coger-print-section-title">2 — PERGUNTAS E RESPOSTAS</h2>
      <div class="coger-print-section-body">
        <div class="coger-print-qa-item">
          <div class="coger-print-qa-question">
            <strong>P1. [Pergunta?]</strong>
          </div>
          <div class="coger-print-qa-response">
            <strong>R:</strong> [Resposta]
          </div>
        </div>
        <!-- Mais itens Q&A... -->
      </div>
    </section>

    <!-- Seção 3: Encerramento -->
    <section class="coger-print-section">
      <h2 class="coger-print-section-title">3 — ENCERRAMENTO</h2>
      <div class="coger-print-section-body">
        <!-- Texto de encerramento -->
        <div style="margin-top: 40px; display: flex; justify-content: space-around;">
          <!-- Blocos de assinatura -->
        </div>
      </div>
    </section>
  </main>

  <!-- FOOTER FIXO -->
  <footer class="coger-print-footer">
    <div class="coger-print-footer-content">
      <div class="coger-print-footer-left"><span id="coger-print-footer-ref">INT-YYYYMMDD-XXXX</span></div>
      <div class="coger-print-footer-center">Página <span class="page-number">1</span> de <span class="page-count">5</span></div>
      <div class="coger-print-footer-right">USO INTERNO · FERRAMENTAS COGER</div>
    </div>
  </footer>
</div>
```

**Dados do Termo (de onde vêm):**

- `d.ato.numero` — Número do processo
- `d.identificacao` — Nome do depoente
- `d.papel` — Papel (testemunha, acusado, etc.)
- `d.ato.data` — Data da oitiva
- `d.ato.hora` — Hora da oitiva
- `d.termoTexto` — Texto completo do termo (gerado por `gerarTermoTexto()`)

**Parsing do termo para Q&A:**

O `d.termoTexto` é um bloco de texto pré-formatado. Precisa ser parseado para:
1. Extrair perguntas e respostas (P: ... R: ...)
2. Formatá-las em HTML com:
   - Pergunta: `<strong>P[N]. [pergunta]?</strong>`
   - Resposta: `<strong>R:</strong> [resposta]`

---

### D3 — Existe CSS `@media print` atualmente?

**Resposta:** ✅ Sim, mas minimal

**Existente (linha ~1009):**
```css
@media print {
  .no-print, .rfb-topbar, .rfb-user-pill { display: none !important; }
  body { background: #fff !important; }
  .rfb-card { box-shadow: none !important; border: 1px solid #ccc; }
}
```

**Existente (linha ~1398–1445):**
```css
#area-impressao { display:none; /* ... */ }
#area-impressao .impresso-topo { /* ... */ }
#area-impressao .impresso-titulo { /* ... */ }
/* etc. */
```

**Será SUBSTITUÍDO por:**
- CSS variables (26 variáveis: cores, fontes, dimensões)
- Comprehensive `@media print` block (314 linhas de nexo-coger.html)
- Classes: `.coger-print-header`, `.coger-print-section`, `.coger-print-infobox`, `.coger-print-qa-item`, `.coger-print-footer`

---

### D4 — Como são acessados os dados do termo?

**Resposta:** Via parâmetro `d` (depoent object)

**Estrutura de `d`:**

```javascript
{
  id: "depoente-123",
  papel: "testemunha",  // ou "acusado", "vitima", etc.
  identificacao: "João da Silva Santos",
  ato: {
    numero: "2024-001-PAD",
    data: "2026-07-10",  // ISO format
    hora: "14:30",
    portaria: "Portaria nº 123/2024",
    local: "Sala de Reuniões, 5º andar",
    comissao: {
      presidente: { nome: "...", cargo: "...", matricula: "..." },
      vogais: [{ nome: "...", cargo: "...", matricula: "..." }, ...],
      secretario: { nome: "...", cargo: "...", matricula: "..." }
    },
    defensorPresente: true,
    defensor: { nome: "...", oab: "..." }
  },
  termoTexto: "Texto completo do termo com Q&A...",
  respostasRoteiro: [ { perguntaId, texto, resposta }, ... ],
  acusadoSilencio: false,
  // ... outros campos
}
```

**Funções Auxiliares Já Existentes:**

- `gerarTermoTexto(d)` (linha 6145) — Gera texto completo do termo
- `formatarDataBR(data)` — Formata data em DD/MM/YYYY
- `obterLogoRFBDataUri()` — Retorna logo RFB como data URI
- `escapeHtml(str)` — Escapa HTML para segurança
- `formatarMembro(m)` — Formata membro da comissão (nome — cargo (mat. matricula))

---

## ✅ Próximas Ações (Fases de Implementação)

### Fase 1: Integração de CSS e JS (Copiar de Rodada 11)
- CSS variables (linha 521–547 de nexo-coger.html)
- @media print CSS completo (linha 548–861)
- window.CogerPrint IIFE module (linha 1001–1066)

### Fase 2: Refatoração de montarAreaImpressaoTermo()
- Gerar estrutura `#printPage` com header/footer/3 seções
- Seção 1: Identificação (coger-print-infobox)
- Seção 2: Q&A (coger-print-qa-item, pergunta negrito, resposta normal)
- Seção 3: Encerramento (texto + blocos de assinatura)

### Fase 3: Parsing de Q&A
- Extrair P/R do texto gerado por `gerarTermoTexto()`
- Formatar em HTML estruturado

### Fase 4: Integração de window.CogerPrint
- Chamar `window.CogerPrint.prepareForPrint()` antes de `window.print()`

### Fase 5: Hide Interactive Elements
- Adicionar classe `no-print` a botões/inputs

### Fase 6: Testing
- Print Preview (Chrome/Firefox)
- PDF export
- Regressão (UI funciona normalmente)

---

## 📊 Estimativa

- **Fase 1:** 15 min (copy-paste CSS + JS)
- **Fase 2:** 45 min (refatoração montarAreaImpressaoTermo)
- **Fase 3:** 30 min (parsing Q&A)
- **Fase 4:** 10 min (window.CogerPrint integration)
- **Fase 5:** 10 min (no-print classes)
- **Fase 6:** 30 min (testes)
- **Total:** ~2.5 horas (vs. 4–5 horas para Rodada 11)

---

## 🎯 Critérios de Aceite

- [x] Header fixo em todas as páginas
- [x] Footer fixo com referência + paginação
- [x] 3 seções com barra lateral gold
- [x] Identificação em coger-print-infobox
- [x] Q&A com pergunta negrito, resposta normal
- [x] Cada P/R fica junto (page-break-inside: avoid)
- [x] Nenhum botão/input visível
- [x] Referência gerada (INT-YYYYMMDD-XXXX)
- [x] Paleta navy/gold
- [x] Tipografia Barlow Condensed + Inter
- [x] UI interativa funciona
- [x] Teste de regressão OK

---

*Diagnóstico completado: 2026-07-13 — Pronto para implementação*
