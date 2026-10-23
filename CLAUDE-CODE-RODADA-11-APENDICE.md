# Apêndice — Rodada 11 — Formatos de Documento no Nexo Coger

> **⚠️ CORREÇÃO (Rodada 13 — verificação de 2026-07-13):** este apêndice originalmente descrevia o **Termo de Intimação** (Formato 1, abaixo) como já implementado com a estrutura de 7 seções do Print Standard (`coger-print-section`, header/footer fixos). **Isso é incorreto.** A Rodada 11 migrou apenas `renderIndiciacao()` (Nota de Indiciação) ao Print Standard — a função `renderIntimacao()` (Termo de Intimação) continua usando o renderer legado `openPrint()`/`.pv-doc` (parágrafos corridos, sem header/footer fixo, sem seções numeradas, sem paleta/tipografia COGER), confirmado por inspeção direta do código-fonte e captura da impressão renderizada. A estrutura de 7 seções abaixo é a especificação **desejada**, não o estado real do código. Ver `relatorio-verificacao-print-standard-2026-07-13.md`, item 4.1 e não conformidade crítica nº 2, para detalhes. Correção pendente para rodada subsequente.

## 📋 Escopo

Rodada 11 implementou **Print Standard unificado** (header, footer, seções, estilos) no Nexo Coger — **apenas para a Nota de Indiciação** (`renderIndiciacao()`). Este apêndice esclarece os **formatos específicos de documento** que o Nexo Coger gera e como eles se relacionam com o Print Standard (ver correção acima quanto ao Termo de Intimação).

---

## 🎯 Contexto Legal

### PAD (Processo Administrativo Disciplinar)
- Regido pela **Lei nº 8.112/90** (Servidor Público Federal)
- Procedimento: sindicância → apuração → **indiciação** → julgamento
- **Nexo Coger gera 2 minutas:**
  1. **Termo de Intimação** — notifica acusado do início do processo
  2. **Nota de Indiciação** — recomenda ao presidente da comissão que instaure PAD

---

## 📄 FORMATO 1: TERMO DE INTIMAÇÃO (PAD)

### Propósito
Notificação formal ao acusado de que está sendo instaurado Processo Administrativo Disciplinar, informando direitos, acusação, provas e data para audiência.

### Estrutura de Impressão (7 seções com Print Standard)

```
┌─────────────────────────────────┐
│ HEADER FIXO                     │ ← Logo + "TERMO DE INTIMAÇÃO"
│ MF Logo | RFB Logo              │ ← Referência INT-YYYYMMDD-XXXX
├─────────────────────────────────┤
│ ——— CABEÇALHO INTRODUTÓRIO      │
│ "Aos [data], na cidade de..."   │
│                                 │
│ 1 — NOTIFICAÇÃO E DIREITOS      │ ← Seção 1, barra gold
│ • Acusação de infração          │
│ • Instauração de PAD            │
│ • Direitos à defesa...          │
│                                 │
│ 2 — ACUSAÇÃO E FATOS            │ ← Seção 2, barra gold
│ [Caixa de info com fatos]       │
│                                 │
│ 3 — PROVAS E FUNDAMENTAÇÃO      │ ← Seção 3, barra gold
│ Síntese de provas...            │
│                                 │
│ 4 — CITAÇÃO                     │ ← Seção 4, barra gold
│ "Fica citado para..."           │
│                                 │
│ 5 — DIREITOS E ADVERTÊNCIAS     │ ← Seção 5, barra gold
│ • Não comparecimento...         │
│ • Direito ao silêncio...        │
│                                 │
│ 6 — ENCERRAMENTO                │ ← Seção 6, barra gold
│ [Blocos de assinatura 3 col]    │ ← Presidente, Acusado, Testemunha
├─────────────────────────────────┤
│ FOOTER FIXO                     │ ← Referência | Página X de Y | USO INTERNO
└─────────────────────────────────┘
```

### Campos Preenchidos pelo Nexo Coger
- **Acusado:** Nome, matrícula, cargo, unidade
- **Comissão:** Presidente, vogais, secretário
- **Fatos:** Descrição de cada fato apurado
- **Normas:** Artigos violados (Lei 8.112/90, arts. 116/117/132)
- **Provas:** Síntese de provas coletadas
- **Data da audiência:** Para PAD ordinário
- **Prazo de defesa:** Para apresentar defesa escrita

### Diferença vs. Nota de Indiciação
- **Dirigida ao:** Acusado (ato processual)
- **Função:** Notificar e convocar para audiência
- **Tom:** Formal, legal, listando direitos
- **Timing:** Emitida **após** a Nota de Indiciação

### CSS Classes Print Standard
- `.coger-print-section` (seções numeradas com barra gold)
- `.coger-print-section-title` (título da seção)
- `.coger-print-section-body` (conteúdo)
- `.coger-print-infobox` (caixa de identificação)
- `.coger-print-infobox-row` (linhas com rótulo + valor)
- Header + Footer fixos (`.coger-print-header`, `.coger-print-footer`)

---

## 📄 FORMATO 2: NOTA DE INDICIAÇÃO (PAD)

### Propósito
Parecer técnico recomendando ao presidente da comissão que instaure Processo Administrativo Disciplinar contra o acusado, baseado em fatos apurados e enquadramento legal.

### Estrutura de Impressão (6–7 seções com Print Standard)

```
┌─────────────────────────────────┐
│ HEADER FIXO                     │ ← Logo + "NOTA DE INDICIAÇÃO"
│ MF Logo | RFB Logo              │ ← Referência INT-YYYYMMDD-XXXX
├─────────────────────────────────┤
│ ——— CABEÇALHO INTRODUTÓRIO      │
│ "À consideração de Vossa..."    │
│                                 │
│ 1 — IDENTIFICAÇÃO DO ACUSADO    │ ← Seção 1, barra gold
│ [Caixa de info]                 │ ← Nome, matrícula, cargo, unidade
│                                 │
│ 2 — FATOS APURADOS              │ ← Seção 2, barra gold
│ Durante investigação foram...   │
│                                 │
│ 3 — PROVAS COLETADAS            │ ← Seção 3, barra gold
│ As seguintes provas...          │
│                                 │
│ 4 — ENQUADRAMENTO LEGAL         │ ← Seção 4, barra gold
│ [Tabela fato-prova-norma]       │ ← thead replicado em multiplas páginas
│                                 │
│ 5 — PARECER TÉCNICO             │ ← Seção 5, barra gold
│ "Diante do exposto, opina..."   │
│                                 │
│ 6 — ASSINATURA                  │ ← Seção 6, barra gold
│ [Bloco assinatura 1 coluna]     │ ← Servidor responsável
├─────────────────────────────────┤
│ FOOTER FIXO                     │ ← Referência | Página X de Y | USO INTERNO
└─────────────────────────────────┘
```

### Campos Preenchidos pelo Nexo Coger
- **Acusado:** Nome, matrícula, cargo, unidade (identificação formal)
- **Fatos apurados:** Descrição de cada fato com numeração
- **Provas:** Síntese de documentos, depoimentos, perícias
- **Enquadramento legal:** Tabela (Fato | Prova | Artigo Lei 8.112/90)
- **Rito:** Simplificado ou ordinário
- **Responsável:** Servidor que elabora (nome, cargo, matrícula)

### Diferença vs. Termo de Intimação
- **Dirigida a:** Presidente da comissão (ato administrativo)
- **Função:** Fundamentar a decisão de instaurer PAD
- **Tom:** Parecer técnico, conclusivo
- **Timing:** Emitida **antes** do Termo de Intimação
- **Conteúdo:** Análise jurídica completa (fato-prova-norma)

### CSS Classes Print Standard
- `.coger-print-section` (seções numeradas)
- `.coger-print-section-title` (títulos)
- `.coger-print-section-body` (conteúdo)
- `.coger-print-infobox` (identificação do acusado)
- `.coger-print-table` (tabela com thead replicado)
- Header + Footer fixos

### Diferença Técnica: Tabelas Multi-página
Nota de Indiciação pode ter tabela **Síntese Fato-Prova-Norma** com múltiplas linhas que quebrará em várias páginas. A Rodada 11 implementou:

```css
.coger-print-table thead {
  display: table-header-group;  /* Replica thead em cada página */
  page-break-inside: avoid;
}
```

Isso garante que o cabeçalho da tabela seja repetido em cada página, mantendo inteligibilidade.

---

## 🔄 Fluxo de Documentos no PAD

```
[Investigação prévia]
        ↓
[Nota de Indiciação] ← Enviada ao Presidente
        ↓
[Presidente decide instaurer PAD]
        ↓
[Termo de Intimação] ← Enviado ao Acusado
        ↓
[Audiência/Defesa]
        ↓
[Julgamento]
```

**Importante:** Ambos os documentos devem ter o mesmo Print Standard (header/footer/seções gold), mas serve a públicos diferentes:
- **Nota** é parecer técnico (interno)
- **Termo** é ato processual (externo)

---

## ✅ Critérios de Aceite para Rodada 11

Print Standard foi implementado em `ferramentas/nexo-coger.html` com:

- [x] Header fixo em todas as páginas (logos + "NOTA DE INDICIAÇÃO")
- [x] Footer fixo em todas as páginas (referência + paginação)
- [x] 7 seções com barra lateral gold (#C9A35C)
- [x] Caixa de informações com rótulos (`.coger-print-infobox`)
- [x] Tabela fato-prova-norma com thead replicado (multi-página)
- [x] Page-break: nenhuma seção-título fica órfã
- [x] Referência gerada: INT-YYYYMMDD-XXXX
- [x] Paleta navy (#0B2F5F) / gold (#C9A35C)
- [x] Tipografia: Barlow Condensed + Inter
- [x] UI interativa funcionando normalmente
- [x] Nenhum botão/input visível na impressão

---

## 📌 Relação com Rodada 12

Rodada 12 implementará o mesmo Print Standard no **Oitiva 360**, que gera:

- **Único documento:** Termo de Oitiva (termo de redução com Q&A)
- **Estrutura:** 3 seções simples (Identificação, Q&A, Encerramento)
- **Diferença:** Linear (sem tabelas), Q&A formatada (pergunta negrito, resposta normal)
- **Mesmos estilos:** Header/footer fixos, seções gold, mesma paleta

---

## 📚 Referência de Código

Implementação em `ferramentas/nexo-coger.html`:

1. **CSS Print Standard:** Linhas ~1400-1800 (substituiu ~8 linhas anteriores)
2. **JS Module:** `window.CogerPrint` IIFE (~73 linhas) com funções:
   - `generatePrintReference()` — INT-YYYYMMDD-XXXX
   - `formatDatePtBr()` — Data em português
   - `formatTimePtBr()` — Hora em português
   - `fillPrintMetadata()` — Preenche header/footer
   - `prepareForPrint()` — Coordena tudo antes de `window.print()`

3. **Refatoração de renderIndiciacao():** Gera estrutura #printPage com:
   - Header com logos (data URI)
   - Main com 7 sections
   - Footer com paginação

---

## 🎯 Próximo Passo: Rodada 12

Oitiva 360 seguirá o **exato mesmo padrão**:

1. Mesmo CSS Print Standard (copy-paste de nexo-coger.html)
2. Mesmo JS Module (window.CogerPrint)
3. Estrutura adaptada para 3 seções (vs. 7 do Nexo)
4. Q&A com formatação específica (pergunta negrito, resposta normal)
5. Page-break-inside: avoid para cada item Q&A

Estimativa: 3–4 horas (mais simples que Rodada 11, sem tabelas complexas).

---

*Apêndice completado: 2026-07-13 | Rodada 11 — Print Standard COGER*
