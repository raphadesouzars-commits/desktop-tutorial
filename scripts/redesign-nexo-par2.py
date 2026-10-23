#!/usr/bin/env python3
import re

PATH = '/home/user/desktop-tutorial/ferramentas/nexo-par.html'

with open(PATH, encoding='utf-8') as f:
    content = f.read()

old = r'''function renderIndiciacao(id,dataDoc){
  const a=acusadoById(id);
  openPrint(construirTextoIndiciacao(id,dataDoc),'Nota de Indiciação — '+(a.razaoSocial||a.nome||id));
}
function construirTextoIndiciacao(id,dataDoc){
  const p=doc.processo, c=p.comissao, a=acusadoById(id);
  const repLegal=(a.representantes||[]).find(r=>r.vinculo==='PAPEL.REPRESENTANTE_LEGAL'&&(r.nome||'').trim())||(a.representantes||[])[0]||{};
  // fatos ATIVOS imputados ao ente, na ORDEM NARRATIVA definida no painel
  // (arquivados são ignorados: apurados, mas a comissão decidiu não indiciar)
  const fatos=fatosOrdenados(doc.fatos.filter(x=>!fatoArquivado(x)&&(x.condutas||[]).some(cc=>cc.acusadoId===id)));
  const partes=[];
  partes.push(`<div class="inst">MINISTÉRIO DA FAZENDA — RECEITA FEDERAL DO BRASIL</div>
    <div class="inst">CORREGEDORIA DA RECEITA FEDERAL DO BRASIL (Coger/RFB) — ${esc(p.unidade||'')}</div>
    <h1>Nota de Indiciação</h1>
    <p class="center">Processo Administrativo de Responsabilização (PAR) nº ${esc(p.numero)}</p>
    <p class="center">Lei nº 12.846, de 1º de agosto de 2013 (Lei Anticorrupção — LAC)</p>
    <p class="center">Comissão designada pela Portaria nº ${esc(c.portariaInstauracao.numero||'—')}${c.portariaInstauracao.data?', de '+esc(c.portariaInstauracao.data):''}.</p>
    <p class="center">Pessoa jurídica: ${esc(a.razaoSocial||a.nome||'—')}, CNPJ ${esc(a.cnpj||'—')}</p>`);
  // qualificação do ente privado
  partes.push(`<table class="qual">
    <tr><td><b>Razão social</b></td><td>${esc(a.razaoSocial||a.nome||'—')}</td></tr>
    <tr><td><b>CNPJ</b></td><td>${esc(a.cnpj||'—')}</td></tr>
    ${a.nomeFantasia?`<tr><td><b>Nome fantasia</b></td><td>${esc(a.nomeFantasia)}</td></tr>`:''}
    ${a.endereco?`<tr><td><b>Endereço da sede</b></td><td>${esc(a.endereco)}</td></tr>`:''}
    <tr><td><b>Representante legal</b></td><td>${esc(repLegal.nome||'—')}${repLegal.cpf?', CPF '+esc(repLegal.cpf):''}</td></tr>
  </table>`);
  if(a.desconsideracao&&a.desconsideracao.ativa){
    partes.push(`<p><i>Aplica-se a desconsideração da personalidade jurídica (art. 14 da Lei nº 12.846/2013): ${esc(a.desconsideracao.fundamentacao||'')}</i></p>`);
  }
  // conduta lesiva imputada ao ente
  partes.push('<h2>Da conduta lesiva imputada ao ente privado</h2>');
  fatos.forEach((ft,i)=>{
    const cond=(ft.condutas||[]).find(cc=>cc.acusadoId===id)||{};
    partes.push(`<p><b>Fato ${i+1} (${esc(ft.titulo)}).</b> ${esc(ft.descricao)}${ft.periodo&&(ft.periodo.inicio||ft.periodo.fim)?` Período: ${esc(ft.periodo.inicio||'?')} a ${esc(ft.periodo.fim||'?')}.`:''}${ft.local?` Local: ${esc(ft.local)}.`:''}</p>`);
    partes.push(`<p>Quanto à conduta lesiva individualizada, apurou-se que, de forma ${esc(cond.modalidade==='omissiva'?'omissiva':'comissiva')}, ${esc(cond.descricaoConduta||'')}</p>`);
    if((ft.beneficioInteresse||'').trim())
      partes.push(`<p><b>Interesse ou benefício da pessoa jurídica:</b> ${esc(ft.beneficioInteresse)}</p>`);
    if((ft.nexoCausalidade||'').trim())
      partes.push(`<p><b>Nexo de causalidade:</b> ${esc(ft.nexoCausalidade)}</p>`);
  });
  // provas — com índice numerado (item 5, herdado). Numeração derivada, não persistida.
  const provaIndex=[], provaNum={};
  const registra=(pr,fatoId)=>{
    if(!(pr.id in provaNum)){
      const num=provaIndex.length+1;
      provaNum[pr.id]=num;
      provaIndex.push({prova:pr, num, ref:((pr.codigoAnexo||'').trim()||('Prova nº '+num)), fatos:[]});
    }
    const e=provaIndex[provaNum[pr.id]-1]; if(!e.fatos.includes(fatoId)) e.fatos.push(fatoId);
  };
  partes.push('<h2>Das provas</h2>');
  fatos.forEach((ft,i)=>{
    const provas=(ft.provaIds||[]).map(provaById).filter(Boolean);
    if(!provas.length){ partes.push(`<p>Fato ${i+1}: (sem prova vinculada).</p>`); return; }
    provas.forEach(pr=>registra(pr,ft.id));
    let s=`<p>Fato ${i+1} — sustenta-se em: `;
    s+=provas.map(pr=>{
      let r=`(${esc(provaIndex[provaNum[pr.id]-1].ref)}) ${esc(pr.titulo)} (${esc(pr.tipo)}`;
      if(pr.refAutos&&(pr.refAutos.documento||pr.refAutos.folhas)) r+=`, ${esc(pr.refAutos.documento||'')}${pr.refAutos.folhas?' fls. '+esc(pr.refAutos.folhas):''}`;
      r+=')';
      return r;
    }).join('; ')+'.</p>';
    partes.push(s);
    provas.forEach(pr=>(pr.trechosSignificativos||[]).forEach(t=>{ if((t.citacao||'').trim())
      partes.push(`<div class="quote">"${esc(t.citacao)}"${t.ref?' ('+esc(t.ref)+')':''}</div>`); }));
  });
  // enquadramento
  partes.push('<h2>Do enquadramento legal</h2>');
  fatos.forEach((ft,i)=>{
    const ativos=enquadramentosAtivos(ft);
    const afastados=(ft.enquadramentos||[]).filter(e=>e.afastado);
    ativos.forEach(e=>{
      const n=normaById(e.normaId);
      // Fork PAR: sem elemento subjetivo (responsabilidade objetiva, art. 2º da LAC).
      partes.push(`<p>Fato ${i+1}: a conduta amolda-se ao <b>${esc(n.dispositivo)}</b> (${esc(n.rotulo)}). ${esc(e.fundamentacao||'')}</p>`);
    });
    if(ft.multiplicidade&&ft.multiplicidade.classificacao==='concurso_formal'&&ativos.length>1)
      partes.push(`<p><i>Reconhece-se concurso formal entre os dispositivos acima, cuja repercussão se dará na dosimetria da pena.</i></p>`);
    if(ft.multiplicidade&&ft.multiplicidade.classificacao==='conflito_aparente'&&afastados.length){
      const prev=normaById(ft.multiplicidade.normaPrevalente);
      partes.push(`<p><i>Prevalece o ${esc(prev?prev.dispositivo:'')} por ${esc(ft.multiplicidade.principioAplicado)}. Afasta-se: ${afastados.map(e=>esc((normaById(e.normaId)||{}).dispositivo)).join('; ')}. ${esc(ft.multiplicidade.justificativa||'')}</i></p>`);
    }
  });
  // síntese fato × prova × enquadramento (item 4 — substitui o antigo "Índice de Provas Citadas" por prova)
  partes.push('<h2>Síntese dos fatos, provas e enquadramentos</h2>');
  partes.push(tabelaFatoProvaEnquadramento(fatos));
  // alegações da defesa não acatadas
  partes.push('<h2>Das alegações da defesa não acatadas</h2>');
  const alegacoes=(a.alegacoesDefesaNaoAcatadas||'').trim();
  partes.push(`<div class="editable-block" contenteditable="true">${alegacoes
    ? esc(alegacoes).replace(/\n/g,'<br>')
    : '[Inserir alegações da defesa não acatadas durante a instrução, se houver, e a motivação de sua rejeição]'}</div>`);
  // Textos obrigatórios/recomendados pela IN CGU nº 13/2019 e pelo Manual CGU (item 3.6) — parágrafos fixos.
  partes.push(`<h2>Da multa, do faturamento bruto e do programa de integridade</h2>
    <p>Faculta-se expressamente à pessoa jurídica indiciada apresentar informações e provas relativas aos parâmetros de cálculo da multa e ao seu faturamento bruto no exercício anterior ao da instauração do processo.</p>
    <p>Solicitam-se, ainda, informações e documentos necessários à análise do parâmetro previsto no inciso IV do art. 22 do Decreto nº 11.129, de 11 de julho de 2022.</p>
    <p>Fica assegurado o prazo de 30 (trinta) dias para apresentação de defesa escrita, contado da intimação desta Nota de Indiciação, podendo a pessoa jurídica apresentar, em conjunto com a defesa, evidências da existência e do funcionamento de programa de integridade, nos termos da Portaria CGU nº 909, de 7 de abril de 2025.</p>
    <p>Registra-se, por fim, a possibilidade de resolução negociada do processo, por meio de Termo de Compromisso ou de Acordo de Leniência, na forma da legislação de regência.</p>`);
  // fecho
  const dt=parseDate(dataDoc);
  const dataFmt=dt?fmtDate(dt):(dataDoc||new Date().toLocaleDateString('pt-BR'));
  partes.push(`<h2>Do encerramento</h2>
    <p>Ressalva-se que o enquadramento ora proposto poderá ser adequado por ocasião do Relatório Final, à luz da defesa, uma vez que o indiciado se defende dos fatos e não da sua capitulação.</p>
    <p>Intime-se a pessoa jurídica indiciada para, no prazo de 30 (trinta) dias contado da intimação desta Nota de Indiciação, apresentar defesa escrita (art. 17 da IN CGU nº 13/2019).</p>
    <p class="center" style="margin-top:36px">${esc(p.cidade||p.unidade||'')}, ${esc(dataFmt)}.</p>
    ${blocoAssinatura3(c)}`);

  return partes.join('\n');
}'''

assert old in content, "old renderIndiciacao/construirTextoIndiciacao block not found"

new = r'''function renderIndiciacao(id,dataDoc){
  const a=acusadoById(id);
  openPrint(construirTextoIndiciacao(id,dataDoc),'Nota de Indiciação — '+(a.razaoSocial||a.nome||id));
  window.CogerPrint.prepareForPrint();
}
function construirTextoIndiciacao(id,dataDoc){
  const p=doc.processo, c=p.comissao, a=acusadoById(id);
  const repLegal=(a.representantes||[]).find(r=>r.vinculo==='PAPEL.REPRESENTANTE_LEGAL'&&(r.nome||'').trim())||(a.representantes||[])[0]||{};
  // fatos ATIVOS imputados ao ente, na ORDEM NARRATIVA definida no painel
  // (arquivados são ignorados: apurados, mas a comissão decidiu não indiciar)
  const fatos=fatosOrdenados(doc.fatos.filter(x=>!fatoArquivado(x)&&(x.condutas||[]).some(cc=>cc.acusadoId===id)));

  let html = '<div id="printPage" style="font-family:Inter,sans-serif;color:#1A2740;font-size:10.5pt;line-height:1.6">';
  html += impCabecalho('NOTA DE INDICIAÇÃO', 'Processo Administrativo de Responsabilização (PAR) nº ' + esc(p.numero||'—') + ' · Lei nº 12.846/2013 (LAC)');

  /* SEÇÃO 1: IDENTIFICAÇÃO DO ENTE PRIVADO */
  const infoRows=[
    ['Razão social', esc(a.razaoSocial||a.nome||'—')],
    ['CNPJ', esc(a.cnpj||'—')],
  ];
  if(a.nomeFantasia) infoRows.push(['Nome fantasia', esc(a.nomeFantasia)]);
  if(a.endereco) infoRows.push(['Endereço da sede', esc(a.endereco)]);
  infoRows.push(['Representante legal', esc(repLegal.nome||'—')+(repLegal.cpf?', CPF '+esc(repLegal.cpf):'')]);
  let s1 = impInfobox(infoRows);
  if(a.desconsideracao&&a.desconsideracao.ativa){
    s1 += '<p style="text-align:justify;margin:0"><i>Aplica-se a desconsideração da personalidade jurídica (art. 14 da Lei nº 12.846/2013): ' + esc(a.desconsideracao.fundamentacao||'') + '</i></p>';
  }
  html += impSecao('1','Identificação do ente privado', s1);

  /* SEÇÃO 2: DA CONDUTA LESIVA IMPUTADA AO ENTE PRIVADO */
  let s2='';
  fatos.forEach((ft,i)=>{
    const cond=(ft.condutas||[]).find(cc=>cc.acusadoId===id)||{};
    s2 += '<p style="text-align:justify;margin:0 0 8pt"><b>Fato ' + (i+1) + ' (' + esc(ft.titulo) + ').</b> ' + esc(ft.descricao);
    if(ft.periodo&&(ft.periodo.inicio||ft.periodo.fim)) s2 += ' Período: ' + esc(ft.periodo.inicio||'?') + ' a ' + esc(ft.periodo.fim||'?') + '.';
    if(ft.local) s2 += ' Local: ' + esc(ft.local) + '.';
    s2 += '</p>';
    s2 += '<p style="text-align:justify;margin:0 0 8pt">Quanto à conduta lesiva individualizada, apurou-se que, de forma ' + esc(cond.modalidade==='omissiva'?'omissiva':'comissiva') + ', ' + esc(cond.descricaoConduta||'') + '</p>';
    if((ft.beneficioInteresse||'').trim())
      s2 += '<p style="text-align:justify;margin:0 0 8pt"><b>Interesse ou benefício da pessoa jurídica:</b> ' + esc(ft.beneficioInteresse) + '</p>';
    if((ft.nexoCausalidade||'').trim())
      s2 += '<p style="text-align:justify;margin:0 0 8pt"><b>Nexo de causalidade:</b> ' + esc(ft.nexoCausalidade) + '</p>';
  });
  html += impSecao('2','Da conduta lesiva imputada ao ente privado', s2);

  /* SEÇÃO 3: DAS PROVAS */
  const provaIndex=[], provaNum={};
  const registra=(pr,fatoId)=>{
    if(!(pr.id in provaNum)){
      const num=provaIndex.length+1;
      provaNum[pr.id]=num;
      provaIndex.push({prova:pr, num, ref:((pr.codigoAnexo||'').trim()||('Prova nº '+num)), fatos:[]});
    }
    const e=provaIndex[provaNum[pr.id]-1]; if(!e.fatos.includes(fatoId)) e.fatos.push(fatoId);
  };
  let s3='';
  fatos.forEach((ft,i)=>{
    const provas=(ft.provaIds||[]).map(provaById).filter(Boolean);
    if(!provas.length){ s3 += '<p style="text-align:justify;margin:0 0 8pt">Fato ' + (i+1) + ': (sem prova vinculada).</p>'; return; }
    provas.forEach(pr=>registra(pr,ft.id));
    s3 += '<p style="text-align:justify;margin:0 0 8pt">Fato ' + (i+1) + ' — sustenta-se em: ';
    s3 += provas.map(pr=>{
      let r='(' + esc(provaIndex[provaNum[pr.id]-1].ref) + ') ' + esc(pr.titulo) + ' (' + esc(pr.tipo);
      if(pr.refAutos&&(pr.refAutos.documento||pr.refAutos.folhas)) r += ', ' + esc(pr.refAutos.documento||'') + (pr.refAutos.folhas?' fls. '+esc(pr.refAutos.folhas):'');
      r += ')';
      return r;
    }).join('; ') + '.</p>';
    provas.forEach(pr=>(pr.trechosSignificativos||[]).forEach(t=>{ if((t.citacao||'').trim())
      s3 += '<div style="margin:8pt 0;padding:8pt 12pt;background:#F5F8FC;border-left:3px solid #0B2F5F;font-style:italic;color:#1A2740;font-size:9.5pt">"' + esc(t.citacao) + '"' + (t.ref?' ('+esc(t.ref)+')':'') + '</div>'; }));
  });
  html += impSecao('3','Das provas', s3);

  /* SEÇÃO 4: DO ENQUADRAMENTO LEGAL */
  let s4='';
  fatos.forEach((ft,i)=>{
    const ativos=enquadramentosAtivos(ft);
    const afastados=(ft.enquadramentos||[]).filter(e=>e.afastado);
    ativos.forEach(e=>{
      const n=normaById(e.normaId);
      // Fork PAR: sem elemento subjetivo (responsabilidade objetiva, art. 2º da LAC).
      s4 += '<p style="text-align:justify;margin:0 0 8pt">Fato ' + (i+1) + ': a conduta amolda-se ao <b>' + esc(n.dispositivo) + '</b> (' + esc(n.rotulo) + '). ' + esc(e.fundamentacao||'') + '</p>';
    });
    if(ft.multiplicidade&&ft.multiplicidade.classificacao==='concurso_formal'&&ativos.length>1)
      s4 += '<p style="text-align:justify;margin:0 0 8pt"><i>Reconhece-se concurso formal entre os dispositivos acima, cuja repercussão se dará na dosimetria da pena.</i></p>';
    if(ft.multiplicidade&&ft.multiplicidade.classificacao==='conflito_aparente'&&afastados.length){
      const prev=normaById(ft.multiplicidade.normaPrevalente);
      s4 += '<p style="text-align:justify;margin:0 0 8pt"><i>Prevalece o ' + esc(prev?prev.dispositivo:'') + ' por ' + esc(ft.multiplicidade.principioAplicado) + '. Afasta-se: ' + afastados.map(e=>esc((normaById(e.normaId)||{}).dispositivo)).join('; ') + '. ' + esc(ft.multiplicidade.justificativa||'') + '</i></p>';
    }
  });
  html += impSecao('4','Do enquadramento legal', s4);

  /* SEÇÃO 5: SÍNTESE DOS FATOS, PROVAS E ENQUADRAMENTOS */
  html += impSecao('5','Síntese dos fatos, provas e enquadramentos', impTabelaSintese(fatos));

  /* SEÇÃO 6: DAS ALEGAÇÕES DA DEFESA NÃO ACATADAS */
  const alegacoes=(a.alegacoesDefesaNaoAcatadas||'').trim();
  html += impSecao('6','Das alegações da defesa não acatadas',
    '<div class="no-print" contenteditable="true" style="border:1px dashed #9AA3AD;border-radius:5px;padding:10pt 12pt;min-height:24pt;color:#1A2740">' +
      (alegacoes ? esc(alegacoes).replace(/\n/g,'<br>') : '[Inserir alegações da defesa não acatadas durante a instrução, se houver, e a motivação de sua rejeição]') +
    '</div>');

  /* SEÇÃO 7: DA MULTA, DO FATURAMENTO BRUTO E DO PROGRAMA DE INTEGRIDADE */
  html += impSecao('7','Da multa, do faturamento bruto e do programa de integridade',
    '<p style="text-align:justify;margin:0 0 8pt">Faculta-se expressamente à pessoa jurídica indiciada apresentar informações e provas relativas aos parâmetros de cálculo da multa e ao seu faturamento bruto no exercício anterior ao da instauração do processo.</p>' +
    '<p style="text-align:justify;margin:0 0 8pt">Solicitam-se, ainda, informações e documentos necessários à análise do parâmetro previsto no inciso IV do art. 22 do Decreto nº 11.129, de 11 de julho de 2022.</p>' +
    '<p style="text-align:justify;margin:0 0 8pt">Fica assegurado o prazo de 30 (trinta) dias para apresentação de defesa escrita, contado da intimação desta Nota de Indiciação, podendo a pessoa jurídica apresentar, em conjunto com a defesa, evidências da existência e do funcionamento de programa de integridade, nos termos da Portaria CGU nº 909, de 7 de abril de 2025.</p>' +
    '<p style="text-align:justify;margin:0">Registra-se, por fim, a possibilidade de resolução negociada do processo, por meio de Termo de Compromisso ou de Acordo de Leniência, na forma da legislação de regência.</p>');

  /* SEÇÃO 8: DO ENCERRAMENTO */
  const dt=parseDate(dataDoc);
  const dataFmt=dt?fmtDate(dt):(dataDoc||new Date().toLocaleDateString('pt-BR'));
  html += impSecao('8','Do encerramento',
    '<p style="text-align:justify;margin:0 0 8pt">Ressalva-se que o enquadramento ora proposto poderá ser adequado por ocasião do Relatório Final, à luz da defesa, uma vez que o indiciado se defende dos fatos e não da sua capitulação.</p>' +
    '<p style="text-align:justify;margin:0 0 8pt">Intime-se a pessoa jurídica indiciada para, no prazo de 30 (trinta) dias contado da intimação desta Nota de Indiciação, apresentar defesa escrita (art. 17 da IN CGU nº 13/2019).</p>' +
    '<p style="text-align:center;margin-top:28pt">' + esc(p.cidade||p.unidade||'') + ', ' + esc(dataFmt) + '.</p>' +
    blocoAssinatura3(c));

  html += impRodape();
  html += '</div>';

  return html;
}'''

content = content.replace(old, new)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fase 2 (renderIndiciacao/construirTextoIndiciacao) concluída.")
