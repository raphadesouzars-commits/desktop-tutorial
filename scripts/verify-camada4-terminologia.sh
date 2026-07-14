#!/bin/bash
# Rodada 13 — Camada 4.5: Verificação cruzada de terminologia (não contaminação PAD <-> PAR)
# Escopo: apenas as FUNÇÕES DE GERAÇÃO DE DOCUMENTO/MINUTA (renderIndiciacao, renderIntimacao),
# não o arquivo inteiro — o catálogo canônico embutido (CATALOGO_COGER) referencia normas de
# AMBOS os domínios (pad/par) em todas as ferramentas, por design, para permitir validação
# cruzada (ex.: recusar prova PAR importada no Nexo Coger). Isso não é contaminação: é dado de
# referência, nunca aparece no documento final gerado. Veritas e Oitiva 360 são ferramentas
# DUAL-MODO (PAD/PAR) por desenho (Rodadas PAR-2/PAR-4) — não fazem parte desta checagem, que
# se aplica apenas a Nexo Coger (exclusivo PAD) vs. Nexo PAR (exclusivo PAR).
# Reutilizável a cada nova rodada de mudança nos templates de geração de minuta.
set -e
cd "$(dirname "$0")/.."

PROIBIDOS_PAR_EM_PAD='ato les[ivo][a-z]*|pessoa jurídica investigada|12\.846|12846'
PROIBIDOS_PAD_EM_PAR='\bservidor[a-z]*\b|matr[íi]cula|infra[cç][aã]o funcional|8\.112|8112'

echo "=== [Escopo: função] Nexo Coger — renderIndiciacao/renderIntimacao não devem conter termos PAR ==="
for fn in renderIndiciacao renderIntimacao; do
  echo ">> function $fn (nexo-coger.html)"
  awk "/^function $fn\(/,/^function [a-zA-Z]/" ferramentas/nexo-coger.html | grep -noE "$PROIBIDOS_PAR_EM_PAD" || echo "   (nenhuma ocorrência)"
done

echo ""
echo "=== [Escopo: função] Nexo PAR — renderIndiciacao não deve conter termos PAD ==="
echo ">> function renderIndiciacao (nexo-par.html)"
awk '/^function renderIndiciacao\(/,/^function [a-zA-Z]/' ferramentas/nexo-par.html | grep -noE "$PROIBIDOS_PAD_EM_PAR" || echo "   (nenhuma ocorrência)"

echo ""
echo "=== [Referência — arquivo inteiro, INFORMATIVO, não é falha] ==="
echo "Ocorrências fora do escopo de função (catálogo/validação cruzada, esperado > 0):"
for f in ferramentas/nexo-coger.html; do
  n=$(grep -coE "$PROIBIDOS_PAR_EM_PAD" "$f" || true)
  echo "  $f (termos PAR, arquivo inteiro): $n"
done
n=$(grep -coE "$PROIBIDOS_PAD_EM_PAR" ferramentas/nexo-par.html || true)
echo "  ferramentas/nexo-par.html (termos PAD, arquivo inteiro): $n"
