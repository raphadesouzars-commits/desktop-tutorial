# COGER Print Standard — Guia de Implementação

## Introdução

O COGER Print Standard é um conjunto unificado de CSS, HTML e JavaScript para padronizar a aparência de documentos impressos em três ferramentas:

- **Veritas** (dossiês de análise de conduta)
- **Nexo Coger** (minutas de indiciação)
- **Oitiva 360** (termos de oitiva)

Este padrão harmoniza a apresentação impressa com o design visual do Integritas, sem quebrar a funcionalidade interativa das ferramentas.

---

## Arquivos Fornecidos

1. **`coger-print-standard.css`** — CSS unificado com variáveis, estilos de header/footer/seções/tabelas
2. **`coger-print-template.html`** — Exemplo de markup HTML mostrando a estrutura esperada
3. **`coger-print-utility.js`** — Funções JavaScript para preparação de impressão e metadados
4. **`GUIA-COGER-PRINT-STANDARD.md`** — Este arquivo (documentação)

---

## Arquitetura

### Princípios

- **Offline-first**: Nenhuma dependência de CDN ou recurso externo
- **CSS puro**: Toda a estilização ocorre via `@media print`
- **Sem regressão**: UI interativa não é afetada — mudanças isoladas ao print
- **Portável**: O mesmo CSS funciona em todas as três ferramentas

### Estrutura de Página

```
┌─────────────────────────────────────┐
│ Header Fixo (60px)                  │
│ • Logos institucionais              │
│ • Título do documento               │
│ • Metadata (ref, data, hora)        │
├─────────────────────────────────────┤
│                                     │
│ Conteúdo Principal                  │
│ • Seções numeradas com barra lateral│
│ • Tabelas com cabeçalho navy        │
│ • Info boxes com dados estruturados │
│ • Blocos legais com citações        │
│                                     │
├─────────────────────────────────────┤
│ Footer Fixo (40px)                  │
│ • Referência | Página X de Y | USO  │
│ INTERNO                             │
└─────────────────────────────────────┘
```

---

## Implementação Passo a Passo

### 1. Copiar o CSS

Copie **o conteúdo completo** de `coger-print-standard.css` para a seção `<style>` de sua ferramenta HTML (ou crie um bloco `<style>` se não existir).

```html
<style>
  /* ... estilos interativos existentes ... */

  /* Copiar coger-print-standard.css aqui */
</style>
```

### 2. Adicionar Estrutura de Header

Adicione este HTML **imediatamente após a abertura do `<body>`**:

```html
<header class="coger-print-header">
  <div class="coger-print-header-logos">
    <!-- Logo Ministério -->
    <svg class="coger-logo-mf" viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg">
      <text x="50" y="25" text-anchor="middle" font-size="12" fill="#0B2F5F" font-weight="bold">Ministério</text>
    </svg>
    <!-- Logo RFB -->
    <svg class="coger-logo-rfb" viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg">
      <text x="50" y="25" text-anchor="middle" font-size="12" fill="#0B2F5F" font-weight="bold">Receita Federal</text>
    </svg>
  </div>
  <div class="coger-print-header-title">
    <h1 class="coger-print-doc-title">TÍTULO DO DOCUMENTO</h1>
    <p class="coger-print-doc-subtitle">Ferramentas COGER · [Contexto]</p>
  </div>
  <div class="coger-print-header-meta">
    <span>Referência: <strong id="coger-print-ref">INT-XXXXXXX-XXXX</strong></span>
    <span>Data: <strong id="coger-print-date">—</strong></span>
    <span>Hora: <strong id="coger-print-time">—</strong></span>
  </div>
  <div class="coger-print-header-divider"></div>
</header>
```

### 3. Adicionar Estrutura de Footer

Adicione este HTML **imediatamente antes do fechamento do `</body>`**:

```html
<footer class="coger-print-footer">
  <div class="coger-print-footer-divider"></div>
  <div class="coger-print-footer-content">
    <div class="coger-print-footer-left">
      <span id="coger-print-footer-ref">INT-XXXXXXX-XXXX</span>
    </div>
    <div class="coger-print-footer-center">
      <span>Página <span class="page-number">1</span> de <span class="page-count">—</span></span>
    </div>
    <div class="coger-print-footer-right">
      <span>USO INTERNO · FERRAMENTAS COGER</span>
    </div>
  </div>
</footer>
```

### 4. Copiar o JavaScript Utility

Copie **o conteúdo completo** de `coger-print-utility.js` para a seção `<script>` de sua ferramenta (ou crie um bloco `<script>` se não existir):

```html
<script>
  // Conteúdo de coger-print-utility.js aqui
</script>
```

### 5. Inicializar Print Support

No seu código de inicialização (ou ao final do `<script>`), adicione:

```javascript
document.addEventListener('DOMContentLoaded', initPrintSupport);
```

### 6. Adaptador do Conteúdo

Quando seu código JavaScript gera o documento para impressão, **antes de chamar `window.print()`**, chame:

```javascript
// Supondo que você tenha um botão ou ação de print
function gerarImpressao() {
  // ... seu código de geração de conteúdo ...

  // Preparar para print
  prepareForPrint({
    documentTitle: 'Meu Documento'
  });

  // Abrir diálogo de impressão
  window.print();
}
```

---

## Elementos Principais

### Seções Numeradas

```html
<section class="coger-print-section">
  <h2 class="coger-print-section-title">1 — TÍTULO DA SEÇÃO</h2>
  <div class="coger-print-section-body">
    <p>Conteúdo da seção...</p>
  </div>
</section>
```

**Resultado:**
- Título em Barlow Condensed, 13pt, navy-900
- Barra lateral dourada (3px sólido)
- Conteúdo justificado, 11pt, Inter

### Info Boxes

```html
<div class="coger-print-infobox">
  <div class="coger-print-infobox-row">
    <span class="coger-print-infobox-label">Campo:</span>
    <span class="coger-print-infobox-value">Valor</span>
  </div>
</div>
```

**Resultado:**
- Fundo cinza claro (F5F8FC)
- Bordas suaves (1.5px cinza-300)
- Labels em negrito navy-700
- Valores em texto primário

### Blocos Legais

```html
<div class="coger-print-legal-block">
  <div class="coger-print-legal-label">LEI Nº 8.112/90 — ART. 116, IX</div>
  <blockquote class="coger-print-legal-quote">
    "São deveres do servidor: […]"
  </blockquote>
</div>
```

**Resultado:**
- Fundo cinza claro
- Barra lateral navy (3px sólido)
- Label em Barlow Condensed, 9pt, uppercase
- Quote em JetBrains Mono, itálico, 10pt

### Tabelas

```html
<table class="coger-print-table">
  <thead class="coger-print-table-head">
    <tr>
      <th>Coluna 1</th>
      <th>Coluna 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dado 1</td>
      <td>Dado 2</td>
    </tr>
  </tbody>
</table>
```

**Resultado:**
- Cabeçalho navy-900 com texto branco
- Linhas alternadas (sim/cinza-100)
- Bordas inferiores cinza-300
- Fonte 10pt com espaçamento adequado

---

## Paleta de Cores

```css
--coger-print-navy-900:    #0B2F5F   (heróis, cabeçalhos, barras laterais)
--coger-print-navy-700:    #1E4C99   (bordas, backgrounds secundários)
--coger-print-navy-600:    #2E5F99   (texto muted)
--coger-print-gold-500:    #C9A35C   (acentos, barras laterais de seções)
--coger-print-gold-100:    #F5F0E8   (background muito claro)
--coger-print-gray-100:    #F5F8FC   (background neutro, info boxes)
--coger-print-gray-300:    #DCE6F4   (divisores, bordas)
--coger-print-text-primary: #1A2740  (corpo principal)
--coger-print-text-muted:   #4A5568  (texto secundário)
```

---

## Tipografia

```css
--coger-print-font-sans:     "Inter", "Barlow Condensed", sans-serif
--coger-print-font-display:  "Barlow Condensed", sans-serif
--coger-print-font-mono:     "JetBrains Mono", monospace
```

### Uso

- **Corpo principal (paragrafos):** Inter, 11pt
- **Títulos de seção:** Barlow Condensed, 13pt, uppercase
- **Labels/cabeçalhos de tabela:** Barlow Condensed, 9pt–13pt, uppercase
- **Citações legais:** JetBrains Mono, 10pt, itálico

---

## Espaçamento e Margens

```css
--coger-print-margin-top:           20mm
--coger-print-margin-bottom:        20mm
--coger-print-margin-left:          20mm
--coger-print-margin-right:         20mm
--coger-print-header-height:        60px
--coger-print-footer-height:        40px
```

Estes valores garantem que header, footer e conteúdo principal se alinhem corretamente em A4.

---

## Quebras de Página

O CSS já cuida de quebras automáticas:

- **Títulos (h1, h2, h3, h4):** `page-break-after: avoid` + `orphans: 3` + `widows: 3`
- **Seções, tabelas, boxes:** `page-break-inside: avoid`
- **Parágrafos:** `orphans: 3` + `widows: 3` (evita linhas órfãs/viúvas)

Para forçar quebra de página **antes** de um elemento, use a classe:

```html
<section class="coger-print-section coger-print-page-break-before">
  <!-- Conteúdo -->
</section>
```

---

## Funções JavaScript Disponíveis

### `prepareForPrint(options)`

Prepara o documento para impressão. Gera referência, preenche metadados, dispara evento `beforeprint`.

```javascript
// Uso simples:
prepareForPrint();
window.print();

// Com opções:
const ref = prepareForPrint({
  reference: 'INT-20260713-9999',
  documentTitle: 'Minuta de Indiciação'
});
console.log('Referência gerada:', ref);
```

### `generatePrintReference()`

Gera referência única no formato `INT-YYYYMMDD-XXXX`.

```javascript
const ref = generatePrintReference();
console.log(ref); // ex: INT-20260713-0042
```

### `formatDatePT(date)` / `formatTimePT(date)`

Formata data/hora para português.

```javascript
const now = new Date();
console.log(formatDatePT(now));  // "13 de julho de 2026"
console.log(formatTimePT(now));  // "18:35"
```

### `validatePrintStructure()`

Valida se o HTML possui todos os elementos críticos de print.

```javascript
const validation = validatePrintStructure();
if (!validation.isValid) {
  console.error('Erros encontrados:', validation.errors);
}
```

### `initPrintSupport()`

Inicializa suporte de print: registra listeners, valida estrutura.

```javascript
document.addEventListener('DOMContentLoaded', initPrintSupport);
```

---

## Exemplo de Fluxo Completo

```javascript
// Ao usuário clicar em "Gerar Impressão"
document.getElementById('printButton').addEventListener('click', function(e) {
  e.preventDefault();

  // 1. Gerar conteúdo (seu código específico)
  const documento = gerarDocumento();

  // 2. Preparar para print
  prepareForPrint({
    documentTitle: 'Minuta de Indiciação — PAD'
  });

  // 3. Abrir print dialog
  window.print();
});

// Cleanup opcional após print
window.addEventListener('afterprint', function() {
  console.log('Impressão concluída ou cancelada');
});
```

---

## Testes

### Via Navegador

1. Abra a ferramenta no navegador
2. Pressione **Ctrl+P** (Windows) ou **Cmd+P** (Mac)
3. Na pré-visualização de impressão, confirme:
   - Header aparece em todas as páginas
   - Footer aparece em todas as páginas
   - Conteúdo não é cortado nas margens
   - Tabelas não quebram no meio
   - Cores (navy/gold) aparecem corretamente

### Via Headless (Chromium + Puppeteer/Playwright)

```javascript
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto('file:///path/to/tool.html');
await page.emulateMedia({ media: 'print' });
await page.pdf({ path: 'output.pdf', format: 'A4' });
```

---

## Troubleshooting

### "Header/footer não aparecem"
- Verifique que o CSS `@media print` foi copiado completamente
- Confirme que `position: fixed` e `z-index: 1000` estão presentes
- Teste no navegador com **Ctrl+P** (print preview)

### "Conteúdo é cortado"
- Confira se as margens (20mm em tudo) estão sendo aplicadas
- Verifique o padding do `#printPage` ou `[role="main"]`

### "Tabelas quebram incorretamente"
- Adicione `page-break-inside: avoid` ao container da tabela
- Se a tabela é muito longa, divida em seções com quebra manual

### "Referência não aparece"
- Confirme que `#coger-print-ref` e `#coger-print-footer-ref` existem no HTML
- Chame `prepareForPrint()` **antes** de `window.print()`

### "UI interativa foi afetada"
- Confirme que todo o CSS impresso está **dentro de `@media print { }`**
- Teste com DevTools: `window.matchMedia('print').matches` deve retornar `false` na UI

---

## Próximas Etapas (Rodadas 10–12)

- **Rodada 10:** Integrar este padrão no **Veritas**
- **Rodada 11:** Integrar este padrão no **Nexo Coger**
- **Rodada 12:** Integrar este padrão no **Oitiva 360**

Cada rodada será uma sessão de teste e ajuste fino específico da ferramenta.

---

## Referência Rápida

| Classe/ID | Uso |
|-----------|-----|
| `.coger-print-header` | Container fixo do header |
| `.coger-print-footer` | Container fixo do footer |
| `.coger-print-section` | Seção numerada com barra lateral |
| `.coger-print-infobox` | Caixa de dados estruturados |
| `.coger-print-legal-block` | Bloco de legislação |
| `.coger-print-table` | Tabela padronizada |
| `#coger-print-ref` | ID para referência no header |
| `#coger-print-footer-ref` | ID para referência no footer |
| `#coger-print-date` | ID para data no header |
| `#coger-print-time` | ID para hora no header |
| `.no-print` | Oculta elemento em print |
| `.coger-print-page-break-before` | Força quebra antes do elemento |
| `.coger-print-no-break` | Evita quebra dentro do elemento |

---

## Suporte Técnico

Para dúvidas ou relatórios de bugs:
1. Verifique que o CSS foi copiado completamente
2. Valide a estrutura com `validatePrintStructure()`
3. Teste em diferentes navegadores (Chrome, Firefox, Safari)
4. Consulte o arquivo `coger-print-template.html` para exemplo completo
