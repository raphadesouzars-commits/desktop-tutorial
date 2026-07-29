#!/usr/bin/env python3
# Rodada 13 (extensão): aplica o mesmo redesign Integritas do Nexo Coger ao Nexo PAR.
import re

PATH = '/home/user/desktop-tutorial/ferramentas/nexo-par.html'
B64_PATH = '/tmp/cabecalho-b64.txt'

with open(B64_PATH) as f:
    b64 = f.read().strip()

with open(PATH, encoding='utf-8') as f:
    content = f.read()

# ---------------------------------------------------------------------------
# 1. CSS: print-color-adjust + @page margin já existe, mantemos; adicionamos
#    a regra de cor exata logo no início do bloco @media print existente.
# ---------------------------------------------------------------------------
old_print_css = """@media print{
  body{height:auto;overflow:visible;display:block}
  .topbar,.hero,.lensbar,.main,.panel,.footer,.fab,.col-headers{display:none!important}
  .printview.open{position:static}
  .printview .pv-toolbar{display:none!important}
  .pv-doc{margin:0;max-width:none}
  @page{margin:18mm}
}"""
assert old_print_css in content, "print CSS block not found"
new_print_css = """@media print{
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
  body{height:auto;overflow:visible;display:block}
  .topbar,.hero,.lensbar,.main,.panel,.footer,.fab,.col-headers{display:none!important}
  .printview.open{position:static}
  .printview .pv-toolbar{display:none!important}
  .pv-doc{margin:0;max-width:none}
  @page{margin:15mm 18mm}
}"""
content = content.replace(old_print_css, new_print_css)

# ---------------------------------------------------------------------------
# 2. Substituir tabelaFatoProvaEnquadramento() por uma versão com estilo inline
#    (mesmo defeito do Nexo Coger: class="qual fp" nunca recebia estilo real).
#    Mantemos a função antiga com outro nome caso algo mais a use (nada usa,
#    mas por segurança/rastreabilidade), e adicionamos os helpers de impressão.
# ---------------------------------------------------------------------------
old_helpers_anchor = """function tabelaFatoProvaEnquadramento(fatos){
  const linhas=[];
  fatos.forEach((ft,i)=>{
    const provas=(ft.provaIds||[]).map(provaById).filter(Boolean);
    const enqTxt=enquadramentosAtivos(ft).map(e=>{const n=normaById(e.normaId); return n?esc(n.dispositivo):'';}).filter(Boolean).join('<br>')||'—';
    const fatoTxt=`Fato ${i+1} — ${esc(ft.titulo||'')}`;
    const rows=provas.length?provas:[null];
    rows.forEach((pr,j)=>{
      const provaTxt=pr?esc(pr.titulo)+(pr.codigoAnexo?' ('+esc(pr.codigoAnexo)+')':''):'(sem prova vinculada)';
      const fls=pr&&pr.refAutos&&(pr.refAutos.documento||pr.refAutos.folhas)
        ? `${esc(pr.refAutos.documento||'')}${pr.refAutos.folhas?' fls. '+esc(pr.refAutos.folhas):''}` : '—';
      linhas.push({fatoTxt:j===0?fatoTxt:null, rowspan:rows.length, provaTxt, fls, enqTxt:j===0?enqTxt:null});
    });
  });
  return '<table class="qual fp"><tr><td><b>Fatos de que se acusa</b></td><td><b>Provas acerca dos fatos</b></td><td><b>Fls. dos autos</b></td><td><b>Enquadramentos</b></td></tr>'+
    linhas.map(l=>`<tr>${l.fatoTxt!=null?`<td rowspan="${l.rowspan}">${l.fatoTxt}</td>`:''}<td>${l.provaTxt}</td><td>${l.fls}</td>${l.enqTxt!=null?`<td rowspan="${l.rowspan}">${l.enqTxt}</td>`:''}</tr>`).join('')+
    '</table>';
}"""
assert old_helpers_anchor in content, "tabelaFatoProvaEnquadramento not found"

new_helpers = old_helpers_anchor + """

// ── Impressão institucional (padrão Integritas — Rodada 13, extensão ao Nexo PAR) ──
// Mesmo princípio do Nexo Coger: estilo inline em cada elemento, nada depende de
// classes CSS compartilhadas. Cabeçalho/rodapé em fluxo normal (sem position:fixed).
function impLogosInst(){
  // Cabeçalho oficial (Ministério da Fazenda + Receita Federal) — mesmo arquivo do Nexo Coger.
  const cabecalhoOficial = 'data:image/jpeg;base64,__B64__';
  return '<div style="margin-bottom:10pt">' +
    '<img src="' + cabecalhoOficial + '" alt="Ministério da Fazenda — Receita Federal" style="width:100%;max-width:620px;height:auto;display:block">' +
    '</div>';
}
function impCabecalho(titulo,subtitulo){
  return impLogosInst() +
    '<div style="border-bottom:3px solid #0B2F5F;padding-bottom:9pt;margin-bottom:6pt">' +
      '<div style="font-family:\\'Barlow Condensed\\',sans-serif;font-size:19pt;font-weight:700;color:#0B2F5F;text-transform:uppercase;letter-spacing:.4px">' + esc(titulo) + '</div>' +
      '<div style="font-size:9.5pt;color:#5B6781;margin-top:2pt">' + esc(subtitulo) + '</div>' +
      '<div style="display:flex;gap:24pt;font-size:9pt;color:#5B6781;margin-top:7pt">' +
        '<span><strong style="color:#1A2740">Referência:</strong> <strong id="coger-print-ref" style="font-family:\\'JetBrains Mono\\',monospace;color:#0B2F5F">INT-YYYYMMDD-XXXX</strong></span>' +
        '<span><strong style="color:#1A2740">Data:</strong> <strong id="coger-print-date">—</strong></span>' +
        '<span><strong style="color:#1A2740">Hora:</strong> <strong id="coger-print-time">—</strong></span>' +
      '</div>' +
    '</div>';
}
function impSecao(numero,titulo,bodyHtml){
  return '<div style="page-break-inside:avoid;margin-bottom:16pt">' +
    '<div style="font-family:\\'Barlow Condensed\\',sans-serif;font-size:12.5pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#0B2F5F;border-left:4px solid #C9A35C;padding-left:10px;margin-bottom:10pt">' + esc(numero) + ' — ' + esc(titulo) + '</div>' +
    '<div style="font-size:10.5pt;color:#1A2740;line-height:1.65">' + bodyHtml + '</div>' +
  '</div>';
}
function impInfobox(rows){
  return '<div style="background:#F5F8FC;border:1.5px solid #DCE6F4;border-radius:5px;padding:12pt 14pt;margin-bottom:12pt">' +
    rows.map(r=>'<div style="display:flex;gap:12pt;margin-bottom:6pt;font-size:10pt"><span style="font-weight:700;color:#1E4C99;min-width:130pt;flex-shrink:0">' + esc(r[0]) + ':</span><span style="color:#1A2740">' + r[1] + '</span></div>').join('') +
  '</div>';
}
function impRodape(){
  return '<div style="background:#0B2F5F;color:#fff;padding:8pt 14pt;font-size:8pt;margin-top:18pt;display:flex;justify-content:space-between;align-items:center">' +
    '<span>Ferramentas COGER · Nexo PAR</span>' +
    '<span>USO INTERNO · <span id="coger-print-footer-ref">INT-YYYYMMDD-XXXX</span></span>' +
  '</div>';
}
// Tabela de síntese com estilo 100% inline (thead navy real, zebra striping) — substitui a
// versão por classes CSS (tabelaFatoProvaEnquadramento(), mantida acima para não quebrar nada
// que a use, mas seu HTML nunca recebia estilo real: mesmo defeito do Nexo Coger).
function impTabelaSintese(fatos){
  const linhas=[];
  fatos.forEach((ft,i)=>{
    const provas=(ft.provaIds||[]).map(provaById).filter(Boolean);
    const enqTxt=enquadramentosAtivos(ft).map(e=>{const n=normaById(e.normaId); return n?esc(n.dispositivo):'';}).filter(Boolean).join('<br>')||'—';
    const fatoTxt='Fato ' + (i+1) + ' — ' + esc(ft.titulo||'');
    const rows=provas.length?provas:[null];
    rows.forEach((pr,j)=>{
      const provaTxt=pr?esc(pr.titulo)+(pr.codigoAnexo?' ('+esc(pr.codigoAnexo)+')':''):'(sem prova vinculada)';
      const fls=pr&&pr.refAutos&&(pr.refAutos.documento||pr.refAutos.folhas)
        ? (esc(pr.refAutos.documento||'')+(pr.refAutos.folhas?' fls. '+esc(pr.refAutos.folhas):'')) : '—';
      linhas.push({fatoTxt:j===0?fatoTxt:null, rowspan:rows.length, provaTxt, fls, enqTxt:j===0?enqTxt:null});
    });
  });
  const th='padding:7pt 9pt;text-align:left;font-size:8pt;text-transform:uppercase;letter-spacing:.05em;color:#fff;font-weight:700;background:#0B2F5F;border-bottom:1px solid #0B2F5F';
  const td='padding:7pt 9pt;font-size:9.5pt;color:#1A2740;border-bottom:1px solid #DCE6F4;vertical-align:top';
  let out='<table style="width:100%;border-collapse:collapse;margin:8pt 0;page-break-inside:auto"><thead><tr>' +
    '<th style="'+th+'">Fatos de que se acusa</th>' +
    '<th style="'+th+'">Provas acerca dos fatos</th>' +
    '<th style="'+th+'">Fls. dos autos</th>' +
    '<th style="'+th+'">Enquadramentos</th>' +
  '</tr></thead><tbody>';
  out += linhas.map((l,i)=>{
    const bg = (i%2===1) ? 'background:#F5F8FC' : '';
    return '<tr style="'+bg+';page-break-inside:avoid">' +
      (l.fatoTxt!=null?'<td rowspan="'+l.rowspan+'" style="'+td+'">'+l.fatoTxt+'</td>':'') +
      '<td style="'+td+'">'+l.provaTxt+'</td>' +
      '<td style="'+td+'">'+l.fls+'</td>' +
      (l.enqTxt!=null?'<td rowspan="'+l.rowspan+'" style="'+td+'">'+l.enqTxt+'</td>':'') +
    '</tr>';
  }).join('');
  out += '</tbody></table>';
  return out;
}
// window.CogerPrint — módulo idêntico ao já usado em Veritas/Nexo Coger/Oitiva 360 (Rodadas 10-12).
window.CogerPrint = window.CogerPrint || {};
(function(){
  function generatePrintReference() {
    var now = new Date();
    var yyyy = now.getFullYear();
    var mm = String(now.getMonth() + 1).padStart(2, '0');
    var dd = String(now.getDate()).padStart(2, '0');
    var xxxx = String(Math.floor(Math.random() * 10000)).padStart(4, '0');
    return 'INT-' + yyyy + mm + dd + '-' + xxxx;
  }
  function formatDatePtBr(date) {
    if (!date) return '';
    var d = new Date(date);
    var meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
    return d.getDate() + ' de ' + meses[d.getMonth()] + ' de ' + d.getFullYear();
  }
  function formatTimePtBr(date) {
    if (!date) return '';
    var d = new Date(date);
    return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
  }
  function fillPrintMetadata(options) {
    options = options || {};
    var reference = options.reference || generatePrintReference();
    var now = new Date();
    var dateStr = formatDatePtBr(now);
    var timeStr = formatTimePtBr(now);
    var refEl = document.getElementById('coger-print-ref');
    var dateEl = document.getElementById('coger-print-date');
    var timeEl = document.getElementById('coger-print-time');
    var footerRefEl = document.getElementById('coger-print-footer-ref');
    if (refEl) refEl.textContent = reference;
    if (dateEl) dateEl.textContent = dateStr;
    if (timeEl) timeEl.textContent = timeStr;
    if (footerRefEl) footerRefEl.textContent = reference;
    return reference;
  }
  function prepareForPrint(options) {
    options = options || {};
    return fillPrintMetadata(options);
  }
  window.CogerPrint.generatePrintReference = generatePrintReference;
  window.CogerPrint.formatDatePtBr = formatDatePtBr;
  window.CogerPrint.formatTimePtBr = formatTimePtBr;
  window.CogerPrint.fillPrintMetadata = fillPrintMetadata;
  window.CogerPrint.prepareForPrint = prepareForPrint;
})();"""
new_helpers = new_helpers.replace('__B64__', b64)
content = content.replace(old_helpers_anchor, new_helpers)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fase 1 (CSS + helpers) concluída. Tamanho do arquivo:", len(content))
