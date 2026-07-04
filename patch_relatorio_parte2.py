#!/usr/bin/env python3
"""Parte 2: função geradora única gerarBlocosFundamentado(), montagem em texto
plano e em HTML, impressão do Relatório Fundamentado, unificação da minuta,
renomeação/adição de botões."""

SCRATCH = '/tmp/claude-0/-home-user-desktop-tutorial/3517a069-00ce-5e7e-8ba1-0624996120fa/scratchpad'
with open(f'{SCRATCH}/decoded.html', 'r', encoding='utf-8') as f:
    doc = f.read()

def rep(old, new, n=1, label=''):
    global doc
    c = doc.count(old)
    assert c == n, f'[{label}] esperado {n} ocorrência(s), achou {c}: {old[:90]!r}'
    doc = doc.replace(old, new, n)

# ═══════════════════════════════════════════════════════════════════════════
# 6) Funções auxiliares de leitura de DOM (novas, apenas leitura — não tocam
#    em nenhuma lógica de cálculo ou de seleção existente)
# ═══════════════════════════════════════════════════════════════════════════
HELPERS_JS = r'''
    // ─── Fase D: Relatório Fundamentado — funções auxiliares de leitura ───
    function mdToHtml(s) { return s.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\*(.+?)\*/g, '<i>$1</i>'); }
    function mdToText(s) { return s.replace(/\*\*(.+?)\*\*/g, '$1').replace(/\*(.+?)\*/g, '$1'); }

    function radioLabelTexto(name) {
        const r = document.querySelector('input[name="' + name + '"]:checked');
        if (!r) return '';
        const lbl = document.querySelector('label[for="' + r.id + '"]');
        if (!lbl) return '';
        const clone = lbl.cloneNode(true);
        const pctEl = clone.querySelector('.pct');
        if (pctEl) pctEl.remove();
        return clone.textContent.trim();
    }

    function numeroDaCelula(label) {
        const m = label.match(/^(\d+)(\s+ou mais)?/);
        if (!m) return label;
        return m[1] + (m[2] ? ' ou mais' : '');
    }

    function concursoCondutasEspecies() {
        const cell = document.querySelector('#concurso-matrix td.selected');
        if (!cell) return { condutas: '', especies: '' };
        const row = cell.parentElement;
        const rowLabel = row.cells[0].textContent.trim();
        const colIndex = Array.from(row.cells).indexOf(cell);
        const headerRow = document.querySelector('#concurso-matrix thead tr');
        const colLabel = headerRow.cells[colIndex] ? headerRow.cells[colIndex].textContent.trim() : '';
        return { condutas: numeroDaCelula(rowLabel), especies: numeroDaCelula(colLabel) };
    }

    function hipoteseArt22III(gServ, gObra, gReg) {
        const max = Math.max(gServ, gObra, gReg);
        if (max <= 0) return '';
        if (gServ === max) {
            return 'interrupção no fornecimento de serviço público — ' + radioLabelTexto('g-serv').toLowerCase();
        }
        if (gObra === max) {
            const cell = document.querySelector('#obra-matrix td.selected');
            if (!cell) return 'interrupção na execução de obra contratada';
            const row = cell.parentElement;
            const periodo = row.cells[0].textContent.trim();
            const colIndex = Array.from(row.cells).indexOf(cell);
            const headerRow = document.querySelector('#obra-matrix thead tr');
            const residual = headerRow.cells[colIndex] ? headerRow.cells[colIndex].textContent.trim() : '';
            return 'interrupção na execução de obra contratada — período de paralisação de ' + periodo.toLowerCase() + ', com percentual da obra ainda não executado ' + residual.toLowerCase();
        }
        return 'descumprimento de requisitos regulatórios — ' + radioLabelTexto('g-reg').toLowerCase();
    }

    function descricaoLimite(labelElId, prefixo) {
        const el = document.getElementById(labelElId);
        if (!el) return '';
        let t = el.textContent.trim();
        t = t.replace(new RegExp('^' + prefixo + ' \\('), '').replace(/\)$/, '');
        return t;
    }

'''
rep("    // ─── Fase C: Manual Vivo (F1) ───",
    HELPERS_JS + "    // ─── Fase C: Manual Vivo (F1) ───",
    label='helpers de leitura')
print('6/12 funções auxiliares de leitura inseridas.')

with open(f'{SCRATCH}/decoded.html', 'w', encoding='utf-8') as f:
    f.write(doc)
print('OK parte 2a (helpers).')
