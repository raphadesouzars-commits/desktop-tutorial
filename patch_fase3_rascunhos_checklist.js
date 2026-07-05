
    // ═══════════════════════════════════════════════════════════════════════
    // FASE 3 — F2: Rascunhos nomeados (localStorage)
    //         F4: Checklist de blindagem pré-impressão
    // ═══════════════════════════════════════════════════════════════════════

    // ── F4: itens do checklist (Manual, item 11.7 — fácil edição/ajuste de redação) ──
    const CHECKLIST_BLINDAGEM = [
        'Cada valor numérico do cálculo tem fonte documental identificada nos autos (memorial de cálculo com remissão a folhas/documentos).',
        'Faturamento bruto e tributos dedutíveis extraídos de documento formal juntado aos autos (DRE/ECF/BP), com data e origem identificadas.',
        'Custos e tributos deduzidos da vantagem auferida foram enfrentados individualmente, com aceitação ou rejeição motivada de cada rubrica.',
        'Pessoa jurídica foi expressamente intimada para apresentar os relatórios do Programa de Integridade (perfil e conformidade), e a intimação está documentada.',
        'Cada agravante aplicada (art. 22) tem prova específica citada na fundamentação da respectiva etapa.',
        'Cada atenuante negada tem motivação expressa de não incidência (art. 50, Lei nº 9.784/1999) — conferir que nenhum campo de justificativa ficou vazio.',
        'Verificação prescricional preliminar realizada e documentada (marco de ciência identificado; conferência empresa por empresa, se PAR plural).',
        'Classificação da infração (instantânea/permanente/continuada) é a mesma na preliminar prescricional e na contagem do concurso do art. 22, I.',
        'Provas sob sigilo compartilhadas têm decisão judicial autorizadora juntada aos autos.',
        'Valores provenientes de RIF/COAF foram corroborados por prova documental sob contraditório.',
    ];

    function montarChecklistHtml() {
        const body = document.getElementById('checklist-body');
        if (!body) return;
        body.innerHTML = CHECKLIST_BLINDAGEM.map((texto, i) =>
            '<label style="display:flex; align-items:flex-start; gap:8px; font-size:9.5pt; padding:6px 0; border-bottom:1px solid #eee;">' +
            '<input type="checkbox" id="checklist-' + i + '" style="margin-top:3px;">' +
            '<span>' + escHtml(texto) + '</span></label>'
        ).join('');
    }

    function coletarChecklistBlindagem() {
        const out = {};
        CHECKLIST_BLINDAGEM.forEach((_, i) => {
            const el = document.getElementById('checklist-' + i);
            if (el) out[i] = el.checked;
        });
        return out;
    }

    function aplicarChecklistBlindagem(dados) {
        if (!dados) return;
        Object.keys(dados).forEach(i => {
            const el = document.getElementById('checklist-' + i);
            if (el) el.checked = !!dados[i];
        });
    }

    function contarChecklistNaoMarcados() {
        return CHECKLIST_BLINDAGEM.filter((_, i) => {
            const el = document.getElementById('checklist-' + i);
            return el && !el.checked;
        }).length;
    }

    function verificarAntesDeImprimir(fnImprimir) {
        const naoMarcados = contarChecklistNaoMarcados();
        if (naoMarcados > 0) {
            const prosseguir = confirm('Há ' + naoMarcados + ' itens do checklist de blindagem não confirmados. Imprimir mesmo assim?');
            if (!prosseguir) return;
        }
        fnImprimir();
    }

    // ── F2: rascunhos nomeados ──
    const RASCUNHOS_KEY = 'calcPAR.rascunhos';
    const RASCUNHOS_AVISO_KEY = 'calcPAR.rascunhos.avisoMostrado';
    let _rascunhoAtivo = null;

    function rascunhosDisponiveis() {
        try {
            const t = '__calcPAR_teste__';
            localStorage.setItem(t, '1');
            localStorage.removeItem(t);
            return true;
        } catch (e) { return false; }
    }

    function lerRascunhos() {
        try {
            const raw = localStorage.getItem(RASCUNHOS_KEY);
            return raw ? JSON.parse(raw) : {};
        } catch (e) { return {}; }
    }

    function gravarRascunhos(obj) {
        try { localStorage.setItem(RASCUNHOS_KEY, JSON.stringify(obj)); return true; }
        catch (e) { return false; }
    }

    function abrirRascunhosModal() {
        const btnRascunhos = document.querySelector('button[onclick="abrirRascunhosModal()"]');
        if (!rascunhosDisponiveis()) {
            document.getElementById('rascunhos-indisponivel').style.display = 'block';
            document.getElementById('rascunhos-lista').style.display = 'none';
            document.getElementById('rascunhos-vazio').style.display = 'none';
            document.querySelector('#rascunhos-modal button[onclick="salvarComoRascunho()"]').style.display = 'none';
        } else {
            document.getElementById('rascunhos-indisponivel').style.display = 'none';
            document.getElementById('rascunhos-lista').style.display = 'block';
            if (!localStorage.getItem(RASCUNHOS_AVISO_KEY)) {
                document.getElementById('rascunhos-aviso-primeira-vez').style.display = 'block';
                try { localStorage.setItem(RASCUNHOS_AVISO_KEY, '1'); } catch (e) {}
            }
            renderizarListaRascunhos();
        }
        document.getElementById('rascunhos-modal').classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function fecharRascunhosModal() {
        document.getElementById('rascunhos-modal').classList.remove('active');
        document.body.style.overflow = '';
    }

    function renderizarListaRascunhos() {
        const rascunhos = lerRascunhos();
        const nomes = Object.keys(rascunhos).sort((a, b) => (rascunhos[b].salvoEm || '').localeCompare(rascunhos[a].salvoEm || ''));
        const lista = document.getElementById('rascunhos-lista');
        const vazio = document.getElementById('rascunhos-vazio');
        if (!nomes.length) { lista.innerHTML = ''; vazio.style.display = 'block'; return; }
        vazio.style.display = 'none';
        lista.innerHTML = nomes.map(nome => {
            const r = rascunhos[nome];
            const quando = r.salvoEm ? new Date(r.salvoEm).toLocaleString('pt-BR') : '—';
            const processo = (r.dados && r.dados.textos && r.dados.textos['id-processo']) || '';
            const ativo = nome === _rascunhoAtivo;
            return '<div class="rascunho-item" data-nome="' + escHtml(nome) + '" style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #eee;' + (ativo ? ' background:#eaf5e1;' : '') + '">' +
                '<div><div style="font-weight:700; color:var(--p281);">' + escHtml(nome) + (ativo ? ' <span style="font-size:8pt; color:#27ae60;">● ativo</span>' : '') + '</div>' +
                '<div style="font-size:8.5pt; color:#888;">' + (processo ? escHtml(processo) + ' • ' : '') + 'salvo em ' + quando + '</div></div>' +
                '<div style="display:flex; gap:6px; flex-wrap:wrap;">' +
                '<button class="btn btn-aux btn-sm rascunho-carregar">Carregar</button>' +
                '<button class="btn btn-aux btn-sm rascunho-renomear">Renomear</button>' +
                '<button class="btn btn-danger btn-sm rascunho-excluir">Excluir</button>' +
                '</div></div>';
        }).join('');
        lista.querySelectorAll('.rascunho-carregar').forEach(btn => btn.addEventListener('click', e => carregarRascunho(e.target.closest('.rascunho-item').dataset.nome)));
        lista.querySelectorAll('.rascunho-renomear').forEach(btn => btn.addEventListener('click', e => renomearRascunho(e.target.closest('.rascunho-item').dataset.nome)));
        lista.querySelectorAll('.rascunho-excluir').forEach(btn => btn.addEventListener('click', e => excluirRascunho(e.target.closest('.rascunho-item').dataset.nome)));
    }

    function salvarComoRascunho() {
        if (!rascunhosDisponiveis()) return;
        const nome = prompt('Nome do rascunho:', _rascunhoAtivo || '');
        if (!nome) return;
        const rascunhos = lerRascunhos();
        if (rascunhos[nome] && !confirm('Já existe um rascunho com esse nome. Sobrescrever?')) return;
        rascunhos[nome] = { salvoEm: new Date().toISOString(), dados: coletarEstadoCompleto() };
        if (gravarRascunhos(rascunhos)) {
            _rascunhoAtivo = nome;
            atualizarIndicadorRascunho();
            renderizarListaRascunhos();
        }
    }

    function carregarRascunho(nome) {
        const rascunhos = lerRascunhos();
        const r = rascunhos[nome];
        if (!r) return;
        if (algumCampoPreenchido() && !confirm('Carregar este rascunho substituirá todos os dados atuais. Continuar?')) return;
        aplicarEstadoCompleto(r.dados);
        _rascunhoAtivo = nome;
        atualizarIndicadorRascunho();
        fecharRascunhosModal();
    }

    function excluirRascunho(nome) {
        if (!confirm('Excluir o rascunho "' + nome + '"? Esta ação não pode ser desfeita.')) return;
        const rascunhos = lerRascunhos();
        delete rascunhos[nome];
        gravarRascunhos(rascunhos);
        if (_rascunhoAtivo === nome) { _rascunhoAtivo = null; atualizarIndicadorRascunho(); }
        renderizarListaRascunhos();
    }

    function renomearRascunho(nome) {
        const novoNome = prompt('Novo nome para "' + nome + '":', nome);
        if (!novoNome || novoNome === nome) return;
        const rascunhos = lerRascunhos();
        if (rascunhos[novoNome] && !confirm('Já existe um rascunho com esse nome. Sobrescrever?')) return;
        rascunhos[novoNome] = rascunhos[nome];
        delete rascunhos[nome];
        gravarRascunhos(rascunhos);
        if (_rascunhoAtivo === nome) _rascunhoAtivo = novoNome;
        renderizarListaRascunhos();
    }

    function atualizarIndicadorRascunho() {
        const el = document.getElementById('rascunho-indicador');
        if (!el) return;
        el.textContent = _rascunhoAtivo
            ? ('Rascunho ativo: ' + _rascunhoAtivo)
            : 'O arquivo exportado pode ser juntado aos autos como memória do cálculo.';
    }

    function autosaveRascunhoAtivo() {
        if (!_rascunhoAtivo || !rascunhosDisponiveis()) return;
        const rascunhos = lerRascunhos();
        if (!rascunhos[_rascunhoAtivo]) return;
        rascunhos[_rascunhoAtivo] = { salvoEm: new Date().toISOString(), dados: coletarEstadoCompleto() };
        gravarRascunhos(rascunhos);
        const el = document.getElementById('rascunho-indicador');
        if (el) el.textContent = 'Rascunho "' + _rascunhoAtivo + '" salvo às ' + new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    const _nextOriginalF3 = next;
    next = function (i) { _nextOriginalF3(i); autosaveRascunhoAtivo(); };
    const _prevOriginalF3 = prev;
    prev = function (i) { _prevOriginalF3(i); autosaveRascunhoAtivo(); };

