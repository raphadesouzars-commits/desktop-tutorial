// Aprende, dos temas e dos descritores dos pareceres reais da COGER, os termos que indicam cada atividade, mede o ganho
// por validação cruzada (5 partes) e grava parecer/vocabulario_coger.json (só termos; nenhum nome de pessoa).
// Uso: node parecer/avaliacao/treinar_vocabulario.js <casos.json> [--gravar]
//   casos.json = [{tema, esperado (id da atividade), texto}]  (arquivo local, com nomes de pessoas: NÃO versionar)
const {chromium} = require('playwright'); const fs = require('fs'); const path = require('path');
const RAIZ = path.resolve(__dirname, '..', '..');
(async () => {
  const casos = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')).filter(c => c.esperado);
  const temas = Object.entries(JSON.parse(fs.readFileSync(path.join(__dirname, 'temas_coger.json'), 'utf8'))).filter(([k, v]) => v).map(([k, v]) => ({texto: k, esperado: v, tema: k}));
  const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
  await p.goto('file://' + path.join(RAIZ, 'gerador-parecer-conflito.html'));
  const aprender = (treino, temas) => p.evaluate(([treino, temas]) => {
    // só entram termos que já existem nos modelos ou nas ementas públicas da CGU (evita nomes de pessoas)
    const permitido = new Set(); MODELOS.forEach(m => { tokensJs([m.nome, m.descricao, (m.palavrasChave || []).join(' ')].join(' ')).forEach(t => permitido.add(t)); m.variantes.forEach(v => tokensJs([v.rotulo, v.quandoUsar].join(' ')).forEach(t => permitido.add(t))); });
    (PRECEDENTES.itens || []).forEach(x => tokensJs(x.x.slice(0, 300)).forEach(t => permitido.add(t)));
    const cm = {}, ct = {};
    const soma = (id, toks, peso) => { for (const t of new Set(toks)){ if (t.length < 4 || /^\d+$/.test(t)) continue; (cm[id] = cm[id] || {})[t] = (cm[id][t] || 0) + peso; ct[t] = (ct[t] || 0) + peso; } };
    treino.forEach(c => soma(c.esperado, tokensJs(c.texto).filter(t => permitido.has(t)), 1));
    temas.forEach(c => soma(c.esperado, tokensJs(c.texto), 2));   // os nomes das pastas de tema são confiáveis
    const out = {};
    for (const id in cm) for (const t in cm[id]){ const n = cm[id][t], pr = n / ct[t]; if (n >= 2 && pr >= 0.6){ (out[id] = out[id] || {})[t] = Math.round(pr * Math.log(1 + n) * 100) / 100; } }
    return out;
  }, [treino, temas]);
  const medir = (conj, vocab, pesos) => p.evaluate(([conj, vocab, pesos]) => { VOCAB = vocab; if (pesos) Object.assign(PESOS_REC, pesos); let n1 = 0, n3 = 0;
    for (const c of conj){ const r = pontuar(c.texto, c.texto).map(x => x.m.id); if (r[0] === c.esperado) n1++; if (r.slice(0, 3).includes(c.esperado)) n3++; } return {n: conj.length, n1, n3}; }, [conj, vocab, pesos]);
  const pc = (x, n) => (100 * x / n).toFixed(1) + '%';
  const base = await medir(casos, {}, null);
  console.log(`sem vocabulário:   top1 ${pc(base.n1, base.n)}  top3 ${pc(base.n3, base.n)}  (n=${base.n})`);
  // validação cruzada: aprende em 4/5 e mede no 1/5 que não viu (os temas das pastas entram no treino)
  let t1 = 0, t3 = 0;
  for (let f = 0; f < 5; f++){ const teste = casos.filter((_, i) => i % 5 === f), treino = casos.filter((_, i) => i % 5 !== f); const r = await medir(teste, await aprender(treino, temas), null); t1 += r.n1; t3 += r.n3; }
  console.log(`com vocabulário (validação cruzada, casos não vistos): top1 ${pc(t1, casos.length)}  top3 ${pc(t3, casos.length)}`);
  const final = await aprender(casos, temas);
  const rt = await medir(temas, final, null); console.log(`temas das pastas (vistos no treino): top1 ${pc(rt.n1, rt.n)}  top3 ${pc(rt.n3, rt.n)}`);
  const nTermos = Object.values(final).reduce((s, o) => s + Object.keys(o).length, 0);
  console.log(`vocabulário final: ${Object.keys(final).length} atividades, ${nTermos} termos`);
  if (process.argv.includes('--gravar')){
    fs.writeFileSync(path.join(RAIZ, 'parecer', 'vocabulario_coger.json'), JSON.stringify({origem: 'temas e descritores de ' + casos.length + ' pareceres da COGER; só termos presentes nos modelos ou nas ementas públicas da CGU', validacao_cruzada: {n: casos.length, top1_sem: base.n1, top3_sem: base.n3, top1_com: t1, top3_com: t3}, termos: final}, null, 1));
    console.log('gravado em parecer/vocabulario_coger.json');
  }
  await b.close();
})();
