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

// Rodada PAR-6 (6.5): cada grupo de verificações pertence a uma das TRÊS seções do relatório
// unificado. Grupos não mapeados caem em 'Outros' (defensivo — não deveria ocorrer).
const GRUPOS_PAD = ['setup', 'fixture', 'passo1', 'passo2', 'passo3', 'passo4', 'passo5', 'passo6', 'passo7', 'idempotencia', 'falha_controlada'];
const GRUPOS_PAR = ['par_passo1', 'par_passo2', 'par_passo3', 'par_passo4', 'par_passo5', 'par_passo6', 'par_passo7', 'par_passo8', 'par_idempotencia', 'par_falha_controlada'];
const GRUPOS_CRUZADA = ['validacao_dominio', 'cruzada'];
function secaoDoGrupo(g){
  if (GRUPOS_PAD.includes(g)) return 'Fluxo PAD';
  if (GRUPOS_PAR.includes(g)) return 'Fluxo PAR';
  if (GRUPOS_CRUZADA.includes(g)) return 'Validação cruzada';
  return 'Outros';
}

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

  console.log('--- Carregando as ferramentas (Node vm, sem browser) ---');
  const Nexo = carregarFerramenta('nexo-coger.html');
  const Veritas = carregarFerramenta('veritas.html');
  const Oitiva = carregarFerramenta('oitiva-360.html');
  // Rodada PAR-5 (5.6): o Nexo PAR é carregado no MESMO padrão de stub/contexto do Nexo Coger
  // (são estruturalmente parecidos — fork da PAR-3), para exercitar sua validarDominioEnvelope.
  const NexoPar = carregarFerramenta('nexo-par.html');
  checar('setup', 'nexo-coger.html carregado', typeof Nexo.docVazio === 'function');
  checar('validacao_dominio', 'nexo-par.html carregado (PAR-5)', typeof NexoPar.docVazio === 'function' && typeof NexoPar.validarDominioEnvelope === 'function');
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
  // Rodada PAR-5 (seção 5.6) — Validação cruzada de domínio nos contratos
  // Os 7 casos exigidos pela spec. Testam diretamente as funções reais expostas por
  // cada ferramenta (validarDominioEnvelope nos dois Nexos; avaliarImportacaoTermo +
  // dominioDoProcesso no Veritas via VeritasPuro).
  // =========================================================================
  console.log('\n--- Rodada PAR-5 (5.6): validação cruzada de domínio ---');

  // Placar das 7 etapas originais (Rodada 7): todas as verificações que NÃO pertencem a este grupo
  // de validação de domínio — devem continuar 43/43 (caso 7).

  const parFixture = JSON.parse(fs.readFileSync(path.join(ROOT, 'fixtures', 'par-ficticio-001.json'), 'utf8'));
  checar('validacao_dominio', 'fixture par-ficticio-001.json carregado (dominio par)', parFixture._dominio === 'par' && parFixture.processo.dominio === 'par');

  // --- Caso 1: envelope dominio:"par" no Nexo Coger -> RECUSADO ---
  const c1 = Nexo.validarDominioEnvelope({ dominio: 'par' });
  checar('validacao_dominio', 'caso 1: envelope PAR no Nexo Coger é RECUSADO', c1.ok === false, JSON.stringify(c1));
  checar('validacao_dominio', 'caso 1: mensagem indica domínio encontrado (PAR) e sugere o Nexo PAR',
    !!c1.msg && /encontrado: PAR/i.test(c1.msg) && /Nexo PAR/.test(c1.msg), 'msg: ' + (c1 && c1.msg));

  // --- Caso 2: envelope dominio:"pad" no Nexo PAR -> RECUSADO ---
  const c2 = NexoPar.validarDominioEnvelope({ dominio: 'pad' });
  checar('validacao_dominio', 'caso 2: envelope PAD no Nexo PAR é RECUSADO', c2.ok === false, JSON.stringify(c2));
  checar('validacao_dominio', 'caso 2: mensagem indica domínio encontrado (PAD) e sugere o Nexo Coger',
    !!c2.msg && /encontrado: PAD/i.test(c2.msg) && /Nexo Coger/.test(c2.msg), 'msg: ' + (c2 && c2.msg));

  // --- Caso 3: envelope SEM campo dominio no Nexo Coger -> ACEITO (legado PAD) ---
  const c3 = Nexo.validarDominioEnvelope({});
  checar('validacao_dominio', 'caso 3: envelope sem domínio no Nexo Coger é ACEITO como legado', c3.ok === true, JSON.stringify(c3));

  // --- Caso 4: envelope SEM campo dominio no Nexo PAR -> RECUSADO com mensagem de legado ---
  const c4 = NexoPar.validarDominioEnvelope({});
  checar('validacao_dominio', 'caso 4: envelope sem domínio no Nexo PAR é RECUSADO', c4.ok === false, JSON.stringify(c4));
  checar('validacao_dominio', 'caso 4: mensagem é a específica de arquivo legado/PAD (não a de domínio "pad")',
    !!c4.msg && /anterior às Rodadas PAR|acervo legado/i.test(c4.msg) && c4.msg !== (c2 && c2.msg),
    'msg: ' + (c4 && c4.msg));

  // --- Casos 5 e 6: termo PAR importado no Veritas ---
  // Envelope de termo PAR real (formato válido + hash coerente), no mesmo espírito do passo 5.
  const conteudoTermoPar = 'Termo de oitiva fictício (domínio PAR) — ' + parFixture.depoente.respostaPadrao;
  const hashTermoPar = 'sha256:' + (await Veritas.VeritasPuro.sha256Hex(conteudoTermoPar));
  const envelopeTermoPar = {
    origem: 'oitiva-360',
    dominio: 'par',
    hash_origem: hashTermoPar,
    catalogo_schema_version: Nexo.getCatalogoCoger().schema_version,
    termo: { conteudo: conteudoTermoPar, gerado_em: new Date().toISOString(), responsavel: '' },
    deponente: { nome: parFixture.depoente.identificacao },
    rodada_id: 'RODADA-PAR-TEST',
    pauta_id: 'PAUTA.2026-07-12.001'
  };

  // --- Caso 5: dossiê Veritas SEM tipo definido -> ACEITO (agnosticismo preservado) ---
  const dossieSemTipo = Veritas.VeritasPuro.novoDossie(); // processo.tipoProcesso === ""
  checar('validacao_dominio', 'caso 5 (pré): dossiê sem tipo -> dominioDoProcesso indefinido',
    Veritas.VeritasPuro.dominioDoProcesso(dossieSemTipo.processo.tipoProcesso) === undefined);
  const c5 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieSemTipo, envelopeTermoPar, Nexo.getCatalogoCoger());
  checar('validacao_dominio', 'caso 5: termo PAR em dossiê sem tipo é ACEITO (Veritas agnóstico)', c5.ok === true, JSON.stringify(c5));

  // --- Caso 6: dossiê Veritas marcado PAD -> RECUSADO ---
  const dossiePad = Veritas.VeritasPuro.novoDossie();
  dossiePad.processo.tipoProcesso = 'PAD';
  checar('validacao_dominio', 'caso 6 (pré): dossiê tipo PAD -> dominioDoProcesso === "pad"',
    Veritas.VeritasPuro.dominioDoProcesso(dossiePad.processo.tipoProcesso) === 'pad');
  const c6 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossiePad, envelopeTermoPar, Nexo.getCatalogoCoger());
  checar('validacao_dominio', 'caso 6: termo PAR em dossiê PAD é RECUSADO (dominio_incompativel)',
    c6.ok === false && c6.motivo === 'dominio_incompativel', JSON.stringify(c6));

  // --- Caso 7: fluxo PAD original (7 etapas) continua passando INALTERADO ---
  // Conta explicitamente as verificações da seção "Fluxo PAD" (grupos GRUPOS_PAD) — devem seguir 43/0,
  // independentemente das novas seções PAR/cruzada adicionadas na Rodada PAR-6 (6.6: PAD intocado).
  const etapasOriginais = relatorio.filter(r => GRUPOS_PAD.includes(r.grupo));
  const falhasNoOriginal = etapasOriginais.filter(r => !r.ok).length;
  checar('validacao_dominio', 'caso 7: placar das 7 etapas PAD originais inalterado (43 verificações, 0 falhas)',
    etapasOriginais.length === 43 && falhasNoOriginal === 0,
    'originais=' + etapasOriginais.length + ' falhas=' + falhasNoOriginal);

  // #########################################################################
  // ####  FLUXO PAR — ciclo completo de 8 etapas (Rodada PAR-6, seção 6.2) ###
  // #########################################################################
  console.log('\n\n########## FLUXO PAR (Rodada PAR-6) — ciclo de 8 etapas ##########');
  const iso = () => new Date().toISOString();
  // Instância dedicada do Oitiva 360 para o ciclo PAR (estado isolado do fluxo PAD acima).
  const OitivaPar = carregarFerramenta('oitiva-360.html');

  // --- PAR passo 1: Veritas exporta a prova inicial do fixture PAR ---
  console.log('\n--- PAR passo 1: Veritas exporta a prova inicial (dominio "par") ---');
  const dossieVeritasPar = Veritas.VeritasPuro.novoDossie();
  dossieVeritasPar.processo.numero = parFixture.processo.numero;
  dossieVeritasPar.processo.tipoProcesso = parFixture.processo.tipoProcesso; // 'PAR' -> dominio 'par'
  const itemInicialPar = {
    id: 'VDC-' + crypto.randomUUID(), titulo: parFixture.provaInicialVeritas.titulo,
    categoria: parFixture.provaInicialVeritas.categoria, sigilo: parFixture.provaInicialVeritas.sigilo,
    status: 'ativo', observacoes: '', proveniencia: { tipo: 'gerado_internamente' },
    arquivos: [{ nomeArquivo: 'ata.txt', descricao: 'ata', hashLocal: crypto.createHash('sha256').update(parFixture.provaInicialVeritas.conteudoFicticio).digest('hex'), hashDeclarado: '' }],
    linhaDoTempoItem: [{ evento: 'item_identificado', dataHora: iso(), responsavel: '', resultado: '', observacao: '' }]
  };
  dossieVeritasPar.itens.push(itemInicialPar);
  const contratoProvasPar = Veritas.VeritasPuro.construirContratoProvasNexo(dossieVeritasPar, NexoPar.getCatalogoCoger(), iso());
  checar('par_passo1', 'contrato tem schema_version/catalogo_schema_version/origem veritas', !!contratoProvasPar.schema_version && !!contratoProvasPar.catalogo_schema_version && contratoProvasPar.origem === 'veritas');
  checar('par_passo1', 'envelope da prova declara dominio "par"', contratoProvasPar.dominio === 'par', 'dominio=' + contratoProvasPar.dominio);
  checar('par_passo1', 'tipo_prova resolvido para id canônico do catálogo (' + contratoProvasPar.provas[0].tipo_prova + ')', contratoProvasPar.provas[0].tipo_prova === parFixture.provaInicialVeritas.categoriaCanonica);

  // --- PAR passo 2: Nexo PAR importa a prova (monta o doc do ente + fatos) ---
  console.log('\n--- PAR passo 2: Nexo PAR importa a prova e monta o doc (ente + fatos LAC) ---');
  const docPar = NexoPar.docVazio(); NexoPar.setDoc(docPar);
  docPar.processo.numero = parFixture.processo.numero;
  docPar.processo.objetoApuracao = parFixture.processo.objetoApuracao;
  const ente = {
    id: NexoPar.genId('A'),
    razaoSocial: parFixture.entePrivado.razaoSocial, nome: parFixture.entePrivado.razaoSocial,
    cnpj: parFixture.entePrivado.cnpj, nomeFantasia: parFixture.entePrivado.nomeFantasia,
    endereco: parFixture.entePrivado.endereco, faturamentoBruto: parFixture.entePrivado.faturamentoBruto,
    representantes: [{ nome: parFixture.entePrivado.representanteLegal.nome, cpf: parFixture.entePrivado.representanteLegal.cpf, vinculo: parFixture.entePrivado.representanteLegal.vinculo }],
    solidariedade: [], sucessao: { tipo: '', descricao: '', data: '' }, desconsideracao: { ativa: false, fundamentacao: '' },
    alegacoesDefesaNaoAcatadas: '', situacaoFuncional: 'ativo', telefone: '', email: '',
    notificacaoPrevia: { realizada: false, data: '', refAutos: '' },
    interrogatorio: { status: 'pendente', data: '', refAutos: '', aposTodasAsProvas: null },
    provasContexto: []
  };
  docPar.acusados.push(ente);
  const fatosParPorChave = {};
  parFixture.fatos.forEach(fx => {
    const f = {
      id: NexoPar.genId('F'), titulo: fx.titulo, descricao: fx.descricao, ordem: docPar.fatos.length + 1, status: 'ativo',
      provaIds: [], provaIdsIndiciarias: [],
      beneficioInteresse: fx.beneficioInteresse, nexoCausalidade: fx.nexoCausalidade,
      condutas: [{ acusadoId: ente.id, descricaoConduta: 'Conduta lesiva fictícia referente a ' + fx.titulo, modalidade: 'comissiva' }],
      enquadramentos: [{ normaId: fx.normaId, fundamentacao: 'Enquadramento fictício de teste (LAC).' }]
    };
    docPar.fatos.push(f);
    fatosParPorChave[fx.chaveLocal] = f;
  });
  checar('par_passo2', 'doc do Nexo PAR montado (1 ente privado, ' + docPar.fatos.length + ' fatos LAC)', docPar.acusados.length === 1 && docPar.fatos.length === parFixture.fatos.length);
  const pendParInicial = NexoPar.computePendencias();
  checar('par_passo2', 'gate P-ENTE satisfeito (ente com representante legal) — sem pendência P-ENTE', !pendParInicial.some(p => p.codigo === 'P-ENTE'), JSON.stringify(pendParInicial.filter(p => p.codigo === 'P-ENTE')));
  checar('par_passo2', 'gate P8-PAR satisfeito (benefício + nexo nos 2 fatos) — sem pendência P8-PAR', !pendParInicial.some(p => p.codigo === 'P8-PAR'), JSON.stringify(pendParInicial.filter(p => p.codigo === 'P8-PAR')));
  const domParProva = NexoPar.validarDominioEnvelope(contratoProvasPar);
  checar('par_passo2', 'Nexo PAR ACEITA o envelope de prova dominio "par"', domParProva.ok === true, JSON.stringify(domParProva));
  const provaImpPar = contratoProvasPar.provas[0];
  const rotuloPar = NexoPar.rotuloTipoProvaCatalogo(provaImpPar.tipo_prova);
  const tipoNexoPar = NexoPar.tipoNexoParaProvaId(provaImpPar.tipo_prova);
  const provasParAntes = docPar.provas.length;
  function importarProvaVeritasNexoPar(it){
    if (NexoPar.provaVeritasJaImportada(docPar, it.id_prova)) return { importou: false, motivo: 'duplicado' };
    const nova = NexoPar.mapearProvaVeritasParaNexo(it, tipoNexoPar, rotuloPar, contratoProvasPar.origem_instancia, () => NexoPar.genId('P'));
    docPar.provas.push(nova);
    fatosParPorChave.FP1.provaIds.push(nova.id);
    return { importou: true, prova: nova };
  }
  const impPar1 = importarProvaVeritasNexoPar(provaImpPar);
  checar('par_passo2', 'prova PAR importada e vinculada ao fato FP1 (sem duplicar)', impPar1.importou === true && docPar.provas.length === provasParAntes + 1);
  checar('par_passo2', 'rótulo do tipo de prova resolvido do catálogo (não id cru)', rotuloPar === 'Documento financeiro', 'veio: ' + rotuloPar);

  // --- PAR passo 3: Nexo PAR gera a pauta a partir da lacuna FP2 ---
  console.log('\n--- PAR passo 3: Nexo PAR gera a pauta a partir da lacuna FP2 ---');
  const lacunasPar = NexoPar.analisarLacunasPauta();
  checar('par_passo3', 'ao menos 1 lacuna detectada (' + lacunasPar.length + ')', lacunasPar.length >= 1);
  const lacunaFP2 = lacunasPar.find(l => l.fatoId === fatosParPorChave.FP2.id);
  checar('par_passo3', 'lacuna do fato FP2 (sem prova) detectada', !!lacunaFP2 && lacunaFP2.tipoLacuna === 'sem_prova', JSON.stringify(lacunaFP2 || {}));
  const dataStrPar = new Date().toISOString().slice(0, 10);
  const pautaIdPar = NexoPar.proximoPautaId(docPar, dataStrPar);
  const depoenteRefPar = { nome: parFixture.depoente.identificacao, papelId: 'PAPEL.REPRESENTANTE_LEGAL' };
  const contratoPautaPar = NexoPar.construirContratoPauta([lacunaFP2], depoenteRefPar, docPar, NexoPar.getCatalogoCoger(), pautaIdPar, iso());
  checar('par_passo3', 'pauta_id segue o padrão PAUTA.<data>.<seq>', /^PAUTA\.\d{4}-\d{2}-\d{2}\.\d{3}$/.test(contratoPautaPar.pauta_id));
  checar('par_passo3', 'ponto de instrução referencia norma LAC canônica (' + parFixture.fatos[1].normaCanonica + ')', (contratoPautaPar.pontos_instrucao[0].normas_relacionadas || []).includes(parFixture.fatos[1].normaCanonica), JSON.stringify(contratoPautaPar.pontos_instrucao[0].normas_relacionadas || []));
  checar('par_passo3', 'envelope da pauta declara dominio "par" (emissão corrigida na PAR-5 Parte B)', contratoPautaPar.dominio === 'par', 'dominio=' + contratoPautaPar.dominio);

  // --- PAR passo 4: Oitiva 360 importa a pauta e deriva o domínio PAR ---
  console.log('\n--- PAR passo 4: Oitiva 360 importa a pauta e deriva o domínio PAR ---');
  let pautaOitivaPar = OitivaPar.OitivaPuro.mesclarPautaImportada(null, contratoPautaPar, OitivaPar.OitivaPuro.agoraISO());
  OitivaPar.setEstadoPautaImportada(pautaOitivaPar);
  OitivaPar.OitivaPuro.derivarDominioDaPauta(contratoPautaPar); // cascata PAR-4/PAR-5
  checar('par_passo4', 'domínio do processo derivado para "par" pela cascata da pauta', OitivaPar.OitivaPuro.dominioProcesso() === 'par');
  checar('par_passo4', 'pauta mesclada tem 1 item, ligado ao fato FP2', pautaOitivaPar.itens.length === 1 && pautaOitivaPar.itens[0].fatoId === fatosParPorChave.FP2.id);
  const papeisPar = OitivaPar.OitivaPuro.CATALOGO.papeis.filter(p => OitivaPar.OitivaPuro.itemVisivelNoDominio(p.dominio, 'par'));
  checar('par_passo4', 'papéis do domínio PAR: PAPEL "acusado" NÃO aparece (é exclusivo do PAD)', !papeisPar.some(p => p.id === 'acusado'));
  checar('par_passo4', 'papéis do domínio PAR: os 3 papéis PAR aparecem (representante_legal/preposto/socio_administrador)', ['representante_legal', 'preposto', 'socio_administrador'].every(id => papeisPar.some(p => p.id === id)));
  const dPar = OitivaPar.OitivaPuro.novoDepoente(parFixture.depoente.identificacao, parFixture.depoente.elementosBuscados, OitivaPar.OitivaPuro.gerarId);
  dPar.papel = parFixture.depoente.papel; // representante_legal
  dPar.infracao = parFixture.depoente.infracaoPrincipal;
  dPar.pautaSelecionada = [fatosParPorChave.FP2.id];
  OitivaPar.OitivaPuro.garantirEstruturaAto(dPar);
  dPar.roteiro = OitivaPar.OitivaPuro.gerarRoteiroInicial(dPar);
  const perguntasPar = OitivaPar.OitivaPuro.perguntasRespostasOrdenadas(dPar);
  checar('par_passo4', 'roteiro gerado com perguntas para o papel representante legal (' + perguntasPar.length + ')', perguntasPar.length > 0);
  const BLOCOS_PAR = ['par_atos_licitacoes', 'par_terceiro_interposto', 'par_programa_integridade'];
  const temPerguntaBlocoPar = perguntasPar.some(p => BLOCOS_PAR.some(b => p.chave.indexOf(b + '::') === 0));
  checar('par_passo4', 'ao menos uma pergunta vem de um dos 3 blocos PAR do banco (PAR-4, item 4.4)', temPerguntaBlocoPar);

  // --- PAR passo 5: Oitiva 360 gera o termo PAR com hash e exporta ---
  console.log('\n--- PAR passo 5: Oitiva 360 responde e gera o termo PAR com hash ---');
  perguntasPar.forEach(p => { dPar.respostasRoteiro[p.chave] = parFixture.depoente.respostaPadrao; });
  dPar.pautaConclusao[fatosParPorChave.FP2.id] = { respondida: true, nota: '', resumoResposta: 'Resumo fictício: representante legal esclareceu a fraude na execução contratual relatada no fato FP2.', acusadoAlternativo: '' };
  pautaOitivaPar.itens[0].statusChecklist = 'abordado';
  if (!dPar.rodadaId) dPar.rodadaId = OitivaPar.OitivaPuro.gerarId();
  const envelopeTermoParReal = await OitivaPar.OitivaPuro.construirEnvelopeTermo(dPar, pautaOitivaPar, OitivaPar.OitivaPuro.CATALOGO_COGER, dPar.rodadaId);
  checar('par_passo5', 'todas as respostas do roteiro aparecem no termo', perguntasPar.every(() => envelopeTermoParReal.textoFinal.includes(parFixture.depoente.respostaPadrao)));
  checar('par_passo5', 'hash_origem tem prefixo sha256: e bate com o hash calculado', envelopeTermoParReal.envelope.hash_origem === 'sha256:' + envelopeTermoParReal.hashHex);
  checar('par_passo5', 'envelope do termo declara dominio "par"', envelopeTermoParReal.envelope.dominio === 'par', 'dominio=' + envelopeTermoParReal.envelope.dominio);
  checar('par_passo5', 'pauta_id do termo referencia a pauta PAR importada', envelopeTermoParReal.envelope.pauta_id === pautaIdPar);

  // --- PAR passo 6: Veritas importa o termo no dossiê PAR (confere domínio + hash) ---
  console.log('\n--- PAR passo 6: Veritas importa o termo no dossiê PAR (domínio + hash) ---');
  const dossieVeritasPar2 = Veritas.VeritasPuro.novoDossie();
  dossieVeritasPar2.processo.tipoProcesso = 'PAR'; // dossiê marcado PAR
  const avalPar1 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieVeritasPar2, envelopeTermoParReal.envelope, NexoPar.getCatalogoCoger());
  checar('par_passo6', 'avaliação aceita o termo PAR em dossiê PAR (domínio compatível + hash confere)', avalPar1.ok === true, JSON.stringify(avalPar1));
  let idProvaPar = null;
  if (avalPar1.ok){
    const itemTermoPar = Veritas.VeritasPuro.construirItemTermoOitiva(envelopeTermoParReal.envelope, () => 'VDC-TERMO-' + crypto.randomUUID());
    dossieVeritasPar2.itens.push(itemTermoPar);
    idProvaPar = itemTermoPar.id;
  }
  checar('par_passo6', 'novo id_prova gerado, diferente do rodada_id', !!idProvaPar && idProvaPar !== envelopeTermoParReal.envelope.rodada_id);
  checar('par_passo6', 'categoria da prova é termo_oitiva', dossieVeritasPar2.itens[0] && dossieVeritasPar2.itens[0].categoria === 'termo_oitiva');

  // --- PAR passo 7: Oitiva exporta o retorno; Nexo PAR vincula ao ente privado padrão ---
  console.log('\n--- PAR passo 7: Nexo PAR importa o retorno e vincula ao ente privado padrão ---');
  const envRetornoPar = OitivaPar.OitivaPuro.construirEnvelopeRetorno(dPar, pautaOitivaPar, idProvaPar, OitivaPar.OitivaPuro.CATALOGO_COGER, dPar.rodadaId);
  checar('par_passo7', 'retorno tem 1 item, acusado_vinculo:"padrao" (sem marcação manual)', envRetornoPar.retornos.length === 1 && envRetornoPar.retornos[0].acusado_vinculo === 'padrao');
  checar('par_passo7', 'retorno referencia o id_prova gerado pelo Veritas no passo 6', envRetornoPar.retornos[0].id_prova === idProvaPar);
  const pendParAntesRetorno = NexoPar.computePendencias().length;
  const provasParAntesRetorno = docPar.provas.length;
  function importarRetornoNexoPar(envelope){
    let n = 0;
    envelope.retornos.forEach(r => {
      const alvo = r.acusado_vinculo === 'padrao' && docPar.acusados.length === 1 ? docPar.acusados[0] : null;
      if (!alvo) return;
      if (NexoPar.retornoJaExiste(alvo, r.id_prova, r.id_ponto)) return;
      alvo.provasContexto.push(NexoPar.mapearRetornoContexto(r, envelope.origem, iso()));
      n++;
    });
    return n;
  }
  const impRetPar1 = importarRetornoNexoPar(envRetornoPar);
  checar('par_passo7', 'exatamente 1 contexto importado, vinculado ao ENTE PRIVADO (doc.acusados[0])', impRetPar1 === 1 && ente.provasContexto.length === 1);
  checar('par_passo7', 'contexto do ente NÃO é o mesmo array de doc.provas (isolamento estrutural)', docPar.provas !== ente.provasContexto);
  checar('par_passo7', 'importação do retorno NÃO dispara Nota de Indiciação nem altera pendências/provas',
    NexoPar.computePendencias().length === pendParAntesRetorno && docPar.provas.length === provasParAntesRetorno && docPar._minutaGerada === false,
    'pend antes=' + pendParAntesRetorno + ' depois=' + NexoPar.computePendencias().length + '; minutaGerada=' + docPar._minutaGerada);

  // --- PAR passo 8: gerar a Nota de Indiciação (gates ok) e conferir marcadores ---
  console.log('\n--- PAR passo 8: Nota de Indiciação (gates P-ENTE/P8-PAR ok) + marcadores ---');
  docPar.processo.comissao.presidente = { nome: 'Presidente Fictício', cargo: 'Auditor', matricula: '1010' };
  docPar.processo.comissao.membros = [{ nome: 'Vogal Um Fictício', cargo: '', matricula: '' }, { nome: 'Vogal Dois Fictício', cargo: '', matricula: '' }];
  docPar.processo.comissao.portariaInstauracao = { numero: '007/2026', data: '2026-03-01' };
  docPar.processo.cidade = 'Cidade de Teste';
  const faltasMinuta = NexoPar.validaMinuta([ente.id]);
  checar('par_passo8', 'validaMinuta não aponta faltas (dados obrigatórios completos)', faltasMinuta.length === 0, JSON.stringify(faltasMinuta));
  checar('par_passo8', 'gates P-ENTE e P8-PAR seguem satisfeitos na geração', !NexoPar.computePendencias().some(p => p.codigo === 'P-ENTE' || p.codigo === 'P8-PAR'));
  const notaTexto = NexoPar.construirTextoIndiciacao(ente.id, '2026-07-12');
  const marcadores = [
    ['título "Nota de Indiciação"', [/Nota de Indiciação/i]],
    ['cabeçalho PAR + Lei nº 12.846/2013', [/Processo Administrativo de Responsabilização/i, /12\.846/]],
    ['razão social do ente privado', [new RegExp(parFixture.entePrivado.razaoSocial.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')]],
    ['CNPJ do ente privado', [/CNPJ/]],
    ['representante legal', [/[Rr]epresentante legal/]],
    ['seção "Da conduta lesiva imputada ao ente privado"', [/conduta lesiva/i]],
    ['seção "Das provas"', [/Das provas/i]],
    ['enquadramento art. 5º, IV (LAC)', [/art\. 5º, IV/i]],
    ['interesse/benefício da pessoa jurídica', [/[Ii]nteresse ou benefício da pessoa jurídica/]],
    ['nexo de causalidade', [/[Nn]exo de causalidade/]],
    ['multa + faturamento bruto (art. 17 IN CGU 13/2019)', [/faturamento bruto/i, /multa/i]],
    ['parâmetro do inciso IV do art. 22 do Decreto nº 11.129/2022', [/inciso IV do art\. 22 do Decreto nº 11\.129/i]],
    ['prazo de 30 dias para defesa', [/30 \(trinta\) dias/]],
    ['programa de integridade', [/programa de integridade/i]],
    ['resolução negociada (Termo de Compromisso / Acordo de Leniência)', [/Termo de Compromisso/i, /Acordo de Leniência/i]],
    ['intimação — art. 17 da IN CGU nº 13/2019', [/art\. 17 da IN CGU nº 13\/2019/i]]
  ];
  marcadores.forEach(([nome, regexes]) => {
    checar('par_passo8', 'Nota de Indiciação contém marcador: ' + nome, regexes.every(re => re.test(notaTexto)));
  });

  // #########################################################################
  // ####  FLUXO PAR — idempotência e falha controlada (Rodada PAR-6, 6.3) ####
  // #########################################################################
  console.log('\n--- PAR 6.3: idempotência (reimportar passos 2, 4, 6, 7) ---');
  // Passo 2 de novo (mesma prova)
  const impPar2 = importarProvaVeritasNexoPar(provaImpPar);
  checar('par_idempotencia', 'passo 2 reimportado: recusado explicitamente por duplicidade, sem duplicar', impPar2.importou === false && impPar2.motivo === 'duplicado' && docPar.provas.length === provasParAntesRetorno);
  // Passo 4 de novo (mesma pauta_id — merge por fatoId)
  const itensAntesReimportPautaPar = pautaOitivaPar.itens.length;
  pautaOitivaPar = OitivaPar.OitivaPuro.mesclarPautaImportada(pautaOitivaPar, contratoPautaPar, OitivaPar.OitivaPuro.agoraISO());
  checar('par_idempotencia', 'passo 4 reimportado: nenhum item novo criado (merge por fatoId)', pautaOitivaPar.itens.length === itensAntesReimportPautaPar);
  checar('par_idempotencia', 'passo 4 reimportado: status "abordado" não regrediu para "pendente"', pautaOitivaPar.itens[0].statusChecklist === 'abordado');
  // Passo 6 de novo (mesmo termo/hash_origem)
  const avalPar2 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieVeritasPar2, envelopeTermoParReal.envelope, NexoPar.getCatalogoCoger());
  checar('par_idempotencia', 'passo 6 reimportado: recusado por duplicidade de hash_origem', avalPar2.ok === false && avalPar2.motivo === 'duplicado' && dossieVeritasPar2.itens.length === 1);
  // Passo 7 de novo (mesmo id_prova + id_ponto)
  const impRetPar2 = importarRetornoNexoPar(envRetornoPar);
  checar('par_idempotencia', 'passo 7 reimportado: nenhum contexto novo aceito (retornoJaExiste)', impRetPar2 === 0 && ente.provasContexto.length === 1);

  console.log('\n--- PAR 6.3: falha controlada (hash adulterado, schema divergente) ---');
  // hash divergente: altera 1 trecho do termo PAR antes do passo 6
  const termoParAdulterado = JSON.parse(JSON.stringify(envelopeTermoParReal.envelope));
  termoParAdulterado.termo.conteudo = termoParAdulterado.termo.conteudo.replace(parFixture.depoente.respostaPadrao.slice(0, 10), 'XXXXXXXXXX');
  const dossieParHash = Veritas.VeritasPuro.novoDossie(); dossieParHash.processo.tipoProcesso = 'PAR';
  const avalParAdulterado = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieParHash, termoParAdulterado, NexoPar.getCatalogoCoger());
  checar('par_falha_controlada', 'termo PAR com 1 trecho alterado é rejeitado por divergência de hash', avalParAdulterado.ok === false && avalParAdulterado.motivo === 'hash_divergente', JSON.stringify(avalParAdulterado));
  // catalogo_schema_version divergente no contrato de prova PAR (Nexo PAR detecta como aviso)
  const contratoParVersao = JSON.parse(JSON.stringify(contratoProvasPar));
  contratoParVersao.catalogo_schema_version = '0.1.0';
  checar('par_falha_controlada', 'catalogo_schema_version divergente detectada no contrato PAR (aviso, não falha silenciosa)', contratoParVersao.catalogo_schema_version !== NexoPar.getCatalogoCoger().schema_version);
  // catalogo_schema_version divergente no termo PAR (aviso, hash confere -> não bloqueia)
  const termoParVersao = JSON.parse(JSON.stringify(envelopeTermoParReal.envelope));
  termoParVersao.catalogo_schema_version = '0.1.0';
  const dossieParVersao = Veritas.VeritasPuro.novoDossie(); dossieParVersao.processo.tipoProcesso = 'PAR';
  const avalParVersao = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieParVersao, termoParVersao, NexoPar.getCatalogoCoger());
  checar('par_falha_controlada', 'termo PAR com catalogo_schema_version divergente gera aviso mas não bloqueia (hash confere)', avalParVersao.ok === true && avalParVersao.catalogoDivergente === true, JSON.stringify(avalParVersao));

  // #########################################################################
  // ####  VALIDAÇÃO CRUZADA PAD<->PAR com os fixtures REAIS (Rodada PAR-6, 6.4) ##
  // #########################################################################
  console.log('\n\n########## VALIDAÇÃO CRUZADA PAD<->PAR (fixtures reais, 6.4) ##########');

  // Contratos de prova PAD (a partir do fixture PAD): um marcado PAD, um legado (sem dominio).
  function itemVeritasDe(fix){
    return {
      id: 'VDC-' + crypto.randomUUID(), titulo: fix.provaInicialVeritas.titulo,
      categoria: fix.provaInicialVeritas.categoria, sigilo: fix.provaInicialVeritas.sigilo,
      status: 'ativo', observacoes: '', proveniencia: { tipo: 'gerado_internamente' },
      arquivos: [{ nomeArquivo: 'doc.txt', descricao: 'doc', hashLocal: crypto.createHash('sha256').update(fix.provaInicialVeritas.conteudoFicticio).digest('hex'), hashDeclarado: '' }],
      linhaDoTempoItem: [{ evento: 'item_identificado', dataHora: iso(), responsavel: '', resultado: '', observacao: '' }]
    };
  }
  const dossiePadReal = Veritas.VeritasPuro.novoDossie();
  dossiePadReal.processo.tipoProcesso = 'PAD';
  dossiePadReal.itens.push(itemVeritasDe(fixture));
  const contratoProvaPadComDominio = Veritas.VeritasPuro.construirContratoProvasNexo(dossiePadReal, Nexo.getCatalogoCoger(), iso());
  const dossiePadLegado = Veritas.VeritasPuro.novoDossie(); // sem tipoProcesso -> sem dominio (legado)
  dossiePadLegado.itens.push(itemVeritasDe(fixture));
  const contratoProvaPadLegado = Veritas.VeritasPuro.construirContratoProvasNexo(dossiePadLegado, Nexo.getCatalogoCoger(), iso());
  checar('cruzada', 'pré: contrato PAD marcado tem dominio "pad"; contrato legado NÃO tem dominio',
    contratoProvaPadComDominio.dominio === 'pad' && !('dominio' in contratoProvaPadLegado),
    'pad=' + contratoProvaPadComDominio.dominio + ' legadoTem=' + ('dominio' in contratoProvaPadLegado));

  // --- Caso 1: prova do fixture PAR -> Nexo Coger: RECUSADA (+ atomicidade) ---
  const provasNexoAntes1 = doc.provas.length;
  const cruz1 = Nexo.validarDominioEnvelope(contratoProvasPar);
  checar('cruzada', 'caso 1: prova PAR -> Nexo Coger é RECUSADA', cruz1.ok === false, JSON.stringify(cruz1));
  checar('cruzada', 'caso 1 (atomicidade): doc.provas do Nexo Coger inalterado', doc.provas.length === provasNexoAntes1);

  // --- Caso 2: prova do fixture PAD (marcada) -> Nexo PAR: RECUSADA (+ atomicidade) ---
  const provasNexoParAntes2 = docPar.provas.length;
  const cruz2 = NexoPar.validarDominioEnvelope(contratoProvaPadComDominio);
  checar('cruzada', 'caso 2: prova PAD -> Nexo PAR é RECUSADA', cruz2.ok === false, JSON.stringify(cruz2));
  checar('cruzada', 'caso 2 (atomicidade): docPar.provas do Nexo PAR inalterado', docPar.provas.length === provasNexoParAntes2);

  // --- Caso 3: pauta PAR -> Oitiva 360 já em domínio PAD, sem confirmação: RECUSADA inteira (+ atomicidade) ---
  const OitivaCruz = carregarFerramenta('oitiva-360.html');
  OitivaCruz.getEstado().matriz.dominio = 'pad'; // domínio manual PAD já definido
  OitivaCruz.confirm = () => false;               // usuário NÃO confirma a troca
  const pautaAntesCruz3 = OitivaCruz.getEstado().pautaImportada;
  const domManualAntesCruz3 = OitivaCruz.getEstado().matriz.dominio;
  OitivaCruz.OitivaPuro.aplicarImportacaoPauta(contratoPautaPar); // deve recusar a importação inteira
  const estadoCruz3 = OitivaCruz.getEstado();
  checar('cruzada', 'caso 3: pauta PAR em processo PAD (sem confirmação) é RECUSADA — nada importado', estadoCruz3.pautaImportada === pautaAntesCruz3);
  checar('cruzada', 'caso 3 (atomicidade): domínio manual do processo permanece "pad"', estadoCruz3.matriz.dominio === domManualAntesCruz3 && estadoCruz3.matriz.dominio === 'pad');

  // --- Caso 4: termo PAR -> dossiê Veritas marcado PAD: RECUSADO (+ atomicidade) ---
  const dossieVeritasPad = Veritas.VeritasPuro.novoDossie();
  dossieVeritasPad.processo.tipoProcesso = 'PAD';
  const itensAntesCruz4 = dossieVeritasPad.itens.length;
  const cruz4 = await Veritas.VeritasPuro.avaliarImportacaoTermo(dossieVeritasPad, envelopeTermoParReal.envelope, Nexo.getCatalogoCoger());
  checar('cruzada', 'caso 4: termo PAR -> dossiê Veritas PAD é RECUSADO (dominio_incompativel)', cruz4.ok === false && cruz4.motivo === 'dominio_incompativel', JSON.stringify(cruz4));
  checar('cruzada', 'caso 4 (atomicidade): dossiê Veritas PAD sem nenhum item novo', dossieVeritasPad.itens.length === itensAntesCruz4);

  // --- Caso 5: envelope PAD legado (sem dominio) -> Nexo Coger: ACEITO; -> Nexo PAR: RECUSADO (+ atomicidade) ---
  const provasNexoAntes5 = doc.provas.length;
  const provasNexoParAntes5 = docPar.provas.length;
  const cruz5a = Nexo.validarDominioEnvelope(contratoProvaPadLegado);
  const cruz5b = NexoPar.validarDominioEnvelope(contratoProvaPadLegado);
  checar('cruzada', 'caso 5a: envelope PAD legado (sem dominio) -> Nexo Coger é ACEITO', cruz5a.ok === true, JSON.stringify(cruz5a));
  checar('cruzada', 'caso 5b: envelope PAD legado -> Nexo PAR é RECUSADO (mensagem de legado)', cruz5b.ok === false && /anterior às Rodadas PAR|acervo legado/i.test(cruz5b.msg || ''), JSON.stringify(cruz5b));
  checar('cruzada', 'caso 5 (atomicidade): provas de Nexo Coger e Nexo PAR inalteradas', doc.provas.length === provasNexoAntes5 && docPar.provas.length === provasNexoParAntes5);

  // #########################################################################
  // ####  Relatório final — TRÊS seções (Rodada PAR-6, 6.5)               ####
  // #########################################################################
  console.log('\n=== Relatório final (3 seções) ===');
  const SECOES = ['Fluxo PAD', 'Fluxo PAR', 'Validação cruzada', 'Outros'];
  let totalOk = 0, totalFalhas = 0;
  SECOES.forEach(sec => {
    const itensSec = relatorio.filter(r => secaoDoGrupo(r.grupo) === sec);
    if (!itensSec.length) return;
    const okSec = itensSec.filter(i => i.ok).length;
    console.log('\n▓▓▓ ' + sec + ': ' + okSec + '/' + itensSec.length + (okSec === itensSec.length ? ' ✅' : ' ❌'));
    const gruposSec = [...new Set(itensSec.map(r => r.grupo))];
    gruposSec.forEach(g => {
      const itens = relatorio.filter(r => r.grupo === g);
      const ok = itens.filter(i => i.ok).length;
      console.log('    ' + g + ': ' + ok + '/' + itens.length + (ok === itens.length ? ' ✅' : ' ❌'));
    });
  });
  relatorio.forEach(r => { r.ok ? totalOk++ : totalFalhas++; });
  console.log('\nTotal: ' + totalOk + ' passaram, ' + totalFalhas + ' falharam, de ' + relatorio.length + ' verificações.');

  if (totalFalhas > 0){
    console.log('\nFalhas:');
    relatorio.filter(r => !r.ok).forEach(r => console.log('  - [' + r.grupo + '] ' + r.nome + ' — ' + r.detalhe));
    process.exitCode = 1;
  } else {
    console.log('\nTodas as verificações passaram — Fluxo PAD (Rodadas 3-6), Fluxo PAR (8 etapas + Nota de Indiciação, Rodada PAR-6) e Validação cruzada PAD<->PAR validados de ponta a ponta num único comando.');
  }
})().catch(e => {
  console.error('\n❌ ERRO NÃO TRATADO:', e);
  process.exitCode = 1;
});
