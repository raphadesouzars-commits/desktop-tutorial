#!/usr/bin/env bash
# Download das bibliotecas JavaScript necessárias para o Tarjamento Coger
# Execute uma vez para preparar a pasta para uso offline.

set -e
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Download das Bibliotecas — Tarjamento Coger            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Este script baixa as bibliotecas necessárias para uso offline."
echo "Após a conclusão, a ferramenta não precisará mais de internet."
echo ""

mkdir -p assets/js/tesseract
mkdir -p assets/lang

# ── PDF.js (Mozilla) — versão 3.11.174, estável e amplamente testada ─────────
PDFJS_VERSION="3.11.174"
echo "[1/4] Baixando PDF.js v${PDFJS_VERSION}..."
curl -fsSL "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_VERSION}/pdf.min.js" \
  -o assets/js/pdf.min.js
curl -fsSL "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_VERSION}/pdf.worker.min.js" \
  -o assets/js/pdf.worker.min.js

# Verificar se o download funcionou
if [ ! -s "assets/js/pdf.min.js" ]; then
  echo "   ⚠ cdnjs falhou, tentando unpkg..."
  curl -fsSL "https://unpkg.com/pdfjs-dist@${PDFJS_VERSION}/build/pdf.min.js" \
    -o assets/js/pdf.min.js
  curl -fsSL "https://unpkg.com/pdfjs-dist@${PDFJS_VERSION}/build/pdf.worker.min.js" \
    -o assets/js/pdf.worker.min.js
fi
echo "   ✓ PDF.js instalado"

# ── jsPDF ─────────────────────────────────────────────────────────────────────
echo "[2/4] Baixando jsPDF..."
curl -fsSL "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js" \
  -o assets/js/jspdf.min.js
if [ ! -s "assets/js/jspdf.min.js" ]; then
  curl -fsSL "https://unpkg.com/jspdf@2.5.1/dist/jspdf.umd.min.js" \
    -o assets/js/jspdf.min.js
fi
echo "   ✓ jsPDF instalado"

# ── Tesseract.js ─────────────────────────────────────────────────────────────
echo "[3/4] Baixando Tesseract.js..."
curl -fsSL "https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/tesseract.min.js" \
  -o assets/js/tesseract.min.js
curl -fsSL "https://cdn.jsdelivr.net/npm/tesseract.js@4/dist/worker.min.js" \
  -o assets/js/tesseract/worker.min.js
curl -fsSL "https://cdn.jsdelivr.net/npm/tesseract.js-core@4/tesseract-core.wasm.js" \
  -o assets/js/tesseract/tesseract-core.wasm.js
echo "   ✓ Tesseract.js instalado"

# ── Dados de idioma português (Tesseract) ──────────────────────────────────
echo "[4/4] Baixando dados de idioma português (~10 MB)..."
echo "      (necessário para OCR de documentos escaneados)"
curl -fsSL "https://github.com/naptha/tessdata/raw/gh-pages/4.0.0/por.traineddata.gz" \
  -o assets/lang/por.traineddata.gz
if command -v gunzip &>/dev/null; then
  gunzip -f assets/lang/por.traineddata.gz
  echo "   ✓ Dados de idioma instalados (assets/lang/por.traineddata)"
else
  echo "   ⚠ Não foi possível descompactar automaticamente."
  echo "     Descompacte assets/lang/por.traineddata.gz manualmente para habilitar o OCR."
fi

echo ""
echo "✅ Download concluído! Você pode agora usar a ferramenta offline."
echo "   Execute: bash iniciar.sh"
echo ""
