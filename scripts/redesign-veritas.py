#!/usr/bin/env python3
# Rodada 13 (extensão): aplica o mesmo redesign Integritas ao Veritas.
import re

PATH = '/home/user/desktop-tutorial/ferramentas/veritas.html'
B64_PATH = '/tmp/cabecalho-b64.txt'

with open(B64_PATH) as f:
    b64 = f.read().strip()

with open(PATH, encoding='utf-8') as f:
    content = f.read()

# ---------------------------------------------------------------------------
# 1. print-color-adjust:exact no topo do @media print existente
# ---------------------------------------------------------------------------
anchor = """@media print {
  :root {
    --font-sans: var(--coger-print-font-sans);
    --font-display: var(--coger-print-font-display);
    --font-mono: var(--coger-print-font-mono);
  }

  body {"""
assert anchor in content, "media print anchor not found"
replacement = """@media print {
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
  @page { margin: 15mm 18mm; }

  :root {
    --font-sans: var(--coger-print-font-sans);
    --font-display: var(--coger-print-font-display);
    --font-mono: var(--coger-print-font-mono);
  }

  body {"""
content = content.replace(anchor, replacement)

# ---------------------------------------------------------------------------
# 2. Remover a reserva de padding baseada em header/footer fixos (não usamos
#    mais position:fixed no novo viewRelatorio — mesmo motivo do Nexo Coger:
#    mais robusto entre motores de impressão, sem recorte por overflow).
# ---------------------------------------------------------------------------
old_padding = """  .vdc-main, [role="main"], #printPage {
    max-width: none;
    padding: calc(var(--coger-print-header-height) + var(--coger-print-margin-top))
             var(--coger-print-margin-right)
             calc(var(--coger-print-footer-height) + var(--coger-print-margin-bottom))
             var(--coger-print-margin-left);
    width: 100%;
    margin: 0;
  }"""
assert old_padding in content, "padding rule not found"
new_padding = """  .vdc-main, [role="main"], #printPage {
    max-width: none;
    width: 100%;
    margin: 0;
  }"""
content = content.replace(old_padding, new_padding)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fase 1 (CSS) concluída.")
