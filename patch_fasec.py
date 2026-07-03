#!/usr/bin/env python3
"""Fase C — Manual Vivo (F1) + Caixa de Justificativa (F2), exceto o item 4.4
(extensão do generateMinuta), que aguarda decisão do usuário sobre a
ambiguidade dos blocos de agravantes/atenuantes colapsados a 0%."""
import re

SCRATCH = '/tmp/claude-0/-home-user-desktop-tutorial/3517a069-00ce-5e7e-8ba1-0624996120fa/scratchpad'
with open(f'{SCRATCH}/decoded.html', 'r', encoding='utf-8') as f:
    doc = f.read()

def rep(old, new, n=1, label=''):
    global doc
    c = doc.count(old)
    assert c == n, f'[{label}] esperado {n} ocorrência(s), achou {c}: {old[:80]!r}'
    doc = doc.replace(old, new, n)

# ═══════════════════════════════════════════════════════════════════════════
# 1) CSS
# ═══════════════════════════════════════════════════════════════════════════
CSS_BLOCK = '''
        /* ─── Fase C: Manual Vivo (F1) ─── */
        .help-btn {
            background: transparent; border: 1px solid #1d3a78; color: #1d3a78;
            border-radius: 6px; font-size: 9pt; padding: 2px 10px;
            cursor: pointer; float: right;
        }
        .help-btn:hover { background: #1d3a78; color: white; }
        .help-close {
            cursor: pointer; font-size: 22pt;
            background: rgba(255,255,255,0.15); color: white;
            border: none; border-radius: 50%;
            width: 36px; height: 36px;
            line-height: 1; padding: 0;
        }
        .help-close:hover { background: rgba(255,255,255,0.3); }
        .help-warn {
            background: #fff7e6; border-left: 3px solid #d97706;
            padding: 8px 12px; margin: 10px 0;
        }

        /* ─── Fase C: Caixa de Justificativa (F2) ─── */
        .just-box { margin-top: 14px; }
        .just-box textarea {
            width: 100%; border: 1px solid #c8d0e0; border-radius: 6px;
            font-size: 10pt; padding: 8px; resize: vertical;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .just-hint { font-weight: 400; opacity: .65; font-size: 8.5pt; }
        .results-just { margin-top: 25px; }
        .results-just h3 { color: var(--p281); font-size: 12pt; margin-bottom: 10px; }
        .results-just .rj-item { margin-bottom: 10px; font-size: 10pt; line-height: 1.5; }
        .results-just .rj-item b { color: var(--p281); }
    </style>'''
CSS_ANCHOR = '''            .pi-q-ctrls { width: 100%; }
        }
    </style>'''
rep(CSS_ANCHOR, CSS_ANCHOR.replace('    </style>', CSS_BLOCK.lstrip('\n')), label='CSS block')
print('1/9 CSS inserido.')

# ═══════════════════════════════════════════════════════════════════════════
# 2) help-modal (após o fechamento do #pi-modal, antes do restore-banner)
# ═══════════════════════════════════════════════════════════════════════════
HELP_MODAL = '''
    <div class="pi-modal" id="help-modal" onclick="if(event.target===this) closeHelp()">
        <div class="pi-card" style="max-width: 760px;">
            <div class="pi-header">
                <div>
                    <h2 id="help-title"></h2>
                    <p id="help-ref" style="opacity:.75;"></p>
                </div>
                <button type="button" onclick="closeHelp()" class="help-close">✕</button>
            </div>
            <div id="help-body" style="max-height:60vh; overflow-y:auto; font-size:10.5pt; line-height:1.55; padding:20px 26px;"></div>
        </div>
    </div>
'''
rep('    <!-- Banner de restauração de rascunho (substitui window.confirm) -->',
    HELP_MODAL + '\n    <!-- Banner de restauração de rascunho (substitui window.confirm) -->',
    label='help-modal insertion')
print('2/9 help-modal inserido.')

# ═══════════════════════════════════════════════════════════════════════════
# 3) 14 botões "📖 Manual" — logo após cada step-badge
# ═══════════════════════════════════════════════════════════════════════════
BADGES = [
    '<span class="step-badge">Base de Cálculo</span>',
    '<span class="step-badge vantagem">Vantagens Auferida e Pretendida — Art. 26, Decreto nº 11.129/2022</span>',
    '<span class="step-badge agravante">Agravante — Art. 22, I</span>',
    '<span class="step-badge agravante">Agravante — Art. 22, II</span>',
    '<span class="step-badge agravante">Agravante — Art. 22, III</span>',
    '<span class="step-badge agravante">Agravante — Art. 22, IV</span>',
    '<span class="step-badge agravante">Agravante — Art. 22, V</span>',
    '<span class="step-badge agravante">Agravante — Art. 22, VI</span>',
    '<span class="step-badge atenuante">Atenuante — Art. 23, I</span>',
    '<span class="step-badge atenuante">Atenuante — Art. 23, II</span>',
    '<span class="step-badge atenuante">Atenuante — Art. 23, III</span>',
    '<span class="step-badge atenuante">Atenuante — Art. 23, IV</span>',
    '<span class="step-badge atenuante">Atenuante — Art. 23, V</span>',
    '<span class="step-badge" style="background:#1d3a78;">Publicação Extraordinária — Art. 6º, II, Lei nº 12.846/2013</span>',
]
for n, badge_html in enumerate(BADGES):
    rep(badge_html, badge_html + f'\n            <button type="button" class="help-btn" onclick="openHelp({n})">📖 Manual</button>',
        label=f'help-btn step{n}')
print('3/9 14 botões 📖 Manual inseridos.')

# ═══════════════════════════════════════════════════════════════════════════
# 4) 14 caixas de justificativa — imediatamente antes de cada nav-buttons,
#    localizadas por índice dentro de cada step-container (evita colisão de
#    strings repetidas entre etapas).
# ═══════════════════════════════════════════════════════════════════════════
JUST_TEMPLATE = '''            <div class="just-box">
                <label class="field-label" for="just-step{n}">
                    Justificativa da marcação (opcional)
                    <span class="just-hint">— será transcrita no relatório e na minuta</span>
                </label>
                <textarea id="just-step{n}" rows="2" maxlength="2000"
                    placeholder="Ex.: fonte da informação, prova dos autos (fls.), critério adotado…"
                    oninput="autosave()"></textarea>
            </div>

'''
for n in range(14):
    m = re.search(rf'<div class="step-container[^"]*" id="step{n}">', doc)
    assert m, f'step-container {n} não encontrado'
    start = m.start()
    nav_idx = doc.index('<div class="nav-buttons">', start)
    marker = f'just-step{n}'
    assert marker not in doc[start:nav_idx], f'justificativa já presente em step{n}'
    doc = doc[:nav_idx] + JUST_TEMPLATE.format(n=n) + doc[nav_idx:]
print('4/9 14 caixas de justificativa inseridas.')

# ═══════════════════════════════════════════════════════════════════════════
# 5) Seção "Justificativas do Operador" — após pub-results-card, antes do
#    nav-buttons de #results
# ═══════════════════════════════════════════════════════════════════════════
RESULTS_JUST = '''
        <div class="results-just" id="results-just" style="display:none;">
            <h3>Justificativas do Operador</h3>
            <div id="results-just-body"></div>
        </div>
'''
ANCHOR = '<div id="pub-results-body"></div>\n        </div>\n\n        <div class="nav-buttons" style="border: none'
rep(ANCHOR, ANCHOR.replace('\n\n        <div class="nav-buttons" style="border: none',
                            RESULTS_JUST + '\n        <div class="nav-buttons" style="border: none'),
    label='results-just insertion')
print('5/9 seção "Justificativas do Operador" inserida.')

# ═══════════════════════════════════════════════════════════════════════════
# 6) escHtml utility (perto de fmt/pct/num)
# ═══════════════════════════════════════════════════════════════════════════
rep(
    "    const num = (id) => parseFloat(document.getElementById(id).value) || 0;",
    "    const num = (id) => parseFloat(document.getElementById(id).value) || 0;\n"
    "    function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')\n"
    "        .replace(/>/g,'&gt;').replace(/\"/g,'&quot;'); }\n"
    "    const STEP_LABELS = ['Base de Cálculo','Vantagens Auferida e Pretendida',\n"
    "        'Agravante — Concurso de Atos (22, I)','Agravante — Ciência Hierárquica (22, II)',\n"
    "        'Agravante — Interrupção (22, III)','Agravante — Situação Econômica (22, IV)',\n"
    "        'Agravante — Reincidência (22, V)','Agravante — Contratos (22, VI)',\n"
    "        'Atenuante — Não Consumação (23, I)','Atenuante — Ressarcimento (23, II)',\n"
    "        'Atenuante — Colaboração (23, III)','Atenuante — Admissão (23, IV)',\n"
    "        'Atenuante — Programa de Integridade (23, V)','Publicação Extraordinária'];",
    label='escHtml + STEP_LABELS')
print('6/9 escHtml + STEP_LABELS inseridos.')

# ═══════════════════════════════════════════════════════════════════════════
# 7) HELP_CONTENT + openHelp/closeHelp + tecla Esc — inserido junto às
#    funções de PI (antes de "function onPiExisteChange")
# ═══════════════════════════════════════════════════════════════════════════

def warn(p):
    """Converte um <p>⚠ ...</p> do Anexo A em bloco .help-warn."""
    inner = p[3:-4]
    if inner.startswith('⚠'):
        inner = inner[1:].strip()
        return f'<div class="help-warn"><p>⚠ {inner}</p></div>'
    return p

HELP_ENTRIES = []

def mk(title, ref, paragraphs):
    body = '\n'.join(warn(p) for p in paragraphs)
    return title, ref, body

HELP_ENTRIES.append(mk(
    'Base de Cálculo: Faturamento Bruto',
    'Manual da Calculadora PAR, Parte II, item 4 (e itens 13.2–13.4 para exceções)',
    [
        '<p>A base de cálculo da multa é o <b>faturamento bruto do último exercício anterior ao da instauração do PAR</b> (art. 20 do Decreto nº 11.129/2022) — não o do ano do ato lesivo, nem o do julgamento. Errar o exercício contamina todo o cálculo.</p>',
        '<p>Da receita bruta deduzem-se <b>apenas os tributos</b> incidentes sobre o faturamento.</p>',
        '<p>⚠ Na DRE contábil, a receita bruta é deduzida também de abatimentos, devoluções e vendas canceladas. Para fins de PAR, contudo, APENAS os tributos têm previsão legal de exclusão. Atenção redobrada ao importar números diretamente da DRE.</p>',
        '<p>Se o faturamento não for apurável: use a <b>estimativa fundamentada</b> (documentando cada premissa — capital social, CNAE, carga tributária, atualização) ou, em último grau, o regime do <b>piso absoluto de R$ 6.000,00</b>. A atualização pelo IPCA (art. 21) deve ser feita previamente (Calculadora do Cidadão/BCB), informando aqui o valor já corrigido.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Vantagens Auferida e Pretendida (Art. 26)',
    'Manual da Calculadora PAR, Parte II, item 5',
    [
        '<p><b>Vantagem auferida</b> é o ganho real e efetivamente obtido: constitui o <b>piso inafastável</b> da multa. <b>Vantagem pretendida</b> é o ganho planejado: compõe o <b>teto</b> (a multa não pode superar três vezes o maior valor entre elas, respeitado o limite legal).</p>',
        '<p>⚠ Não confunda as duas funções: inflar o piso mínimo com a vantagem pretendida é erro metodológico recorrente — e tese defensiva de alta taxa de êxito.</p>',
        '<p>A quantificação segue os métodos do art. 26 do Decreto nº 11.129/2022. Elegido o método, <b>justifique-o expressamente</b>; a dedução de custos lícitos exige comprovação pela pessoa jurídica, e cada custo pleiteado pela defesa deve ser deferido ou recusado individualmente, com motivação. Erro aqui contamina piso e teto simultaneamente.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Agravante — Concurso de Atos Lesivos (Art. 22, I)',
    'Manual da Calculadora PAR, Parte II, item 6.1',
    [
        '<p>O percentual resulta do cruzamento entre a <b>quantidade de condutas ilícitas</b> (linhas) e o <b>número de espécies distintas</b> de atos lesivos do art. 5º da LAC (colunas). Selecione a célula que retrata o caso concreto.</p>',
        '<p>O pressuposto é uma <b>nota de indiciação bem individualizada</b>: cada conduta datada, enquadrada e ancorada em prova própria. Imputações "em bloco" impedem a contagem correta do concurso.</p>',
        '<p>⚠ A fronteira entre pluralidade de condutas autônomas e desdobramentos de uma mesma conduta é juridicamente controvertida (continuidade vs. atos autônomos — v. Parte I, item 4.3.1). Na dúvida, motive por que cada conduta foi contada como autônoma.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Agravante — Ciência ou Tolerância Hierárquica (Art. 22, II)',
    'Manual da Calculadora PAR, Parte II, item 6.2',
    [
        '<p>Exige prova de que a <b>administração superior</b> da pessoa jurídica sabia (ciência) ou deliberadamente ignorou (tolerância) a prática do ato lesivo.</p>',
        '<p>⚠ A mera posição do agente no organograma <b>não</b> demonstra ciência de quem lhe é superior. O enquadramento exige lastro probatório robusto, ainda que indiciário: e-mails, atas, fluxos de aprovação, testemunhos. Agravar pelo inciso II com base exclusivamente no cargo é oferecer à defesa sua melhor tese dosimétrica.</p>',
        '<p>Registre na justificativa desta etapa <b>qual prova dos autos</b> (fls.) sustenta a marcação.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Agravante — Interrupção/Descumprimento (Art. 22, III)',
    'Manual da Calculadora PAR, Parte II, item 6.3',
    [
        '<p>Três hipóteses distintas — verifique a sub-aba correta: interrupção de <b>serviço público</b>, paralisação de <b>obra contratada</b> e situação de <b>descumprimento regulatório</b> conexa.</p>',
        '<p>O requisito central é o <b>nexo causal</b>: o ato lesivo deve ter sido determinante para a interrupção ou paralisação. Coincidência temporal com paralisação decorrente de causa autônoma (crise setorial, rescisão por conveniência) <b>não</b> configura a agravante. Comprovado o nexo, é irrelevante demonstrar dano adicional.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Agravante — Situação Econômica do Infrator (Art. 22, IV)',
    'Manual da Calculadora PAR, Parte II, item 6.4',
    [
        '<p>Percentual <b>fixo de 1%</b>, aplicável quando presentes, <b>cumulativamente</b>: índice de Solvência Geral superior a 1, índice de Liquidez Geral superior a 1 e lucro líquido no último exercício.</p>',
        '<p>O contencioso desta agravante é contábil: os índices devem referir-se ao <b>exercício correto</b> e resultar de <b>demonstrações idôneas</b>. Empresa em crise ou recuperação judicial tenderá a não preencher os requisitos — é por estes critérios objetivos, e não por juízo equitativo, que a condição econômica ingressa no cálculo.</p>',
        '<p>Registre na justificativa a fonte das demonstrações utilizadas (fls. dos autos).</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Agravante — Reincidência (Art. 22, V)',
    'Manual da Calculadora PAR, Parte II, item 6.5',
    [
        '<p>Pressupõe <b>condenação anterior definitiva</b> por infração à LAC dentro do interstício de 5 anos. Verifique: (a) a definitividade da decisão anterior; (b) a contagem do prazo — a partir da publicação do julgamento anterior ou, no caso de empresa que celebrou leniência, da declaração de cumprimento do acordo (v. Parte I, item 9.6.1).</p>',
        '<p>⚠ Consulte o CNEP antes de marcar. A defesa atacará a datação e a definitividade — documente ambas na justificativa.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Agravante — Valor dos Contratos com o Ente Lesado (Art. 22, VI)',
    'Manual da Calculadora PAR, Parte II, item 6.6',
    [
        '<p>O percentual escala conforme o <b>somatório dos valores dos contratos mantidos com o órgão ou entidade lesada</b>, no período de referência normativo.</p>',
        '<p>⚠ Erros típicos que a defesa vasculhará: inclusão de contratos celebrados com <b>outro</b> órgão ou entidade que não o lesado, e inclusão de instrumentos fora do período de vigência considerado. Faça a conferência aritmética antes — e registre na justificativa a relação de contratos computados.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Atenuante — Não Consumação (Art. 23, I)',
    'Manual da Calculadora PAR, Parte II, item 7.1',
    [
        '<p>Aplicável quando a infração <b>não se consumou</b> — a tentativa cujo resultado lesivo não se materializou. A fração da atenuante acompanha o grau de não consumação demonstrado nos autos.</p>',
        '<p>Atenção à coerência sistêmica: a não consumação dialoga com a Etapa 1 — se houve apenas vantagem <b>pretendida</b> (sem vantagem auferida), isso reforça a plausibilidade desta atenuante; vantagem efetivamente auferida tende a afastá-la.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Atenuante — Ressarcimento e Devolução Espontânea (Art. 23, II)',
    'Manual da Calculadora PAR, Parte II, item 7.2',
    [
        '<p>Premia a reparação espontânea do dano.</p>',
        '<p>⚠ O percentual máximo de 1,0% exige <b>confirmação expressa de devolução integral</b>. Devolução parcial reduz o percentual para 0,5%. Exija comprovação documental (guias, comprovantes) e registre-a na justificativa.</p>',
        '<p>Espontaneidade importa: devolução forçada por bloqueio judicial não equivale à conduta reparatória voluntária que o dispositivo premia.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Atenuante — Colaboração (Art. 23, III)',
    'Manual da Calculadora PAR, Parte II, item 7.3',
    [
        '<p>Três condições acumuláveis; presentes as três, o percentual é <b>fixo de 1,5%</b>; uma ou duas, faixa discricionária de 0,5% a 1,0% — motive a escolha dentro da faixa.</p>',
        '<p>⚠ A mera entrega de documentos exigidos por lei ou por intimação <b>NÃO</b> configura colaboração: contam a <b>utilidade</b> e o <b>ineditismo</b> das informações e provas trazidas, sob o pressuposto da boa-fé processual.</p>',
        '<p>Não confunda com o inciso IV: admitir a ocorrência do fato sem assumir responsabilidade enquadra-se aqui (III); o inciso IV exige reconhecimento formal da responsabilidade.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Atenuante — Admissão Voluntária da Responsabilidade (Art. 23, IV)',
    'Manual da Calculadora PAR, Parte II, item 7.4',
    [
        '<p>Exige <b>reconhecimento formal da responsabilidade</b> pela pessoa jurídica — declaração inequívoca, não mera confissão de fatos nem colaboração instrutória (que é o terreno do inciso III).</p>',
        '<p>Verifique o instrumento nos autos (petição, termo) e o momento processual. A defesa frequentemente pleiteia o duplo enquadramento (III + IV) a partir do mesmo ato: examine se os pressupostos <b>distintos</b> de cada inciso estão autonomamente preenchidos, e motive.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Atenuante — Programa de Integridade (Art. 23, V)',
    'Manual da Calculadora PAR, Parte II, item 7.5',
    [
        '<p>A avaliação segue os <b>três blocos</b> (COI — cultura organizacional; MPI — mecanismos, políticas e procedimentos; APJ — atuação em relação ao ato lesivo), combinados pela fórmula normativa, com o <b>fator multiplicador de 1,25</b> nas condições regulamentares. Programa <b>anterior</b> ao ato lesivo é avaliado de modo distinto do programa <b>posterior</b>.</p>',
        '<p>⚠ Momento de comprovação: a apresentação dos relatórios de perfil e de conformidade sujeita-se ao prazo da defesa — a intimação deve tê-lo consignado expressamente, com advertência da consequência da inércia. Documente a intimação na justificativa: é ela que sustenta eventual preclusão.</p>',
    ]))

HELP_ENTRIES.append(mk(
    'Publicação Extraordinária — Dosimetria do Prazo (Art. 6º, II)',
    'Manual da Calculadora PAR, Parte II, item 9',
    [
        '<p>Sanção <b>autônoma</b>, de caráter pedagógico e dissuasório — não se confunde com a publicação ordinária da decisão no DOU. O prazo (30 a 135 dias) é função da <b>Alíquota de Referência</b>, extraída do resultado da dosimetria pecuniária; o sistema identifica automaticamente o cenário aplicável (A ou B) e o cálculo consta do relatório.</p>',
        '<p>⚠ A dosimetria da publicação é consequência direta do valor final da multa: qualquer alteração nas etapas anteriores modifica o prazo. Revise esta etapa <b>sempre</b> após mexer em qualquer parâmetro.</p>',
        '<p>Lembre-se: a imposição cumulativa e o dimensionamento desta sanção exigem motivação específica (art. 6º, §1º, da LAC) — a justificativa desta etapa é o lugar dela.</p>',
    ]))

assert len(HELP_ENTRIES) == 14

def js_str(s):
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

entries_js = ',\n        '.join(
    "{ title: `%s`, ref: `%s`, html: `%s` }" % (js_str(t), js_str(r), js_str(b))
    for t, r, b in HELP_ENTRIES
)

HELP_JS = f'''
    // ─── Fase C: Manual Vivo (F1) ───
    const HELP_CONTENT = [
        {entries_js}
    ];
    function openHelp(n) {{
        const c = HELP_CONTENT[n];
        if (!c) return;
        document.getElementById('help-title').textContent = c.title;
        document.getElementById('help-ref').textContent = 'Aprofunde: ' + c.ref;
        document.getElementById('help-body').innerHTML = c.html;
        document.getElementById('help-modal').classList.add('active');
        document.body.style.overflow = 'hidden';
    }}
    function closeHelp() {{
        document.getElementById('help-modal').classList.remove('active');
        document.body.style.overflow = '';
    }}
    document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeHelp(); }});

'''

rep('    function onPiExisteChange() {', HELP_JS + '    function onPiExisteChange() {', label='HELP_CONTENT + openHelp/closeHelp')
print('7/9 HELP_CONTENT (14 entradas) + openHelp/closeHelp inseridos.')

# ═══════════════════════════════════════════════════════════════════════════
# 8) autosave / applyAutosaveData — justificativas
# ═══════════════════════════════════════════════════════════════════════════
rep(
    "            const data = { ts: Date.now(), step, metodo: activeMethod, radios, checkboxes, texts };",
    "            const justificativas = {};\n"
    "            for (let n = 0; n < TOTAL_STEPS; n++) {\n"
    "                const jel = document.getElementById('just-step' + n);\n"
    "                if (jel && jel.value.trim()) justificativas[n] = jel.value;\n"
    "            }\n\n"
    "            const data = { ts: Date.now(), step, metodo: activeMethod, radios, checkboxes, texts, justificativas };",
    label='autosave justificativas')

rep(
    "    function applyAutosaveData(data) {\n        try {",
    "    function applyAutosaveData(data) {\n        try {\n"
    "            // 0. Justificativas (aditivo/retrocompatível — ausência não gera erro)\n"
    "            if (data.justificativas) {\n"
    "                for (let n = 0; n < TOTAL_STEPS; n++) {\n"
    "                    const jel = document.getElementById('just-step' + n);\n"
    "                    if (jel && data.justificativas[n] !== undefined) jel.value = data.justificativas[n];\n"
    "                }\n"
    "            }\n",
    label='applyAutosaveData justificativas')
print('8/9 autosave/applyAutosaveData estendidos com justificativas.')

# ═══════════════════════════════════════════════════════════════════════════
# 9) renderJustificativas() + chamada em finish()
# ═══════════════════════════════════════════════════════════════════════════
RENDER_JUST = '''
    function renderJustificativas() {
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
rep(
    "    function finish() {\n        document.getElementById('step13').classList.remove('active');\n        document.getElementById('results').style.display = 'block';\n        calculate();\n        window.scrollTo(0, 0);\n    }",
    "    function finish() {\n        document.getElementById('step13').classList.remove('active');\n        document.getElementById('results').style.display = 'block';\n        calculate();\n        renderJustificativas();\n        window.scrollTo(0, 0);\n    }" + RENDER_JUST,
    label='finish() + renderJustificativas')
print('9/9 renderJustificativas() inserida e chamada em finish().')

with open(f'{SCRATCH}/decoded.html', 'w', encoding='utf-8') as f:
    f.write(doc)
print('\nOK — Fase C (exceto item 4.4 / minuta) aplicada e salva em decoded.html')
