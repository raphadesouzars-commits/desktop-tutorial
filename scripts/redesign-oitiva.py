#!/usr/bin/env python3
PATH = '/home/user/desktop-tutorial/ferramentas/oitiva-360.html'
B64_PATH = '/tmp/cabecalho-b64.txt'

with open(B64_PATH) as f:
    b64 = f.read().strip()

with open(PATH, encoding='utf-8') as f:
    content = f.read()

old = r'''function montarAreaImpressaoTermo(d){
  const papelNome = (CATALOGO.papeis.find(p => p.id === d.papel) || {}).nome || d.papel;
  const logoMF = obterLogoRFBDataUri(); // Will use same logo for both for consistency
  const logoRFB = obterLogoRFBDataUri();
  const processNum = d.ato.numero || estado.processo.numero || "—";
  const dataBR = formatarDataBR(d.ato.data) || "—";

  let html = "<div id=\"printPage\">";

  // HEADER FIXO
  html += "<header class=\"coger-print-header\">" +
    "<div class=\"coger-print-header-logos\">" +
      (logoMF ? "<img src=\"" + logoMF + "\" alt=\"Ministério da Fazenda\" class=\"coger-logo-mf\"/>" : "") +
      (logoRFB ? "<img src=\"" + logoRFB + "\" alt=\"Receita Federal\" class=\"coger-logo-rfb\"/>" : "") +
    "</div>" +
    "<div class=\"coger-print-header-title\">" +
      "<h1 class=\"coger-print-doc-title\">TERMO DE OITIVA</h1>" +
      "<p class=\"coger-print-doc-subtitle\">Ferramentas COGER · Oitiva 360</p>" +
    "</div>" +
    "<div class=\"coger-print-header-meta\">" +
      "<span>Referência: <strong id=\"coger-print-ref\">INT-YYYYMMDD-XXXX</strong></span>" +
      "<span>Data: <strong id=\"coger-print-date\">...</strong></span>" +
      "<span>Hora: <strong id=\"coger-print-time\">...</strong></span>" +
    "</div>" +
    "<div class=\"coger-print-header-divider\"></div>" +
  "</header>";

  // MAIN CONTENT
  html += "<main>";

  // Seção 1: Identificação
  html += "<section class=\"coger-print-section\">" +
    "<h2 class=\"coger-print-section-title\">1 — IDENTIFICAÇÃO</h2>" +
    "<div class=\"coger-print-section-body\">" +
      "<div class=\"coger-print-infobox\">" +
        "<div class=\"coger-print-infobox-row\">" +
          "<span class=\"coger-print-infobox-label\">Processo nº:</span>" +
          "<span class=\"coger-print-infobox-value\">" + escapeHtml(processNum) + "</span>" +
        "</div>" +
        "<div class=\"coger-print-infobox-row\">" +
          "<span class=\"coger-print-infobox-label\">Depoente:</span>" +
          "<span class=\"coger-print-infobox-value\">" + escapeHtml(d.identificacao || "—") + "</span>" +
        "</div>" +
        "<div class=\"coger-print-infobox-row\">" +
          "<span class=\"coger-print-infobox-label\">Papel:</span>" +
          "<span class=\"coger-print-infobox-value\">" + escapeHtml(papelNome) + "</span>" +
        "</div>" +
        "<div class=\"coger-print-infobox-row\">" +
          "<span class=\"coger-print-infobox-label\">Data:</span>" +
          "<span class=\"coger-print-infobox-value\">" + escapeHtml(dataBR) + "</span>" +
        "</div>" +
      "</div>" +
    "</div>" +
  "</section>";

  // Seção 2: Perguntas e Respostas (parsed from d.termoTexto)
  const qaItems = extrairQADoTermo(d.termoTexto || "");
  html += "<section class=\"coger-print-section\">" +
    "<h2 class=\"coger-print-section-title\">2 — PERGUNTAS E RESPOSTAS</h2>" +
    "<div class=\"coger-print-section-body\">";

  qaItems.forEach((item, idx) => {
    html += "<div class=\"coger-print-qa-item\">" +
      "<div class=\"coger-print-qa-question\"><strong>P" + (idx + 1) + ". " + escapeHtml(item.pergunta) + "</strong></div>" +
      "<div class=\"coger-print-qa-response\"><strong>R:</strong> " + escapeHtml(item.resposta) + "</div>" +
    "</div>";
  });

  html += "  </div>" +
  "</section>";

  // Seção 3: Encerramento
  html += "<section class=\"coger-print-section\">" +
    "<h2 class=\"coger-print-section-title\">3 — ENCERRAMENTO</h2>" +
    "<div class=\"coger-print-section-body\">" +
      "<p style=\"text-align: justify; margin-bottom: 20pt;\">Nada mais havendo, encerrou-se o presente termo, que, lido e achado conforme, vai assinado por todos os presentes.</p>" +
      "<div style=\"margin-top: 40px; display: flex; justify-content: space-around; padding-top: 40px; border-top: 1px solid #ddd;\">" +
        "<div style=\"text-align: center; flex: 1;\">" +
          "<div style=\"height: 60px; margin-bottom: 8px;\"></div>" +
          "<strong>Investigador</strong>" +
        "</div>" +
        "<div style=\"text-align: center; flex: 1;\">" +
          "<div style=\"height: 60px; margin-bottom: 8px;\"></div>" +
          "<strong>Investigado</strong>" +
        "</div>" +
        "<div style=\"text-align: center; flex: 1;\">" +
          "<div style=\"height: 60px; margin-bottom: 8px;\"></div>" +
          "<strong>Testemunha</strong>" +
        "</div>" +
      "</div>" +
    "</div>" +
  "</section>";

  html += "</main>";

  // FOOTER FIXO
  html += "<footer class=\"coger-print-footer\">" +
    "<div class=\"coger-print-footer-divider\"></div>" +
    "<div class=\"coger-print-footer-content\">" +
      "<div class=\"coger-print-footer-left\"><span id=\"coger-print-footer-ref\">INT-YYYYMMDD-XXXX</span></div>" +
      "<div class=\"coger-print-footer-center\">Página <span class=\"page-number\">1</span> de <span class=\"page-count\">1</span></div>" +
      "<div class=\"coger-print-footer-right\">USO INTERNO · FERRAMENTAS COGER</div>" +
    "</div>" +
  "</footer>";

  html += "</div>";

  document.getElementById("area-impressao").innerHTML = html;
}'''

assert old in content, "old montarAreaImpressaoTermo not found"

new = r'''// ── Impressão institucional (padrão Integritas — Rodada 13, extensão ao Oitiva 360) ──
function impLogosInst(){
  const cabecalhoOficial = "data:image/jpeg;base64,__B64__";
  return "<div style=\"margin-bottom:10pt\">" +
    "<img src=\"" + cabecalhoOficial + "\" alt=\"Ministério da Fazenda — Receita Federal\" style=\"width:100%;max-width:620px;height:auto;display:block\">" +
    "</div>";
}
function impCabecalho(titulo, subtitulo){
  return impLogosInst() +
    "<div style=\"border-bottom:3px solid #0B2F5F;padding-bottom:9pt;margin-bottom:6pt\">" +
      "<div style=\"font-family:'Barlow Condensed',sans-serif;font-size:19pt;font-weight:700;color:#0B2F5F;text-transform:uppercase;letter-spacing:.4px\">" + escapeHtml(titulo) + "</div>" +
      "<div style=\"font-size:9.5pt;color:#5B6781;margin-top:2pt\">" + escapeHtml(subtitulo) + "</div>" +
      "<div style=\"display:flex;gap:24pt;font-size:9pt;color:#5B6781;margin-top:7pt\">" +
        "<span><strong style=\"color:#1A2740\">Referência:</strong> <strong id=\"coger-print-ref\" style=\"font-family:'JetBrains Mono',monospace;color:#0B2F5F\">INT-YYYYMMDD-XXXX</strong></span>" +
        "<span><strong style=\"color:#1A2740\">Data:</strong> <strong id=\"coger-print-date\">—</strong></span>" +
        "<span><strong style=\"color:#1A2740\">Hora:</strong> <strong id=\"coger-print-time\">—</strong></span>" +
      "</div>" +
    "</div>";
}
function impSecao(numero, titulo, bodyHtml){
  return "<div style=\"page-break-inside:avoid;margin-bottom:16pt\">" +
    "<div style=\"font-family:'Barlow Condensed',sans-serif;font-size:12.5pt;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#0B2F5F;border-left:4px solid #C9A35C;padding-left:10px;margin-bottom:10pt\">" + escapeHtml(numero) + " — " + escapeHtml(titulo) + "</div>" +
    "<div style=\"font-size:10.5pt;color:#1A2740;line-height:1.65\">" + bodyHtml + "</div>" +
  "</div>";
}
function impInfobox(rows){
  return "<div style=\"background:#F5F8FC;border:1.5px solid #DCE6F4;border-radius:5px;padding:12pt 14pt;margin-bottom:12pt\">" +
    rows.map(r => "<div style=\"display:flex;gap:12pt;margin-bottom:6pt;font-size:10pt\"><span style=\"font-weight:700;color:#1E4C99;min-width:110pt;flex-shrink:0\">" + escapeHtml(r[0]) + ":</span><span style=\"color:#1A2740\">" + r[1] + "</span></div>").join("") +
  "</div>";
}
function impRodape(){
  return "<div style=\"background:#0B2F5F;color:#fff;padding:8pt 14pt;font-size:8pt;margin-top:18pt;display:flex;justify-content:space-between;align-items:center\">" +
    "<span>Ferramentas COGER · Oitiva 360</span>" +
    "<span>USO INTERNO · <span id=\"coger-print-footer-ref\">INT-YYYYMMDD-XXXX</span></span>" +
  "</div>";
}

function montarAreaImpressaoTermo(d){
  const papelNome = (CATALOGO.papeis.find(p => p.id === d.papel) || {}).nome || d.papel;
  const processNum = d.ato.numero || estado.processo.numero || "—";
  const dataBR = formatarDataBR(d.ato.data) || "—";

  let html = "<div id=\"printPage\" style=\"font-family:Inter,sans-serif;color:#1A2740;font-size:10.5pt;line-height:1.6\">";
  html += impCabecalho("TERMO DE OITIVA", "Ferramentas COGER · Oitiva 360");

  // Seção 1: Identificação
  html += impSecao("1", "Identificação", impInfobox([
    ["Processo nº", escapeHtml(processNum)],
    ["Depoente", escapeHtml(d.identificacao || "—")],
    ["Papel", escapeHtml(papelNome)],
    ["Data", escapeHtml(dataBR)],
  ]));

  // Seção 2: Perguntas e Respostas
  const qaItems = extrairQADoTermo(d.termoTexto || "");
  let s2 = "";
  qaItems.forEach((item, idx) => {
    s2 += "<div style=\"page-break-inside:avoid;margin-bottom:10pt\">" +
      "<div style=\"font-weight:700;margin-bottom:4pt;font-size:10pt;color:#0B2F5F\">P" + (idx + 1) + ". " + escapeHtml(item.pergunta) + "</div>" +
      "<div style=\"font-size:10pt;color:#1A2740;line-height:1.5\"><strong>R:</strong> " + escapeHtml(item.resposta) + "</div>" +
    "</div>";
  });
  html += impSecao("2", "Perguntas e Respostas", s2);

  // Seção 3: Encerramento
  html += impSecao("3", "Encerramento",
    "<p style=\"text-align:justify;margin:0 0 20pt\">Nada mais havendo, encerrou-se o presente termo, que, lido e achado conforme, vai assinado por todos os presentes.</p>" +
    "<div style=\"margin-top:40px;display:flex;justify-content:space-around;padding-top:40px;border-top:1px solid #ddd\">" +
      "<div style=\"text-align:center;flex:1\"><div style=\"height:60px;margin-bottom:8px\"></div><strong>Investigador</strong></div>" +
      "<div style=\"text-align:center;flex:1\"><div style=\"height:60px;margin-bottom:8px\"></div><strong>Investigado</strong></div>" +
      "<div style=\"text-align:center;flex:1\"><div style=\"height:60px;margin-bottom:8px\"></div><strong>Testemunha</strong></div>" +
    "</div>");

  html += impRodape();
  html += "</div>";

  document.getElementById("area-impressao").innerHTML = html;
}'''
new = new.replace('__B64__', b64)

content = content.replace(old, new)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Redesign concluído. Tamanho:", len(content))
