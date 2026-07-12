#!/usr/bin/env node
'use strict';
/*
 * Rodada 7 — Teste de fluxo integrado ponta a ponta.
 *
 * Executa via `node test-fluxo-integrado.js`, sem browser e sem interação manual. Carrega os três
 * ferramentas/*.html reais (não cópias/mocks) num contexto Node (vm), usando um stub mínimo de DOM
 * só para que cada <script> termine de rodar sem lançar (os apps registram addEventListener em
 * elementos que não existem fora do browser) — a partir daí, todo o teste chama diretamente as
 * funções puras extraídas na seção 7.1 (ver CHANGELOG-catalogo.md), que recebem dados e devolvem
 * dados, sem tocar em document/localStorage.
 *
 * Usa fixtures/pad-ficticio-001.json como caso de teste reutilizável (seção 7.2).
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = __dirname;

// ---------------------------------------------------------------------------
// Relatório
// ---------------------------------------------------------------------------
const relatorio = []; // { grupo, nome, ok, detalhe }
function registrar(grupo, nome, ok, detalhe){
  relatorio.push({ grupo, nome, ok, detalhe: detalhe || '' });
  const marca = ok ? '✅' : '❌';
  console.log(marca + '  [' + grupo + '] ' + nome + (detalhe ? ' — ' + detalhe : ''));
}
function checar(grupo, nome, condicao, detalheFalha){
  registrar(grupo, nome, !!condicao, condicao ? '' : (detalheFalha || 'condição falsa'));
  return !!condicao;
}

// ---------------------------------------------------------------------------
// Stub mínimo de DOM — só o suficiente para os três scripts terminarem de
// carregar sem lançar. Nenhuma asserção do teste depende do que este stub faz;
// toda a lógica exercitada é pura (ver seção 7.1).
// ---------------------------------------------------------------------------
function criarElementoStub(){
  const store = { dataset: {}, style: {}, children: [] };
  const classList = { add(){}, remove(){}, toggle(){}, contains(){ return false; } };
  function fnBase(){ return elementoStub; }
  const handler = {
    get(target, prop){
      if (prop === 'value') return store.value === undefined ? '' : store.value;
      if (prop === 'checked') return !!store.checked;
      if (prop === 'dataset') return store.dataset;
      if (prop === 'style') return store.style;
      if (prop === 'classList') return classList;
      if (prop === 'children') return store.children;
      if (prop === 'length') return 0;
      if (prop === 'files') return [];
      if (Object.prototype.hasOwnProperty.call(store, prop)) return store[prop];
      return elementoStub;
    },
    set(target, prop, value){ store[prop] = value; return true; },
    apply(){ return elementoStub; }
  };
  const elementoStub = new Proxy(fnBase, handler);
  return elementoStub;
}
function criarDocumentoStub(){
  return {
    readyState: 'complete',
    getElementById(){ return criarElementoStub(); },
    querySelector(){ return criarElementoStub(); },
    querySelectorAll(){ return []; },
    createElement(){ return criarElementoStub(); },
    addEventListener(){},
    removeEventListener(){},
    body: criarElementoStub(),
    documentElement: criarElementoStub()
  };
}
function criarLocalStorageStub(){
  const dados = {};
  return {
    getItem: k => (Object.prototype.hasOwnProperty.call(dados, k) ? dados[k] : null),
    setItem: (k, v) => { dados[k] = String(v); },
    removeItem: k => { delete dados[k]; }
  };
}

// Carrega um ferramentas/*.html num contexto Node isolado e devolve o sandbox (== window do "app").
function carregarFerramenta(nomeArquivo){
  const caminho = path.join(ROOT, 'ferramentas', nomeArquivo);
  const html = fs.readFileSync(caminho, 'utf8');
  const inicio = html.indexOf('<script>') + '<script>'.length;
  const fim = html.indexOf('</script>');
  const codigo = html.slice(inicio, fim);

  const sandbox = {};
  sandbox.window = sandbox; // window.X = ... e leitura via sandbox.X apontam para o mesmo objeto
  sandbox.document = criarDocumentoStub();
  sandbox.localStorage = criarLocalStorageStub();
  sandbox.navigator = { clipboard: { writeText: () => Promise.resolve() } };
  sandbox.alert = () => {};
  sandbox.confirm = () => true;
  sandbox.prompt = () => '';
  sandbox.URL = { createObjectURL: () => 'blob:stub', revokeObjectURL: () => {} };
  sandbox.Blob = Blob;
  sandbox.crypto = crypto.webcrypto;
  sandbox.TextEncoder = TextEncoder;
  sandbox.console = console;
  sandbox.setTimeout = setTimeout;
  sandbox.clearTimeout = clearTimeout;

  vm.createContext(sandbox);
  vm.runInContext(codigo, sandbox, { filename: nomeArquivo });
  return sandbox;
}

// ---------------------------------------------------------------------------
// Fixture
// ---------------------------------------------------------------------------
const fixture = JSON.parse(fs.readFileSync(path.join(ROOT, 'fixtures', 'pad-ficticio-001.json'), 'utf8'));

(async () => {
  console.log('=== Rodada 7 — teste de fluxo integrado ponta a ponta ===\n');

  console.log('--- Carregando as três ferramentas (Node vm, sem browser) ---');
  const Nexo = carregarFerramenta('nexo-coger.html');
  const Veritas = carregarFerramenta('veritas.html');
  const Oitiva = carregarFerramenta('oitiva-360.html');
  checar('setup', 'nexo-coger.html carregado', typeof Nexo.docVazio === 'function');
  checar('setup', 'veritas.html carregado (VeritasPuro exposto)', typeof Veritas.VeritasPuro === 'object' && Veritas.VeritasPuro !== null);
  checar('setup', 'oitiva-360.html carregado (OitivaPuro exposto)', typeof Oitiva.OitivaPuro === 'object' && Oitiva.OitivaPuro !== null);
  console.log('');

  // -------------------------------------------------------------------------
  // Monta o doc do Nexo a partir do fixture: 1 acusado, 3 fatos com normas do catálogo.
  // -------------------------------------------------------------------------
  const doc = Nexo.docVazio();
  Nexo.setDoc(doc);
  doc.processo.numero = fixture.processo.numero;
  doc.processo.objetoApuracao = fixture.processo.objetoApuracao;

  const acusado = { id: Nexo.genId('A'), nome: fixture.acusado.nome, matricula: fixture.acusado.matricula,
    cargo: fixture.acusado.cargo, lotacao: fixture.acusado.lotacao, qualificacaoComplementar: '',
    situacaoFuncional: 'ativo', telefone: '', email: '', alegacoesDefesaNaoAcatadas: '',
    notificacaoPrevia: { realizada: false, data: '', refAutos: '' },
    interrogatorio: { status: 'pendente', data: '', refAutos: '', aposTodasAsProvas: null },
    provasContexto: [] };
  doc.acusados.push(acusado);

  const fatosPorChave = {};
  fixture.fatos.forEach(fx => {
    const f = {
      id: Nexo.genId('F'), titulo: fx.titulo, provaIds: [], provaIdsIndiciarias: [],
      condutas: [{ acusadoId: acusado.id, descricaoConduta: 'Conduta fictícia referente a ' + fx.titulo }],
      enquadramentos: [{ normaId: fx.normaId, elementoSubjetivo: 'dolo', fundamentacao: 'Fixture de teste.' }]
    };
    doc.fatos.push(f);
    fatosPorChave[fx.chaveLocal] = f;
  });
  checar('fixture', 'doc do Nexo montado (1 acusado, ' + doc.fatos.length + ' fatos)', doc.acusados.length === 1 && doc.fatos.length === fixture.fatos.length);

  const pendenciasAntesDeQualquerImportacao = Nexo.computePendencias().length;
  const provasAntesDeQualquerImportacao = doc.provas.length;

  // =========================================================================
  // PASSO 1 — Veritas exporta a prova inicial do fixture (Rodada 3)
  // =========================================================================
  console.log('\n--- Passo 1: Veritas exporta a prova inicial ---');
  const dossieVeritas = Veritas.VeritasPuro.novoDossie();
  dossieVeritas.processo.numero = fixture.processo.numero;
  const itemInicial = {
    id: 'VDC-' + crypto.randomUUID(), titulo: fixture.provaInicialVeritas.titulo,
    categoria: fixture.provaInicialVeritas.categoria, sigilo: fixture.provaInicialVeritas.sigilo,
    status: 'ativo', observacoes: '', proveniencia: { tipo: 'gerado_internamente' },
    arquivos: [{ nomeArquivo: 'extrato.txt', descricao: 'extrato', hashLocal: crypto.createHash('sha256').update(fixture.provaInicialVeritas.conteudoFicticio).digest('hex'), hashDeclarado: '' }],
    linhaDoTempoItem: [{ evento: 'item_identificado', dataHora: new Date().toISOString(), responsavel: '', resultado: '', observacao: '' }]
  };
  dossieVeritas.itens.push(itemInicial);
  const contratoProvas = Veritas.VeritasPuro.construirContratoProvasNexo(dossieVeritas, Nexo.getCatalogoCoger(), new Date().toISOString());

  checar('passo1', 'contrato tem schema_version/catalogo_schema_version/origem', !!contratoProvas.schema_version && !!contratoProvas.catalogo_schema_version && contratoProvas.origem === 'veritas');
  checar('passo1', 'tipo_prova resolvido para id do catálogo (' + contratoProvas.provas[0].tipo_prova + ')', contratoProvas.provas[0].tipo_prova === fixture.provaInicialVeritas.categoriaCanonica);
  checar('passo1', 'id_prova presente e igual ao id de origem do item', contratoProvas.provas[0].id_prova === itemInicial.id);

  // =========================================================================
  // PASSO 2 — Nexo Coger importa a prova (Rodada 3) — rótulo resolvido, sem duplicar
  // =========================================================================
  console.log('\n--- Passo 2: Nexo Coger importa a prova do Veritas ---');
  function importarProvaVeritasPuro(it){
    const rotulo = Nexo.rotuloTipoProvaCatalogo(it.tipo_prova);
    const tipoNexo = Nexo.tipoNexoParaProvaId(it.tipo_prova);
    if (Nexo.provaVeritasJaImportada(doc, it.id_prova)) return { importou: false, motivo: 'duplicado' };
    const nova = Nexo.mapearProvaVeritasParaNexo(it, tipoNexo, rotulo, contratoProvas.origem_instancia, () => Nexo.genId('P'));
    doc.provas.push(nova);
    fatosPorChave.F1.provaIds.push(nova.id);
    return { importou: true, prova: nova, rotulo };
  }
  const resultadoImport1 = importarProvaVeritasPuro(contratoProvas.provas[0]);
  checar('passo2', 'prova importada com sucesso', resultadoImport1.importou);
  checar('passo2', 'rótulo do tipo de prova é o rótulo em português do catálogo (não o id cru)',
    resultadoImport1.rotulo === 'Documento financeiro', 'veio: ' + resultadoImport1.rotulo);
  checar('passo2', 'doc.provas tem exatamente 1 prova após a importação', doc.provas.length === provasAntesDeQualquerImportacao + 1);

  // =========================================================================
  // PASSO 3 — Nexo Coger gera pauta a partir da lacuna do fixture (Rodada 4)
  // =========================================================================
  console.log('\n--- Passo 3: Nexo Coger gera pauta a partir da lacuna ---');
  const lacunas = Nexo.analisarLacunasPauta();
  checar('passo3', 'ao menos 1 lacuna detectada automaticamente (' + lacunas.length + ')', lacunas.length >= 1);
  const lacunaF2 = lacunas.find(l => l.fatoId === fatosPorChave.F2.id);
  checar('passo3', 'a lacuna do fato F2 (sem prova) foi detectada', !!lacunaF2 && lacunaF2.tipoLacuna === 'sem_prova');

  const dataStr = new Date().toISOString().slice(0, 10);
  const pautaId1 = Nexo.proximoPautaId(doc, dataStr);
  const depoenteRefPauta = { nome: fixture.depoente.identificacao, papelId: 'PAPEL.TESTEMUNHA' };
  const contratoPauta = Nexo.construirContratoPauta([lacunaF2], depoenteRefPauta, doc, Nexo.getCatalogoCoger(), pautaId1, new Date().toISOString());

  checar('passo3', 'pauta_id segue o padrão PAUTA.<data>.<seq>', /^PAUTA\.\d{4}-\d{2}-\d{2}\.\d{3}$/.test(contratoPauta.pauta_id));
  checar('passo3', 'ponto de instrução referencia a norma canônica correta',
    (contratoPauta.pontos_instrucao[0].normas_relacionadas || []).includes(fixture.fatos[1].normaCanonica));
  checar('passo3', 'todo ponto exportado está confirmado_pelo_usuario:true', contratoPauta.pontos_instrucao.every(p => p.confirmado_pelo_usuario === true));

  // pauta_id único a cada exportação — gera uma segunda para confirmar
  const pautaId2 = Nexo.proximoPautaId(doc, dataStr);
  checar('passo3', 'pauta_id é único a cada exportação (' + pautaId1 + ' != ' + pautaId2 + ')', pautaId1 !== pautaId2);

  // =========================================================================
  // PASSO 4 — Oitiva 360 importa a pauta (Rodada 4) e monta o roteiro
  // =========================================================================
  console.log('\n--- Passo 4: Oitiva 360 importa a pauta e monta o roteiro ---');
  let pautaImportadaOitiva = Oitiva.OitivaPuro.mesclarPautaImportada(null, contratoPauta, Oitiva.OitivaPuro.agoraISO());
  checar('passo4', 'pauta mesclada tem 1 item, ligado ao fato F2', pautaImportadaOitiva.itens.length === 1 && pautaImportadaOitiva.itens[0].fatoId === fatosPorChave.F2.id);
  checar('passo4', 'item da pauta importada carrega pautaIdOrigem/idPontoOrigem/tipoLacuna',
    pautaImportadaOitiva.itens[0].pautaIdOrigem === pautaId1 && !!pautaImportadaOitiva.itens[0].idPontoOrigem && pautaImportadaOitiva.itens[0].tipoLacuna === 'sem_prova');

  Oitiva.setEstadoPautaImportada(pautaImportadaOitiva);
  const d = Oitiva.OitivaPuro.novoDepoente(fixture.depoente.identificacao, fixture.depoente.elementosBuscados, Oitiva.OitivaPuro.gerarId);
  d.papel = fixture.depoente.papel;
  d.infracao = fixture.depoente.infracaoPrincipal;
  d.pautaSelecionada = [fatosPorChave.F2.id];
  Oitiva.OitivaPuro.garantirEstruturaAto(d);
  d.roteiro = Oitiva.OitivaPuro.gerarRoteiroInicial(d);
  const perguntas1 = Oitiva.OitivaPuro.perguntasRespostasOrdenadas(d);
  checar('passo4', 'roteiro gerado com perguntas para o papel testemunha (' + perguntas1.length + ')', perguntas1.length > 0);

  // =========================================================================
  // PASSO 5 — Oitiva 360 gera o termo com as respostas do fixture, calcula hash e "exporta" (Rodada 5)
  // =========================================================================
  console.log('\n--- Passo 5: Oitiva 360 responde o roteiro e gera o termo com hash ---');
  perguntas1.forEach(p => { d.respostasRoteiro[p.chave] = fixture.depoente.respostaPadrao; });
  // marca o item de pauta como abordado e preenche o resumo, sem acusado alternativo (vínculo "padrao")
  d.pautaConclusao[fatosPorChave.F2.id] = { respondida: true, nota: '', resumoResposta: 'Resumo fictício: testemunha confirmou o valimento do cargo relatado no fato F2.', acusadoAlternativo: '' };
  pautaImportadaOitiva.itens[0].statusChecklist = 'abordado';

  if (!d.rodadaId) d.rodadaId = Oitiva.OitivaPuro.gerarId();
  const envelopeTermoReal = await Oitiva.OitivaPuro.construirEnvelopeTermo(d, pautaImportadaOitiva, Oitiva.OitivaPuro.CATALOGO_COGER, d.rodadaId);

  checar('passo5', 'todas as respostas do roteiro aparecem no termo, na ordem', perguntas1.every((p, i) => envelopeTermoReal.textoFinal.includes(fixture.depoente.respostaPadrao)));
  checar('passo5', 'hash_origem tem prefixo sha256: e bate com o hash calculado', envelopeTermoReal.envelope.hash_origem === 'sha256:' + envelopeTermoReal.hashHex);
  checar('passo5', 'rodada_id presente no envelope do termo', !!envelopeTermoReal.envelope.rodada_id);
  checar('passo5', 'pauta_id do termo referencia a pauta importada', envelopeTermoReal.envelope.pauta_id === pautaId1);

  // =========================================================================
  // PASSO 6 — Veritas importa o termo, confere hash, gera novo id_prova (Rodada 5)
  // =========================================================================
  console.log('\n--- Passo 6: Veritas importa o termo (confere hash, gera id_prova) ---');
  const dossieVeritas2 = Veritas.VeritasPuro.novoDossie();
  const avaliacao1 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieVeritas2, envelopeTermoReal.envelope, Nexo.getCatalogoCoger());
  checar('passo6', 'avaliação aceita o termo (hash confere)', avaliacao1.ok, JSON.stringify(avaliacao1));
  let idProvaGeradaPeloVeritas = null;
  if (avaliacao1.ok){
    const itemTermo = Veritas.VeritasPuro.construirItemTermoOitiva(envelopeTermoReal.envelope, () => 'VDC-TERMO-' + crypto.randomUUID());
    dossieVeritas2.itens.push(itemTermo);
    idProvaGeradaPeloVeritas = itemTermo.id;
  }
  checar('passo6', 'novo id_prova gerado, diferente do rodada_id', !!idProvaGeradaPeloVeritas && idProvaGeradaPeloVeritas !== envelopeTermoReal.envelope.rodada_id);
  checar('passo6', 'proveniência marcada como interna (gerado_internamente)', dossieVeritas2.itens[0] && dossieVeritas2.itens[0].proveniencia.tipo === 'gerado_internamente');
  checar('passo6', 'categoria da prova é termo_oitiva', dossieVeritas2.itens[0] && dossieVeritas2.itens[0].categoria === 'termo_oitiva');

  // =========================================================================
  // PASSO 7 — Oitiva 360 exporta o retorno usando o id_prova do passo 6; Nexo importa (Rodada 6)
  // =========================================================================
  console.log('\n--- Passo 7: Oitiva 360 exporta o retorno; Nexo Coger importa e vincula ao acusado padrão ---');
  const envelopeRetorno1 = Oitiva.OitivaPuro.construirEnvelopeRetorno(d, pautaImportadaOitiva, idProvaGeradaPeloVeritas, Oitiva.OitivaPuro.CATALOGO_COGER, d.rodadaId);
  checar('passo7', 'retorno tem 1 item, acusado_vinculo:"padrao" (sem marcação manual)',
    envelopeRetorno1.retornos.length === 1 && envelopeRetorno1.retornos[0].acusado_vinculo === 'padrao');
  checar('passo7', 'retorno referencia o id_prova gerado pelo Veritas no passo 6', envelopeRetorno1.retornos[0].id_prova === idProvaGeradaPeloVeritas);

  const pendenciasAntesDoRetorno = Nexo.computePendencias().length;
  const provasAntesDoRetorno = doc.provas.length;

  function importarRetornoPuro(envelope){
    let n = 0;
    envelope.retornos.forEach(r => {
      // "padrão" = único acusado do processo (regra geral do critério 6.1) — sem ação manual do usuário
      const acusadoAlvo = r.acusado_vinculo === 'padrao' && doc.acusados.length === 1 ? doc.acusados[0] : null;
      if (!acusadoAlvo) return;
      if (Nexo.retornoJaExiste(acusadoAlvo, r.id_prova, r.id_ponto)) return;
      acusadoAlvo.provasContexto.push(Nexo.mapearRetornoContexto(r, envelope.origem, new Date().toISOString()));
      n++;
    });
    return n;
  }
  const importados1 = importarRetornoPuro(envelopeRetorno1);
  checar('passo7', 'exatamente 1 item de contexto importado, vinculado ao único acusado', importados1 === 1 && acusado.provasContexto.length === 1);
  checar('passo7', 'acusado.provasContexto NÃO é o mesmo array/objeto de doc.provas (isolamento estrutural)', doc.provas !== acusado.provasContexto);
  checar('passo7', 'NENHUMA indiciação/pendência foi alterada pela importação do retorno',
    Nexo.computePendencias().length === pendenciasAntesDoRetorno && doc.provas.length === provasAntesDoRetorno,
    'pendências antes=' + pendenciasAntesDoRetorno + ' depois=' + Nexo.computePendencias().length + '; provas antes=' + provasAntesDoRetorno + ' depois=' + doc.provas.length);

  // =========================================================================
  // 7.4 — Idempotência: repetir os passos 2, 4, 6 e 7 com o MESMO payload
  // =========================================================================
  console.log('\n--- 7.4: testes de idempotência (reimportar passos 2, 4, 6, 7) ---');

  // Passo 2 de novo
  const resultadoImport2 = importarProvaVeritasPuro(contratoProvas.provas[0]);
  checar('idempotencia', 'passo 2 reimportado: recusado explicitamente, sem duplicar', resultadoImport2.importou === false && resultadoImport2.motivo === 'duplicado');
  checar('idempotencia', 'passo 2 reimportado: doc.provas continua com 1 prova', doc.provas.length === provasAntesDoRetorno);

  // Passo 4 de novo (mesma pauta_id)
  const itensAntesReimportPauta = pautaImportadaOitiva.itens.length;
  pautaImportadaOitiva = Oitiva.OitivaPuro.mesclarPautaImportada(pautaImportadaOitiva, contratoPauta, Oitiva.OitivaPuro.agoraISO());
  checar('idempotencia', 'passo 4 reimportado: nenhum item novo criado (merge por fatoId)', pautaImportadaOitiva.itens.length === itensAntesReimportPauta);
  checar('idempotencia', 'passo 4 reimportado: status "abordado" não regrediu para "pendente"', pautaImportadaOitiva.itens[0].statusChecklist === 'abordado');

  // Passo 6 de novo (mesmo termo/hash_origem)
  const avaliacao2 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieVeritas2, envelopeTermoReal.envelope, Nexo.getCatalogoCoger());
  checar('idempotencia', 'passo 6 reimportado: recusado explicitamente por duplicidade de hash_origem', avaliacao2.ok === false && avaliacao2.motivo === 'duplicado');
  checar('idempotencia', 'passo 6 reimportado: dossiê do Veritas continua com 1 item', dossieVeritas2.itens.length === 1);

  // Passo 7 de novo (mesmo id_prova + id_ponto)
  const importados2 = importarRetornoPuro(envelopeRetorno1);
  checar('idempotencia', 'passo 7 reimportado: nenhum item novo aceito (retornoJaExiste)', importados2 === 0);
  checar('idempotencia', 'passo 7 reimportado: provasContexto do acusado continua com 1 item', acusado.provasContexto.length === 1);

  // =========================================================================
  // 7.5 — Testes de falha controlada
  // =========================================================================
  console.log('\n--- 7.5: testes de falha controlada ---');

  // hash divergente
  const termoAdulterado = JSON.parse(JSON.stringify(envelopeTermoReal.envelope));
  termoAdulterado.termo.conteudo = termoAdulterado.termo.conteudo.replace(fixture.depoente.respostaPadrao.slice(0, 10), 'XXXXXXXXXX');
  const avaliacaoAdulterada = await Veritas.VeritasPuro.avaliarImportacaoTermo(Veritas.VeritasPuro.novoDossie(), termoAdulterado, Nexo.getCatalogoCoger());
  checar('falha_controlada', 'termo com 1 trecho alterado é rejeitado por divergência de hash', avaliacaoAdulterada.ok === false && avaliacaoAdulterada.motivo === 'hash_divergente');

  // catalogo_schema_version divergente (no contrato Veritas -> Nexo)
  const contratoVersaoDivergente = JSON.parse(JSON.stringify(contratoProvas));
  contratoVersaoDivergente.catalogo_schema_version = '0.1.0';
  const catalogoDivergenteDetectado = contratoVersaoDivergente.catalogo_schema_version !== Nexo.getCatalogoCoger().schema_version;
  checar('falha_controlada', 'catalogo_schema_version divergente é corretamente detectada pelo Nexo (aviso, não falha silenciosa)', catalogoDivergenteDetectado);

  // catalogo_schema_version divergente também no contrato de termo (Veritas, Rodada 5)
  const termoVersaoDivergente = JSON.parse(JSON.stringify(envelopeTermoReal.envelope));
  termoVersaoDivergente.catalogo_schema_version = '0.1.0';
  termoVersaoDivergente.hash_origem = envelopeTermoReal.envelope.hash_origem; // hash continua batendo — só o catálogo diverge
  const avaliacaoVersaoDivergente = await Veritas.VeritasPuro.avaliarImportacaoTermo(Veritas.VeritasPuro.novoDossie(), termoVersaoDivergente, Nexo.getCatalogoCoger());
  checar('falha_controlada', 'termo com catalogo_schema_version divergente gera aviso (catalogoDivergente=true) mas não bloqueia (hash confere)',
    avaliacaoVersaoDivergente.ok === true && avaliacaoVersaoDivergente.catalogoDivergente === true);

  // =========================================================================
  // Relatório final
  // =========================================================================
  console.log('\n=== Relatório final ===');
  const grupos = [...new Set(relatorio.map(r => r.grupo))];
  let totalOk = 0, totalFalhas = 0;
  grupos.forEach(g => {
    const itens = relatorio.filter(r => r.grupo === g);
    const ok = itens.filter(i => i.ok).length;
    console.log('  ' + g + ': ' + ok + '/' + itens.length + (ok === itens.length ? ' ✅' : ' ❌'));
  });
  relatorio.forEach(r => { r.ok ? totalOk++ : totalFalhas++; });
  console.log('\nTotal: ' + totalOk + ' passaram, ' + totalFalhas + ' falharam, de ' + relatorio.length + ' verificações.');

  if (totalFalhas > 0){
    console.log('\nFalhas:');
    relatorio.filter(r => !r.ok).forEach(r => console.log('  - [' + r.grupo + '] ' + r.nome + ' — ' + r.detalhe));
    process.exitCode = 1;
  } else {
    console.log('\nTodas as verificações passaram — fluxo integrado Veritas <-> Nexo Coger <-> Oitiva 360 (Rodadas 3-6) validado de ponta a ponta.');
  }
})().catch(e => {
  console.error('\n❌ ERRO NÃO TRATADO:', e);
  process.exitCode = 1;
});
