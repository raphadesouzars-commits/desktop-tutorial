#!/usr/bin/env python3
"""Relatório Fundamentado + Painel de Identificação + Unificação da Minuta.
Opera sobre decoded.html. Nenhuma função de cálculo é tocada; apenas leitura
de estado já computado (lastCalc, publicacaoResult, piState) e de rótulos de
radios/matrizes já selecionados."""
import re

SCRATCH = '/tmp/claude-0/-home-user-desktop-tutorial/3517a069-00ce-5e7e-8ba1-0624996120fa/scratchpad'
with open(f'{SCRATCH}/decoded.html', 'r', encoding='utf-8') as f:
    doc = f.read()

def rep(old, new, n=1, label=''):
    global doc
    c = doc.count(old)
    assert c == n, f'[{label}] esperado {n} ocorrência(s), achou {c}: {old[:90]!r}'
    doc = doc.replace(old, new, n)

# ═══════════════════════════════════════════════════════════════════════════
# 1) CSS — painel de identificação
# ═══════════════════════════════════════════════════════════════════════════
CSS_ANCHOR = '''        .results-just .rj-item b { color: var(--p281); }
    </style>'''
CSS_NEW = '''        /* ─── Painel de Identificação ─── */
        .id-panel { background: #f4f7f9; border: 1px solid #d3def0; border-radius: 8px; margin: 0 0 18px 0; overflow: hidden; }
        .id-panel-header {
            padding: 12px 18px; cursor: pointer; display: flex; justify-content: space-between;
            align-items: center; font-weight: 700; color: var(--p281); background: #eaf0f9;
        }
        .id-panel-header .chev { transition: transform 0.2s; }
        .id-panel.open .id-panel-header .chev { transform: rotate(90deg); }
        .id-panel-body { display: none; padding: 16px 18px; }
        .id-panel.open .id-panel-body { display: block; }
        .id-panel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .id-panel-grid .full { grid-column: 1 / -1; }
        .id-panel label { display: block; font-size: 9.5pt; font-weight: 600; color: var(--p281); margin-bottom: 4px; }
        .id-panel input, .id-panel textarea {
            width: 100%; padding: 8px 10px; border: 1px solid #c8d0e0; border-radius: 6px; font-size: 10pt;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .id-panel textarea { resize: vertical; }
        @media (max-width: 700px) { .id-panel-grid { grid-template-columns: 1fr; } }
    </style>'''
rep(CSS_ANCHOR, CSS_ANCHOR.replace('    </style>', CSS_NEW), label='CSS id-panel')
print('1/12 CSS do painel de identificação inserido.')

# ═══════════════════════════════════════════════════════════════════════════
# 2) HTML — painel de identificação, antes do Step 0
# ═══════════════════════════════════════════════════════════════════════════
ID_PANEL = '''
    <div class="id-panel" id="id-panel">
        <div class="id-panel-header" onclick="document.getElementById('id-panel').classList.toggle('open')">
            <span>Identificação do processo (opcional)</span>
            <span class="chev">▶</span>
        </div>
        <div class="id-panel-body">
            <div class="id-panel-grid">
                <div>
                    <label for="id-processo">Nº do processo (PAR)</label>
                    <input type="text" id="id-processo" placeholder="10000.000000/2026-00" oninput="autosave()">
                </div>
                <div>
                    <label for="id-cnpj">CNPJ</label>
                    <input type="text" id="id-cnpj" placeholder="00.000.000/0000-00" oninput="autosave()">
                </div>
                <div class="full">
                    <label for="id-razao-social">Razão social</label>
                    <input type="text" id="id-razao-social" oninput="autosave()">
                </div>
                <div class="full">
                    <label for="id-comissao">Membros da comissão</label>
                    <textarea id="id-comissao" rows="3" placeholder="Um por linha: Nome — matrícula/cargo" oninput="autosave()"></textarea>
                </div>
            </div>
        </div>
    </div>

'''
rep('        <!-- STEP 0: FATURAMENTO -->',
    ID_PANEL + '        <!-- STEP 0: FATURAMENTO -->',
    label='painel de identificação')
print('2/12 painel de identificação inserido antes do Step 0.')

# ═══════════════════════════════════════════════════════════════════════════
# 3) Remover a seção "Justificativas do Operador" da tela de resultados
# ═══════════════════════════════════════════════════════════════════════════
RESULTS_JUST_HTML = '''
        <div class="results-just" id="results-just" style="display:none;">
            <h3>Justificativas do Operador</h3>
            <div id="results-just-body"></div>
        </div>
'''
rep(RESULTS_JUST_HTML, '\n', label='remover HTML results-just')

rep(
    "    function finish() {\n        document.getElementById('step13').classList.remove('active');\n        document.getElementById('results').style.display = 'block';\n        calculate();\n        renderJustificativas();\n        window.scrollTo(0, 0);\n    }",
    "    function finish() {\n        document.getElementById('step13').classList.remove('active');\n        document.getElementById('results').style.display = 'block';\n        calculate();\n        window.scrollTo(0, 0);\n    }",
    label='finish() sem renderJustificativas')

OLD_RENDER_JUST = '''    function renderJustificativas() {
        const wrap = document.getElementById('results-just');
        const body = document.getElementById('results-just-body');
        let html = '';
        for (let n = 0; n < TOTAL_STEPS; n++) {
            const el = document.getElementById('just-step' + n);
            const val = el ? el.value.trim() : '';
            if (!val) continue;
            html += '<div class="rj-item"><b>Etapa ' + n + ' — ' + escHtml(STEP_LABELS[n]) + ':</b> ' + escHtml(val) + '</div>';
        }
        if (html) {
            body.innerHTML = html;
            wrap.style.display = 'block';
        } else {
            body.innerHTML = '';
            wrap.style.display = 'none';
        }
    }

'''
rep(OLD_RENDER_JUST, '', label='remover função renderJustificativas')
print('3/12 seção "Justificativas do Operador" removida (HTML + JS + chamada).')

# ═══════════════════════════════════════════════════════════════════════════
# 4) Autosave: incluir os 4 campos do painel de identificação
# ═══════════════════════════════════════════════════════════════════════════
rep(
    "            const textIds = ['in-ano-par','in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano','colab-valor'];",
    "            const textIds = ['in-ano-par','in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano','colab-valor','id-processo','id-cnpj','id-razao-social','id-comissao'];",
    label='autosave textIds painel identificação')
rep(
    "                ['in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano','colab-valor'].forEach(id => {",
    "                ['in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano','colab-valor','id-processo','id-cnpj','id-razao-social','id-comissao'].forEach(id => {",
    label='restore textIds painel identificação')
print('4/12 painel de identificação incluído no autosave/restore.')

# ═══════════════════════════════════════════════════════════════════════════
# 5) STEP_LABELS não é mais necessário (só era usado por renderJustificativas)
# ═══════════════════════════════════════════════════════════════════════════
rep(
    "    const STEP_LABELS = ['Base de Cálculo','Vantagens Auferida e Pretendida',\n"
    "        'Agravante — Concurso de Atos (22, I)','Agravante — Ciência Hierárquica (22, II)',\n"
    "        'Agravante — Interrupção (22, III)','Agravante — Situação Econômica (22, IV)',\n"
    "        'Agravante — Reincidência (22, V)','Agravante — Contratos (22, VI)',\n"
    "        'Atenuante — Não Consumação (23, I)','Atenuante — Ressarcimento (23, II)',\n"
    "        'Atenuante — Colaboração (23, III)','Atenuante — Admissão (23, IV)',\n"
    "        'Atenuante — Programa de Integridade (23, V)','Publicação Extraordinária'];\n",
    "",
    label='remover STEP_LABELS')
print('5/12 STEP_LABELS removido (não mais usado).')

with open(f'{SCRATCH}/decoded.html', 'w', encoding='utf-8') as f:
    f.write(doc)
print('\nParte 1/2 salva. Prosseguindo com a Parte 2 (função geradora + botões)...')
