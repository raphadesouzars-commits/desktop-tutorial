/**
 * Tarjamento Coger — Ferramenta de Tarjamento Automático de PDF
 * Corregedoria da Receita Federal do Brasil
 * Aplicação 100% client-side, sem envio de dados pela rede.
 */

'use strict';

// ─── Estado global ────────────────────────────────────────────────────────────
const App = {
  etapaAtual: 1,
  pdfBytes: null,
  pdfNome: '',
  pdfDoc: null,
  totalPaginas: 0,
  paginaAtual: 1,
  escala: 1.5,
  escalaAtual: 1.5,
  viewportAtual: null,

  contexto: { julgado: 'nao', assedio: false },
  termos: [],
  regrasAtivas: new Set(),

  // Map<pagina, Array<Marcacao>>
  marcacoesPorPagina: new Map(),
  // Map<pagina, { indice: Array<{item, charOffset}>, textoPlano: string, viewport }>
  textoPorPagina: new Map(),

  modoSelecao: false,
  tesseractWorker: null,
};

// ─── Regras de detecção automática ───────────────────────────────────────────
const REGRAS = [
  {
    id: 'cpf',
    nome: 'CPF',
    // Aceita com e sem pontuação, com espaços entre partes (OCR às vezes insere espaços)
    regex: /\b\d{3}[\s.]?\d{3}[\s.]?\d{3}[\s\-]?\d{2}\b/g,
    tratamento: 'descaracterizar',
    ativa: true,
  },
  {
    id: 'cnpj',
    nome: 'CNPJ',
    regex: /\b\d{2}[\s.]?\d{3}[\s.]?\d{3}[\s\/]?\d{4}[\s\-]?\d{2}\b/g,
    tratamento: 'tarjar',
    ativa: false,
  },
  {
    id: 'rg',
    nome: 'RG / Identidade',
    regex: /(?:R\.?G\.?|Identidade|Cédula de Identidade)[:\s#nNºo°]*([0-9]{1,2}[\s.]?[0-9]{3}[\s.]?[0-9]{3}[\s\-]?[0-9A-Za-z])/gi,
    tratamento: 'tarjar',
    ativa: true,
  },
  {
    id: 'matricula',
    nome: 'Matrícula / SIAPE',
    regex: /(?:matr[íi]cula|SIAPE)[:\s#nNºo°]*([0-9]{6,8})/gi,
    tratamento: 'tarjar',
    ativa: true,
  },
  {
    id: 'conta',
    nome: 'Conta Bancária / Agência',
    regex: /(?:ag[eê]ncia|conta(?:\s+corrente|\s+poupan[çc]a)?)[:\s#nNºo°]*([0-9]{3,6}[\s\-]?[0-9X])/gi,
    tratamento: 'tarjar',
    ativa: true,
  },
  {
    id: 'nascimento',
    nome: 'Data de Nascimento',
    regex: /(?:nasc(?:ido|eu|imento)?(?:\s+em)?|data\s+de\s+nascimento)[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})/gi,
    tratamento: 'tarjar',
    ativa: true,
  },
  {
    id: 'email',
    nome: 'E-mail',
    regex: /\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b/g,
    tratamento: 'tarjar',
    ativa: true,
    filtro: (m) => !m.toLowerCase().includes('@receita.fazenda.gov.br') && !m.toLowerCase().includes('@rfb.gov.br'),
  },
  {
    id: 'telefone',
    nome: 'Telefone',
    regex: /(?:\+?55[\s\-]?)?(?:\(?[0-9]{2}\)?[\s\-]?)?(?:9[\s]?)?[0-9]{4}[\s\-]?[0-9]{4}/g,
    tratamento: 'tarjar',
    ativa: true,
  },
  {
    id: 'endereco',
    nome: 'Endereço Residencial',
    regex: /(?:Rua|Av\.|Avenida|Travessa|Alameda|Estrada|R\.)\s+[A-Za-zÀ-ú\s]{3,40},?\s*n[°º]?\s*[0-9]+/gi,
    tratamento: 'tarjar',
    ativa: true,
  },
  {
    id: 'saude',
    nome: 'Palavras-chave de Saúde',
    regex: /\b(CID[\s\-]?[A-Z][0-9]+|atestado\s+m[eé]dico|laudo\s+m[eé]dico|afastamento\s+por|diagn[oó]stico|gestante|gravidez|licen[çc]a[\s\-]saúde|saúde\s+mental|transtorno|depress[aãa]o|ansiedade)\b/gi,
    tratamento: 'tarjar',
    ativa: true,
  },
];

const IDENTIFICADORES_INDIRETOS = [
  /\bcargo\b/i, /\blota[çc][aã]o\b/i, /\bsetor\b/i, /\bunidade\b/i,
  /\bcomiss[aã]o\b/i, /\d{1,2}\/\d{1,2}\/\d{2,4}/,
  /\bn[°º\.]\s*(?:processo|proc\.?)\b/i, /\bfilia[çc][aã]o\b/i,
];

// ─── Inicialização ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  inicializarRegrasAtivas();
  configurarUpload();
  configurarFormularioEtapa2();
  configurarBotoesNavegacao();
  renderizarListaRegras();
});

function inicializarRegrasAtivas() {
  REGRAS.forEach(r => { if (r.ativa) App.regrasAtivas.add(r.id); });
}

// ─── ETAPA 1: Upload ──────────────────────────────────────────────────────────
function configurarUpload() {
  const area = document.getElementById('area-upload');
  const input = document.getElementById('input-arquivo');

  area.addEventListener('click', () => input.click());
  area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('drag-over'); });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault();
    area.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) processarArquivo(file);
  });
  input.addEventListener('change', e => {
    if (e.target.files[0]) processarArquivo(e.target.files[0]);
  });
}

async function processarArquivo(file) {
  if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
    mostrarAlerta('erro', 'Arquivo inválido. Por favor, selecione um arquivo PDF.');
    return;
  }
  exibirCarregando(true, 'Lendo arquivo PDF...');
  try {
    const bytes = await lerArquivoComoArrayBuffer(file);
    App.pdfBytes = new Uint8Array(bytes);
    App.pdfNome = file.name;
    const loadingTask = pdfjsLib.getDocument({ data: App.pdfBytes });
    App.pdfDoc = await loadingTask.promise;
    App.totalPaginas = App.pdfDoc.numPages;

    document.getElementById('nome-arquivo').textContent = file.name;
    document.getElementById('paginas-arquivo').textContent = `${App.totalPaginas} página(s)`;
    document.getElementById('tamanho-arquivo').textContent = formatarTamanho(file.size);
    document.getElementById('info-arquivo').classList.add('visivel');
    document.getElementById('btn-avancar-etapa1').disabled = false;
  } catch (err) {
    console.error('Erro ao abrir PDF:', err);
    let msg = 'Não foi possível abrir o PDF.';
    if (typeof pdfjsLib === 'undefined') {
      msg = 'A biblioteca PDF.js não foi carregada. Verifique sua conexão com a internet e recarregue a página.';
    } else if (err && err.name === 'PasswordException') {
      msg = 'O PDF está protegido por senha. Remova a senha antes de processar.';
    } else if (err && err.name === 'InvalidPDFException') {
      msg = 'O arquivo não é um PDF válido ou está corrompido.';
    }
    mostrarAlerta('erro', msg);
  } finally {
    exibirCarregando(false);
  }
}

function lerArquivoComoArrayBuffer(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

// ─── ETAPA 2: Formulário ──────────────────────────────────────────────────────
function configurarFormularioEtapa2() {
  [
    ['btn-add-investigado', 'investigado', 'lista-investigados'],
    ['btn-add-vitima',      'vitima',      'lista-vitimas'],
    ['btn-add-testemunha',  'testemunha',  'lista-testemunhas'],
    ['btn-add-denunciante', 'denunciante', 'lista-denunciantes'],
    ['btn-add-terceiro',    'terceiro',    'lista-terceiros'],
    ['btn-add-livre',       'livre',       'lista-livres'],
  ].forEach(([btnId, papel, listaId]) => {
    document.getElementById(btnId).addEventListener('click', () =>
      adicionarTermoPapel(papel, listaId));
  });

  document.querySelectorAll('input[name="julgado"]').forEach(el =>
    el.addEventListener('change', () => { App.contexto.julgado = el.value; atualizarTagInvestigado(); }));
  document.querySelectorAll('input[name="assedio"]').forEach(el =>
    el.addEventListener('change', () => { App.contexto.assedio = el.value === 'sim'; }));
}

function atualizarTagInvestigado() {
  const tag = document.getElementById('tag-investigado');
  if (!tag) return;
  const isManter = App.contexto.julgado === 'sancionado';
  tag.textContent = isManter ? 'Manter' : 'Tarjar';
  tag.className = 'tag-tratamento ' + (isManter ? 'tag-manter' : 'tag-tarjar');
}

function tratamentoPorPapel(papel) {
  if (papel === 'investigado') return App.contexto.julgado === 'sancionado' ? 'manter' : 'tarjar';
  return 'tarjar';
}

function adicionarTermoPapel(papel, listaId) {
  const lista = document.getElementById(listaId);
  const div = document.createElement('div');
  div.className = 'item-termo';
  div.innerHTML = `
    <input type="text" placeholder="Nome ou termo..." class="input-termo" data-papel="${papel}">
    <select class="select-busca" title="Tipo de busca">
      <option value="exata">Palavra exata</option>
      <option value="substring">Substring</option>
    </select>
    <button class="btn-remover-termo" title="Remover" onclick="this.closest('.item-termo').remove()">✕</button>
  `;
  lista.appendChild(div);
  div.querySelector('.input-termo').focus();
}

function coletarTermosFormulario() {
  App.termos = [];
  document.querySelectorAll('.input-termo').forEach(input => {
    const val = input.value.trim();
    if (!val) return;
    const papel = input.dataset.papel;
    const busca = input.closest('.item-termo').querySelector('.select-busca').value;
    val.split(',').forEach(t => {
      const termo = t.trim();
      if (!termo) return;
      App.termos.push({ termo, papel, tratamento: tratamentoPorPapel(papel), buscaExata: busca === 'exata' });
    });
  });
}

// ─── ETAPA 3: Pré-processamento ───────────────────────────────────────────────
const OCR_SCALE = 2.0; // escala usada para renderizar o canvas do OCR

async function executarPreProcessamento() {
  coletarTermosFormulario();
  App.marcacoesPorPagina.clear();
  App.textoPorPagina.clear();

  document.getElementById('barra-progresso-container').style.display = 'block';
  atualizarProgresso(0, `Iniciando (0 / ${App.totalPaginas} páginas)...`);

  // Inicializar worker Tesseract uma vez para todas as páginas (mais eficiente)
  let tesseractWorker = null;
  if (typeof Tesseract !== 'undefined') {
    try {
      atualizarProgresso(2, 'Inicializando OCR (Tesseract.js)...');
      tesseractWorker = await Tesseract.createWorker('por', 1, {
        logger: () => {},
      });
    } catch (e) {
      console.warn('Não foi possível inicializar Tesseract:', e);
    }
  }

  for (let p = 1; p <= App.totalPaginas; p++) {
    const pct = Math.round(((p - 1) / App.totalPaginas) * 88) + 2;
    atualizarProgresso(pct, `Analisando página ${p} de ${App.totalPaginas}...`);

    const page = await App.pdfDoc.getPage(p);

    // ── Extrair texto nativo via PDF.js ──────────────────────────────────────
    const textContent = await page.getTextContent();
    // viewport scale=1.0 → coordenadas em "pontos PDF" convertidos para canvas
    const viewport1 = page.getViewport({ scale: 1.0 });

    // Construir índice de posições com rastreamento de offset de caractere
    // Cada entrada: { texto, x, y, largura, altura, charStart, charEnd }
    const indice = [];
    let textoPlano = '';

    textContent.items.forEach(item => {
      if (!item.str) return;
      // Aplicar transform do viewport para obter coordenadas de canvas
      const tx = pdfjsLib.Util.transform(viewport1.transform, item.transform);
      const x = tx[4];
      // tx[5] é a posição Y do baseline no canvas (Y cresce para baixo)
      // Subtraímos item.height para chegar ao TOPO da caixa de texto
      // Usamos abs() porque fontes rotacionadas podem dar valores negativos
      const alturaReal = Math.abs(item.height) || Math.abs(tx[3]) || 12;
      const y = tx[5] - alturaReal;
      const largura = Math.abs(item.width) || 10;

      const charStart = textoPlano.length;
      // Adicionar o texto sem espaço extra — espaço será adicionado depois
      // mas guardamos o offset ANTES do espaço
      textoPlano += item.str;
      const charEnd = textoPlano.length;
      // Separador entre itens (espaço) para evitar colagem de palavras
      textoPlano += ' ';

      indice.push({ texto: item.str, x, y, largura, altura: alturaReal, charStart, charEnd });
    });

    const temTextoNativo = textoPlano.trim().replace(/\s+/g, '').length > 20;

    // ── OCR para páginas escaneadas ───────────────────────────────────────────
    if (!temTextoNativo && tesseractWorker) {
      atualizarProgresso(pct + 2, `OCR na página ${p}...`);
      try {
        // Renderizar página em alta resolução para o OCR
        const vpOcr = page.getViewport({ scale: OCR_SCALE });
        const cvOcr = document.createElement('canvas');
        cvOcr.width = vpOcr.width;
        cvOcr.height = vpOcr.height;
        const ctxOcr = cvOcr.getContext('2d');
        // Fundo branco (melhora o OCR)
        ctxOcr.fillStyle = '#fff';
        ctxOcr.fillRect(0, 0, cvOcr.width, cvOcr.height);
        await page.render({ canvasContext: ctxOcr, viewport: vpOcr }).promise;

        const resultado = await tesseractWorker.recognize(cvOcr);

        resultado.data.words.forEach(word => {
          if (!word.text || !word.text.trim()) return;

          // CORREÇÃO CRÍTICA: coordenadas do Tesseract estão no espaço do canvas OCR
          // (escala OCR_SCALE). Dividimos por OCR_SCALE para converter para escala 1.0
          const x = word.bbox.x0 / OCR_SCALE;
          const y = word.bbox.y0 / OCR_SCALE;
          const largura = (word.bbox.x1 - word.bbox.x0) / OCR_SCALE;
          const altura = (word.bbox.y1 - word.bbox.y0) / OCR_SCALE;

          const charStart = textoPlano.length;
          textoPlano += word.text;
          const charEnd = textoPlano.length;
          textoPlano += ' ';

          indice.push({ texto: word.text, x, y, largura, altura, charStart, charEnd, deOcr: true });
        });
      } catch (e) {
        console.warn(`OCR falhou na página ${p}:`, e);
      }
    }

    App.textoPorPagina.set(p, { indice, textoPlano, viewport: viewport1 });

    const marcacoes = [];
    detectarPadroesAutomaticos(p, textoPlano, indice, marcacoes);
    detectarTermosCadastrados(p, textoPlano, indice, marcacoes);
    App.marcacoesPorPagina.set(p, marcacoes);
  }

  // Encerrar worker OCR
  if (tesseractWorker) {
    try { await tesseractWorker.terminate(); } catch (e) {}
  }

  atualizarProgresso(95, 'Verificando alertas de identificação indireta...');
  verificarIdentificacaoIndireta();
  atualizarProgresso(100, 'Concluído!');

  const totalMarcacoes = [...App.marcacoesPorPagina.values()].reduce((s, m) => s + m.length, 0);
  document.getElementById('stat-marcacoes').textContent = totalMarcacoes;
  document.getElementById('stat-paginas').textContent = App.totalPaginas;

  setTimeout(() => {
    document.getElementById('barra-progresso-container').style.display = 'none';
    document.getElementById('resultados-processamento').classList.remove('hidden');
    document.getElementById('nav-etapa3').style.display = 'flex';
  }, 400);
}

// ─── Detecção com índice de offsets (ABORDAGEM CORRIGIDA) ────────────────────
//
// Em vez de buscar strings nos itens depois do fato (frágil, falha quando
// PDF.js divide "123.456." e "789-01" em itens separados), agora:
// 1. textoPlano é construído rastreando charStart/charEnd de cada item
// 2. O regex roda no textoPlano → encontra match em [matchStart, matchEnd]
// 3. Buscamos todos os itens cujo [charStart, charEnd] se sobrepõe ao match
// 4. Unimos os bboxes desses itens → bbox final correto mesmo com itens divididos

function bboxDoMatch(matchStart, matchEnd, indice) {
  const itensMatch = indice.filter(item =>
    item.charEnd > matchStart && item.charStart < matchEnd
  );
  if (itensMatch.length === 0) return null;

  const x = Math.min(...itensMatch.map(i => i.x));
  const y = Math.min(...itensMatch.map(i => i.y));
  const xMax = Math.max(...itensMatch.map(i => i.x + i.largura));
  const yMax = Math.max(...itensMatch.map(i => i.y + i.altura));

  // Pequena folga para garantir cobertura total (OCR tem imprecisão)
  const PAD = 2;
  return { x: x - PAD, y: y - PAD, largura: (xMax - x) + PAD * 2, altura: (yMax - y) + PAD * 2 };
}

function detectarPadroesAutomaticos(pagina, texto, indice, marcacoes) {
  REGRAS.forEach(regra => {
    if (!App.regrasAtivas.has(regra.id)) return;

    const re = new RegExp(regra.regex.source, regra.regex.flags);
    let match;
    while ((match = re.exec(texto)) !== null) {
      const textoMatch = match[0];
      if (regra.filtro && !regra.filtro(textoMatch)) continue;

      const matchStart = match.index;
      const matchEnd = match.index + textoMatch.length;
      const bbox = bboxDoMatch(matchStart, matchEnd, indice);
      if (!bbox) continue;

      marcacoes.push({
        id: gerarId(),
        pagina,
        texto: textoMatch,
        bbox,
        origem: `Regra automática: ${regra.nome}`,
        tipo: regra.tratamento,
        estado: 'incluido',
        fonteRegra: regra.id,
      });
    }
  });
}

function detectarTermosCadastrados(pagina, texto, indice, marcacoes) {
  App.termos.forEach(termo => {
    if (termo.tratamento === 'manter') return;

    const termoNorm = normalizarTexto(termo.termo);
    const textoNorm = normalizarTexto(texto);

    let idx = 0;
    while (idx < textoNorm.length) {
      const pos = textoNorm.indexOf(termoNorm, idx);
      if (pos === -1) break;

      if (termo.buscaExata) {
        const antes = pos > 0 ? textoNorm[pos - 1] : ' ';
        const depois = pos + termoNorm.length < textoNorm.length ? textoNorm[pos + termoNorm.length] : ' ';
        if (/[a-z0-9àáâãäéêíóõôúçüñ]/i.test(antes) || /[a-z0-9àáâãäéêíóõôúçüñ]/i.test(depois)) {
          idx = pos + 1;
          continue;
        }
      }

      const bbox = bboxDoMatch(pos, pos + termoNorm.length, indice);
      if (bbox) {
        marcacoes.push({
          id: gerarId(),
          pagina,
          texto: texto.slice(pos, pos + termo.termo.length) || termo.termo,
          bbox,
          origem: `Termo cadastrado: ${nomeExibicaoPapel(termo.papel)} — ${termo.termo}`,
          tipo: termo.tratamento,
          estado: 'incluido',
          fonteTermo: termo,
        });
      }
      idx = pos + termoNorm.length;
    }
  });
}

// ─── Alerta de identificação indireta ────────────────────────────────────────
function verificarIdentificacaoIndireta() {
  const alertas = [];
  App.textoPorPagina.forEach((dados, pagina) => {
    const texto = dados.textoPlano;
    const encontrados = IDENTIFICADORES_INDIRETOS.filter(re => re.test(texto));
    if (encontrados.length >= 3) {
      const marcacoesPagina = App.marcacoesPorPagina.get(pagina) || [];
      const temNomeMarcado = marcacoesPagina.some(m =>
        m.fonteTermo && ['vitima', 'testemunha', 'investigado'].includes(m.fonteTermo.papel) && m.estado === 'incluido'
      );
      if (!temNomeMarcado) alertas.push({ pagina });
    }
  });

  if (alertas.length > 0) {
    const container = document.getElementById('alertas-indiretos');
    if (container) {
      container.innerHTML = alertas.map(a => `
        <div class="alerta alerta-aviso">
          <span class="alerta-icone">⚠️</span>
          <div><strong>Atenção — Página ${a.pagina}:</strong>
          Identificadores indiretos detectados que podem permitir identificação mesmo sem o nome explícito. Revise o tarjamento.</div>
        </div>`).join('');
      container.classList.remove('hidden');
    }
  }
}

// ─── ETAPA 4: Revisão visual ──────────────────────────────────────────────────
let renderTaskAtual = null;

async function inicializarRevisao() {
  App.paginaAtual = 1;
  const alertasEt3 = document.getElementById('alertas-indiretos');
  const alertasEt4 = document.getElementById('alertas-indiretos-revisao');
  if (alertasEt3 && alertasEt4 && alertasEt3.innerHTML.trim()) {
    alertasEt4.innerHTML = alertasEt3.innerHTML;
    alertasEt4.classList.remove('hidden');
  }
  await renderizarPaginaRevisao(1);
  atualizarPainelMarcacoes();
  configurarSelecaoManual();
}

async function renderizarPaginaRevisao(numPagina) {
  if (renderTaskAtual) { try { renderTaskAtual.cancel(); } catch (e) {} renderTaskAtual = null; }

  const page = await App.pdfDoc.getPage(numPagina);
  const canvasPdf = document.getElementById('canvas-pdf');
  const overlayCanvas = document.getElementById('overlay-marcacoes');
  const ctxPdf = canvasPdf.getContext('2d');

  const viewport = page.getViewport({ scale: App.escala });
  canvasPdf.width = viewport.width;
  canvasPdf.height = viewport.height;
  overlayCanvas.width = viewport.width;
  overlayCanvas.height = viewport.height;
  overlayCanvas.style.width = canvasPdf.style.width;
  overlayCanvas.style.height = canvasPdf.style.height;

  App.escalaAtual = App.escala;
  App.viewportAtual = viewport;

  ctxPdf.fillStyle = '#fff';
  ctxPdf.fillRect(0, 0, canvasPdf.width, canvasPdf.height);

  renderTaskAtual = page.render({ canvasContext: ctxPdf, viewport });
  await renderTaskAtual.promise;
  renderTaskAtual = null;

  desenharMarcacoesOverlay(numPagina);
  atualizarNavPaginas();
}

function desenharMarcacoesOverlay(numPagina) {
  const overlay = document.getElementById('overlay-marcacoes');
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);

  const marcacoes = App.marcacoesPorPagina.get(numPagina) || [];
  marcacoes.forEach(m => {
    if (m.estado !== 'incluido') return;
    // As bbox estão em coordenadas de escala 1.0; multiplicamos pela escala atual
    const x = m.bbox.x * App.escalaAtual;
    const y = m.bbox.y * App.escalaAtual;
    const w = m.bbox.largura * App.escalaAtual;
    const h = m.bbox.altura * App.escalaAtual;

    if (m.tipo === 'tarjar') {
      ctx.fillStyle = 'rgba(220, 38, 38, 0.38)';
      ctx.strokeStyle = '#dc2626';
    } else if (m.tipo === 'descaracterizar') {
      ctx.fillStyle = 'rgba(217, 119, 6, 0.38)';
      ctx.strokeStyle = '#d97706';
    } else {
      return;
    }
    ctx.fillRect(x, y, w, h);
    ctx.lineWidth = 1.5;
    ctx.strokeRect(x, y, w, h);
  });
}

function atualizarPainelMarcacoes() {
  const lista = document.getElementById('lista-marcacoes-painel');
  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  const contEl = document.getElementById('contador-marcacoes-painel');

  const incluidas = marcacoes.filter(m => m.estado === 'incluido').length;
  if (contEl) contEl.textContent = `${incluidas} / ${marcacoes.length}`;

  if (marcacoes.length === 0) {
    lista.innerHTML = '<p style="color:#6b7280;padding:12px;font-size:12px;text-align:center">Nenhuma marcação nesta página</p>';
    return;
  }

  lista.innerHTML = marcacoes.map(m => {
    const removida = m.estado !== 'incluido';
    return `
      <div class="item-marcacao ${removida ? 'removida' : ''}" id="marcacao-${m.id}">
        <div class="texto-marcacao">${escapeHtml(m.texto)}</div>
        <div class="origem-marcacao">${escapeHtml(m.origem)}</div>
        <div class="acoes-marcacao">
          ${!removida ? `
            <button class="btn-marcacao btn-tipo-tarjar ${m.tipo === 'tarjar' ? 'ativo' : ''}"
              onclick="alterarTipoMarcacao('${m.id}', 'tarjar')">■ Tarjar</button>
            <button class="btn-marcacao btn-tipo-descarac ${m.tipo === 'descaracterizar' ? 'ativo' : ''}"
              onclick="alterarTipoMarcacao('${m.id}', 'descaracterizar')">▒ Descarac.</button>
            <button class="btn-marcacao btn-remover-marcacao"
              onclick="removerMarcacao('${m.id}')">✕ Remover</button>
          ` : `
            <button class="btn-marcacao btn-restaurar-marcacao"
              onclick="restaurarMarcacao('${m.id}')">↺ Restaurar</button>
          `}
        </div>
      </div>`;
  }).join('');
}

function alterarTipoMarcacao(id, novoTipo) {
  const m = (App.marcacoesPorPagina.get(App.paginaAtual) || []).find(x => x.id === id);
  if (m) { m.tipo = novoTipo; desenharMarcacoesOverlay(App.paginaAtual); atualizarPainelMarcacoes(); }
}

function removerMarcacao(id) {
  const m = (App.marcacoesPorPagina.get(App.paginaAtual) || []).find(x => x.id === id);
  if (m) { m.estado = 'removido'; desenharMarcacoesOverlay(App.paginaAtual); atualizarPainelMarcacoes(); }
}

function restaurarMarcacao(id) {
  const m = (App.marcacoesPorPagina.get(App.paginaAtual) || []).find(x => x.id === id);
  if (m) { m.estado = 'incluido'; desenharMarcacoesOverlay(App.paginaAtual); atualizarPainelMarcacoes(); }
}

function atualizarNavPaginas() {
  document.getElementById('num-pagina-atual').textContent = App.paginaAtual;
  document.getElementById('total-paginas-revisao').textContent = App.totalPaginas;
  document.getElementById('btn-pagina-anterior').disabled = App.paginaAtual <= 1;
  document.getElementById('btn-proxima-pagina').disabled = App.paginaAtual >= App.totalPaginas;
}

// ─── Seleção manual no canvas ─────────────────────────────────────────────────
function configurarSelecaoManual() {
  const canvas = document.getElementById('canvas-pdf');
  const painelCanvas = document.getElementById('painel-canvas');
  let arrastando = false;
  let inicio = { x: 0, y: 0 };
  let selRect = null;

  canvas.addEventListener('mousedown', e => {
    if (!App.modoSelecao) return;
    arrastando = true;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    inicio = { x: (e.clientX - rect.left) * scaleX, y: (e.clientY - rect.top) * scaleX };
    selRect = document.getElementById('selecao-manual-rect') || document.createElement('div');
    selRect.id = 'selecao-manual-rect';
    painelCanvas.appendChild(selRect);
    selRect.style.cssText = `position:absolute;border:2px solid #2563eb;background:rgba(37,99,235,0.12);display:block;pointer-events:none;left:${e.clientX - rect.left + painelCanvas.scrollLeft}px;top:${e.clientY - rect.top}px;width:0;height:0`;
  });

  canvas.addEventListener('mousemove', e => {
    if (!arrastando || !selRect) return;
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
    const x0 = Math.min(inicio.x / (canvas.width / rect.width), cx);
    const y0 = Math.min(inicio.y / (canvas.width / rect.width), cy);
    selRect.style.left = x0 + 'px';
    selRect.style.top = y0 + 'px';
    selRect.style.width = Math.abs(cx - inicio.x / (canvas.width / rect.width)) + 'px';
    selRect.style.height = Math.abs(cy - inicio.y / (canvas.width / rect.width)) + 'px';
  });

  canvas.addEventListener('mouseup', e => {
    if (!arrastando) return;
    arrastando = false;
    if (selRect) selRect.style.display = 'none';

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const fim = { x: (e.clientX - rect.left) * scaleX, y: (e.clientY - rect.top) * scaleX };
    const w = Math.abs(fim.x - inicio.x);
    const h = Math.abs(fim.y - inicio.y);
    if (w < 5 || h < 5) return;

    // Converter de coordenadas canvas (escala atual) para coordenadas bbox (escala 1.0)
    const bboxPdf = {
      x: Math.min(inicio.x, fim.x) / App.escalaAtual,
      y: Math.min(inicio.y, fim.y) / App.escalaAtual,
      largura: w / App.escalaAtual,
      altura: h / App.escalaAtual,
    };
    adicionarMarcacaoManual(bboxPdf);
  });
}

function adicionarMarcacaoManual(bbox) {
  const tipo = confirm('Clique OK para TARJAR (bloco preto)\nClique Cancelar para DESCARACTERIZAR (máscara parcial)') ? 'tarjar' : 'descaracterizar';
  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  marcacoes.push({
    id: gerarId(), pagina: App.paginaAtual, texto: '[Seleção manual]',
    bbox, origem: 'Marcação manual', tipo, estado: 'incluido',
  });
  App.marcacoesPorPagina.set(App.paginaAtual, marcacoes);
  desenharMarcacoesOverlay(App.paginaAtual);
  atualizarPainelMarcacoes();
  App.modoSelecao = false;
  document.getElementById('canvas-pdf').classList.remove('modo-selecao');
  document.getElementById('btn-selecao-manual').textContent = '✏️ Selecionar área';
  const info = document.getElementById('info-selecao');
  if (info) info.style.display = 'none';
}

// ─── ETAPA 5: Geração do PDF final ────────────────────────────────────────────
async function gerarPDFFinal() {
  const jsPDFLib = window.jspdf;
  if (!jsPDFLib) {
    mostrarAlerta('erro', 'jsPDF não carregado. Verifique sua conexão e recarregue a página.');
    return;
  }
  const { jsPDF } = jsPDFLib;

  document.getElementById('barra-progresso-container').style.display = 'block';
  atualizarProgresso(0, 'Preparando PDF final...');

  const DPI = 150;
  const ESCALA_FINAL = DPI / 72;

  try {
    const doc = new jsPDF({ unit: 'pt', compress: true, hotfixes: ['px_scaling'] });
    let primeira = true;

    for (let p = 1; p <= App.totalPaginas; p++) {
      atualizarProgresso(
        Math.round((p / App.totalPaginas) * 95),
        `Rasterizando página ${p} de ${App.totalPaginas}...`
      );

      const page = await App.pdfDoc.getPage(p);
      const vp = page.getViewport({ scale: ESCALA_FINAL });

      const cv = document.createElement('canvas');
      cv.width = Math.round(vp.width);
      cv.height = Math.round(vp.height);
      const ctx = cv.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, cv.width, cv.height);
      await page.render({ canvasContext: ctx, viewport: vp }).promise;

      // Aplicar marcações no canvas (nível de pixel)
      const marcacoes = App.marcacoesPorPagina.get(p) || [];
      marcacoes.forEach(m => {
        if (m.estado !== 'incluido') return;

        // bbox está em escala 1.0 → multiplicar por ESCALA_FINAL para canvas final
        const x = Math.floor(m.bbox.x * ESCALA_FINAL);
        const y = Math.floor(m.bbox.y * ESCALA_FINAL);
        const w = Math.ceil(m.bbox.largura * ESCALA_FINAL);
        const h = Math.ceil(m.bbox.altura * ESCALA_FINAL);

        if (m.tipo === 'tarjar') {
          ctx.fillStyle = '#000000';
          ctx.fillRect(x, y, w, h);
        } else if (m.tipo === 'descaracterizar') {
          if (m.fonteRegra === 'cpf') {
            aplicarDescaracterizacaoCPF(ctx, x, y, w, h);
          } else {
            // Genérico: cobrir 30% inicial + 20% final
            ctx.fillStyle = '#000000';
            ctx.fillRect(x, y, Math.ceil(w * 0.30), h);
            ctx.fillRect(x + Math.floor(w * 0.80), y, Math.ceil(w * 0.20), h);
          }
        }
      });

      // Tamanho da página em pontos para o jsPDF
      const largPt = vp.width / ESCALA_FINAL;
      const altPt = vp.height / ESCALA_FINAL;

      if (!primeira) {
        doc.addPage([largPt, altPt]);
      } else {
        // Ajustar primeira página
        doc.internal.pageSize.width = largPt;
        doc.internal.pageSize.height = altPt;
        primeira = false;
      }

      const imgData = cv.toDataURL('image/jpeg', 0.90);
      doc.addImage(imgData, 'JPEG', 0, 0, largPt, altPt, undefined, 'FAST');
    }

    atualizarProgresso(100, 'Gerando download...');
    const nomeBase = App.pdfNome.replace(/\.pdf$/i, '');
    doc.save(`${nomeBase}_tarjado.pdf`);
    document.getElementById('nome-arquivo-gerado').textContent = `${nomeBase}_tarjado.pdf`;
    document.getElementById('barra-progresso-container').style.display = 'none';
    avancarEtapa(5);
  } catch (err) {
    console.error('Erro na geração:', err);
    mostrarAlerta('erro', 'Erro ao gerar PDF: ' + err.message);
    document.getElementById('barra-progresso-container').style.display = 'none';
  }
}

function aplicarDescaracterizacaoCPF(ctx, x, y, w, h) {
  // Formato CPF: AAA.BBB.CCC-DD → ocultar AAA e DD, manter BBB.CCC
  // Aproximação por posição proporcional
  const fsBold = Math.max(8, Math.min(h * 0.85, 13));

  // Cobrir primeiros ~27% (3 dígitos) e últimos ~18% (2 dígitos)
  ctx.fillStyle = '#000000';
  ctx.fillRect(x, y, Math.ceil(w * 0.28), h);
  ctx.fillRect(x + Math.floor(w * 0.82), y, Math.ceil(w * 0.18), h);

  // Escrever asteriscos brancos sobre as faixas pretas
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${fsBold}px monospace`;
  ctx.textBaseline = 'middle';
  ctx.fillText('***', x + 1, y + h / 2);
  ctx.fillText('**', x + Math.floor(w * 0.82) + 1, y + h / 2);
}

// ─── Navegação entre etapas ───────────────────────────────────────────────────
function configurarBotoesNavegacao() {
  document.getElementById('btn-avancar-etapa1').addEventListener('click', () => avancarEtapa(2));
  document.getElementById('btn-avancar-etapa2').addEventListener('click', async () => {
    avancarEtapa(3);
    await executarPreProcessamento();
  });
  document.getElementById('btn-avancar-etapa3').addEventListener('click', async () => {
    avancarEtapa(4);
    await inicializarRevisao();
  });
  document.getElementById('btn-gerar-pdf').addEventListener('click', gerarPDFFinal);
  document.getElementById('btn-pagina-anterior').addEventListener('click', async () => {
    if (App.paginaAtual > 1) {
      App.paginaAtual--;
      await renderizarPaginaRevisao(App.paginaAtual);
      atualizarPainelMarcacoes();
    }
  });
  document.getElementById('btn-proxima-pagina').addEventListener('click', async () => {
    if (App.paginaAtual < App.totalPaginas) {
      App.paginaAtual++;
      await renderizarPaginaRevisao(App.paginaAtual);
      atualizarPainelMarcacoes();
    }
  });
  document.getElementById('btn-selecao-manual').addEventListener('click', () => {
    App.modoSelecao = !App.modoSelecao;
    const canvas = document.getElementById('canvas-pdf');
    const btn = document.getElementById('btn-selecao-manual');
    const info = document.getElementById('info-selecao') || (() => {
      const el = document.createElement('div');
      el.id = 'info-selecao';
      document.body.appendChild(el);
      return el;
    })();
    if (App.modoSelecao) {
      canvas.classList.add('modo-selecao');
      btn.textContent = '✕ Cancelar seleção';
      info.textContent = 'Clique e arraste para selecionar a área a tarjar';
      info.style.display = 'block';
    } else {
      canvas.classList.remove('modo-selecao');
      btn.textContent = '✏️ Selecionar área';
      info.style.display = 'none';
    }
  });
  document.getElementById('btn-novo-documento').addEventListener('click', () => {
    if (confirm('Iniciar novo processamento? O trabalho atual será perdido.')) location.reload();
  });
}

function avancarEtapa(num) {
  const anterior = document.querySelector(`.step[data-step="${App.etapaAtual}"]`);
  if (anterior) { anterior.classList.remove('ativa'); anterior.classList.add('concluida'); }
  App.etapaAtual = num;
  document.querySelectorAll('.step').forEach(s => s.classList.remove('ativa'));
  const nova = document.querySelector(`.step[data-step="${num}"]`);
  if (nova) nova.classList.add('ativa');
  document.querySelectorAll('.etapa-secao').forEach(s => s.classList.add('hidden'));
  const secao = document.getElementById(`etapa-${num}`);
  if (secao) secao.classList.remove('hidden');
  window.scrollTo(0, 0);
}

// ─── Lista de regras (Etapa 2) ────────────────────────────────────────────────
function renderizarListaRegras() {
  const lista = document.getElementById('lista-regras-auto');
  if (!lista) return;
  lista.innerHTML = REGRAS.map(r => `
    <div class="item-regra">
      <input type="checkbox" id="regra-${r.id}" ${r.ativa ? 'checked' : ''}
        onchange="toggleRegra('${r.id}', this.checked)">
      <label for="regra-${r.id}" class="nome-regra">${r.nome}</label>
      <span class="tag-tratamento ${r.tratamento === 'tarjar' ? 'tag-tarjar' : 'tag-descaracterizar'}">
        ${r.tratamento === 'descaracterizar' ? 'Descarac.' : 'Tarjar'}
      </span>
    </div>`).join('');
}

function toggleRegra(id, ativo) {
  if (ativo) App.regrasAtivas.add(id); else App.regrasAtivas.delete(id);
}

// ─── Utilitários ─────────────────────────────────────────────────────────────
function normalizarTexto(texto) {
  return texto.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
}

function nomeExibicaoPapel(papel) {
  return { investigado: 'Investigado', vitima: 'Vítima', testemunha: 'Testemunha',
           denunciante: 'Denunciante', terceiro: 'Terceiro', livre: 'Termo livre' }[papel] || papel;
}

function gerarId() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function formatarTamanho(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function exibirCarregando(ativo, msg = '') {
  const el = document.getElementById('indicador-carregando');
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle('hidden', !ativo);
}

function atualizarProgresso(pct, label) {
  const fill = document.getElementById('barra-progresso-fill');
  const lbl = document.getElementById('progresso-label');
  if (fill) fill.style.width = pct + '%';
  if (lbl) lbl.textContent = label;
}

function mostrarAlerta(tipo, msg) {
  const el = document.getElementById('alerta-global');
  if (!el) { alert(msg); return; }
  const icones = { erro: '❌', aviso: '⚠️', info: 'ℹ️', sucesso: '✅' };
  el.className = `alerta alerta-${tipo}`;
  el.innerHTML = `<span class="alerta-icone">${icones[tipo] || 'ℹ️'}</span><div>${msg}</div>`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 10000);
}
