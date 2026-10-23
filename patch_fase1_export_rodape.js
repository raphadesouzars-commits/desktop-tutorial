
    // ═══════════════════════════════════════════════════════════════════════
    // FASE 1 — F1: Exportação/Importação do estado em JSON
    // FASE 1 — F3: Rodapé de integridade do relatório
    // ═══════════════════════════════════════════════════════════════════════

    const VERSAO_CALCULADORA = "2.0.0"; // atualizar a cada modificação da ferramenta
    const METODOLOGIA_NORMATIVA = "Lei nº 12.846/2013; Decreto nº 11.129/2022; Portaria Conjunta CGU nº 6/2022; IN CGU nº 13/2019";

    // ── Serialização determinística (chaves ordenadas recursivamente) ──
    function ordenarChaves(obj) {
        if (Array.isArray(obj)) return obj.map(ordenarChaves);
        if (obj && typeof obj === 'object') {
            const out = {};
            Object.keys(obj).sort().forEach(k => { out[k] = ordenarChaves(obj[k]); });
            return out;
        }
        return obj;
    }

    async function sha256Hex(texto) {
        const enc = new TextEncoder().encode(texto);
        const buf = await crypto.subtle.digest('SHA-256', enc);
        return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
    }

    function sanitizarNomeArquivo(s) {
        return (s || 'rascunho').replace(/[\/\\.: ]+/g, '-');
    }

    // ── Coleta genérica de todo o estado dos formulários ──
    function coletarEstadoCompleto() {
        const dados = { radios: {}, checkboxes: {}, textos: {}, meta: {} };

        document.querySelectorAll('input[type="radio"]:checked').forEach(r => {
            if (!r.name) return;
            if (r.name.indexOf('prelim-') === 0) return; // tratado via piState
            if (PI_ITEMS.some(it => it.id === r.name)) return; // tratado via piState
            dados.radios[r.name] = r.value;
        });

        document.querySelectorAll('input[type="checkbox"][id]').forEach(cb => {
            dados.checkboxes[cb.id] = cb.checked;
        });

        document.querySelectorAll('input[type="text"][id], input[type="number"][id], input[type="hidden"][id], input[type="date"][id], textarea[id]').forEach(el => {
            if (el.id.indexOf('page-') === 0 || el.id.indexOf('prelim-page-') === 0) return; // tratados junto ao PI
            dados.textos[el.id] = el.value;
        });

        // Linhas dinâmicas — Vantagem, Método I (múltiplos exercícios)
        dados.anosI = [];
        document.querySelectorAll('#anos-i-body tr').forEach(tr => {
            dados.anosI.push({
                label: tr.querySelector('[data-field="label"]').value,
                rec: tr.querySelector('[data-field="rec"]').value,
                cmv: tr.querySelector('[data-field="cmv"]').value,
                desp: tr.querySelector('[data-field="desp"]').value,
                ir: tr.querySelector('[data-field="ir"]').value,
            });
        });

        // Linhas dinâmicas — Vantagem, Método II (itens de custo evitado)
        dados.itensII = [];
        document.querySelectorAll('#ii-itens .pagamento-row').forEach(div => {
            const inputs = div.querySelectorAll('input');
            dados.itensII.push({ label: inputs[0] ? inputs[0].value : '', val: inputs[1] ? inputs[1].value : '' });
        });

        // Linhas dinâmicas — Propina (SELIC/câmbio)
        dados.propina = [];
        document.querySelectorAll('#propina-lista .pagamento-row').forEach(div => {
            const row = {};
            div.querySelectorAll('[data-f]').forEach(el => { row[el.dataset.f] = el.value; });
            dados.propina.push(row);
        });

        // Programa de Integridade — fonte de verdade central (piState) + páginas de referência
        dados.piState = JSON.parse(JSON.stringify(piState));
        dados.piPaginas = {};
        document.querySelectorAll('input[id^="page-"], input[id^="prelim-page-"]').forEach(el => {
            dados.piPaginas[el.id] = el.value;
        });

        dados.meta = {
            step: step,
            activeMethod: activeMethod,
            metodoLabel: metodoLabel,
        };

        // Reservado para a Fase 3 (F4 — checklist de blindagem); mantido vazio por ora
        dados.checklistBlindagem = (typeof coletarChecklistBlindagem === 'function') ? coletarChecklistBlindagem() : {};

        return dados;
    }

    async function exportarEstado() {
        const dados = coletarEstadoCompleto();
        const dadosOrdenados = ordenarChaves(dados);
        const jsonOrdenado = JSON.stringify(dadosOrdenados);
        const hash = await sha256Hex(jsonOrdenado);

        const pacote = {
            _meta: {
                aplicacao: 'Calculadora PAR - COGER/RFB',
                versaoCalculadora: VERSAO_CALCULADORA,
                versaoSchema: 1,
                geradoEm: new Date().toISOString(),
                hashConteudo: hash,
            },
            dados: dados,
        };

        const numeroProcesso = document.getElementById('id-processo') ? document.getElementById('id-processo').value : '';
        const agora = new Date();
        const carimbo = agora.getFullYear() + '-' + String(agora.getMonth() + 1).padStart(2, '0') + '-' + String(agora.getDate()).padStart(2, '0')
            + '_' + String(agora.getHours()).padStart(2, '0') + String(agora.getMinutes()).padStart(2, '0');
        const nomeArquivo = 'PAR_' + sanitizarNomeArquivo(numeroProcesso) + '_' + carimbo + '.json';

        const blob = new Blob([JSON.stringify(pacote, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = nomeArquivo;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        URL.revokeObjectURL(url);
        return nomeArquivo;
    }

    function algumCampoPreenchido() {
        const d = coletarEstadoCompleto();
        if (Object.values(d.textos).some(v => v && String(v).trim())) return true;
        if (Object.values(d.checkboxes).some(v => v)) return true;
        if (d.anosI.length || d.itensII.length || d.propina.length) return true;
        if (d.piState.evaluated) return true;
        return false;
    }

    function restaurarLinhasDinamicas(dados) {
        document.getElementById('anos-i-body').innerHTML = '';
        (dados.anosI || []).forEach(a => addAnoI(a.label, a.rec, a.cmv, a.desp, a.ir));

        document.getElementById('ii-itens').innerHTML = '';
        (dados.itensII || []).forEach(it => addItemII(it.label, it.val));

        const listaPropina = document.getElementById('propina-lista');
        if (listaPropina) {
            listaPropina.innerHTML = '';
            (dados.propina || []).forEach(() => addPropina());
            const linhas = document.querySelectorAll('#propina-lista .pagamento-row');
            (dados.propina || []).forEach((row, i) => {
                const linha = linhas[i];
                if (!linha) return;
                Object.keys(row).forEach(campo => {
                    const el = linha.querySelector('[data-f="' + campo + '"]');
                    if (el) el.value = row[campo];
                });
            });
            if (typeof recalcPropina === 'function') recalcPropina();
        }
    }

    function restaurarProgramaIntegridade(dados) {
        if (!document.getElementById('pi-prelim-list').children.length) {
            renderPiPrelim();
            renderPiBlocks();
        }
        Object.assign(piState, dados.piState || {});
        Object.keys(piState.prelim || {}).forEach(pid => {
            const val = piState.prelim[pid];
            const r = document.querySelector('input[name="prelim-' + pid + '"][value="' + val + '"]');
            if (r) r.checked = true;
        });
        Object.keys(piState.answers || {}).forEach(iid => {
            const val = piState.answers[iid];
            const r = document.querySelector('input[name="' + iid + '"][value="' + val + '"]');
            if (r) r.checked = true;
        });
        Object.keys(dados.piPaginas || {}).forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = dados.piPaginas[id];
        });
        if (typeof updatePiVisibility === 'function') updatePiVisibility();
        piRecalc();
        document.getElementById('t-pi-value').value = piState.capped;
    }

    function aplicarEstadoCompleto(dados) {
        Object.keys(dados.radios || {}).forEach(name => {
            const r = document.querySelector('input[name="' + name + '"][value="' + dados.radios[name] + '"]');
            if (r) r.checked = true;
        });
        Object.keys(dados.textos || {}).forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = dados.textos[id];
        });
        Object.keys(dados.checkboxes || {}).forEach(id => {
            const el = document.getElementById(id);
            if (el) el.checked = dados.checkboxes[id];
        });

        restaurarLinhasDinamicas(dados);

        if (dados.meta && dados.meta.activeMethod) {
            selectMethod(dados.meta.activeMethod);
        }
        if (typeof switchFatCenario === 'function') switchFatCenario();
        if (typeof onFatTemFaturChange === 'function') onFatTemFaturChange();
        if (typeof toggleDevIntegral === 'function') toggleDevIntegral();
        if (typeof recalcColab === 'function') recalcColab();

        restaurarProgramaIntegridade(dados);

        if (dados.meta && typeof dados.meta.step === 'number') {
            document.getElementById('step' + step).classList.remove('active');
            step = dados.meta.step;
            document.getElementById('step' + step).classList.add('active');
            updateProgress();
        }

        calculate();
    }

    function importarEstado(file) {
        const reader = new FileReader();
        reader.onload = async () => {
            let pacote;
            try {
                pacote = JSON.parse(reader.result);
            } catch (e) {
                alert('Arquivo inválido: não foi possível interpretar o JSON. Nenhum dado foi alterado.');
                return;
            }
            try {
                if (!pacote._meta || pacote._meta.aplicacao !== 'Calculadora PAR - COGER/RFB') {
                    alert('Arquivo não reconhecido como exportação desta calculadora. Importação cancelada.');
                    return;
                }
                if (!pacote._meta.versaoSchema || pacote._meta.versaoSchema > 1) {
                    alert('Este arquivo foi gerado por uma versão mais recente da calculadora (schema desconhecido). Importação cancelada para evitar perda de dados.');
                    return;
                }

                const jsonOrdenado = JSON.stringify(ordenarChaves(pacote.dados));
                const hashRecalculado = await sha256Hex(jsonOrdenado);
                if (pacote._meta.hashConteudo && hashRecalculado !== pacote._meta.hashConteudo) {
                    const prosseguir = confirm('Atenção: o arquivo foi modificado após a exportação (hash não confere). Deseja importar mesmo assim?');
                    if (!prosseguir) return;
                }

                if (algumCampoPreenchido()) {
                    const prosseguir = confirm('A importação substituirá todos os dados atuais. Continuar?');
                    if (!prosseguir) return;
                }

                aplicarEstadoCompleto(pacote.dados);
                alert('Estado importado com sucesso.');
            } catch (e) {
                alert('Erro ao importar o arquivo: ' + e.message + '. Nenhum dado foi alterado além do que já tiver sido aplicado.');
            }
        };
        reader.onerror = () => alert('Não foi possível ler o arquivo selecionado.');
        reader.readAsText(file);
    }

    // ── F3: Rodapé de integridade ──
    let _ultimoArquivoImportado = null; // { nome, hash } — setado por importarEstado quando aplicável

    function montarRodapeIntegridade(formato) {
        const agora = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo', dateStyle: 'short', timeStyle: 'short' });
        let linha1 = `Relatório gerado em ${agora} (horário de Brasília) pela Calculadora PAR — COGER/RFB, versão ${VERSAO_CALCULADORA}, aplicando a metodologia de dosimetria da ${METODOLOGIA_NORMATIVA}. Este demonstrativo é memória de cálculo auxiliar e não substitui a motivação da comissão nos autos.`;
        let linha2 = '';
        if (_ultimoArquivoImportado && _ultimoArquivoImportado.nome) {
            linha2 = `Estado do cálculo: arquivo ${_ultimoArquivoImportado.nome}, hash SHA-256 ${_ultimoArquivoImportado.hash.substring(0, 16)}…`;
        }
        if (formato === 'html') {
            let html = `<hr style="margin-top:24px; border:none; border-top:1px solid #ccc;">`;
            html += `<p style="font-size:9pt; color:#555; text-align:left;">${linha1}</p>`;
            if (linha2) html += `<p style="font-size:9pt; color:#555; text-align:left;">${linha2}</p>`;
            return html;
        }
        return '\n\n' + '—'.repeat(20) + '\n' + linha1 + (linha2 ? '\n' + linha2 : '');
    }

