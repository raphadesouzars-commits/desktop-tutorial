#!/usr/bin/env bash
# Tarjamento Coger — Script de inicialização (Linux/macOS)
# Corregedoria da Receita Federal do Brasil

set -e
cd "$(dirname "$0")"

PORTA=8765

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Tarjamento Coger — Corregedoria da Receita Federal     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Verificar se as bibliotecas foram baixadas
if [ ! -f "assets/js/pdf.min.js" ]; then
  echo "ATENÇÃO: Bibliotecas não encontradas!"
  echo "Execute primeiro: bash download-libs.sh"
  echo ""
  exit 1
fi

URL="http://localhost:$PORTA"

# Abrir navegador em background
abrir_navegador() {
  sleep 1
  if command -v xdg-open &>/dev/null; then
    xdg-open "$URL" &>/dev/null &
  elif command -v open &>/dev/null; then
    open "$URL" &
  fi
}

echo "Servidor local na porta $PORTA..."
echo "Acesse: $URL"
echo "Pressione Ctrl+C para encerrar."
echo ""

abrir_navegador &

# Tentar Python 3
if command -v python3 &>/dev/null; then
  python3 -m http.server $PORTA
  exit 0
fi

# Tentar Python 2
if command -v python &>/dev/null; then
  PY_VERSION=$(python -c 'import sys; print(sys.version_info[0])')
  if [ "$PY_VERSION" = "3" ]; then
    python -m http.server $PORTA
  else
    python -m SimpleHTTPServer $PORTA
  fi
  exit 0
fi

# Tentar Node.js
if command -v node &>/dev/null; then
  if command -v npx &>/dev/null; then
    npx serve -l $PORTA .
    exit 0
  fi
fi

echo "ERRO: Nenhum servidor HTTP disponível."
echo "Instale Python 3 (apt install python3 / brew install python3)"
echo "ou Node.js (nodejs.org) e execute este script novamente."
exit 1
