#!/usr/bin/env bash
# Inicia o motor AICI (Linux/macOS). Na primeira vez, instala as dependencias.
cd "$(dirname "$0")" || exit 1
command -v python3 >/dev/null || { echo "Python 3.12+ nao encontrado."; exit 1; }
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
[ -f .venv/instalado.txt ] || { pip install -r requirements.txt && echo ok > .venv/instalado.txt; } || exit 1
echo "Motor AICI em http://127.0.0.1:8765 (Ctrl+C para desligar)"
exec python main.py
