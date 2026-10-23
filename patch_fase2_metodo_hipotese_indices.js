
    // ═══════════════════════════════════════════════════════════════════════
    // FASE 2 — F5: Confirmação ao trocar método de vantagem
    //         F6: Fundamentação específica do art. 22, III
    //         F7: Validação visual dos índices do art. 22, IV
    // ═══════════════════════════════════════════════════════════════════════

    // ── Estrutura de avisos pré-impressão (consumida pela F4 na Fase 3) ──
    let _avisosPreImpressao = [];
    function registrarAvisosPreImpressao() {
        _avisosPreImpressao = [];
        const gServVal = parseFloat(document.querySelector('input[name="g-serv"]:checked').value) || 0;
        const gObraVal = parseFloat(document.getElementById('g-obra').value) || 0;
        const gRegVal = parseFloat(document.querySelector('input[name="g-reg"]:checked').value) || 0;
        const gIIIVal = Math.max(gServVal, gObraVal, gRegVal);
        if (gIIIVal > 0 && !(document.getElementById('fund-22-iii').value || '').trim()) {
            _avisosPreImpressao.push('Agravante do art. 22, III ativada sem fundamentação específica da hipótese incidente (Etapa 4).');
        }
        const gEconVal = parseFloat(document.querySelector('input[name="g-econ"]:checked').value) || 0;
        if (gEconVal > 0 && _econIndiceAbaixoDe1) {
            _avisosPreImpressao.push('Agravante do art. 22, IV ativada com índice (ISG ou ILG) inferior a 1 — confirme a motivação.');
        }
        return _avisosPreImpressao;
    }

    // ── F6: fundamentação específica por hipótese do art. 22, III ──
    const FUND_22_III_PLACEHOLDERS = [
        'Indique a prova dos autos que demonstra a duração da interrupção e/ou a população do município afetado (ex.: laudo técnico, notícia veiculada, estimativa IBGE vigente na data do ato lesivo).',
        'Indique a prova dos autos que demonstra o período de paralisação e o percentual da obra não executado (ex.: relatório de fiscalização, medições, laudo de engenharia).',
        'Indique a prova dos autos que demonstra o descumprimento regulatório e se houve ou não prestação do serviço (ex.: auto de infração do órgão regulador, relatório de fiscalização).',
    ];
    function validarFund22III() {
        const gServVal = parseFloat(document.querySelector('input[name="g-serv"]:checked').value) || 0;
        const gObraVal = parseFloat(document.getElementById('g-obra').value) || 0;
        const gRegVal = parseFloat(document.querySelector('input[name="g-reg"]:checked').value) || 0;
        const gIIIVal = Math.max(gServVal, gObraVal, gRegVal);
        const vazio = !(document.getElementById('fund-22-iii').value || '').trim();
        const box = document.getElementById('fund-22-iii-box');
        const aviso = document.getElementById('fund-22-iii-aviso');
        const destacar = gIIIVal > 0 && vazio;
        if (box) box.style.borderLeft = destacar ? '3px solid #d97706' : '';
        if (aviso) aviso.style.display = destacar ? 'block' : 'none';
    }

    const _switchTabOriginal = switchTab;
    switchTab = function(idx) {
        _switchTabOriginal(idx);
        const campo = document.getElementById('fund-22-iii');
        if (campo && FUND_22_III_PLACEHOLDERS[idx]) campo.placeholder = FUND_22_III_PLACEHOLDERS[idx];
        validarFund22III();
    };

    // ── F7: validação visual ISG/ILG ──
    let _econIndiceAbaixoDe1 = false;
    function normalizarDecimalEvent(el) {
        if (el.value.indexOf(',') !== -1) el.value = el.value.replace(',', '.');
    }
    function atualizarBadgesEcon() {
        const ac = parseFloat(document.getElementById('ec-ac').value) || 0;
        const anc = parseFloat(document.getElementById('ec-anc').value) || 0;
        const arlp = parseFloat(document.getElementById('ec-arlp').value) || 0;
        const pc = parseFloat(document.getElementById('ec-pc').value) || 0;
        const pnc = parseFloat(document.getElementById('ec-pnc').value) || 0;
        const passivoTotal = pc + pnc;
        const semDados = passivoTotal === 0 && (ac + anc + arlp) === 0;

        const sgBadge = document.getElementById('ec-sg-badge');
        const lgBadge = document.getElementById('ec-lg-badge');
        if (semDados) {
            sgBadge.style.display = 'none'; lgBadge.style.display = 'none';
            _econIndiceAbaixoDe1 = false;
            return;
        }
        const sg = passivoTotal > 0 ? (ac + anc) / passivoTotal : 0;
        const lg = passivoTotal > 0 ? (ac + arlp) / passivoTotal : 0;

        function aplicarBadge(el, indice) {
            if (indice < 1) {
                el.className = 'econ-badge amber';
                el.textContent = 'Índice inferior a 1 — indica situação econômica desfavorável; verifique a inaplicabilidade da agravante (art. 22, IV).';
            } else {
                el.className = 'econ-badge green';
                el.textContent = 'Índice compatível com a análise da agravante.';
            }
            el.style.display = 'block';
        }
        aplicarBadge(sgBadge, sg);
        aplicarBadge(lgBadge, lg);
        _econIndiceAbaixoDe1 = (sg < 1) || (lg < 1);
    }

    // ── F5: confirmação ao trocar método de apuração da vantagem ──
    const METODO_LABELS_F5 = {
        'direto': 'Valor informado diretamente',
        'i': 'Inciso I — Receita do contrato − custos lícitos',
        'ii': 'Inciso II — Despesas/custos evitados',
        'iii': 'Inciso III — Lucro adicional',
    };
    function metodoTemDadosPreenchidos(m) {
        if (m === 'direto') return !!(document.getElementById('van-direto').value || '').trim();
        if (m === 'i') return Array.from(document.querySelectorAll('#anos-i-body tr')).some(tr =>
            ['rec', 'cmv', 'desp', 'ir'].some(f => (tr.querySelector('[data-field="' + f + '"]').value || '').trim()));
        if (m === 'ii') return Array.from(document.querySelectorAll('#ii-itens .pagamento-row input')).some(inp => (inp.value || '').trim());
        if (m === 'iii') return ['iii-direto', 'iii-valor', 'iii-periodo', 'iii-taxa-ilicita', 'iii-taxa-mercado']
            .some(id => document.getElementById(id) && (document.getElementById(id).value || '').trim());
        return false;
    }
    const _selectMethodOriginal = selectMethod;
    selectMethod = function(novoMetodo) {
        if (activeMethod && activeMethod !== novoMetodo && metodoTemDadosPreenchidos(activeMethod)) {
            const atualLabel = METODO_LABELS_F5[activeMethod] || activeMethod;
            const prosseguir = confirm(
                'Trocar o método de apuração para o novo método fará com que o cálculo passe a usar os valores dele. ' +
                'Os dados do método atual (' + atualLabel + ') permanecem preenchidos nesta sessão, mas deixam de ' +
                'alimentar o cálculo enquanto não for selecionado novamente. Deseja continuar?'
            );
            if (!prosseguir) return;
        }
        _selectMethodOriginal(novoMetodo);
    };

