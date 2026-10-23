#!/usr/bin/env python3
"""Parte 3: inserir gerarBlocosFundamentado() + unificar minuta + botões."""

SCRATCH = '/tmp/claude-0/-home-user-desktop-tutorial/3517a069-00ce-5e7e-8ba1-0624996120fa/scratchpad'
with open(f'{SCRATCH}/decoded.html', 'r', encoding='utf-8') as f:
    doc = f.read()
with open(f'{SCRATCH}/gerar_blocos.js', 'r', encoding='utf-8') as f:
    gerar_blocos_js = f.read()

def rep(old, new, n=1, label=''):
    global doc
    c = doc.count(old)
    assert c == n, f'[{label}] esperado {n} ocorrência(s), achou {c}: {old[:90]!r}'
    doc = doc.replace(old, new, n)

# ═══════════════════════════════════════════════════════════════════════════
# 7) Inserir gerarBlocosFundamentado() + montarTextoPlano/HTML + impressão
#    logo antes da (antiga) generateMinuta, que será substituída a seguir
# ═══════════════════════════════════════════════════════════════════════════
rep(
    "    function generateMinuta() {\n        const fat = num('in-fat');",
    gerar_blocos_js + "\n    function generateMinuta() {\n        const fat = num('in-fat');",
    label='inserir gerarBlocosFundamentado antes de generateMinuta')
print('7/12 gerarBlocosFundamentado() + montagens + impressão inseridos.')

with open(f'{SCRATCH}/decoded.html', 'w', encoding='utf-8') as f:
    f.write(doc)
print('OK — parte 3a salva.')
