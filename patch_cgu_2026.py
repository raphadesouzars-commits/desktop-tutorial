#!/usr/bin/env python3
"""Aplica os 3 ajustes de conformidade com o Manual CGU (3ª ed., jun/2026)
à Calculadora PAR (Multa_PAR.html). Opera sobre o HTML decodificado do
template JSON e reencoda ao final."""
import json, sys

PATH = '/home/user/desktop-tutorial/Multa_PAR.html'

with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

START_TAG = '<script type="__bundler/template">'
i = html.index(START_TAG) + len(START_TAG)
j = html.index('</script>', i)
raw = html[i:j].strip()
doc = json.loads(raw)          # HTML real
orig = doc

def rep(old, new, n=1, label=''):
    global doc
    c = doc.count(old)
    assert c == n, f'[{label}] esperado {n} ocorrência(s), achou {c}: {old[:70]!r}'
    doc = doc.replace(old, new)

# ═══════════════════════════════════════════════════════════════════════════
# AJUSTE 1 — Art. 22, III, "a": faixas populacionais (Tabela 3.1 Manual CGU)
# ═══════════════════════════════════════════════════════════════════════════
rep('<label for="gs0">Ausência de interrupção <span class="pct zero">0%</span></label>',
    '<label for="gs0">Ausência de interrupção no fornecimento de serviço público <span class="pct zero">0%</span></label>',
    label='gs0')
rep('<label for="gs1">Até 1 semana ou vila/povoado <span class="pct agrav">1,0%</span></label>',
    '<label for="gs1">Até 1 semana, ou impacto em município com até 100 mil habitantes <span class="pct agrav">1,0%</span></label>',
    label='gs1')
rep('<label for="gs2">Até 2 semanas ou cidade até 500 mil hab. <span class="pct agrav">2,0%</span></label>',
    '<label for="gs2">Até 2 semanas, ou impacto em município com até 400 mil habitantes <span class="pct agrav">2,0%</span></label>',
    label='gs2')
rep('<label for="gs3">Até 3 semanas ou cidade +500 mil hab./Estado <span class="pct agrav">3,0%</span></label>',
    '<label for="gs3">Até 3 semanas, ou impacto em município com mais de 400 mil habitantes, ou em mais de um município do mesmo Estado <span class="pct agrav">3,0%</span></label>',
    label='gs3')
rep('<label for="gs4">+4 semanas ou 2+ Estados <span class="pct agrav">4,0%</span></label>',
    '<label for="gs4">Superior a 4 semanas, ou impacto em dois ou mais Estados, ou em dois ou mais municípios com mais de 400 mil habitantes <span class="pct agrav">4,0%</span></label>',
    label='gs4')

# ═══════════════════════════════════════════════════════════════════════════
# AJUSTE 2 — Art. 23, V: fator multiplicador 1,25 (Portaria Conjunta CGU 6/2022)
# ═══════════════════════════════════════════════════════════════════════════
# 2.1 — piState: novos campos
rep('        coi: 0, mpi: 0, apj: 0, raw: 0, capped: 0,\n        evaluated: false,',
    '        coi: 0, mpi: 0, apj: 0, raw: 0, rawPlanilha: 0, multiplied: false, capped: 0,\n        evaluated: false,',
    label='piState-fields')

# 2.2 — piRecalc: aplicar fator 1,25
rep(
'''        // 1st stage: COI * MPI
        const stage1 = coi * mpi;
        // Raw final: stage1 + apj
        const raw = stage1 + apj;
        // Cap at PI_TETO (5%)
        let capped = Math.min(raw, PI_TETO);
        if (capped < 0) capped = 0;

        piState.coi = coi; piState.mpi = mpi; piState.apj = apj;
        piState.raw = raw / 100; // convert to fraction (1.0 = 100% of 1pp... actually raw is in %-points, so /100 gives a decimal)
        // Note: raw is in pontos-percentuais (max ~4-5). The atenuante is raw% of fatuamento.
        // E.g. raw=2.7 means 2.7% atenuante. So in our system: piState.capped = capped / 100
        piState.capped = capped / 100;''',
'''        // 1st stage: COI * MPI
        const stage1 = coi * mpi;
        // Resultado bruto da planilha (pré-multiplicador), em pontos percentuais
        const rawPlanilha = stage1 + apj;
        // Portaria Conjunta CGU nº 6/2022 (Adendo nº 1 ao Manual Prático de Avaliação de PI):
        // aplica-se fator multiplicador de 1,25 quando o resultado da planilha for >= 1%.
        const aplicaFator = rawPlanilha >= 1;
        const rawFinal = aplicaFator ? rawPlanilha * 1.25 : rawPlanilha;
        // Teto de 5% aplicado DEPOIS do multiplicador
        let capped = Math.min(rawFinal, PI_TETO);
        if (capped < 0) capped = 0;

        piState.coi = coi; piState.mpi = mpi; piState.apj = apj;
        piState.rawPlanilha = rawPlanilha / 100; // pré-multiplicador (fração)
        piState.multiplied = aplicaFator;
        piState.raw = rawFinal / 100; // pós-multiplicador, pré-teto (fração)
        piState.capped = capped / 100; // final (fração)''',
    label='piRecalc')

# 2.3 — result box: linha de detalhe do fator
rep(
'''                        <div style="font-size:18pt; font-weight:800; color:var(--p369);" id="pi-result-display">0,00%</div>
                    </div>''',
'''                        <div style="font-size:18pt; font-weight:800; color:var(--p369);" id="pi-result-display">0,00%</div>
                        <div style="font-size:8.5pt; color:#888; margin-top:2px;" id="pi-result-detail"></div>
                    </div>''',
    label='pi-result-detail-box')

# 2.4 — closePiModal: preencher pi-result-detail
rep(
'''        document.getElementById('t-pi-value').value = piState.capped;
        document.getElementById('pi-result-display').textContent = (piState.capped * 100).toFixed(2) + '%';
        document.getElementById('pi-status').textContent = piState.evaluated''',
'''        document.getElementById('t-pi-value').value = piState.capped;
        document.getElementById('pi-result-display').textContent = (piState.capped * 100).toFixed(2) + '%';
        const _piDet = document.getElementById('pi-result-detail');
        if (_piDet) _piDet.textContent = piState.evaluated
            ? (piState.multiplied
                ? `Planilha ${(piState.rawPlanilha*100).toFixed(2)}% × 1,25 (Portaria Conjunta CGU nº 6/2022)`
                : `Planilha ${(piState.rawPlanilha*100).toFixed(2)}% — fator 1,25 não incide (resultado < 1%)`)
            : '';
        document.getElementById('pi-status').textContent = piState.evaluated''',
    label='closePiModal-detail')

# 2.5 — onPiExisteChange: limpar detalhe quando não se aplica
rep(
'''            document.getElementById('t-pi-value').value = 0;
            document.getElementById('pi-result-display').textContent = '0,00%';
            piState.evaluated = false;''',
'''            document.getElementById('t-pi-value').value = 0;
            document.getElementById('pi-result-display').textContent = '0,00%';
            const _d = document.getElementById('pi-result-detail'); if (_d) _d.textContent = '';
            piState.evaluated = false;''',
    label='onPiExiste-clear')

# 2.6 — minuta: detalhe COI×MPI com fator
rep(
"            ? `COI ${piState.coi.toFixed(3)} × MPI ${piState.mpi.toFixed(3)} + APJ ${piState.apj.toFixed(3)} = ${(piState.raw*100).toFixed(2)}% (após teto: ${(tPI*100).toFixed(2)}%)`",
"            ? `COI ${piState.coi.toFixed(3)} × MPI ${piState.mpi.toFixed(3)} + APJ ${piState.apj.toFixed(3)} = ${(piState.rawPlanilha*100).toFixed(2)}%${piState.multiplied ? ' × 1,25 = ' + (piState.raw*100).toFixed(2) + '%' : ''} (após teto: ${(tPI*100).toFixed(2)}%)`",
    label='minuta-piDetail')

# 2.7 — pi modal formula text
rep(
'<div class="pi-score-formula">[COI × MPI] + APJ, com teto de 5% (Decreto 11.129/2022, art. 23, V)</div>',
'<div class="pi-score-formula">[COI × MPI] + APJ, com fator de 1,25 quando ≥ 1% (Portaria Conjunta CGU nº 6/2022) e teto de 5% (Decreto 11.129/2022, art. 23, V)</div>',
    label='pi-modal-formula')

# 2.8 — explanation step12
rep(
'Fórmula final: <b>[COI × MPI] + APJ</b>, com teto de 5%.',
'Fórmula: <b>[COI × MPI] + APJ</b>. Conforme a Portaria Conjunta CGU nº 6/2022, ao resultado da planilha aplica-se um <b>fator multiplicador de 1,25</b> sempre que esse resultado for igual ou superior a 1%, respeitado o teto de 5%.',
    label='explanation-step12')

# 2.9 — relatório PI: cabeçalho da fórmula
rep(
'<p>Decreto nº 11.129/2022, art. 23, V • Fórmula: [COI × MPI] + APJ • Teto: 5%</p>',
'<p>Decreto nº 11.129/2022, art. 23, V • Fórmula: [COI × MPI] + APJ • Fator 1,25 (Portaria Conjunta CGU nº 6/2022, quando ≥ 1%) • Teto: 5%</p>',
    label='relatorio-pi-formula')

# 2.10 — relatório PI: resumo de pontuação com fator
rep(
'''        html += `<div>1ª etapa [COI × MPI]: <b>${(piState.coi * piState.mpi).toFixed(3)}</b></div>`;
        html += `<div>Atenuante apurada (após teto de 5%): <span class="val">${(piState.capped * 100).toFixed(2)}%</span></div>`;''',
'''        html += `<div>1ª etapa [COI × MPI]: <b>${(piState.coi * piState.mpi).toFixed(3)}</b></div>`;
        html += `<div>Resultado da planilha [COI × MPI + APJ]: <b>${(piState.rawPlanilha * 100).toFixed(2)}%</b></div>`;
        html += `<div>Fator multiplicador (Portaria Conjunta CGU nº 6/2022): <b>${piState.multiplied ? '1,25 (aplicado)' : 'não aplicável — resultado < 1%'}</b></div>`;
        html += `<div>Atenuante apurada (após teto de 5%): <span class="val">${(piState.capped * 100).toFixed(2)}%</span></div>`;''',
    label='relatorio-pi-resumo')

# 2.11 — minuta: linha do PI com menção ao fator
rep(
"            if (tPI > 0) linhas.push(`• Programa de integridade (art. 23, V): ${pct(tPI)}.`);",
"            if (tPI > 0) linhas.push(`• Programa de integridade (art. 23, V): ${pct(tPI)}${piState.multiplied ? ' (resultado da planilha majorado pelo fator de 1,25, conforme Portaria Conjunta CGU nº 6/2022)' : ''}.`);",
    label='minuta-pi-linha')

# ═══════════════════════════════════════════════════════════════════════════
# AJUSTE 3 — Art. 23, III: colaboração como faixa discricionária
# ═══════════════════════════════════════════════════════════════════════════
# 3.1 — header do bloco de checkboxes
rep(
'<div style="font-size:10pt; font-weight:700; color:#27ae60; margin-bottom:10px;">Marque cada condição presente (+ 0,5% cada):</div>',
'<div style="font-size:10pt; font-weight:700; color:#27ae60; margin-bottom:10px;">Marque as condições factualmente presentes:</div>',
    label='colab-header')

# 3.2 — remover badges +0,5% dos rótulos (agora não são somas fixas)
rep('<label for="colab-cb-1">Admitiu a prática do ato <span class="pct aten">+0,5%</span></label>',
    '<label for="colab-cb-1">Admitiu a prática do ato</label>', label='colab-lbl-1')
rep('<label for="colab-cb-2">Forneceu elementos para a apuração <span class="pct aten">+0,5%</span></label>',
    '<label for="colab-cb-2">Forneceu elementos para a apuração</label>', label='colab-lbl-2')
rep('<label for="colab-cb-3">Renunciou aos prazos processuais <span class="pct aten">+0,5%</span></label>',
    '<label for="colab-cb-3">Renunciou aos prazos processuais</label>', label='colab-lbl-3')

# 3.3 — inserir bloco de ajuste (faixa 0,5–1,0% ou 1,5% fixo)
rep(
'''                </div>
                <div style="margin-top:12px; padding:10px; background:#eaf5e1; border-radius:6px; font-size:10.5pt;">
                    <b>Atenuante apurada (Art. 23, III):</b> <span id="colab-total-display" style="color:#27ae60; font-weight:800;">0,0%</span>
                </div>''',
'''                </div>
                <div id="colab-adjust" style="display:none; margin-top:12px; padding:12px; background:#eef6ff; border-radius:6px;">
                    <div id="colab-adjust-range">
                        <label style="font-size:10pt; font-weight:600; color:var(--p281);">Percentual (faixa discricionária de 0,5% a 1,0%):
                            <input type="number" id="colab-valor" min="0.5" max="1.0" step="0.1" value="0.5" onchange="recalcColab()" oninput="recalcColab()" style="width:72px; margin-left:6px; padding:4px 6px; border:1px solid #bbb; border-radius:4px;"> %
                        </label>
                        <div style="font-size:8.5pt; color:#666; font-style:italic; margin-top:4px;">A autoridade fixa o valor conforme a utilidade e a relevância da colaboração para a apuração (uma ou duas condições presentes).</div>
                    </div>
                    <div id="colab-adjust-fixed" style="display:none; font-size:10pt; color:#27ae60; font-weight:600;">
                        Três condições presentes simultaneamente: percentual fixo de <b>1,5%</b> (sem margem de discricionariedade, conforme Tabela 6 do Manual CGU).
                    </div>
                </div>
                <div style="margin-top:12px; padding:10px; background:#eaf5e1; border-radius:6px; font-size:10.5pt;">
                    <b>Atenuante apurada (Art. 23, III):</b> <span id="colab-total-display" style="color:#27ae60; font-weight:800;">0,0%</span>
                </div>''',
    label='colab-adjust-block')

# 3.4 — recalcColab: nova lógica
rep(
'''    function recalcColab() {
        let total = 0;
        ['colab-cb-1','colab-cb-2','colab-cb-3'].forEach(id => {
            if (document.getElementById(id).checked) total += 0.005;
        });
        document.getElementById('t-colab').value = total;
        document.getElementById('colab-total-display').textContent = (total * 100).toFixed(1) + '%';
    }''',
'''    function recalcColab() {
        let n = 0;
        ['colab-cb-1','colab-cb-2','colab-cb-3'].forEach(id => {
            if (document.getElementById(id).checked) n++;
        });
        const adjust = document.getElementById('colab-adjust');
        const rangeBox = document.getElementById('colab-adjust-range');
        const fixedBox = document.getElementById('colab-adjust-fixed');
        const valorInput = document.getElementById('colab-valor');
        let total = 0;
        if (n === 0) {
            total = 0;
            if (adjust) adjust.style.display = 'none';
        } else if (n === 3) {
            // Tabela 6 do Manual CGU: três condições => 1,5% fixo, sem discricionariedade
            total = 0.015;
            if (adjust) adjust.style.display = 'block';
            if (rangeBox) rangeBox.style.display = 'none';
            if (fixedBox) fixedBox.style.display = 'block';
        } else {
            // uma ou duas condições => faixa discricionária de 0,5% a 1,0%
            if (adjust) adjust.style.display = 'block';
            if (rangeBox) rangeBox.style.display = 'block';
            if (fixedBox) fixedBox.style.display = 'none';
            let v = parseFloat(valorInput ? valorInput.value : '0.5');
            if (isNaN(v)) v = 0.5;
            if (v < 0.5) v = 0.5;
            if (v > 1.0) v = 1.0;
            total = v / 100;
        }
        document.getElementById('t-colab').value = total;
        document.getElementById('colab-total-display').textContent = (total * 100).toFixed(1) + '%';
    }''',
    label='recalcColab')

# 3.5 — explanation step10
rep(
'<b>Grau de Colaboração da Pessoa Jurídica:</b> reconhecida ainda que não haja admissão de responsabilidade. Marque cada condição presente — cada uma acrescenta 0,5%, podendo totalizar até 1,5%.',
'<b>Grau de Colaboração da Pessoa Jurídica:</b> reconhecida ainda que não haja admissão de responsabilidade. Marque as condições factualmente presentes. Conforme a Tabela 6 do Manual CGU (art. 23, III): uma ou duas condições ensejam percentual <b>discricionário de 0,5% a 1,0%</b>, fixado conforme a utilidade e a relevância da colaboração; as três condições, simultaneamente, ensejam percentual <b>fixo de 1,5%</b>.',
    label='explanation-step10')

# 3.6 — autosave: incluir colab-valor nos textIds
rep(
"            const textIds = ['in-ano-par','in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano'];",
"            const textIds = ['in-ano-par','in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano','colab-valor'];",
    label='autosave-textIds')

# 3.7 — restore: incluir colab-valor na lista de restauração de texto
rep(
"                ['in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano'].forEach(id => {",
"                ['in-ano-fat-ref','in-fat','van-direto','van-pretendida','van-pretendida-justificativa','fat-ultimo-apurado','fat-ultimo-ano','colab-valor'].forEach(id => {",
    label='restore-textIds')

# ═══════════════════════════════════════════════════════════════════════════
# Reencode
# ═══════════════════════════════════════════════════════════════════════════
new_raw = json.dumps(doc, ensure_ascii=False)
# proteger </script (único no conteúdo) para não encerrar o <script> externo
new_raw = new_raw.replace('</script', '<\\u002Fscript')
# validar round-trip
assert json.loads(new_raw) == doc, 'round-trip falhou'

new_html = html[:i] + new_raw + html[j:]
with open(PATH, 'w', encoding='utf-8') as f:
    f.write(new_html)

print('OK — ajustes aplicados. Tamanho HTML:', len(new_html))
print('Mudança no conteúdo decodificado:', len(orig), '->', len(doc), 'chars')
