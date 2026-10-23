#!/usr/bin/env python3
PATH = '/home/user/desktop-tutorial/ferramentas/veritas.html'
B64_PATH = '/tmp/cabecalho-b64.txt'

with open(B64_PATH) as f:
    b64 = f.read().strip()

with open(PATH, encoding='utf-8') as f:
    content = f.read()

old = r'''function viewRelatorio() {
  var d = DB.dossie, p = d.processo;
  var temSigilo = d.itens.some(function (i) { return i.sigilo !== "publico"; });

  // SVG logos como data URIs (placeholders simples)
  var logoMF = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 40%22%3E%3Crect width=%22100%22 height=%2240%22 fill=%22%230B2F5F%22/%3E%3Ctext x=%2250%22 y=%2228%22 text-anchor=%22middle%22 font-size=%2216%22 fill=%22white%22 font-family=%22Arial%22%3EMF%3C/text%3E%3C/svg%3E';
  var logoRFB = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 40%22%3E%3Crect width=%22100%22 height=%2240%22 fill=%221E4C99%22/%3E%3Ctext x=%2250%22 y=%2228%22 text-anchor=%22middle%22 font-size=%2216%22 fill=%22white%22 font-family=%22Arial%22%3ERFB%3C/text%3E%3C/svg%3E';

  return '<div class="vdc-page">' +
    '<div class="vdc-actions no-print" style="margin-bottom:20px;"><button class="rfb-btn rfb-btn--ghost rfb-btn--sm" onclick="App.voltarProcesso()">&larr; Voltar</button><button class="rfb-btn rfb-btn--primary rfb-btn--sm" onclick="window.CogerPrint.prepareForPrint(); window.print();">Imprimir / Salvar PDF</button></div>' +

    '<div id="printPage">' +
      /* HEADER FIXO */
      '<header class="coger-print-header">' +
        '<div class="coger-print-header-logos">' +
          '<img src="' + logoMF + '" alt="Ministério da Fazenda"/>' +
          '<img src="' + logoRFB + '" alt="Receita Federal"/>' +
        '</div>' +
        '<div class="coger-print-header-title">' +
          '<h1 class="coger-print-doc-title">DOSSIÊ DE PROVAS</h1>' +
          '<p class="coger-print-doc-subtitle">Ferramentas COGER · Veritas</p>' +
        '</div>' +
        '<div class="coger-print-header-meta">' +
          '<span>Referência: <strong id="coger-print-ref">INT-YYYYMMDD-XXXX</strong></span>' +
          '<span>Data: <strong id="coger-print-date">—</strong></span>' +
          '<span>Hora: <strong id="coger-print-time">—</strong></span>' +
        '</div>' +
        '<div class="coger-print-header-divider"></div>' +
      '</header>' +

      /* CONTEÚDO PRINCIPAL */
      '<main>' +
        /* SEÇÃO 1: DADOS DO PROCESSO */
        '<section class="coger-print-section">' +
          '<h2 class="coger-print-section-title">1 — DADOS DO PROCESSO</h2>' +
          '<div class="coger-print-section-body">' +
            '<div class="coger-print-infobox">' +
              '<div class="coger-print-infobox-row">' +
                '<span class="coger-print-infobox-label">Processo:</span>' +
                '<span class="coger-print-infobox-value">' + escapeHtml(p.numero || "—") + '</span>' +
              '</div>' +
              '<div class="coger-print-infobox-row">' +
                '<span class="coger-print-infobox-label">Portaria:</span>' +
                '<span class="coger-print-infobox-value">' + escapeHtml(p.portaria || "—") + '</span>' +
              '</div>' +
              '<div class="coger-print-infobox-row">' +
                '<span class="coger-print-infobox-label">Seção/Unidade:</span>' +
                '<span class="coger-print-infobox-value">' + escapeHtml(p.secaoResponsavel || "—") + '</span>' +
              '</div>' +
              '<div class="coger-print-infobox-row">' +
                '<span class="coger-print-infobox-label">Tipo de Processo:</span>' +
                '<span class="coger-print-infobox-value">' + escapeHtml((p.tipoProcesso && TIPOS_PROCESSO[p.tipoProcesso] && TIPOS_PROCESSO[p.tipoProcesso].nome) || "—") + '</span>' +
              '</div>' +
            '</div>' +
            '<div class="coger-print-infobox">' +
              '<div class="coger-print-infobox-row">' +
                '<span class="coger-print-infobox-label">Presidente:</span>' +
                '<span class="coger-print-infobox-value">' + (p.comissao.presidente.nome ? escapeHtml(p.comissao.presidente.nome) + (p.comissao.presidente.cargo ? ' (' + escapeHtml(p.comissao.presidente.cargo) + ')' : '') : "—") + '</span>' +
              '</div>' +
              '<div class="coger-print-infobox-row">' +
                '<span class="coger-print-infobox-label">Secretário(a):</span>' +
                '<span class="coger-print-infobox-value">' + (p.comissao.secretario.nome ? escapeHtml(p.comissao.secretario.nome) + (p.comissao.secretario.cargo ? ' (' + escapeHtml(p.comissao.secretario.cargo) + ')' : '') : "—") + '</span>' +
              '</div>' +
              (p.comissao.vogais.length > 0 ?
                '<div class="coger-print-infobox-row">' +
                  '<span class="coger-print-infobox-label">Vogais:</span>' +
                  '<span class="coger-print-infobox-value">' + p.comissao.vogais.map(function(v) { return escapeHtml(v.nome || "—") + (v.cargo ? ' (' + escapeHtml(v.cargo) + ')' : ''); }).join('; ') + '</span>' +
                '</div>'
                : '') +
            '</div>' +
          '</div>' +
        '</section>' +

        /* SEÇÃO 2: ELEMENTOS DE PROVA */
        '<section class="coger-print-section">' +
          '<h2 class="coger-print-section-title">2 — ELEMENTOS DE PROVA</h2>' +
          '<div class="coger-print-section-body">' +
            (d.itens.length === 0 ?
              '<p>Nenhum elemento de prova catalogado neste dossiê.</p>'
              : d.itens.map(function(it) {
                var ef = it.proveniencia.elementoFisico;
                return '<div class="coger-print-infobox">' +
                  '<div class="coger-print-infobox-row">' +
                    '<span class="coger-print-infobox-label">Título:</span>' +
                    '<span class="coger-print-infobox-value">' + escapeHtml(it.titulo) + '</span>' +
                  '</div>' +
                  '<div class="coger-print-infobox-row">' +
                    '<span class="coger-print-infobox-label">Categoria:</span>' +
                    '<span class="coger-print-infobox-value">' + (CATEGORIAS_TODAS[it.categoria] || "—") + '</span>' +
                  '</div>' +
                  '<div class="coger-print-infobox-row">' +
                    '<span class="coger-print-infobox-label">Proveniência:</span>' +
                    '<span class="coger-print-infobox-value">' + (PROVENIENCIA_TIPOS[it.proveniencia.tipo] || "—") + '</span>' +
                  '</div>' +
                  '<div class="coger-print-infobox-row">' +
                    '<span class="coger-print-infobox-label">Folhas nos autos:</span>' +
                    '<span class="coger-print-infobox-value">' + escapeHtml(it.folhaAutos || "—") + '</span>' +
                  '</div>' +
                  '<div class="coger-print-infobox-row">' +
                    '<span class="coger-print-infobox-label">Status:</span>' +
                    '<span class="coger-print-infobox-value">' + (STATUS_ITEM[it.status] || "—") + '</span>' +
                  '</div>' +
                  (it.arquivos.length > 0 ?
                    '<div class="coger-print-infobox-row">' +
                      '<span class="coger-print-infobox-label">Arquivos:</span>' +
                      '<span class="coger-print-infobox-value">' + it.arquivos.length + '</span>' +
                    '</div>'
                    : '') +
                '</div>';
              }).join('')) +
          '</div>' +
        '</section>' +

        /* SEÇÃO 3: LINHA DO TEMPO */
        (d.itens.some(function(it) { return eventosMesclados(it).length > 0; }) ?
          '<section class="coger-print-section">' +
            '<h2 class="coger-print-section-title">3 — LINHA DO TEMPO DETALHADA</h2>' +
            '<div class="coger-print-section-body">' +
              d.itens.map(function(it) {
                var evs = eventosMesclados(it);
                if (evs.length === 0) return '';
                return '<div class="coger-print-infobox">' +
                  '<div style="font-weight:600; margin-bottom:10pt;">' + escapeHtml(it.titulo) + '</div>' +
                  '<div style="font-size:10pt; color:#4A5568;">' +
                  evs.map(function(ev) {
                    return '<div style="margin-bottom:6pt;"><strong>' + escapeHtml(ev.titulo) + '</strong><br/>' +
                      (ev.data ? '<span style="font-size:9pt; color:#666;">' + escapeHtml(ev.data) + '</span>' : '') +
                      (ev.observacoes ? ' — ' + escapeHtml(ev.observacoes) : '') + '</div>';
                  }).join('') +
                  '</div>' +
                '</div>';
              }).join('') +
            '</div>' +
          '</section>'
          : '') +

      '</main>' +

      /* FOOTER FIXO */
      '<footer class="coger-print-footer">' +
        '<div class="coger-print-footer-divider"></div>' +
        '<div class="coger-print-footer-content">' +
          '<div class="coger-print-footer-left">' +
            '<span id="coger-print-footer-ref">INT-YYYYMMDD-XXXX</span>' +
          '</div>' +
          '<div class="coger-print-footer-center">' +
            '<span>Página <span class="page-number">1</span> de <span class="page-count">1</span></span>' +
          '</div>' +
          '<div class="coger-print-footer-right">' +
            '<span>USO INTERNO · FERRAMENTAS COGER</span>' +
          '</div>' +
        '</div>' +
      '</footer>' +
    '</div>' +

  '</div>';
}'''

assert old in content, "old viewRelatorio not found"

new = r'''// ── Impressão institucional (padrão Integritas — Rodada 13, extensão ao Veritas) ──
function impLogosInst() {
  var cabecalhoOficial = 'data:image/jpeg;base64,__B64__';
  return '<div style="margin-bottom:10pt">' +
    '<img src="' + cabecalhoOficial + '" alt="Ministério da Fazenda — Receita Federal" style="width:100%;max-width:620px;height:auto;display:block">' +
    '</div>';
}
function impCabecalho(titulo, subtitulo) {
  return impLogosInst() +
    '<div style="border-bottom:3px solid #0B2F5F;padding-bottom:9pt;margin-bottom:6pt">' +
      '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:19pt;font-weight:700;color:#0B2F5F;text-transform:uppercase;letter-spacing:.4px">' + escapeHtml(titulo) + '</div>' +
      '<div style="font-size:9.5pt;color:#5B6781;margin-top:2pt">' + escapeHtml(subtitulo) + '</div>' +
      '<div style="display:flex;gap:24pt;font-size:9pt;color:#5B6781;margin-top:7pt">' +
        '<span><strong style="color:#1A2740">Referência:</strong> <strong id="coger-print-ref" style="font-family:\'JetBrains Mono\',monospace;color:#0B2F5F">INT-YYYYMMDD-XXXX</strong></span>' +
        '<span><strong style="color:#1A2740">Data:</strong> <strong id="coger-print-date">—</strong></span>' +
        '<span><strong style="color:#1A2740">Hora:</strong> <strong id="coger-print-time">—</strong></span>' +
      '</div>' +
    '</div>';
}
function impSecao(numero, titulo, bodyHtml) {
  return '<div style="page-break-inside:avoid;margin-bottom:16pt">' +
    '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:12.5pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#0B2F5F;border-left:4px solid #C9A35C;padding-left:10px;margin-bottom:10pt">' + escapeHtml(numero) + ' — ' + escapeHtml(titulo) + '</div>' +
    '<div style="font-size:10.5pt;color:#1A2740;line-height:1.65">' + bodyHtml + '</div>' +
  '</div>';
}
function impInfobox(rows) {
  return '<div style="background:#F5F8FC;border:1.5px solid #DCE6F4;border-radius:5px;padding:12pt 14pt;margin-bottom:12pt">' +
    rows.map(function(r) { return '<div style="display:flex;gap:12pt;margin-bottom:6pt;font-size:10pt"><span style="font-weight:700;color:#1E4C99;min-width:120pt;flex-shrink:0">' + escapeHtml(r[0]) + ':</span><span style="color:#1A2740">' + r[1] + '</span></div>'; }).join('') +
  '</div>';
}
function impRodape() {
  return '<div style="background:#0B2F5F;color:#fff;padding:8pt 14pt;font-size:8pt;margin-top:18pt;display:flex;justify-content:space-between;align-items:center">' +
    '<span>Ferramentas COGER · Veritas</span>' +
    '<span>USO INTERNO · <span id="coger-print-footer-ref">INT-YYYYMMDD-XXXX</span></span>' +
  '</div>';
}

function viewRelatorio() {
  var d = DB.dossie, p = d.processo;
  var temSigilo = d.itens.some(function (i) { return i.sigilo !== "publico"; });

  var html = '<div id="printPage" style="font-family:Inter,sans-serif;color:#1A2740;font-size:10.5pt;line-height:1.6">';
  html += impCabecalho('DOSSIÊ DE PROVAS', 'Ferramentas COGER · Veritas');

  // SEÇÃO 1: DADOS DO PROCESSO
  var infoRows1 = [
    ['Processo', escapeHtml(p.numero || "—")],
    ['Portaria', escapeHtml(p.portaria || "—")],
    ['Seção/Unidade', escapeHtml(p.secaoResponsavel || "—")],
    ['Tipo de Processo', escapeHtml((p.tipoProcesso && TIPOS_PROCESSO[p.tipoProcesso] && TIPOS_PROCESSO[p.tipoProcesso].nome) || "—")]
  ];
  var infoRows2 = [
    ['Presidente', p.comissao.presidente.nome ? escapeHtml(p.comissao.presidente.nome) + (p.comissao.presidente.cargo ? ' (' + escapeHtml(p.comissao.presidente.cargo) + ')' : '') : "—"],
    ['Secretário(a)', p.comissao.secretario.nome ? escapeHtml(p.comissao.secretario.nome) + (p.comissao.secretario.cargo ? ' (' + escapeHtml(p.comissao.secretario.cargo) + ')' : '') : "—"]
  ];
  if (p.comissao.vogais.length > 0) {
    infoRows2.push(['Vogais', p.comissao.vogais.map(function(v) { return escapeHtml(v.nome || "—") + (v.cargo ? ' (' + escapeHtml(v.cargo) + ')' : ''); }).join('; ')]);
  }
  html += impSecao('1', 'Dados do Processo', impInfobox(infoRows1) + impInfobox(infoRows2));

  // SEÇÃO 2: ELEMENTOS DE PROVA
  var s2 = d.itens.length === 0
    ? '<p style="text-align:justify;margin:0">Nenhum elemento de prova catalogado neste dossiê.</p>'
    : d.itens.map(function(it) {
        var rows = [
          ['Título', escapeHtml(it.titulo)],
          ['Categoria', CATEGORIAS_TODAS[it.categoria] || "—"],
          ['Proveniência', PROVENIENCIA_TIPOS[it.proveniencia.tipo] || "—"],
          ['Folhas nos autos', escapeHtml(it.folhaAutos || "—")],
          ['Status', STATUS_ITEM[it.status] || "—"]
        ];
        if (it.arquivos.length > 0) rows.push(['Arquivos', String(it.arquivos.length)]);
        return impInfobox(rows);
      }).join('');
  html += impSecao('2', 'Elementos de Prova', s2);

  // SEÇÃO 3: LINHA DO TEMPO (condicional)
  if (d.itens.some(function(it) { return eventosMesclados(it).length > 0; })) {
    var s3 = d.itens.map(function(it) {
      var evs = eventosMesclados(it);
      if (evs.length === 0) return '';
      var body = '<div style="font-weight:600;margin-bottom:10pt;color:#1A2740">' + escapeHtml(it.titulo) + '</div>' +
        '<div style="font-size:10pt;color:#4A5568">' +
        evs.map(function(ev) {
          return '<div style="margin-bottom:6pt"><strong>' + escapeHtml(ev.titulo) + '</strong><br/>' +
            (ev.data ? '<span style="font-size:9pt;color:#666">' + escapeHtml(ev.data) + '</span>' : '') +
            (ev.observacoes ? ' — ' + escapeHtml(ev.observacoes) : '') + '</div>';
        }).join('') +
        '</div>';
      return '<div style="background:#F5F8FC;border:1.5px solid #DCE6F4;border-radius:5px;padding:12pt 14pt;margin-bottom:12pt">' + body + '</div>';
    }).join('');
    html += impSecao('3', 'Linha do Tempo Detalhada', s3);
  }

  html += impRodape();
  html += '</div>';

  return '<div class="vdc-page">' +
    '<div class="vdc-actions no-print" style="margin-bottom:20px;"><button class="rfb-btn rfb-btn--ghost rfb-btn--sm" onclick="App.voltarProcesso()">&larr; Voltar</button><button class="rfb-btn rfb-btn--primary rfb-btn--sm" onclick="window.CogerPrint.prepareForPrint(); window.print();">Imprimir / Salvar PDF</button></div>' +
    html +
  '</div>';
}'''
new = new.replace('__B64__', b64)

content = content.replace(old, new)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fase 2 (viewRelatorio) concluída. Tamanho:", len(content))
