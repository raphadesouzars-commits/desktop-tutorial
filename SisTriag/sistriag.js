/* ================================================================
   SISTRIAG-Coger — Fase 1: Fundação
   Módulos:
   1. IndexedDB
   2. Leitor PDF (PDF.js)
   3. Leitor DOCX (mammoth.js)
   4. Chunking diferenciado por categoria
   5. TF-IDF / busca por relevância
   6. Gestão da base de conhecimento
   7. Interface e navegação
   ================================================================ */

/* ================================================================
   1. INDEXEDDB — INICIALIZAÇÃO E OPERAÇÕES
   ================================================================ */

const DB_NOME    = 'SisTriagCoger';
const DB_VERSAO  = 1;
let db = null;

function abrirDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NOME, DB_VERSAO);

    req.onupgradeneeded = (e) => {
      const d = e.target.result;

      if (!d.objectStoreNames.contains('documentos')) {
        const store = d.createObjectStore('documentos', { keyPath: 'id' });
        store.createIndex('categoria', 'categoria', { unique: false });
        store.createIndex('nome',      'nome',      { unique: false });
      }

      if (!d.objectStoreNames.contains('chunks')) {
        const store = d.createObjectStore('chunks', { keyPath: 'id' });
        store.createIndex('docId',     'docId',     { unique: false });
        store.createIndex('categoria', 'categoria', { unique: false });
      }

      if (!d.objectStoreNames.contains('configuracoes')) {
        d.createObjectStore('configuracoes', { keyPath: 'chave' });
      }

      if (!d.objectStoreNames.contains('historico')) {
        const store = d.createObjectStore('historico', { keyPath: 'id' });
        store.createIndex('data',          'data',          { unique: false });
        store.createIndex('tipo_processo', 'tipo_processo', { unique: false });
      }
    };

    req.onsuccess = (e) => { db = e.target.result; resolve(db); };
    req.onerror   = (e) => reject(e.target.error);
  });
}

function txGet(store, key) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(store, 'readonly');
    const req = tx.objectStore(store).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror   = () => reject(req.error);
  });
}

function txGetAll(store, index, valor) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(store, 'readonly');
    const os  = tx.objectStore(store);
    const req = index ? os.index(index).getAll(valor) : os.getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror   = () => reject(req.error);
  });
}

function txPut(store, obj) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(store, 'readwrite');
    const req = tx.objectStore(store).put(obj);
    req.onsuccess = () => resolve(req.result);
    req.onerror   = () => reject(req.error);
  });
}

function txDelete(store, key) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(store, 'readwrite');
    const req = tx.objectStore(store).delete(key);
    req.onsuccess = () => resolve();
    req.onerror   = () => reject(req.error);
  });
}

function txClear(store) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(store, 'readwrite');
    const req = tx.objectStore(store).clear();
    req.onsuccess = () => resolve();
    req.onerror   = () => reject(req.error);
  });
}

async function getConfig(chave, padrao = null) {
  const r = await txGet('configuracoes', chave);
  return r ? r.valor : padrao;
}

async function setConfig(chave, valor) {
  await txPut('configuracoes', { chave, valor });
}

/* ================================================================
   2. LEITURA DE ARQUIVOS
   ================================================================ */

/* Configura workerSrc do PDF.js */
function inicializarPDFJS() {
  if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdf.worker.min.js';
  }
}

async function lerPDF(arrayBuffer) {
  if (typeof pdfjsLib === 'undefined') throw new Error('PDF.js não carregado. Verifique sua conexão e recarregue a página.');
  const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });

  // Timeout de 30s para evitar hang em PDFs problemáticos
  const pdf = await Promise.race([
    loadingTask.promise,
    new Promise((_, rej) => setTimeout(() => rej(new Error('Timeout ao processar PDF (>30s). Tente converter para DOCX ou TXT.')), 30000)),
  ]);

  let texto = '';
  for (let i = 1; i <= pdf.numPages; i++) {
    const page    = await pdf.getPage(i);
    const content = await page.getTextContent();
    // Preserva quebras de linha reais agrupando por blocos verticais
    const linhas = {};
    content.items.forEach(item => {
      const y = Math.round(item.transform[5]);
      if (!linhas[y]) linhas[y] = [];
      linhas[y].push(item.str);
    });
    const linhaOrdenada = Object.keys(linhas)
      .sort((a, b) => b - a)
      .map(y => linhas[y].join(' '))
      .join('\n');
    texto += linhaOrdenada + '\n\n';
  }
  return { texto: texto.trim(), paginas: pdf.numPages };
}

async function lerDOCX(arrayBuffer) {
  if (typeof mammoth === 'undefined') throw new Error('mammoth.js não carregado. Verifique sua conexão e recarregue a página.');
  const result = await mammoth.extractRawText({ arrayBuffer });
  return { texto: result.value.trim() };
}

async function lerTextoPlano(arquivo) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve({ texto: e.target.result.trim(), tipo: 'txt' });
    reader.onerror = () => reject(new Error('Erro ao ler arquivo de texto'));
    reader.readAsText(arquivo, 'UTF-8');
  });
}

const EXTENSOES_SUPORTADAS = new Set(['pdf', 'docx', 'txt', 'md']);

async function lerArquivo(arquivo) {
  const ext = arquivo.name.split('.').pop().toLowerCase();

  if (ext === 'txt' || ext === 'md') {
    const r = await lerTextoPlano(arquivo);
    return { ...r, tipo: ext, possivelmenteEscaneado: false };
  }

  const buf = await arquivo.arrayBuffer();

  if (ext === 'pdf') {
    const r = await lerPDF(buf);
    const palavrasPorPag = r.texto.split(/\s+/).length / Math.max(r.paginas, 1);
    if (palavrasPorPag < 20 && r.paginas > 0) {
      return { ...r, possivelmenteEscaneado: true, tipo: 'pdf' };
    }
    return { ...r, possivelmenteEscaneado: false, tipo: 'pdf' };
  } else if (ext === 'docx') {
    const r = await lerDOCX(buf);
    return { ...r, tipo: 'docx' };
  } else {
    throw new Error(`Formato não suportado: .${ext} — use PDF, DOCX, TXT ou MD`);
  }
}

/* ================================================================
   3. CHUNKING POR PARÁGRAFO (semântico)
   ================================================================ */

// Divide preservando fronteiras naturais: parágrafos > sentenças > palavras
function dividirEmChunks(texto, categoria) {
  // Tamanhos máximos em palavras por categoria
  const MAX_PAL = {
    'normas': 200, 'pareceres': 180, 'decisoes': 180,
    'notas-tecnicas': 160, 'orientacoes': 140,
  };
  const max = MAX_PAL[categoria] || 180;
  const overlap = Math.floor(max * 0.2); // 20% de sobreposição

  // 1. Separa em parágrafos (linhas duplas ou recuo de artigo)
  const paragrafos = texto
    .split(/\n{2,}|\r\n{2,}/)
    .map(p => p.replace(/\s+/g, ' ').trim())
    .filter(p => p.length > 30);

  if (paragrafos.length === 0) {
    // fallback: texto sem quebras — divide por sentenças
    return dividirPorPalavras(texto, max, overlap);
  }

  const chunks = [];
  let buffer = [];
  let bufPal = 0;

  function flushBuffer() {
    if (buffer.length === 0) return;
    chunks.push(buffer.join(' '));
    // sobreposição: mantém último parágrafo no buffer
    const ultimo = buffer[buffer.length - 1];
    buffer = ultimo.split(/\s+/).length <= overlap ? [ultimo] : [];
    bufPal = buffer.reduce((s, p) => s + p.split(/\s+/).length, 0);
  }

  for (const par of paragrafos) {
    const pal = par.split(/\s+/).length;
    // Se o parágrafo sozinho excede o limite, subdivide
    if (pal > max) {
      flushBuffer();
      const subs = dividirPorPalavras(par, max, overlap);
      subs.forEach(s => chunks.push(s));
      continue;
    }
    if (bufPal + pal > max && buffer.length > 0) {
      flushBuffer();
    }
    buffer.push(par);
    bufPal += pal;
  }
  flushBuffer();

  return chunks.filter(c => c.trim().length > 30);
}

function dividirPorPalavras(texto, max, overlap) {
  const palavras = texto.split(/\s+/).filter(p => p.length > 0);
  const chunks = [];
  let inicio = 0;
  while (inicio < palavras.length) {
    const fim = Math.min(inicio + max, palavras.length);
    chunks.push(palavras.slice(inicio, fim).join(' '));
    if (fim >= palavras.length) break;
    inicio += max - overlap;
  }
  return chunks;
}

/* ================================================================
   4. BM25 + QUERY EXPANSION — INDEXAÇÃO E BUSCA
   ================================================================ */

// Dicionário de expansão jurídica PT-BR
const EXPANSAO_JURIDICA = {
  'demissao':        ['demissao','desligamento','exoneracao','dispensa','rescisao'],
  'suspensao':       ['suspensao','afastamento','impedimento'],
  'advertencia':     ['advertencia','repreensao','censura'],
  'corrupcao':       ['corrupcao','suborno','propina','vantagem indevida'],
  'improbidade':     ['improbidade','desonestidade','ilicito'],
  'dano':            ['dano','prejuizo','lesao','perda'],
  'servidor':        ['servidor','funcionario','agente publico'],
  'processo':        ['processo','procedimento','apuracao','sindicancia'],
  'comissao':        ['comissao','colegiado','tribunal'],
  'pena':            ['pena','sancao','penalidade','punicao'],
  'culpa':           ['culpa','negligencia','imprudencia','imperícia'],
  'dolo':            ['dolo','intencao','ma-fe','fraude'],
  'prescricao':      ['prescricao','decadencia','prazo'],
  'defesa':          ['defesa','contraditorio','ampla defesa'],
  'recurso':         ['recurso','impugnacao','revisao','apelacao'],
  'irregularidade':  ['irregularidade','infração','ilegalidade','violacao'],
  'lei':             ['lei','decreto','portaria','instrucao normativa','resolucao'],
  'responsabilidade':['responsabilidade','imputacao','atribuicao'],
  'absolvi':         ['absolvicao','arquivamento','improcedente'],
  'condena':         ['condenacao','procedente','acolhido'],
};

function tokenizar(texto) {
  const stopwords = new Set([
    'a','ao','aos','as','com','da','das','de','do','dos','e','em','na','nas',
    'no','nos','o','os','ou','para','pela','pelas','pelo','pelos','por','que',
    'se','um','uma','uns','umas','é','à','às','isso','este','esta','esse','essa',
    'seu','sua','seus','suas','ter','ser','foi','são','está','entre',
    'mais','sobre','mas','também','como','quando','onde','qual','quais','não',
    'the','and','for','are','but','not','you','all','can','had','her','was',
  ]);
  return texto
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 2 && !stopwords.has(t));
}

function expandirQuery(tokens) {
  const expandidos = new Set(tokens);
  tokens.forEach(t => {
    if (EXPANSAO_JURIDICA[t]) {
      EXPANSAO_JURIDICA[t].forEach(s => {
        tokenizar(s).forEach(st => expandidos.add(st));
      });
    }
  });
  return [...expandidos];
}

// BM25 parameters
const BM25_K1 = 1.5;  // term frequency saturation
const BM25_B  = 0.75; // length normalization

let indiceMemoria = [];
let bm25_avgdl = 0; // average document length (in tokens)

async function carregarIndiceMemoria() {
  const chunks = await txGetAll('chunks');
  indiceMemoria = chunks.map(c => {
    const tokens = tokenizar(c.texto);
    const tf = {};
    tokens.forEach(t => { tf[t] = (tf[t] || 0) + 1; });
    return { ...c, tokens, tf, dl: tokens.length };
  });
  bm25_avgdl = indiceMemoria.length > 0
    ? indiceMemoria.reduce((s, c) => s + c.dl, 0) / indiceMemoria.length
    : 1;
}

function bm25Score(chunk, queryTokens, idfMap) {
  let score = 0;
  const dl = chunk.dl;
  queryTokens.forEach(t => {
    const idf = idfMap[t] || 0;
    if (idf === 0) return;
    const freq = chunk.tf[t] || 0;
    const num = freq * (BM25_K1 + 1);
    const den = freq + BM25_K1 * (1 - BM25_B + BM25_B * (dl / bm25_avgdl));
    score += idf * (num / den);
  });
  return score;
}

function buscarRAG(query, n = 8, categoriaFiltro = '') {
  if (indiceMemoria.length === 0) return [];

  const corpus = categoriaFiltro
    ? indiceMemoria.filter(c => c.categoria === categoriaFiltro)
    : indiceMemoria;
  if (corpus.length === 0) return [];

  // Expande termos da query com sinônimos jurídicos
  const queryTokensRaw = tokenizar(query);
  const queryTokens    = expandirQuery(queryTokensRaw);
  if (queryTokens.length === 0) return [];

  // IDF suavizado: log((N - n_t + 0.5) / (n_t + 0.5) + 1)
  const N = corpus.length;
  const idfMap = {};
  queryTokens.forEach(t => {
    const nt = corpus.filter(c => c.tf[t] > 0).length;
    idfMap[t] = Math.log((N - nt + 0.5) / (nt + 0.5) + 1);
  });

  // Score BM25
  const scores = corpus.map(chunk => ({
    chunk,
    score: bm25Score(chunk, queryTokens, idfMap),
  }));

  scores.sort((a, b) => b.score - a.score);

  const top = scores.filter(s => s.score > 0).slice(0, n);

  // Adiciona contexto de vizinhança: inclui chunk adjacente se score relevante
  const resultado = [];
  const vistosIds = new Set();
  top.forEach(({ chunk, score }) => {
    if (!vistosIds.has(chunk.id)) {
      vistosIds.add(chunk.id);
      resultado.push({ ...chunk, score });
    }
    // vizinho posterior se existir e não já incluído
    const vizId = `${chunk.docId}_c${chunk.posicao + 1}`;
    const viz = indiceMemoria.find(c => c.id === vizId);
    if (viz && !vistosIds.has(viz.id) && score > 1.0) {
      vistosIds.add(viz.id);
      resultado.push({ ...viz, score: score * 0.6, vizinho: true });
    }
  });

  return resultado.slice(0, n);
}

/* ================================================================
   5. GESTÃO DA BASE DE CONHECIMENTO
   ================================================================ */

function gerarId(nome, tamanho) {
  // Hash simples baseado no nome e tamanho
  let hash = 0;
  const str = nome + tamanho;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(36) + '_' + Date.now().toString(36);
}

async function indexarArquivos(arquivos, categoria) {
  const modal = document.getElementById('modal-processamento');
  const titulo = document.getElementById('proc-titulo');
  const status = document.getElementById('proc-status');
  const barra  = document.getElementById('proc-barra');

  modal.classList.remove('oculto');
  const resultados = [];

  for (let i = 0; i < arquivos.length; i++) {
    const arq = arquivos[i];
    const pct = Math.round(((i) / arquivos.length) * 100);
    barra.style.width  = pct + '%';
    titulo.textContent = `Indexando ${i + 1} de ${arquivos.length}`;
    status.textContent = arq.name;

    try {
      const extracao = await lerArquivo(arq);

      if (!extracao.texto || extracao.texto.trim().length < 50) {
        resultados.push({
          nome: arq.name, ok: false,
          motivo: extracao.possivelmenteEscaneado
            ? 'PDF parece ser imagem/escaneado — texto não extraível'
            : 'Texto extraído está vazio ou muito curto'
        });
        continue;
      }

      const docId  = gerarId(arq.name, arq.size);
      const chunks = dividirEmChunks(extracao.texto, categoria);

      // Salvar documento
      const docObj = {
        id:          docId,
        nome:        arq.name,
        categoria,
        tipo_arquivo: extracao.tipo,
        texto:       extracao.texto,
        num_chunks:  chunks.length,
        num_paginas: extracao.paginas || null,
        tamanho:     arq.size || 0,
        indexado_em: new Date().toISOString(),
        possivelmenteEscaneado: extracao.possivelmenteEscaneado || false,
      };
      await txPut('documentos', docObj);

      // Salvar chunks
      for (let j = 0; j < chunks.length; j++) {
        await txPut('chunks', {
          id:       `${docId}_c${j}`,
          docId,
          docNome:  arq.name,
          categoria,
          posicao:  j,
          total:    chunks.length,
          texto:    chunks[j],
        });
      }

      resultados.push({
        nome: arq.name, ok: true,
        chunks: chunks.length,
        palavras: extracao.texto.split(/\s+/).length,
        escaneado: extracao.possivelmenteEscaneado || false,
      });

    } catch (err) {
      resultados.push({ nome: arq.name, ok: false, motivo: err.message });
    }
  }

  barra.style.width = '100%';
  await setConfig('ultima_indexacao', new Date().toISOString());

  // Recarrega índice em memória
  await carregarIndiceMemoria();

  modal.classList.add('oculto');
  return resultados;
}

async function removerDocumento(docId) {
  // Remove documento e todos seus chunks
  await txDelete('documentos', docId);
  const chunks = await txGetAll('chunks', 'docId', docId);
  for (const c of chunks) await txDelete('chunks', c.id);
  await carregarIndiceMemoria();
}

async function limparBase() {
  await txClear('documentos');
  await txClear('chunks');
  indiceMemoria = [];
}

/* ================================================================
   6. INTERFACE — RENDERIZAÇÃO DA BASE
   ================================================================ */

async function renderizarBase() {
  const docs = await txGetAll('documentos');

  // Atualiza cards de categoria
  const categorias = ['normas','pareceres','decisoes','notas-tecnicas','orientacoes'];
  const mapeamento  = {
    'normas':         { cnt: 'cnt-normas',      chk: 'chk-normas' },
    'pareceres':      { cnt: 'cnt-pareceres',   chk: 'chk-pareceres' },
    'decisoes':       { cnt: 'cnt-decisoes',    chk: 'chk-decisoes' },
    'notas-tecnicas': { cnt: 'cnt-notas',       chk: 'chk-notas' },
    'orientacoes':    { cnt: 'cnt-orientacoes', chk: 'chk-orientacoes' },
  };

  categorias.forEach(cat => {
    const docscat   = docs.filter(d => d.categoria === cat);
    const totalChunks = docscat.reduce((s,d) => s + (d.num_chunks||0), 0);
    const ids = mapeamento[cat];
    document.getElementById(ids.cnt).textContent = docscat.length;
    document.getElementById(ids.chk).textContent = totalChunks + ' chunks';
  });

  // Renderiza lista de documentos
  const lista = document.getElementById('lista-docs');

  if (docs.length === 0) {
    lista.innerHTML = `
      <div class="estado-vazio">
        <div class="vazio-icone">📂</div>
        <div class="vazio-titulo">Nenhum documento indexado</div>
        <div class="vazio-desc">Adicione documentos usando a área acima</div>
      </div>`;
    return;
  }

  const icones = {
    'normas':         '📜',
    'pareceres':      '⚖',
    'decisoes':       '📋',
    'notas-tecnicas': '📝',
    'orientacoes':    '🎓',
  };

  const nomesCat = {
    'normas':         'Norma',
    'pareceres':      'Parecer',
    'decisoes':       'Decisão',
    'notas-tecnicas': 'Nota Técnica',
    'orientacoes':    'Orientação',
  };

  // Ordena por categoria depois nome
  docs.sort((a,b) => a.categoria.localeCompare(b.categoria) || a.nome.localeCompare(b.nome));

  lista.innerHTML = docs.map(doc => `
    <div class="doc-item" id="doc-${doc.id}">
      <div class="doc-icone">${icones[doc.categoria]||'📄'}</div>
      <div class="doc-info">
        <div class="doc-nome">${escapeHtml(doc.nome)}</div>
        <div class="doc-meta">
          <span class="badge badge-cinza" style="font-size:10px">${nomesCat[doc.categoria]||doc.categoria}</span>
          &nbsp;${doc.num_chunks} chunks · ${doc.tipo_arquivo.toUpperCase()}
          ${doc.num_paginas ? ` · ${doc.num_paginas} págs` : ''}
          · indexado ${formatarData(doc.indexado_em)}
          ${doc.possivelmenteEscaneado ? ' <span class="badge badge-amarelo" style="font-size:10px">Pode ser escaneado</span>' : ''}
        </div>
      </div>
      <div class="doc-acoes">
        <button class="btn btn-secundario btn-sm" onclick="togglePreview('${doc.id}')">Ver trecho</button>
        <button class="btn btn-perigo btn-sm" onclick="confirmarRemoverDoc('${doc.id}', '${escapeHtml(doc.nome)}')">Remover</button>
      </div>
    </div>
    <div class="preview-extracao" id="preview-${doc.id}">${escapeHtml((doc.texto||'').substring(0, 600))}${doc.texto && doc.texto.length > 600 ? '...' : ''}</div>
  `).join('');

  atualizarStatusBase(docs.length);
}

function togglePreview(docId) {
  const el = document.getElementById('preview-' + docId);
  if (el) el.classList.toggle('visivel');
}

/* ================================================================
   7. HANDLERS DE UPLOAD
   ================================================================ */

async function handleArquivos(arquivos) {
  if (!arquivos || arquivos.length === 0) return;
  const categoria = document.getElementById('sel-categoria').value;
  const lista = Array.from(arquivos);

  const resultados = await indexarArquivos(lista, categoria);
  await renderizarBase();
  mostrarResultadosIndexacao(resultados);
}

function handleDrop(event) {
  event.preventDefault();
  document.getElementById('zona-upload').classList.remove('arrastando');
  const arquivos = event.dataTransfer.files;
  handleArquivos(arquivos);
}

function mostrarResultadosIndexacao(resultados) {
  const ok    = resultados.filter(r => r.ok);
  const erros = resultados.filter(r => !r.ok);
  const avisos = ok.filter(r => r.escaneado);

  let html = '';

  if (ok.length > 0) {
    html += `<div class="alerta alerta-sucesso">
      <span>✓</span>
      <div>
        <strong>${ok.length} documento(s) indexado(s) com sucesso.</strong><br>
        ${ok.map(r => `${escapeHtml(r.nome)}: ${r.chunks} chunks, ~${r.palavras} palavras`).join('<br>')}
      </div>
    </div>`;
  }

  if (avisos.length > 0) {
    html += `<div class="alerta alerta-aviso">
      <span>⚠</span>
      <div>
        <strong>Atenção:</strong> Os seguintes arquivos podem ser PDFs escaneados (imagens). A extração de texto foi parcial:<br>
        ${avisos.map(r => escapeHtml(r.nome)).join('<br>')}
      </div>
    </div>`;
  }

  if (erros.length > 0) {
    html += `<div class="alerta alerta-erro">
      <span>✗</span>
      <div>
        <strong>${erros.length} arquivo(s) com erro:</strong><br>
        ${erros.map(r => `${escapeHtml(r.nome)}: ${r.motivo}`).join('<br>')}
      </div>
    </div>`;
  }

  // Insere no topo da tela de base
  const painel = document.querySelector('#tela-base .painel');
  const aviso  = document.createElement('div');
  aviso.innerHTML = html;
  painel.parentNode.insertBefore(aviso, painel);

  setTimeout(() => { if (aviso.parentNode) aviso.parentNode.removeChild(aviso); }, 8000);
}

/* ================================================================
   8. BUSCA RAG — INTERFACE
   ================================================================ */

async function executarBuscaRAG() {
  const query = document.getElementById('rag-query').value.trim();
  if (!query) return;

  const n        = parseInt(document.getElementById('rag-n').value);
  const cat      = document.getElementById('rag-categoria').value;
  const container = document.getElementById('resultados-rag');

  if (indiceMemoria.length === 0) {
    container.innerHTML = `<div class="alerta alerta-aviso"><span>⚠</span><span>A base de conhecimento está vazia. Adicione documentos primeiro.</span></div>`;
    return;
  }

  const btn = document.getElementById('btn-buscar-rag');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Buscando...';

  const resultados = buscarRAG(query, n, cat);

  btn.disabled = false;
  btn.textContent = 'Buscar na base';

  if (resultados.length === 0) {
    container.innerHTML = `<div class="alerta alerta-info"><span>ℹ</span><span>Nenhum resultado encontrado para esta query. Tente termos mais específicos ou verifique se a base contém documentos relevantes.</span></div>`;
    return;
  }

  const nomesCat = {
    'normas':         'Norma',
    'pareceres':      'Parecer',
    'decisoes':       'Decisão',
    'notas-tecnicas': 'Nota Técnica',
    'orientacoes':    'Orientação',
  };

  container.innerHTML = `
    <div class="painel-titulo" style="margin-bottom:12px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--azul-acento)">
      ${resultados.length} resultado(s) para: "${escapeHtml(query)}"
    </div>
    ${resultados.map((r, i) => `
      <div class="resultado-rag">
        <div class="rag-rank">#${i+1} — ${nomesCat[r.categoria]||r.categoria}</div>
        <div class="rag-fonte">📄 ${escapeHtml(r.docNome)} · Chunk ${r.posicao+1}/${r.total}</div>
        <div class="rag-texto">${escapeHtml(r.texto)}</div>
        <div class="rag-score">Score BM25: ${r.score.toFixed(3)}${r.vizinho ? ' · contexto adjacente' : ''}</div>
      </div>
    `).join('')}
  `;
}

/* ================================================================
   9. NAVEGAÇÃO SPA
   ================================================================ */

const TELAS = ['inicio', 'base', 'rag', 'config', 'upload', 'resultado'];

function navegarPara(tela) {
  TELAS.forEach(t => {
    document.getElementById('tela-' + t).classList.remove('ativa');
    const nav = document.getElementById('nav-' + t);
    if (nav) nav.classList.remove('ativo');
  });
  document.getElementById('tela-' + tela).classList.add('ativa');
  const nav = document.getElementById('nav-' + tela);
  if (nav) nav.classList.add('ativo');

  if (tela === 'base') { renderizarBase(); verificarCompatibilidadePasta(); }
  if (tela === 'config') carregarConfiguracoes();
  if (tela === 'upload' || tela === 'resultado') {
    // Oculta nav ativo para essas telas internas
    document.getElementById('nav-inicio').classList.remove('ativo');
  }
}

/* ================================================================
   10. SELEÇÃO DE TIPO E OCASIÃO (TELA INICIAL)
   ================================================================ */

let selecaoTipo    = null;
let selecaoOcasiao = null;

function selecionarTipo(tipo) {
  selecaoTipo    = tipo;
  selecaoOcasiao = null;

  ['PAD','PAR'].forEach(t => {
    document.getElementById('card-' + t).classList.toggle('selecionado', t === tipo);
  });

  document.getElementById('selecao-ocasiao').style.display = 'block';
  document.getElementById('inicio-acoes').style.display    = 'none';
  ['triagem','admissibilidade','julgamento'].forEach(o => {
    document.getElementById('card-' + o).classList.remove('selecionado');
  });
}

function selecionarOcasiao(ocasiao) {
  selecaoOcasiao = ocasiao;
  ['triagem','admissibilidade','julgamento'].forEach(o => {
    document.getElementById('card-' + o).classList.toggle('selecionado', o === ocasiao);
  });
  document.getElementById('inicio-acoes').style.display = 'flex';
}

function resetarSelecao() {
  selecaoTipo    = null;
  selecaoOcasiao = null;
  ['PAD','PAR'].forEach(t => document.getElementById('card-' + t).classList.remove('selecionado'));
  ['triagem','admissibilidade','julgamento'].forEach(o => {
    document.getElementById('card-' + o).classList.remove('selecionado');
  });
  document.getElementById('selecao-ocasiao').style.display = 'none';
  document.getElementById('inicio-acoes').style.display    = 'none';
}

function iniciarFluxo() {
  if (!selecaoTipo || !selecaoOcasiao) return;
  // Fase 2: aqui navegará para o formulário correspondente
  alert(`Fluxo: ${selecaoTipo} — ${selecaoOcasiao}\n\nOs formulários de análise serão implementados na Fase 2 (Motor de análise).`);
}

/* ================================================================
   11. CONFIGURAÇÕES
   ================================================================ */

async function carregarConfiguracoes() {
  const docs   = await txGetAll('documentos');
  const chunks = await txGetAll('chunks');
  const ultima = await getConfig('ultima_indexacao');

  const statusEl = document.getElementById('cfg-status-base');
  const badgeEl  = document.getElementById('cfg-badge-base');
  const chunksEl = document.getElementById('cfg-total-chunks');
  const ultimaEl = document.getElementById('cfg-ultima-index');

  if (docs.length === 0) {
    statusEl.textContent = 'Base não indexada — sem documentos';
    badgeEl.className = 'badge badge-vermelho';
    badgeEl.textContent = 'Vazia';
  } else {
    statusEl.textContent = `${docs.length} documento(s) indexado(s)`;
    badgeEl.className = 'badge badge-verde';
    badgeEl.textContent = 'Ativa';
  }

  chunksEl.textContent = chunks.length + ' chunks';
  ultimaEl.textContent = ultima ? formatarData(ultima, true) : 'Nunca';

  // Carrega campos de numeração
  const campos = {
    'cfg-prefixo':        ['prefixo', ''],
    'cfg-seq-triagem':    ['seq_triagem', 1],
    'cfg-seq-admiss':     ['seq_admissibilidade', 1],
    'cfg-seq-decisao-pad':['seq_decisao_pad', 1],
    'cfg-seq-decisao-par':['seq_decisao_par', 1],
  };

  for (const [id, [chave, padrao]] of Object.entries(campos)) {
    const el = document.getElementById(id);
    if (el) el.value = await getConfig(chave, padrao);
  }
}

async function salvarConfiguracao(chave, valor) {
  await setConfig(chave, valor);
}

/* ================================================================
   12. EXPORTAR ÍNDICE
   ================================================================ */

async function exportarIndice() {
  const docs = await txGetAll('documentos');
  if (docs.length === 0) { alert('Nenhum documento indexado.'); return; }

  const linhas = [
    'Categoria\tNome\tChunks\tTipo\tPáginas\tIndexado em',
    ...docs.map(d =>
      `${d.categoria}\t${d.nome}\t${d.num_chunks}\t${d.tipo_arquivo}\t${d.num_paginas||'-'}\t${d.indexado_em}`
    )
  ];

  const blob = new Blob([linhas.join('\n')], { type: 'text/plain;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url;
  a.download = `SisTriag_Indice_${new Date().toISOString().slice(0,10)}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

/* ================================================================
   13. MODAIS
   ================================================================ */

let acaoModal = null;

function abrirModal(titulo, sub, corpo, acaoConfirmar) {
  document.getElementById('modal-titulo').textContent = titulo;
  document.getElementById('modal-sub').textContent    = sub;
  document.getElementById('modal-corpo').innerHTML    = corpo;
  acaoModal = acaoConfirmar;
  document.getElementById('modal-overlay').classList.remove('oculto');
}

function fecharModal() {
  document.getElementById('modal-overlay').classList.add('oculto');
  acaoModal = null;
}

async function executarAcaoModal() {
  if (acaoModal) await acaoModal();
  fecharModal();
}

function confirmarRemoverDoc(docId, nome) {
  abrirModal(
    'Remover documento',
    `Confirma a remoção de "${nome}" da base de conhecimento? Os chunks indexados serão apagados permanentemente.`,
    '',
    async () => {
      await removerDocumento(docId);
      await renderizarBase();
      atualizarStatusRodape();
    }
  );
}

function confirmarLimparBase() {
  abrirModal(
    'Limpar base de conhecimento',
    'Esta ação apagará TODOS os documentos e chunks indexados. O histórico de análises não será afetado. Deseja continuar?',
    '',
    async () => {
      await limparBase();
      await renderizarBase();
      atualizarStatusRodape();
    }
  );
}

function confirmarLimparTudo() {
  abrirModal(
    'Apagar todos os dados',
    'Esta ação apagará TODOS os dados do sistema: base de conhecimento, histórico de análises e configurações. Esta ação é irreversível. Tem certeza?',
    '<div class="alerta alerta-erro" style="margin-top:12px"><span>⚠</span><span>Esta ação não pode ser desfeita.</span></div>',
    async () => {
      await txClear('documentos');
      await txClear('chunks');
      await txClear('configuracoes');
      await txClear('historico');
      indiceMemoria = [];
      await renderizarBase();
      await atualizarStatusRodape();
      location.reload();
    }
  );
}

/* ================================================================
   14. STATUS RODAPÉ
   ================================================================ */

async function atualizarStatusRodape() {
  const docs = await txGetAll('documentos');
  const dot  = document.getElementById('dot-base');
  const txt  = document.getElementById('txt-base');
  const aviso = document.getElementById('aviso-base');

  if (docs.length === 0) {
    dot.className  = 'status-dot vermelho';
    txt.textContent = 'Base não indexada';
    if (aviso) {
      aviso.style.display = 'flex';
      document.getElementById('aviso-base-texto').textContent = 'Base de conhecimento não indexada. Clique aqui para configurar.';
    }
  } else {
    dot.className  = 'status-dot verde';
    txt.textContent = `${docs.length} documento(s) indexado(s) · ${indiceMemoria.length} chunks`;
    if (aviso) aviso.style.display = 'none';
  }
}

function atualizarStatusBase(numDocs) {
  const dot = document.getElementById('dot-base');
  const txt = document.getElementById('txt-base');
  if (numDocs === 0) {
    dot.className  = 'status-dot vermelho';
    txt.textContent = 'Base não indexada';
  } else {
    dot.className  = 'status-dot verde';
    txt.textContent = `${numDocs} documento(s) indexado(s) · ${indiceMemoria.length} chunks`;
  }
}

function atualizarHora() {
  const el = document.getElementById('txt-hora');
  if (el) {
    const agora = new Date();
    el.textContent = agora.toLocaleDateString('pt-BR') + ' ' +
      agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  }
}

/* ================================================================
   15. UTILITÁRIOS
   ================================================================ */

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}

function formatarData(iso, completo = false) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  if (completo) {
    return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', { hour:'2-digit', minute:'2-digit' });
  }
  return d.toLocaleDateString('pt-BR');
}

/* ================================================================
   FASE 2 — ANÁLISE AUTOMÁTICA POR UPLOAD
   ================================================================ */

let contextoFluxo = { tipo: null, ocasiao: null };
window._configSisTriag = {};

/* Títulos exibidos por fluxo */
const TITULOS_FLUXO = {
  PAD: {
    triagem:        { titulo:'Triagem da Ocorrência — PAD',      tipoDoc:'DESPACHO DE TRIAGEM',         seqKey:'seq_triagem' },
    admissibilidade:{ titulo:'Juízo de Admissibilidade — PAD',   tipoDoc:'DESPACHO DE ADMISSIBILIDADE', seqKey:'seq_admissibilidade' },
    julgamento:     { titulo:'Julgamento do Processo — PAD',     tipoDoc:'DECISÃO',                     seqKey:'seq_decisao_pad' },
  },
  PAR: {
    triagem:        { titulo:'Triagem da Ocorrência — PAR',      tipoDoc:'DESPACHO DE TRIAGEM',         seqKey:'seq_triagem' },
    admissibilidade:{ titulo:'Juízo de Admissibilidade — PAR',   tipoDoc:'DESPACHO DE ADMISSIBILIDADE', seqKey:'seq_admissibilidade' },
    julgamento:     { titulo:'Julgamento do PAR',                tipoDoc:'DECISÃO',                     seqKey:'seq_decisao_par' },
  },
};

/* Queries RAG por etapa (serão combinadas com termos extraídos do documento) */
const QUERIES_BASE = {
  PAD: {
    triagem:        ['prescrição pretensão punitiva servidor público Lei 8112 prazo',
                     'triagem ocorrência disciplinar instauração sindicância PAD',
                     'indícios materialidade autoria infração funcional'],
    admissibilidade:['juízo admissibilidade instauração PAD sindicância disciplinar',
                     'materialidade autoria infração funcional servidor público',
                     'prescrição punitiva prazo Lei 8112 processo disciplinar'],
    julgamento:     ['dosimetria penalidade proporcionalidade PAD julgamento',
                     'demissão suspensão advertência infração disciplinar servidor',
                     'defesa prévia contraditório ampla defesa PAD julgamento'],
  },
  PAR: {
    triagem:        ['Lei 12846 ato lesivo pessoa jurídica PAR anticorrupção',
                     'responsabilidade objetiva empresa agente público corrupção',
                     'triagem ocorrência PAR instauração admissibilidade'],
    admissibilidade:['admissibilidade PAR Lei anticorrupção instauração',
                     'nexo causal pessoa jurídica ato lesivo materialidade',
                     'prescrição PAR Lei 12846 prazo cinco anos'],
    julgamento:     ['dosimetria multa PAR faturamento bruto pessoa jurídica',
                     'programa integridade atenuante responsabilização empresa',
                     'publicação extraordinária penalidade Lei anticorrupção'],
  },
};

/* ----------------------------------------------------------------
   INÍCIO DO FLUXO — navegação da tela inicial para upload
   ---------------------------------------------------------------- */

function iniciarFluxo() {
  if (!selecaoTipo || !selecaoOcasiao) return;
  contextoFluxo = { tipo: selecaoTipo, ocasiao: selecaoOcasiao };

  const meta = TITULOS_FLUXO[selecaoTipo]?.[selecaoOcasiao];
  if (!meta) return;

  document.getElementById('upload-tipo-badge').textContent          = selecaoTipo;
  document.getElementById('upload-titulo-principal').textContent     = meta.titulo;
  document.getElementById('upload-subtitulo-principal').textContent  =
    'Envie o relatório ou expediente — a análise será gerada automaticamente';

  navegarPara('upload');
}

/* ----------------------------------------------------------------
   HANDLERS DE ARQUIVO
   ---------------------------------------------------------------- */

function handleDropAnalise(event) {
  event.preventDefault();
  document.getElementById('zona-upload-analise').classList.remove('arrastando');
  const arquivo = event.dataTransfer.files[0];
  if (arquivo) processarDocumentoAnalise(arquivo);
}

async function processarDocumentoAnalise(arquivo) {
  if (!arquivo) return;

  const ext = arquivo.name.split('.').pop().toLowerCase();
  if (!EXTENSOES_SUPORTADAS.has(ext)) {
    alert('Formato não suportado. Envie um arquivo PDF, DOCX, TXT ou MD.');
    return;
  }

  if (indiceMemoria.length === 0) {
    alert('A base de conhecimento está vazia.\nAdicione documentos na aba "Base de Conhecimento" antes de gerar análises.');
    return;
  }

  /* Modal de progresso */
  const modal  = document.getElementById('modal-processamento');
  const titulo = document.getElementById('proc-titulo');
  const status = document.getElementById('proc-status');
  const barra  = document.getElementById('proc-barra');

  modal.classList.remove('oculto');
  titulo.textContent = 'Extraindo texto do documento...';
  status.textContent = arquivo.name;
  barra.style.width  = '20%';

  let extracao;
  try {
    extracao = await lerArquivo(arquivo);
  } catch (err) {
    modal.classList.add('oculto');
    alert('Erro ao ler o arquivo: ' + err.message);
    return;
  }

  if (!extracao.texto || extracao.texto.trim().length < 80) {
    modal.classList.add('oculto');
    alert('Não foi possível extrair texto suficiente do documento.\nVerifique se o PDF é digital (não escaneado) ou tente um DOCX.');
    return;
  }

  barra.style.width  = '50%';
  titulo.textContent = 'Buscando fundamentos jurídicos...';

  const fundamentos = buscarFundamentos(extracao.texto);
  const secoes = fundamentos._secoes || {};

  barra.style.width  = '80%';
  titulo.textContent = LLM.disponivel() ? 'Gerando com modelo LLM...' : 'Montando documento...';

  const textoLLM = await gerarTextoLLM(extracao.texto, fundamentos, contextoFluxo.tipo, contextoFluxo.ocasiao);
  await gerarDocumento(arquivo.name, extracao, fundamentos, textoLLM, secoes);

  barra.style.width = '100%';
  modal.classList.add('oculto');
  navegarPara('resultado');
}

/* ================================================================
   EXTRAÇÃO ESTRUTURADA DO RELATÓRIO
   ================================================================ */

/* Padrões de seção — ordem de prioridade decrescente */
const PADROES_SECAO = {
  conclusao: [
    /(?:^|\n)\s*(?:v+i*\.?\s*)?(?:da\s+)?conclus[aã]o[\s:.\-–]/im,
    /(?:^|\n)\s*(?:v+i*\.?\s*)?(?:do\s+)?enquadramento[\s:.\-–]/im,
    /(?:^|\n)\s*(?:v+i*\.?\s*)?(?:do\s+)?julgamento[\s:.\-–]/im,
    /(?:^|\n)\s*(?:v+i*\.?\s*)?(?:da\s+)?decis[aã]o[\s:.\-–]/im,
    /(?:^|\n)\s*diante do exposto/im,
    /(?:^|\n)\s*(?:ex positis|ante o exposto)/im,
  ],
  conduta: [
    /(?:^|\n)\s*(?:i+\.?\s*)?(?:dos?\s+)?(?:fatos?|ocorr[eê]ncia)[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+\.?\s*)?(?:da\s+)?conduta[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+\.?\s*)?(?:do\s+)?relato[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+\.?\s*)?(?:da\s+)?irregularidade[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+\.?\s*)?(?:da\s+)?infra[cç][aã]o[\s:.\-–]/im,
  ],
  provas: [
    /(?:^|\n)\s*(?:i+i+\.?\s*)?(?:das?\s+)?(?:provas?|evid[eê]ncias?)[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+i+\.?\s*)?(?:dos?\s+)?ind[ií]cios?[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+i+\.?\s*)?(?:da\s+)?instru[cç][aã]o[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+i+\.?\s*)?(?:da\s+)?an[aá]lise[\s:.\-–]/im,
    /(?:^|\n)\s*(?:i+i+\.?\s*)?(?:do\s+)?m[eé]rito[\s:.\-–]/im,
  ],
};

/* Padrões de linguagem jurídica indicando conclusão/achado */
const PADROES_ACHADO = [
  /restou?\s+(?:comprovad[ao]|demonstrad[ao]|apurad[ao]|evidenciad[ao])/gi,
  /ficou?\s+(?:comprovad[ao]|demonstrad[ao]|apurad[ao]|evidenciad[ao])/gi,
  /(?:há|existem?)\s+ind[ií]cios?\s+(?:de\s+)?/gi,
  /(?:constat(?:a|ou)-?se|verifica-?se|observa-?se)\s+(?:que\s+)?/gi,
  /(?:imputad[ao]|atribu[ií]d[ao])\s+ao\s+(?:servidor|acusad[ao]|requerido)/gi,
  /a\s+conduta\s+(?:do|da|adotada)/gi,
  /(?:transgrediu|infringiu|violou|desrespeitou)\s+/gi,
  /conforme\s+(?:documentos?|autos?|provas?|registros?)/gi,
  /consoante\s+(?:documentos?|depoimentos?|provas?)/gi,
  /nos\s+termos?\s+(?:dos?\s+)?(?:autos?|processo)/gi,
];

/* Padrões para dispositivos invocados como fundamento (não mera citação) */
const PADROES_FUNDAMENTO_LEGAL = [
  /(?:nos?\s+termos?\s+do|com\s+fundamento\s+(?:no|na|nos|nas)|(?:em\s+)?face\s+do)\s+(?:art(?:igo)?\.?\s*\d+)/gi,
  /(?:incorre(?:u|ndo)|enquadra(?:ndo)?-?se)\s+(?:na?\s+)?(?:infra[cç][aã]o|conduta|hip[oó]tese)\s+(?:prevista|tipificada)/gi,
  /(?:tipifica(?:da)?|prevista)\s+(?:no|na|nos|nas)\s+art(?:igo)?\.?\s*\d+/gi,
  /(?:penalidade|san[cç][aã]o)\s+(?:de\s+)?(?:demiss[aã]o|suspens[aã]o|advertência|multa)/gi,
];

function extrairSecoesRelatorio(texto) {
  const secoes = { conduta: '', provas: '', conclusao: '', dispositivos: [] };

  // Detecta posições das seções
  const posicoes = {};
  for (const [nome, padroes] of Object.entries(PADROES_SECAO)) {
    for (const pad of padroes) {
      const m = pad.exec(texto);
      if (m) { posicoes[nome] = m.index; break; }
    }
  }

  // Extrai texto de cada seção (até a próxima seção ou fim)
  const posList = Object.entries(posicoes).sort((a, b) => a[1] - b[1]);
  for (let i = 0; i < posList.length; i++) {
    const [nome, inicio] = posList[i];
    const fim = i + 1 < posList.length ? posList[i + 1][1] : texto.length;
    secoes[nome] = texto.slice(inicio, Math.min(fim, inicio + 3000)).trim();
  }

  // Se não detectou seções, usa heurística posicional
  if (!posicoes.conclusao) {
    const pars = texto.split(/\n{2,}/).filter(p => p.trim().length > 40);
    secoes.conclusao = pars.slice(-4).join('\n\n');
  }
  if (!posicoes.conduta) {
    const pars = texto.split(/\n{2,}/).filter(p => p.trim().length > 40);
    secoes.conduta = pars.slice(0, 5).join('\n\n');
  }
  if (!posicoes.provas) {
    const pars = texto.split(/\n{2,}/).filter(p => p.trim().length > 40);
    const meio = Math.floor(pars.length / 2);
    secoes.provas = pars.slice(Math.max(0, meio - 3), meio + 3).join('\n\n');
  }

  // Extrai frases com achados de prova e conduta
  const frasesMarcantes = [];
  for (const pad of PADROES_ACHADO) {
    let m;
    pad.lastIndex = 0;
    while ((m = pad.exec(texto)) !== null) {
      // Captura a frase completa ao redor do match
      const ini = texto.lastIndexOf('\n', m.index) + 1;
      const fim = texto.indexOf('\n', m.index + m[0].length);
      const frase = texto.slice(ini, fim === -1 ? texto.length : fim).trim();
      if (frase.length > 30 && frase.length < 600) frasesMarcantes.push(frase);
      if (frasesMarcantes.length >= 12) break;
    }
  }
  secoes.frasesMarcantes = [...new Set(frasesMarcantes)].slice(0, 10);

  // Extrai dispositivos invocados como fundamento
  for (const pad of PADROES_FUNDAMENTO_LEGAL) {
    let m;
    pad.lastIndex = 0;
    while ((m = pad.exec(texto)) !== null) {
      const ini = texto.lastIndexOf('\n', m.index) + 1;
      const fim = texto.indexOf('\n', m.index + m[0].length);
      const frase = texto.slice(ini, fim === -1 ? texto.length : fim).trim();
      if (frase.length > 20 && !secoes.dispositivos.includes(frase))
        secoes.dispositivos.push(frase);
      if (secoes.dispositivos.length >= 8) break;
    }
  }

  return secoes;
}

/* ----------------------------------------------------------------
   BUSCA DE FUNDAMENTOS (RAG sobre o conteúdo do documento)
   ---------------------------------------------------------------- */

function buscarFundamentos(textoDoc) {
  const { tipo, ocasiao } = contextoFluxo;
  const queriesBase = QUERIES_BASE[tipo]?.[ocasiao] || [];

  /* Extração estruturada: seções, achados e dispositivos */
  const secoes = extrairSecoesRelatorio(textoDoc);

  /* Queries direcionadas a partir do que foi extraído */
  const queriesDirecionadas = [];

  // 1. Conclusão do relatório — maior peso, vai direto ao RAG
  if (secoes.conclusao)
    queriesDirecionadas.push(secoes.conclusao.slice(0, 600));

  // 2. Frases marcantes de conduta/prova
  if (secoes.frasesMarcantes.length > 0) {
    queriesDirecionadas.push(secoes.frasesMarcantes.slice(0, 5).join(' '));
    queriesDirecionadas.push(secoes.frasesMarcantes.slice(5).join(' '));
  }

  // 3. Seção de conduta identificada
  if (secoes.conduta)
    queriesDirecionadas.push(secoes.conduta.slice(0, 400));

  // 4. Seção de provas/instrução
  if (secoes.provas)
    queriesDirecionadas.push(secoes.provas.slice(0, 400));

  // 5. Dispositivos legais invocados como fundamento
  if (secoes.dispositivos.length > 0)
    queriesDirecionadas.push(secoes.dispositivos.join(' '));

  const queries = [...queriesBase, ...queriesDirecionadas];

  const vistos = new Set();
  const resultado = [];

  queries.forEach(q => {
    if (!q.trim()) return;
    const res = buscarRAG(q, 6);
    res.forEach(r => {
      if (!vistos.has(r.id)) {
        vistos.add(r.id);
        resultado.push(r);
      }
    });
  });

  // Ordena pelo score BM25 acumulado e retorna os melhores
  resultado.sort((a, b) => b.score - a.score);

  // Anexa as seções extraídas para uso no gerarDocumento
  resultado._secoes = secoes;

  return resultado.slice(0, 14);
}

/* ----------------------------------------------------------------
   GERAÇÃO DO DOCUMENTO
   ---------------------------------------------------------------- */

async function gerarDocumento(nomeArquivo, extracao, fundamentos, textoLLM = null, secoes = {}) {
  const { tipo, ocasiao } = contextoFluxo;
  const meta    = TITULOS_FLUXO[tipo][ocasiao];
  const config  = window._configSisTriag;
  const prefixo = config.prefixo || 'COGER-RFB';
  const ano     = new Date().getFullYear();
  const dataHoje = new Date().toLocaleDateString('pt-BR', { day:'2-digit', month:'long', year:'numeric' });

  /* Número do documento */
  const seq    = parseInt(config[meta.seqKey] || 1);
  const sufixo = meta.tipoDoc.split(' ').pop();
  const numDoc = `${prefixo ? prefixo + '-' : ''}${sufixo}-${tipo}-${String(seq).padStart(3,'0')}/${ano}`;
  await incrementarSequencia(meta.seqKey);

  /* Subtítulo da tela resultado */
  document.getElementById('resultado-subtitulo').textContent = `${meta.tipoDoc} ${tipo} — ${numDoc}`;

  const nomesCat = { normas:'Norma', pareceres:'Parecer', decisoes:'Decisão',
                     'notas-tecnicas':'Nota Técnica', orientacoes:'Orientação' };

  /* Painel de extração estruturada */
  renderizarPainelExtracao(secoes);

  /* Painel RAG */
  const painelRag = document.getElementById('painel-fundamentacao-rag');
  const listaRag  = document.getElementById('lista-fundamentacao-rag');

  if (fundamentos.length === 0) {
    painelRag.style.display = 'none';
  } else {
    painelRag.style.display = 'block';
    listaRag.innerHTML = fundamentos.map(f => `
      <div class="rag-contexto-item">
        <div class="rag-contexto-fonte">${nomesCat[f.categoria]||f.categoria} · ${escapeHtml(f.docNome)} · Chunk ${f.posicao+1}</div>
        <div class="rag-contexto-texto">${escapeHtml(f.texto.substring(0, 320))}${f.texto.length>320?'…':''}</div>
      </div>`).join('');
  }

  /* Trechos do documento (agora usando seções detectadas) */
  const paragrafos = extracao.texto.split(/\n{2,}/).map(p => p.trim()).filter(p => p.length > 40);
  const resumo = secoes.conduta  || paragrafos.slice(0, 4).join('\n\n');
  const meio   = secoes.provas   || paragrafos.slice(4, 10).join('\n\n');
  const final  = secoes.conclusao|| paragrafos.slice(-3).join('\n\n');

  /* Seção de fundamentos normativos */
  const secFund = fundamentos.length === 0 ? '' : `
    <h2>DOS FUNDAMENTOS NORMATIVOS</h2>
    <p>A análise que se segue tem por base os seguintes excertos da base de conhecimento correcional:</p>
    ${fundamentos.map(f => `
      <div class="fundamentacao-item">
        <div class="fundamentacao-fonte">${nomesCat[f.categoria]||f.categoria} — ${escapeHtml(f.docNome)}</div>
        <p>${escapeHtml(f.texto.substring(0, 500))}${f.texto.length > 500 ? '…' : ''}</p>
      </div>`).join('')}`;

  /* Corpo por fluxo */
  const corpo = montarCorpo({ tipo, ocasiao, numDoc, nomeArquivo, resumo, meio, final, secFund, dataHoje, prefixo, paginas: extracao.paginas, secoes });

  /* Fase 3: se o LLM gerou texto, usa-o como corpo principal */
  const corpoFinal = textoLLM
    ? montarCorpoLLM(textoLLM, numDoc, dataHoje, prefixo, nomeArquivo, extracao.paginas, secFund)
    : corpo;

  document.getElementById('doc-gerado-container').innerHTML =
    `<div class="doc-gerado" id="doc-imprimivel">${corpoFinal}</div>`;
}

function renderizarPainelExtracao(secoes) {
  // Painel pode não existir em versões antigas do HTML — cria dinamicamente
  let painel = document.getElementById('painel-extracao-estruturada');
  if (!painel) {
    const container = document.getElementById('painel-fundamentacao-rag')?.parentElement;
    if (!container) return;
    painel = document.createElement('div');
    painel.id = 'painel-extracao-estruturada';
    painel.className = 'painel-lateral';
    container.insertBefore(painel, container.firstChild);
  }

  const temFrases = secoes.frasesMarcantes?.length > 0;
  const temDisp   = secoes.dispositivos?.length > 0;

  if (!temFrases && !temDisp && !secoes.conclusao) {
    painel.style.display = 'none';
    return;
  }

  painel.style.display = 'block';
  painel.innerHTML = `
    <div class="painel-lateral-titulo">🔍 Extração do Relatório</div>
    ${secoes.frasesMarcantes?.length > 0 ? `
      <div class="extracao-grupo">
        <div class="extracao-label">Elementos de prova / indícios identificados</div>
        <ul class="extracao-lista">
          ${secoes.frasesMarcantes.map(f =>
            `<li>${escapeHtml(f.length > 220 ? f.slice(0, 220) + '…' : f)}</li>`
          ).join('')}
        </ul>
      </div>` : ''}
    ${secoes.dispositivos?.length > 0 ? `
      <div class="extracao-grupo">
        <div class="extracao-label">Dispositivos invocados como fundamento</div>
        <ul class="extracao-lista extracao-lista--disp">
          ${secoes.dispositivos.map(d =>
            `<li>${escapeHtml(d.length > 220 ? d.slice(0, 220) + '…' : d)}</li>`
          ).join('')}
        </ul>
      </div>` : ''}
    ${secoes.conclusao ? `
      <div class="extracao-grupo">
        <div class="extracao-label">Conclusão detectada</div>
        <div class="extracao-conclusao">${escapeHtml(secoes.conclusao.slice(0, 500))}${secoes.conclusao.length > 500 ? '…' : ''}</div>
      </div>` : ''}
  `;
}

function montarCorpo({ tipo, ocasiao, numDoc, nomeArquivo, resumo, meio, final, secFund, dataHoje, prefixo, paginas, secoes = {} }) {
  const cabecalho = `
    <h1>Receita Federal do Brasil — Corregedoria</h1>
    <div class="doc-numero">${numDoc}</div>
    <div class="doc-referencia">Ref.: ${escapeHtml(nomeArquivo)}${paginas ? ' (' + paginas + ' págs.)' : ''}</div>`;

  const rodape = `
    <div class="doc-local-data">Brasília, ${dataHoje}</div>
    <div class="doc-assinatura">
      <p>____________________________________</p>
      <p>${escapeHtml(prefixo || 'Corregedoria RFB')}</p>
    </div>`;

  const textoRelatorio = resumo
    .split('\n\n').map(p => `<p>${escapeHtml(p)}</p>`).join('');

  const textoMeio = meio
    ? meio.split('\n\n').map(p => `<p>${escapeHtml(p)}</p>`).join('') : '';

  const textoFinal = final
    ? final.split('\n\n').map(p => `<p>${escapeHtml(p)}</p>`).join('') : '';

  /* ---- PAD ---- */
  if (tipo === 'PAD' && ocasiao === 'triagem') {
    return `${cabecalho}
      <h2>DO RELATÓRIO</h2>
      ${textoRelatorio}
      ${textoMeio}
      ${secFund}
      <h2>DA ANÁLISE PRELIMINAR</h2>
      <p>Da leitura do expediente em referência, extraem-se os elementos iniciais necessários ao juízo de triagem,
      tendo em vista os requisitos de autoria, materialidade e ausência de prescrição.</p>
      ${textoFinal}
      <h2>DA CONCLUSÃO</h2>
      <p>Ante os elementos colhidos e os fundamentos normativos aplicáveis, submete-se o presente expediente
      à autoridade competente para deliberação quanto ao encaminhamento cabível.</p>
      ${rodape}`;
  }

  if (tipo === 'PAD' && ocasiao === 'admissibilidade') {
    return `${cabecalho}
      <h2>DO RELATÓRIO</h2>
      ${textoRelatorio}
      ${textoMeio}
      ${secFund}
      <h2>DOS ELEMENTOS DE ADMISSIBILIDADE</h2>
      <p>Da análise dos autos, verificam-se os pressupostos de admissibilidade relativos à
      materialidade da infração e aos indícios de autoria, conforme elementos a seguir expostos.</p>
      ${textoFinal}
      <h2>DA DECISÃO</h2>
      <p>Diante dos elementos apurados e dos fundamentos normativos aplicáveis, submete-se a presente
      decisão de admissibilidade à consideração da autoridade instauradora.</p>
      ${rodape}`;
  }

  if (tipo === 'PAD' && ocasiao === 'julgamento') {
    return `${cabecalho}
      <h2>DO RELATÓRIO</h2>
      ${textoRelatorio}
      ${textoMeio}
      ${secFund}
      <h2>DO MÉRITO E DA DOSIMETRIA</h2>
      <p>Analisados os autos do processo disciplinar, passa-se ao exame do mérito das imputações,
      com observância dos princípios da proporcionalidade e da razoabilidade na dosimetria da penalidade.</p>
      ${textoFinal}
      <h2>DA DECISÃO</h2>
      <p>Pelo exposto, à luz das provas produzidas nos autos e dos fundamentos normativos e jurisprudenciais
      aplicáveis, decide-se conforme deliberação da autoridade julgadora.</p>
      ${rodape}`;
  }

  /* ---- PAR ---- */
  if (tipo === 'PAR' && ocasiao === 'triagem') {
    return `${cabecalho}
      <h2>DO RELATÓRIO</h2>
      ${textoRelatorio}
      ${textoMeio}
      ${secFund}
      <h2>DA ANÁLISE PRELIMINAR — LEI Nº 12.846/2013</h2>
      <p>Do exame do expediente, verificam-se os elementos iniciais para o juízo de triagem acerca
      da prática de ato lesivo à Administração Pública, nos termos do art. 5º da Lei nº 12.846/2013.</p>
      ${textoFinal}
      <h2>DA CONCLUSÃO</h2>
      <p>Ante os elementos colhidos, submete-se o expediente à autoridade competente para deliberação
      quanto à instauração ou arquivamento do processo de responsabilização.</p>
      ${rodape}`;
  }

  if (tipo === 'PAR' && ocasiao === 'admissibilidade') {
    return `${cabecalho}
      <h2>DO RELATÓRIO</h2>
      ${textoRelatorio}
      ${textoMeio}
      ${secFund}
      <h2>DOS ELEMENTOS DE ADMISSIBILIDADE — PAR</h2>
      <p>Da análise dos elementos apurados, examina-se o preenchimento dos requisitos de admissibilidade
      para a instauração do Processo Administrativo de Responsabilização, nos termos da Lei nº 12.846/2013
      e do Decreto nº 8.420/2015.</p>
      ${textoFinal}
      <h2>DA DECISÃO</h2>
      <p>Com base nos elementos analisados e nos fundamentos normativos aplicáveis, delibera-se quanto
      à instauração ou arquivamento do PAR.</p>
      ${rodape}`;
  }

  if (tipo === 'PAR' && ocasiao === 'julgamento') {
    return `${cabecalho}
      <h2>DO RELATÓRIO</h2>
      ${textoRelatorio}
      ${textoMeio}
      ${secFund}
      <h2>DO MÉRITO E DA DOSIMETRIA DA MULTA</h2>
      <p>Comprovada a prática do ato lesivo, procede-se à dosimetria da penalidade de multa,
      com observância dos critérios previstos no art. 7º da Lei nº 12.846/2013 e nos arts. 17 a 21
      do Decreto nº 8.420/2015, considerando o porte da pessoa jurídica, o programa de integridade
      e as demais circunstâncias relevantes.</p>
      ${textoFinal}
      <h2>DA DECISÃO</h2>
      <p>Pelo exposto, delibera-se sobre a responsabilização da pessoa jurídica e a aplicação das
      sanções cabíveis, nos termos da legislação aplicável.</p>
      ${rodape}`;
  }

  return '<p>Fluxo não reconhecido.</p>';
}


/* Monta o documento quando o LLM gerou o corpo — Fase 3 */
function montarCorpoLLM(textoGerado, numDoc, dataHoje, prefixo, nomeArquivo, paginas, secFund) {
  return `
    <h1>Receita Federal do Brasil — Corregedoria</h1>
    <div class="doc-numero">${numDoc}</div>
    <div class="doc-referencia">Ref.: ${escapeHtml(nomeArquivo)}${paginas ? ' (' + paginas + ' págs.)' : ''}</div>
    ${textoGerado.split('\n').map(p => p.trim() ? `<p>${escapeHtml(p)}</p>` : '').join('')}
    ${secFund}
    <div class="doc-local-data">Brasília, ${dataHoje}</div>
    <div class="doc-assinatura">
      <p>____________________________________</p>
      <p>${escapeHtml(prefixo || 'Corregedoria RFB')}</p>
    </div>`;
}

/* ----------------------------------------------------------------
   EXPORTAÇÃO
   ---------------------------------------------------------------- */

function imprimirDocumento() {
  const conteudo = document.getElementById('doc-imprimivel');
  if (!conteudo) return;
  const janela = window.open('', '_blank', 'width=900,height=700');
  janela.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8">
    <title>Documento SisTriag-Coger</title>
    <style>
      body { font-family:'Times New Roman',serif; font-size:13px; line-height:1.7;
             color:#1a1a1a; padding:48px 56px; max-width:800px; margin:0 auto; }
      h1 { font-size:14px; text-align:center; text-transform:uppercase; letter-spacing:.08em; margin-bottom:4px; }
      h2 { font-size:13px; text-transform:uppercase; border-bottom:1px solid #ccc; padding-bottom:4px; margin:20px 0 8px; }
      p  { text-align:justify; margin-bottom:10px; }
      .doc-numero     { text-align:center; font-weight:700; margin-bottom:24px; }
      .doc-referencia { text-align:center; color:#555; font-size:12px; margin-bottom:24px; }
      .fundamentacao-item { background:#f8f9fa; border-left:3px solid #2d6ea8; padding:10px 14px; margin-bottom:10px; font-size:12px; }
      .fundamentacao-fonte{ font-size:11px; color:#666; font-style:italic; margin-bottom:4px; }
      .doc-local-data { text-align:right; margin-bottom:32px; font-size:12px; }
      .doc-assinatura { text-align:center; margin-top:40px; }
      @media print { body { padding:20px; } }
    </style></head><body>
    ${conteudo.innerHTML}
    </body></html>`);
  janela.document.close();
  setTimeout(() => janela.print(), 400);
}

function copiarTextoDocumento() {
  const conteudo = document.getElementById('doc-imprimivel');
  if (!conteudo) return;
  const texto = conteudo.innerText;
  navigator.clipboard.writeText(texto).then(() => {
    alert('Texto copiado para a área de transferência.');
  }).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = texto;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    alert('Texto copiado.');
  });
}

/* ----------------------------------------------------------------
   SEQUÊNCIA DE NUMERAÇÃO
   ---------------------------------------------------------------- */

async function carregarConfigEmMemoria() {
  const chaves = ['prefixo','seq_triagem','seq_admissibilidade','seq_decisao_pad','seq_decisao_par'];
  for (const c of chaves) {
    window._configSisTriag[c] = await getConfig(c, c.startsWith('seq') ? 1 : '');
  }
}

async function incrementarSequencia(chave) {
  const atual = parseInt(window._configSisTriag[chave] || 1);
  const prox  = atual + 1;
  window._configSisTriag[chave] = prox;
  await setConfig(chave, prox);
  const mapa = {
    seq_triagem:'cfg-seq-triagem', seq_admissibilidade:'cfg-seq-admiss',
    seq_decisao_pad:'cfg-seq-decisao-pad', seq_decisao_par:'cfg-seq-decisao-par',
  };
  const el = document.getElementById(mapa[chave]);
  if (el) el.value = prox;
}

/* ================================================================
   16. IMPORTAR PASTA LOCAL (File System Access API)
   ================================================================ */

let pastaHandleAtual = null; // FileSystemDirectoryHandle em memória

const MAPA_CATEGORIAS_PASTA = {
  'normas':        'normas', 'norma':'normas', 'legislacao':'normas', 'leis':'normas', 'lei':'normas',
  'pareceres':     'pareceres', 'parecer':'pareceres',
  'decisoes':      'decisoes', 'decisao':'decisoes', 'julgados':'decisoes', 'jurisprudencia':'decisoes', 'acordaos':'decisoes',
  'notas-tecnicas':'notas-tecnicas', 'notas_tecnicas':'notas-tecnicas', 'notas tecnicas':'notas-tecnicas',
  'notas':         'notas-tecnicas', 'nota-tecnica':'notas-tecnicas', 'nota_tecnica':'notas-tecnicas',
  'orientacoes':   'orientacoes', 'orientacao':'orientacoes', 'treinamentos':'orientacoes',
  'treinamento':   'orientacoes', 'manual':'orientacoes', 'manuais':'orientacoes', 'guias':'orientacoes',
};

function detectarCategoriaPasta(nomePasta) {
  const chave = nomePasta.toLowerCase().trim()
    .normalize('NFD').replace(/[̀-ͯ]/g, '');
  return MAPA_CATEGORIAS_PASTA[chave] || null;
}

// Varre recursivamente um diretório já dentro de uma categoria reconhecida
async function varrerArquivosRecursivo(dirHandle, categoria, arquivos) {
  for await (const [nome, handle] of dirHandle) {
    if (handle.kind === 'file') {
      const ext = nome.split('.').pop().toLowerCase();
      if (EXTENSOES_SUPORTADAS.has(ext)) {
        const file = await handle.getFile();
        arquivos.push({ file, categoria });
      }
    } else if (handle.kind === 'directory') {
      // Desce em qualquer subpasta dentro da categoria, sem limite de profundidade
      await varrerArquivosRecursivo(handle, categoria, arquivos);
    }
  }
}

async function varrerDiretorio(dirHandle, categoriaForçada = null) {
  const arquivos = []; // { file, categoria }
  for await (const [nome, handle] of dirHandle) {
    if (handle.kind === 'directory') {
      const cat = detectarCategoriaPasta(nome);
      if (cat) {
        // Pasta de categoria reconhecida: varre recursivamente todo o conteúdo
        await varrerArquivosRecursivo(handle, cat, arquivos);
      }
      // Subpastas com nome não reconhecido na raiz são ignoradas
    } else if (handle.kind === 'file' && categoriaForçada) {
      const ext = nome.split('.').pop().toLowerCase();
      if (ext === 'pdf' || ext === 'docx') {
        const file = await handle.getFile();
        arquivos.push({ file, categoria: categoriaForçada });
      }
    }
  }
  return arquivos;
}

async function importarPastaLocal() {
  if (!('showDirectoryPicker' in window)) {
    document.getElementById('pasta-compat').textContent =
      '⚠ Recurso disponível apenas no Chrome/Edge 86+. No Firefox, use o upload individual.';
    document.getElementById('pasta-compat').style.color = 'var(--amarelo)';
    return;
  }

  let dirHandle;
  try {
    dirHandle = await window.showDirectoryPicker({ mode: 'read' });
  } catch (e) {
    if (e.name !== 'AbortError') console.error(e);
    return;
  }

  pastaHandleAtual = dirHandle;

  // Varre a pasta
  const modal = document.getElementById('modal-processamento');
  const titulo = document.getElementById('proc-titulo');
  const status = document.getElementById('proc-status');
  const barra  = document.getElementById('proc-barra');
  modal.classList.remove('oculto');
  titulo.textContent = 'Escaneando pasta...';
  status.textContent = dirHandle.name;
  barra.style.width = '5%';

  const itens = await varrerDiretorio(dirHandle);

  if (itens.length === 0) {
    modal.classList.add('oculto');
    alert('Nenhum arquivo suportado (PDF, DOCX, TXT, MD) encontrado em subpastas reconhecidas.\n\nVerifique se a estrutura de pastas segue o padrão indicado.');
    return;
  }

  // Verifica quais já existem (pelo nome+tamanho)
  const docsExistentes = await txGetAll('documentos');
  const idsExistentes = new Set(docsExistentes.map(d => d.nome + '_' + (d.tamanho || 0)));

  const novos    = itens.filter(i => !idsExistentes.has(i.file.name + '_' + i.file.size));
  const jaExistem = itens.length - novos.length;

  barra.style.width = '10%';

  // Agrupa por categoria para indexação em lotes
  const porCategoria = {};
  novos.forEach(({ file, categoria }) => {
    if (!porCategoria[categoria]) porCategoria[categoria] = [];
    porCategoria[categoria].push(file);
  });

  const resumo = []; // { categoria, novos, chunks, erros }

  let catIndex = 0;
  const totalCats = Object.keys(porCategoria).length;

  for (const [cat, arquivos] of Object.entries(porCategoria)) {
    titulo.textContent = `Indexando: ${cat} (${catIndex + 1}/${totalCats})`;
    const resultados = await indexarArquivos(arquivos, cat);
    const ok     = resultados.filter(r => r.ok);
    const erros  = resultados.filter(r => !r.ok);
    const chunks = ok.reduce((s, r) => s + (r.chunks || 0), 0);
    resumo.push({ categoria: cat, novos: ok.length, chunks, erros: erros.length });
    catIndex++;
    barra.style.width = (10 + Math.round(catIndex / totalCats * 85)) + '%';
  }

  barra.style.width = '100%';
  modal.classList.add('oculto');

  // Atualiza info pasta ativa
  const totalNovos  = resumo.reduce((s, r) => s + r.novos, 0);
  const totalChunks = resumo.reduce((s, r) => s + r.chunks, 0);
  const totalErros  = resumo.reduce((s, r) => s + r.erros, 0);

  document.getElementById('pasta-ativa-container').style.display = 'flex';
  document.getElementById('pasta-ativa-nome').textContent = '📂 ' + dirHandle.name;
  document.getElementById('pasta-ativa-stats').textContent =
    `${totalNovos} novos · ${jaExistem} já existiam · ${totalChunks} chunks · ${totalErros} erros`;
  document.getElementById('btn-resync').style.display = 'inline-flex';

  // Exibe resumo por categoria
  if (resumo.length > 0) {
    const nomesCat = {
      'normas':'Normas','pareceres':'Pareceres','decisoes':'Decisões',
      'notas-tecnicas':'Notas Técnicas','orientacoes':'Orientações'
    };
    const container = document.getElementById('resumo-importacao-container');
    container.style.display = 'block';
    container.innerHTML = `
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--azul-acento);margin-bottom:8px;margin-top:8px">
        Resumo da importação
      </div>
      ${resumo.map(r => `
        <div class="resumo-linha">
          <span class="resumo-cat">${nomesCat[r.categoria]||r.categoria}</span>
          <span class="resumo-nums">
            <span>${r.novos} doc${r.novos!==1?'s':''}</span>
            <span>${r.chunks} chunks</span>
            ${r.erros ? `<span style="color:var(--vermelho-claro)">${r.erros} erro${r.erros!==1?'s':''}</span>` : ''}
          </span>
        </div>
      `).join('')}
      ${jaExistem > 0 ? `<div style="font-size:11px;color:var(--cinza-texto);margin-top:6px">ℹ ${jaExistem} arquivo(s) já estavam indexados e foram ignorados.</div>` : ''}
    `;
  }

  await renderizarBase();
  await atualizarStatusRodape();
}

async function resincronizarPasta() {
  if (!pastaHandleAtual) {
    alert('Nenhuma pasta ativa nesta sessão. Use "Importar Pasta Local" para selecionar.');
    return;
  }
  // Re-usa o handle já obtido
  await importarPastaLocalComHandle(pastaHandleAtual);
}

async function importarPastaLocalComHandle(dirHandle) {
  pastaHandleAtual = dirHandle;
  await importarPastaLocal._comHandle(dirHandle); // alias; na prática basta chamar de novo
}

// Verifica compatibilidade ao carregar a tela base
function verificarCompatibilidadePasta() {
  const el = document.getElementById('pasta-compat');
  if (!el) return;
  if (!('showDirectoryPicker' in window)) {
    el.textContent = '⚠ Importação de pasta disponível apenas no Chrome/Edge 86+';
    el.style.color = 'var(--amarelo)';
    document.getElementById('btn-importar-pasta').disabled = true;
    document.getElementById('btn-importar-pasta').style.opacity = '0.5';
  } else {
    el.textContent = '✓ Chrome/Edge detectado — recurso disponível';
    el.style.color = 'var(--verde-claro)';
  }
}

/* ================================================================
   17. INICIALIZAÇÃO
   ================================================================ */

async function inicializar() {
  try {
    await abrirDB();
    inicializarPDFJS();
    await carregarIndiceMemoria();
    await carregarConfigEmMemoria();
    await atualizarStatusRodape();
    setInterval(atualizarHora, 1000);
    atualizarHora();
    verificarCompatibilidadePasta();
    // Atualiza status do motor de análise no rodapé
    atualizarModoRodape();

    // Verifica se base está vazia para mostrar orientação
    const docs = await txGetAll('documentos');
    if (docs.length === 0) {
      document.getElementById('aviso-base').style.display = 'flex';
    }

    console.log(`[SisTriag-Coger] Inicializado — ${docs.length} documentos, ${indiceMemoria.length} chunks em memória`);
  } catch (err) {
    console.error('[SisTriag-Coger] Erro na inicialização:', err);
    document.body.insertAdjacentHTML('afterbegin', `
      <div style="background:#b84040;color:#fff;padding:12px 24px;font-size:13px;text-align:center">
        Erro ao inicializar o sistema: ${err.message} — Verifique se o navegador suporta IndexedDB.
      </div>
    `);
  }
}

inicializar();

/* ================================================================
   18. FASE 3 — STUB WEBLLM
   ================================================================
   Este módulo será preenchido na Fase 3.
   A interface abaixo já está integrada ao fluxo de análise:
   processarDocumentoAnalise() chama gerarTextoLLM() antes de
   montar o documento. Enquanto o modelo não estiver carregado,
   a função retorna null e o sistema usa o template da Fase 2.
   ================================================================ */

const LLM = {
  modelo:    null,   // instância WebLLM quando carregada
  nomeAtivo: null,   // string com o nome do modelo ativo
  carregando: false,

  /* Modelos disponíveis — preencher na Fase 3 */
  catalogo: [
    { id: 'Llama-3.1-8B-Instruct-q4f32_1-MLC', nome: 'Llama 3.1 8B (padrão)',    tamanho: '~4,7 GB', contexto: '8k tokens' },
    { id: 'Phi-3.5-mini-instruct-q4f16_1-MLC', nome: 'Phi-3.5 Mini (mais leve)', tamanho: '~2,2 GB', contexto: '128k tokens' },
    { id: 'gemma-2-2b-it-q4f16_1-MLC',         nome: 'Gemma 2 2B (mais rápido)', tamanho: '~1,5 GB', contexto: '8k tokens' },
  ],

  /* Retorna true se há um modelo carregado e pronto */
  disponivel() { return this.modelo !== null; },

  /* Fase 3: inicializar WebLLM e carregar modelo
  async carregar(modelId, onProgresso) {
    this.carregando = true;
    const { CreateMLCEngine } = await import('https://esm.run/@mlc-ai/web-llm');
    this.modelo = await CreateMLCEngine(modelId, {
      initProgressCallback: (p) => onProgresso && onProgresso(p)
    });
    this.nomeAtivo = modelId;
    this.carregando = false;
  },
  */

  /* Fase 3: gerar texto dado um prompt
  async gerar(systemPrompt, userPrompt) {
    if (!this.modelo) return null;
    const resp = await this.modelo.chat.completions.create({
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user',   content: userPrompt  },
      ],
      temperature: 0.3,
      max_tokens:  2048,
    });
    return resp.choices[0].message.content;
  },
  */
};

/* Ponto de integração — chamado por processarDocumentoAnalise()
   Fase 2: retorna null → usa montarCorpo() (template fixo)
   Fase 3: retorna string com o texto gerado pelo LLM            */
async function gerarTextoLLM(textoDoc, fundamentos, tipo, ocasiao) {
  if (!LLM.disponivel()) return null;

  /* Fase 3 — descomentar:
  const sistemaPrompt = construirSystemPrompt(tipo, ocasiao);
  const userPrompt    = construirUserPrompt(textoDoc, fundamentos);
  return await LLM.gerar(sistemaPrompt, userPrompt);
  */

  return null;
}

/* Prompts — prontos para preencher na Fase 3 */
function construirSystemPrompt(tipo, ocasiao) {
  const base = `Você é um assistente jurídico especializado em direito disciplinar e anticorrupção
da Corregedoria da Receita Federal do Brasil. Redige documentos formais em português jurídico,
de forma objetiva, clara e fundamentada. Nunca inventa fatos — usa apenas o que está no
expediente fornecido e nos excertos da base de conhecimento.`;

  const contextos = {
    'PAD-triagem':         'Você vai redigir um Despacho de Triagem de PAD.',
    'PAD-admissibilidade': 'Você vai redigir um Despacho de Juízo de Admissibilidade de PAD.',
    'PAD-julgamento':      'Você vai redigir uma Decisão de Julgamento de PAD.',
    'PAR-triagem':         'Você vai redigir um Despacho de Triagem de PAR (Lei 12.846/2013).',
    'PAR-admissibilidade': 'Você vai redigir um Despacho de Admissibilidade de PAR.',
    'PAR-julgamento':      'Você vai redigir uma Decisão de Julgamento de PAR.',
  };

  return `${base}\n\n${contextos[`${tipo}-${ocasiao}`] || ''}`;
}

function construirUserPrompt(textoDoc, fundamentos) {
  const nomesCat = { normas:'Norma', pareceres:'Parecer', decisoes:'Decisão',
                     'notas-tecnicas':'Nota Técnica', orientacoes:'Orientação/Modelo' };
  const fundStr = fundamentos.map(f =>
    `[${nomesCat[f.categoria]||f.categoria} — ${f.docNome}]\n${f.texto.substring(0, 600)}`
  ).join('\n\n---\n\n');

  return `## EXPEDIENTE / RELATÓRIO DE INVESTIGAÇÃO\n\n${textoDoc.substring(0, 6000)}\n\n` +
         `## BASE DE CONHECIMENTO — EXCERTOS RELEVANTES\n\n${fundStr}\n\n` +
         `## INSTRUÇÃO\nRedija o documento formal completo, com todas as seções pertinentes, ` +
         `usando linguagem jurídica adequada e referenciando os fundamentos normativos acima quando aplicável.`;
}

/* Atualiza o indicador de modo no rodapé */
function atualizarModoRodape() {
  const el = document.getElementById('txt-modelo');
  if (!el) return;
  if (LLM.disponivel()) {
    el.innerHTML = `Modelo ativo <span class="modo-badge llm">LLM</span> — ${LLM.nomeAtivo}`;
    const dot = document.getElementById('dot-modelo');
    if (dot) dot.className = 'status-dot verde';
  } else {
    el.innerHTML = `Modo RAG + template <span class="modo-badge rag">RAG</span>`;
  }
}
