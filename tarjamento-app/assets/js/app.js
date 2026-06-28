/**
 * Tarjamento Coger — Ferramenta de Tarjamento Automático de PDF
 * Corregedoria da Receita Federal do Brasil
 * Aplicação 100% client-side, sem envio de dados pela rede.
 */

'use strict';

// ─── Estado global da aplicação ──────────────────────────────────────────────
const App = {
  etapaAtual: 1,
  pdfBytes: null,
  pdfNome: '',
  pdfDoc: null,          // PDF.js PDFDocumentProxy
  totalPaginas: 0,
  paginaAtual: 1,
  escala: 1.5,

  // Contexto do processo
  contexto: {
    julgado: 'nao',      // 'nao' | 'sancionado' | 'absolvido'
    assedio: false,
  },

  // Termos cadastrados (Etapa 2)
  termos: [],

  // Regras automáticas ativas
  regrasAtivas: new Set(),

  // Candidatos a marcação por página: Map<pagina, Array<Marcacao>>
  marcacoesPorPagina: new Map(),

  // Dados OCR por página (cache)
  ocrCache: new Map(),

  // Dados de texto por página (PDF.js)
  textoPorPagina: new Map(),

  // Modo de seleção manual
  modoSelecao: false,
  selecaoInicio: null,
};

// ─── Regras de detecção automática ───────────────────────────────────────────
const REGRAS = [
  {
    id: 'cpf',
    nome: 'CPF',
    regex: /\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b/g,
    tratamento: 'descaracterizar',
    ativa: true,
    descricao: 'Número de CPF',
  },
  {
    id: 'cnpj',
    nome: 'CNPJ',
    regex: /\b\d{2}\.?\d{3}\.?\d{3}\/?\.?\d{4}-?\d{2}\b/g,
    tratamento: 'tarjar',
    ativa: false,
    descricao: 'CNPJ (dado público — aparece desmarcado por padrão)',
  },
  {
    id: 'rg',
    nome: 'RG / Identidade',
    regex: /(?:RG|R\.G\.|Identidade|Cédula de Identidade)[:\s#nº°]*([0-9]{1,2}\.?[0-9]{3}\.?[0-9]{3}-?[0-9A-Za-z])/gi,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Número de RG / Identidade',
  },
  {
    id: 'matricula',
    nome: 'Matrícula / SIAPE',
    regex: /(?:matr[íi]cula|SIAPE)[:\s#nº°]*([0-9]{6,8})/gi,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Matrícula funcional / SIAPE',
  },
  {
    id: 'conta',
    nome: 'Conta Bancária / Agência',
    regex: /(?:ag[eê]ncia|conta(?:\s+corrente|\s+poupan[çc]a)?)[:\s#nº°]*([0-9]{3,6}-?[0-9X])/gi,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Conta bancária ou agência',
  },
  {
    id: 'nascimento',
    nome: 'Data de Nascimento',
    regex: /(?:nasc(?:ido|eu|imento)?(?:\s+em)?|data\s+de\s+nascimento)[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})/gi,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Data de nascimento',
  },
  {
    id: 'email',
    nome: 'E-mail',
    regex: /\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b/g,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Endereço de e-mail',
    filtro: (match) => !match.includes('@receita.fazenda.gov.br') && !match.includes('@rfb.gov.br'),
  },
  {
    id: 'telefone',
    nome: 'Telefone',
    regex: /(?:\+55\s?)?(?:\(?\d{2}\)?\s?)(?:9\s?)?\d{4}[-\s]?\d{4}/g,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Número de telefone brasileiro',
  },
  {
    id: 'endereco',
    nome: 'Endereço Residencial',
    regex: /(?:Rua|Av\.|Avenida|Travessa|Alameda|Rodovia|Estrada|R\.)\s+[A-Za-zÀ-ú\s]+,?\s*n[°º]?\s*\d+/gi,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Endereço residencial',
  },
  {
    id: 'saude',
    nome: 'Palavras-chave de Saúde',
    regex: /\b(CID|atestado\s+m[eé]dico|laudo\s+m[eé]dico|afastamento\s+por|diagn[oó]stico|doen[çc]a|gestante|gravidez|licen[çc]a\s+saúde|saúde\s+mental|transtorno|depress[aã]o|ans[ie]edade)\b/gi,
    tratamento: 'tarjar',
    ativa: true,
    descricao: 'Informações de saúde (dados sensíveis)',
  },
];

// ─── Identificadores indiretos para alerta ────────────────────────────────────
const IDENTIFICADORES_INDIRETOS = [
  /\bcargo\b/i, /\blota[çc][aã]o\b/i, /\bsetor\b/i, /\bunidade\b/i,
  /\bcomiss[aã]o\b/i, /\bdata\b.*\d{4}/i, /\bn[°º]\s*(?:processo|proc)/i,
  /\bmatrimonial\b/i, /\bfilia[çc][aã]o\b/i,
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

  area.addEventListener('dragover', e => {
    e.preventDefault();
    area.classList.add('drag-over');
  });

  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));

  area.addEventListener('drop', e => {
    e.preventDefault();
    area.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) processarArquivo(file);
  });

  input.addEventListener('change', e => {
    const file = e.target.files[0];
    if (file) processarArquivo(file);
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
      msg = 'A biblioteca PDF.js não foi carregada. Execute o script download-libs para baixar as dependências e use os scripts iniciar.sh/.bat para abrir a ferramenta (não abra o index.html diretamente pelo explorador de arquivos).';
    } else if (err && err.name === 'PasswordException') {
      msg = 'O PDF está protegido por senha. Remova a senha antes de processar.';
    } else if (err && err.name === 'InvalidPDFException') {
      msg = 'O arquivo não é um PDF válido ou está corrompido.';
    } else if (location.protocol === 'file:') {
      msg = 'Abra a ferramenta pelo script iniciar.sh (Linux/Mac) ou iniciar.bat (Windows), não diretamente pelo navegador. O protocolo file:// bloqueia o funcionamento do PDF.js.';
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

// ─── ETAPA 2: Formulário de identificação ────────────────────────────────────
function configurarFormularioEtapa2() {
  document.getElementById('btn-add-investigado').addEventListener('click', () =>
    adicionarTermoPapel('investigado', 'lista-investigados'));
  document.getElementById('btn-add-vitima').addEventListener('click', () =>
    adicionarTermoPapel('vitima', 'lista-vitimas'));
  document.getElementById('btn-add-testemunha').addEventListener('click', () =>
    adicionarTermoPapel('testemunha', 'lista-testemunhas'));
  document.getElementById('btn-add-denunciante').addEventListener('click', () =>
    adicionarTermoPapel('denunciante', 'lista-denunciantes'));
  document.getElementById('btn-add-terceiro').addEventListener('click', () =>
    adicionarTermoPapel('terceiro', 'lista-terceiros'));
  document.getElementById('btn-add-livre').addEventListener('click', () =>
    adicionarTermoPapel('livre', 'lista-livres'));

  // Atualizar tratamento do investigado ao mudar status do julgamento
  document.querySelectorAll('input[name="julgado"]').forEach(el => {
    el.addEventListener('change', () => {
      App.contexto.julgado = el.value;
      atualizarTagInvestigado();
    });
  });

  document.querySelectorAll('input[name="assedio"]').forEach(el => {
    el.addEventListener('change', () => {
      App.contexto.assedio = el.value === 'sim';
    });
  });
}

function atualizarTagInvestigado() {
  const tag = document.getElementById('tag-investigado');
  if (!tag) return;
  if (App.contexto.julgado === 'absolvido') {
    tag.textContent = 'Tarjar';
    tag.className = 'tag-tratamento tag-tarjar';
  } else if (App.contexto.julgado === 'sancionado') {
    tag.textContent = 'Manter';
    tag.className = 'tag-tratamento tag-manter';
  } else {
    tag.textContent = 'Tarjar';
    tag.className = 'tag-tratamento tag-tarjar';
  }
}

function tratamentoPorPapel(papel) {
  switch (papel) {
    case 'investigado':
      return App.contexto.julgado === 'sancionado' ? 'manter' : 'tarjar';
    case 'vitima':
    case 'testemunha':
    case 'denunciante':
    case 'terceiro':
      return 'tarjar';
    case 'livre':
      return 'tarjar';
    default:
      return 'tarjar';
  }
}

function adicionarTermoPapel(papel, listaId) {
  const lista = document.getElementById(listaId);
  const id = `termo-${Date.now()}-${Math.random().toString(36).slice(2)}`;

  const div = document.createElement('div');
  div.className = 'item-termo';
  div.dataset.id = id;

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

    // Suporte a múltiplos termos separados por vírgula
    val.split(',').forEach(t => {
      const termo = t.trim();
      if (!termo) return;
      App.termos.push({
        termo,
        papel,
        tratamento: tratamentoPorPapel(papel),
        buscaExata: busca === 'exata',
      });
    });
  });
}

// ─── ETAPA 3: Pré-processamento ───────────────────────────────────────────────
async function executarPreProcessamento() {
  coletarTermosFormulario();
  App.marcacoesPorPagina.clear();
  App.ocrCache.clear();
  App.textoPorPagina.clear();

  atualizarProgresso(0, `Iniciando processamento (0 / ${App.totalPaginas} páginas)...`);
  document.getElementById('barra-progresso-container').style.display = 'block';

  for (let p = 1; p <= App.totalPaginas; p++) {
    atualizarProgresso(
      Math.round(((p - 1) / App.totalPaginas) * 80),
      `Processando página ${p} de ${App.totalPaginas}...`
    );

    const page = await App.pdfDoc.getPage(p);
    const textContent = await page.getTextContent();
    const itensTexto = textContent.items;
    const viewport = page.getViewport({ scale: 1.0 });

    let textoPlano = '';
    const itensPosicionados = [];

    itensTexto.forEach(item => {
      if (!item.str || !item.str.trim()) return;
      textoPlano += item.str + ' ';
      // Transformar coordenadas PDF (origem inferior-esquerda) para tela (origem superior-esquerda)
      const tx = pdfjsLib.Util.transform(viewport.transform, item.transform);
      const x = tx[4];
      const y = tx[5] - item.height;
      itensPosicionados.push({
        texto: item.str,
        x, y,
        largura: item.width,
        altura: item.height || 12,
      });
    });

    const precisaOCR = textoPlano.trim().length < 50;

    if (precisaOCR) {
      atualizarProgresso(
        Math.round(((p - 1) / App.totalPaginas) * 80) + 5,
        `OCR na página ${p} de ${App.totalPaginas}...`
      );
      const resultadoOCR = await executarOCR(page);
      if (resultadoOCR) {
        App.ocrCache.set(p, resultadoOCR);
        // Adicionar itens do OCR ao texto posicionado
        resultadoOCR.palavras.forEach(w => {
          itensPosicionados.push({
            texto: w.text,
            x: w.bbox.x0,
            y: w.bbox.y0,
            largura: w.bbox.x1 - w.bbox.x0,
            altura: w.bbox.y1 - w.bbox.y0,
            dePocr: true,
          });
          textoPlano += w.text + ' ';
        });
      }
    }

    App.textoPorPagina.set(p, { itens: itensPosicionados, textoPlano, viewport });

    const marcacoes = [];
    detectarPadroesAutomaticos(p, textoPlano, itensPosicionados, marcacoes);
    detectarTermosCadastrados(p, textoPlano, itensPosicionados, marcacoes);

    App.marcacoesPorPagina.set(p, marcacoes);
  }

  atualizarProgresso(90, 'Verificando alertas de identificação indireta...');
  verificarIdentificacaoIndireta();

  atualizarProgresso(100, 'Processamento concluído!');

  const totalMarcacoes = [...App.marcacoesPorPagina.values()].reduce((s, m) => s + m.length, 0);
  document.getElementById('stat-marcacoes').textContent = totalMarcacoes;
  document.getElementById('stat-paginas').textContent = App.totalPaginas;

  setTimeout(() => {
    document.getElementById('barra-progresso-container').style.display = 'none';
    document.getElementById('resultados-processamento').classList.remove('hidden');
    document.getElementById('nav-etapa3').style.display = 'flex';
  }, 500);
}

async function executarOCR(page) {
  if (typeof Tesseract === 'undefined') {
    console.warn('Tesseract.js não disponível — OCR ignorado para esta página.');
    return null;
  }

  // Renderizar página em canvas para OCR
  const viewport = page.getViewport({ scale: 2.0 });
  const canvas = document.createElement('canvas');
  canvas.width = viewport.width;
  canvas.height = viewport.height;
  const ctx = canvas.getContext('2d');
  await page.render({ canvasContext: ctx, viewport }).promise;

  try {
    const resultado = await Tesseract.recognize(canvas, 'por', {
      logger: () => {},
      workerPath: 'assets/js/tesseract/worker.min.js',
      langPath: 'assets/lang/',
      corePath: 'assets/js/tesseract/tesseract-core.wasm.js',
    });

    const palavras = [];
    resultado.data.words.forEach(word => {
      if (word.text.trim()) {
        palavras.push({ text: word.text, bbox: word.bbox, confidence: word.confidence });
      }
    });

    return { palavras, textoCompleto: resultado.data.text };
  } catch (err) {
    console.warn('Erro no OCR:', err);
    return null;
  }
}

// ─── Detecção de padrões automáticos ─────────────────────────────────────────
function detectarPadroesAutomaticos(pagina, texto, itens, marcacoes) {
  REGRAS.forEach(regra => {
    if (!App.regrasAtivas.has(regra.id)) return;

    // Reset lastIndex
    regra.regex.lastIndex = 0;
    let match;
    const regraClone = new RegExp(regra.regex.source, regra.regex.flags);

    while ((match = regraClone.exec(texto)) !== null) {
      const textoMatch = match[0];
      if (regra.filtro && !regra.filtro(textoMatch)) continue;

      // Localizar posição nos itens
      const bboxs = encontrarPosicaoTexto(textoMatch, itens);
      if (bboxs.length === 0) continue;

      bboxs.forEach(bbox => {
        const id = gerarId();
        marcacoes.push({
          id,
          pagina,
          texto: textoMatch,
          bbox,
          origem: `Regra automática: ${regra.nome}`,
          tipo: regra.tratamento,
          estado: 'incluido',
          fonteRegra: regra.id,
          prioridade: regra.ativa ? 'normal' : 'baixa',
        });
      });
    }
  });
}

// ─── Detecção de termos cadastrados ──────────────────────────────────────────
function detectarTermosCadastrados(pagina, texto, itens, marcacoes) {
  App.termos.forEach(termo => {
    if (termo.tratamento === 'manter') return;

    const termoNorm = normalizarTexto(termo.termo);
    const textoNorm = normalizarTexto(texto);

    let idx = 0;
    while (true) {
      const pos = textoNorm.indexOf(termoNorm, idx);
      if (pos === -1) break;

      // Verificar se é palavra exata (se solicitado)
      if (termo.buscaExata) {
        const antes = pos > 0 ? textoNorm[pos - 1] : ' ';
        const depois = pos + termoNorm.length < textoNorm.length ? textoNorm[pos + termoNorm.length] : ' ';
        if (/\w/.test(antes) || /\w/.test(depois)) {
          idx = pos + 1;
          continue;
        }
      }

      const textoOriginal = texto.slice(pos, pos + termo.termo.length);
      const bboxs = encontrarPosicaoTexto(textoOriginal, itens);

      bboxs.forEach(bbox => {
        marcacoes.push({
          id: gerarId(),
          pagina,
          texto: textoOriginal || termo.termo,
          bbox,
          origem: `Termo cadastrado: ${nomeExibicaoPapel(termo.papel)} — ${termo.termo}`,
          tipo: termo.tratamento,
          estado: 'incluido',
          fonteTermo: termo,
        });
      });

      idx = pos + 1;
    }
  });
}

function encontrarPosicaoTexto(busca, itens) {
  const resultados = [];
  const buscaNorm = normalizarTexto(busca);

  // Tentar match direto em itens individuais
  itens.forEach(item => {
    if (normalizarTexto(item.texto).includes(buscaNorm)) {
      resultados.push({ x: item.x, y: item.y, largura: item.largura, altura: item.altura });
    }
  });

  // Se não encontrou, tentar match em janela deslizante de itens consecutivos
  if (resultados.length === 0 && itens.length > 1) {
    for (let i = 0; i < itens.length - 1; i++) {
      let textoJanela = '';
      let j = i;
      while (j < itens.length && textoJanela.length < busca.length * 2) {
        textoJanela += itens[j].texto + ' ';
        if (normalizarTexto(textoJanela).includes(buscaNorm)) {
          const xMin = Math.min(...itens.slice(i, j + 1).map(t => t.x));
          const yMin = Math.min(...itens.slice(i, j + 1).map(t => t.y));
          const xMax = Math.max(...itens.slice(i, j + 1).map(t => t.x + t.largura));
          const yMax = Math.max(...itens.slice(i, j + 1).map(t => t.y + t.altura));
          resultados.push({
            x: xMin, y: yMin,
            largura: xMax - xMin,
            altura: yMax - yMin,
          });
          break;
        }
        j++;
      }
      if (resultados.length > 0) break;
    }
  }

  return resultados;
}

// ─── Alerta de identificação indireta ────────────────────────────────────────
function verificarIdentificacaoIndireta() {
  const alertas = [];

  App.textoPorPagina.forEach((dados, pagina) => {
    const texto = dados.textoPlano;
    let contadorIndiretos = 0;
    const encontrados = [];

    IDENTIFICADORES_INDIRETOS.forEach(re => {
      if (re.test(texto)) {
        contadorIndiretos++;
        encontrados.push(re.source.split('\\b').join('').replace(/[^a-záàãâéêíóõôúç\s]/gi, ''));
      }
    });

    if (contadorIndiretos >= 3) {
      const marcacoesPagina = App.marcacoesPorPagina.get(pagina) || [];
      const temNomeMarcado = marcacoesPagina.some(m =>
        m.fonteTermo && ['vitima', 'testemunha', 'investigado'].includes(m.fonteTermo.papel) && m.estado === 'incluido'
      );

      if (!temNomeMarcado) {
        alertas.push({ pagina, identificadores: encontrados.slice(0, 4) });
      }
    }
  });

  if (alertas.length > 0) {
    App.alertasIdentificacaoIndireta = alertas;
    const container = document.getElementById('alertas-indiretos');
    if (container) {
      container.innerHTML = alertas.map(a => `
        <div class="alerta alerta-aviso">
          <span class="alerta-icone">⚠️</span>
          <div>
            <strong>Atenção — Página ${a.pagina}:</strong>
            Identificadores indiretos detectados (${a.identificadores.join(', ')}).
            Este trecho pode permitir identificação mesmo sem o nome explícito. Revise se o tarjamento é suficiente.
          </div>
        </div>
      `).join('');
      container.classList.remove('hidden');
    }
  }
}

// ─── ETAPA 4: Revisão visual ──────────────────────────────────────────────────
let canvasRenderTask = null;

async function inicializarRevisao() {
  App.paginaAtual = 1;

  // Copiar alertas de identificação indireta para etapa 4
  const alertasEt3 = document.getElementById('alertas-indiretos');
  const alertasEt4 = document.getElementById('alertas-indiretos-revisao');
  if (alertasEt3 && alertasEt4 && alertasEt3.innerHTML) {
    alertasEt4.innerHTML = alertasEt3.innerHTML;
    alertasEt4.classList.remove('hidden');
  }

  await renderizarPaginaRevisao(1);
  atualizarPainelMarcacoes();
  configurarSelecaoManual();
}

async function renderizarPaginaRevisao(numPagina) {
  if (canvasRenderTask) {
    canvasRenderTask.cancel();
    canvasRenderTask = null;
  }

  const page = await App.pdfDoc.getPage(numPagina);
  const canvas = document.getElementById('canvas-pdf');
  const ctx = canvas.getContext('2d');

  const viewport = page.getViewport({ scale: App.escala });
  canvas.width = viewport.width;
  canvas.height = viewport.height;

  const overlay = document.getElementById('overlay-marcacoes');
  overlay.width = viewport.width;
  overlay.height = viewport.height;

  canvasRenderTask = page.render({ canvasContext: ctx, viewport });
  await canvasRenderTask.promise;
  canvasRenderTask = null;

  // Guardar escala atual para conversão de coordenadas
  App.escalaAtual = App.escala;
  App.viewportAtual = viewport;

  desenharMarcacoesOverlay(numPagina, viewport);
  atualizarNavPaginas();
}

function desenharMarcacoesOverlay(numPagina, viewport) {
  const overlay = document.getElementById('overlay-marcacoes');
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);

  const marcacoes = App.marcacoesPorPagina.get(numPagina) || [];

  marcacoes.forEach(m => {
    if (m.estado !== 'incluido') return;
    const { x, y, largura, altura } = escalarBbox(m.bbox, viewport);

    if (m.tipo === 'tarjar') {
      ctx.fillStyle = 'rgba(220, 38, 38, 0.35)';
      ctx.strokeStyle = '#dc2626';
    } else if (m.tipo === 'descaracterizar') {
      ctx.fillStyle = 'rgba(217, 119, 6, 0.35)';
      ctx.strokeStyle = '#d97706';
    } else {
      return; // manter
    }

    ctx.fillRect(x, y, largura, altura);
    ctx.lineWidth = 1.5;
    ctx.strokeRect(x, y, largura, altura);
  });
}

function escalarBbox(bbox, viewport) {
  // As coordenadas dos itens já estão no espaço do viewport com escala 1.0
  // Precisamos multiplicar pela escala atual
  const fatorEscala = viewport.scale;
  return {
    x: bbox.x * fatorEscala,
    y: bbox.y * fatorEscala,
    largura: bbox.largura * fatorEscala,
    altura: bbox.altura * fatorEscala,
  };
}

function atualizarPainelMarcacoes() {
  const lista = document.getElementById('lista-marcacoes-painel');
  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];

  if (marcacoes.length === 0) {
    lista.innerHTML = '<p style="color:#6b7280;padding:12px;font-size:12px;text-align:center">Nenhuma marcação nesta página</p>';
    return;
  }

  lista.innerHTML = marcacoes.map(m => {
    const removida = m.estado !== 'incluido';
    const tipoLabel = m.tipo === 'tarjar' ? 'Tarjar' : m.tipo === 'descaracterizar' ? 'Descaracterizar' : 'Manter';
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
      </div>
    `;
  }).join('');
}

function alterarTipoMarcacao(id, novoTipo) {
  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  const m = marcacoes.find(x => x.id === id);
  if (m) {
    m.tipo = novoTipo;
    desenharMarcacoesOverlay(App.paginaAtual, App.viewportAtual);
    atualizarPainelMarcacoes();
  }
}

function removerMarcacao(id) {
  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  const m = marcacoes.find(x => x.id === id);
  if (m) {
    m.estado = 'removido';
    desenharMarcacoesOverlay(App.paginaAtual, App.viewportAtual);
    atualizarPainelMarcacoes();
  }
}

function restaurarMarcacao(id) {
  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  const m = marcacoes.find(x => x.id === id);
  if (m) {
    m.estado = 'incluido';
    desenharMarcacoesOverlay(App.paginaAtual, App.viewportAtual);
    atualizarPainelMarcacoes();
  }
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
  let selRect = null;
  let arrastando = false;
  let inicio = { x: 0, y: 0 };

  canvas.addEventListener('mousedown', e => {
    if (!App.modoSelecao) return;
    arrastando = true;
    const rect = canvas.getBoundingClientRect();
    inicio = { x: e.clientX - rect.left, y: e.clientY - rect.top };

    selRect = document.getElementById('selecao-manual-rect');
    if (!selRect) {
      selRect = document.createElement('div');
      selRect.id = 'selecao-manual-rect';
      painelCanvas.appendChild(selRect);
    }
    selRect.style.left = inicio.x + 'px';
    selRect.style.top = inicio.y + 'px';
    selRect.style.width = '0';
    selRect.style.height = '0';
    selRect.style.display = 'block';
  });

  canvas.addEventListener('mousemove', e => {
    if (!arrastando || !App.modoSelecao) return;
    const rect = canvas.getBoundingClientRect();
    const atual = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const x = Math.min(inicio.x, atual.x);
    const y = Math.min(inicio.y, atual.y);
    const w = Math.abs(atual.x - inicio.x);
    const h = Math.abs(atual.y - inicio.y);
    selRect.style.left = x + 'px';
    selRect.style.top = y + 'px';
    selRect.style.width = w + 'px';
    selRect.style.height = h + 'px';
  });

  canvas.addEventListener('mouseup', e => {
    if (!arrastando || !App.modoSelecao) return;
    arrastando = false;

    const rect = canvas.getBoundingClientRect();
    const fim = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const x = Math.min(inicio.x, fim.x);
    const y = Math.min(inicio.y, fim.y);
    const w = Math.abs(fim.x - inicio.x);
    const h = Math.abs(fim.y - inicio.y);

    if (selRect) { selRect.style.display = 'none'; }

    if (w < 5 || h < 5) return; // seleção muito pequena

    // Converter coordenadas canvas → PDF (sem escala)
    const fator = 1 / App.escala;
    const bboxPdf = {
      x: x * fator, y: y * fator,
      largura: w * fator, altura: h * fator,
    };

    adicionarMarcacaoManual(bboxPdf);
  });
}

function adicionarMarcacaoManual(bbox) {
  const tipo = prompt('Tipo de marcação:\n1 — Tarjar (bloco preto)\n2 — Descaracterizar (máscara parcial)\nDigite 1 ou 2:');
  const tipoMap = { '1': 'tarjar', '2': 'descaracterizar' };
  const tipoSelecionado = tipoMap[tipo] || 'tarjar';

  const marcacoes = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  marcacoes.push({
    id: gerarId(),
    pagina: App.paginaAtual,
    texto: '[Seleção manual]',
    bbox,
    origem: 'Marcação manual do usuário',
    tipo: tipoSelecionado,
    estado: 'incluido',
  });
  App.marcacoesPorPagina.set(App.paginaAtual, marcacoes);

  desenharMarcacoesOverlay(App.paginaAtual, App.viewportAtual);
  atualizarPainelMarcacoes();

  App.modoSelecao = false;
  document.getElementById('canvas-pdf').classList.remove('modo-selecao');
  document.getElementById('btn-selecao-manual').textContent = '✏️ Selecionar área';
  ocultarInfoSelecao();
}

// ─── ETAPA 5: Geração do PDF final ────────────────────────────────────────────
async function gerarPDFFinal() {
  if (typeof jspdf === 'undefined' && typeof window.jspdf === 'undefined') {
    mostrarAlerta('erro', 'Biblioteca jsPDF não carregada. Verifique se o arquivo assets/js/jspdf.min.js está presente.');
    return;
  }

  const { jsPDF } = window.jspdf || jspdf;

  exibirCarregando(true, 'Gerando PDF final...');
  atualizarProgresso(0, 'Preparando geração do PDF final...');
  document.getElementById('barra-progresso-container').style.display = 'block';

  try {
    const doc = new jsPDF({ unit: 'pt', compress: true });
    let primeiraPagina = true;

    for (let p = 1; p <= App.totalPaginas; p++) {
      atualizarProgresso(
        Math.round((p / App.totalPaginas) * 100),
        `Rasterizando página ${p} de ${App.totalPaginas}...`
      );

      const page = await App.pdfDoc.getPage(p);
      const escalaFinal = 200 / 72; // ~200 DPI
      const viewport = page.getViewport({ scale: escalaFinal });

      // Canvas de rasterização
      const canvas = document.createElement('canvas');
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      const ctx = canvas.getContext('2d');

      // Fundo branco
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Renderizar PDF
      await page.render({ canvasContext: ctx, viewport }).promise;

      // Aplicar marcações
      const marcacoes = App.marcacoesPorPagina.get(p) || [];
      marcacoes.forEach(m => {
        if (m.estado !== 'incluido') return;

        const fator = escalaFinal;
        const x = m.bbox.x * fator;
        const y = m.bbox.y * fator;
        const w = m.bbox.largura * fator;
        const h = m.bbox.altura * fator;

        if (m.tipo === 'tarjar') {
          // Bloco preto sólido
          ctx.fillStyle = '#000000';
          ctx.fillRect(x, y, w, h);
        } else if (m.tipo === 'descaracterizar') {
          // CPF: manter dígitos 4-9, ocultar 1-3 e 10-11
          if (m.fonteRegra === 'cpf') {
            aplicarDescaracterizacaoCPF(ctx, m, fator);
          } else {
            // Genérico: cobrir 70% da área da esquerda
            ctx.fillStyle = '#000000';
            ctx.fillRect(x, y, w * 0.35, h);
            ctx.fillRect(x + w * 0.7, y, w * 0.3, h);
          }
        }
      });

      // Converter canvas para imagem
      const imgData = canvas.toDataURL('image/jpeg', 0.92);

      // Dimensões em pontos (pt) para o PDF
      const largPt = (canvas.width / escalaFinal) * (72 / 96) * (96 / 72);
      const altPt = (canvas.height / escalaFinal) * (72 / 96) * (96 / 72);

      // Calcular tamanho de página em pontos
      const largPdf = viewport.width / escalaFinal * (72 / 72);
      const altPdf = viewport.height / escalaFinal * (72 / 72);

      if (!primeiraPagina) {
        doc.addPage([largPdf, altPdf]);
      } else {
        doc.internal.pageSize.width = largPdf;
        doc.internal.pageSize.height = altPdf;
        primeiraPagina = false;
      }

      doc.addImage(imgData, 'JPEG', 0, 0, largPdf, altPdf);
    }

    const nomeBase = App.pdfNome.replace(/\.pdf$/i, '');
    const nomeArquivo = `${nomeBase}_tarjado.pdf`;
    doc.save(nomeArquivo);

    document.getElementById('nome-arquivo-gerado').textContent = nomeArquivo;
    document.getElementById('barra-progresso-container').style.display = 'none';
    avancarEtapa(5);
  } catch (err) {
    mostrarAlerta('erro', 'Erro ao gerar PDF: ' + err.message);
    console.error(err);
  } finally {
    exibirCarregando(false);
    document.getElementById('barra-progresso-container').style.display = 'none';
  }
}

function aplicarDescaracterizacaoCPF(ctx, marcacao, fator) {
  const x = marcacao.bbox.x * fator;
  const y = marcacao.bbox.y * fator;
  const w = marcacao.bbox.largura * fator;
  const h = marcacao.bbox.altura * fator;

  // CPF: ***.456.789-** → ocultar primeiros 3 dígitos e últimos 2
  // Aproximação: ocultar ~27% inicial e ~18% final
  ctx.fillStyle = '#000000';
  ctx.fillRect(x, y, w * 0.27, h);
  ctx.fillRect(x + w * 0.82, y, w * 0.18, h);

  // Desenhar asteriscos sobre as áreas ocultas
  ctx.fillStyle = '#ffffff';
  const fontSize = Math.min(h * 0.9, 11);
  ctx.font = `bold ${fontSize}px monospace`;
  ctx.textBaseline = 'middle';
  ctx.fillText('***', x + 1, y + h / 2);
  ctx.fillText('**', x + w * 0.82 + 1, y + h / 2);
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
    if (App.modoSelecao) {
      canvas.classList.add('modo-selecao');
      btn.textContent = '✕ Cancelar seleção';
      exibirInfoSelecao();
    } else {
      canvas.classList.remove('modo-selecao');
      btn.textContent = '✏️ Selecionar área';
      ocultarInfoSelecao();
    }
  });

  document.getElementById('btn-novo-documento').addEventListener('click', () => {
    if (confirm('Iniciar novo processamento? O trabalho atual será perdido.')) {
      location.reload();
    }
  });
}

function avancarEtapa(num) {
  // Marcar etapa anterior como concluída
  const etapaAnterior = document.querySelector(`.step[data-step="${App.etapaAtual}"]`);
  if (etapaAnterior) {
    etapaAnterior.classList.remove('ativa');
    etapaAnterior.classList.add('concluida');
  }

  App.etapaAtual = num;

  // Ativar nova etapa
  document.querySelectorAll('.step').forEach(s => {
    s.classList.remove('ativa');
  });
  const novaStep = document.querySelector(`.step[data-step="${num}"]`);
  if (novaStep) novaStep.classList.add('ativa');

  // Mostrar/ocultar seções
  document.querySelectorAll('.etapa-secao').forEach(s => s.classList.add('hidden'));
  const secao = document.getElementById(`etapa-${num}`);
  if (secao) secao.classList.remove('hidden');

  window.scrollTo(0, 0);
}

// ─── Renderizar lista de regras (Etapa 2) ────────────────────────────────────
function renderizarListaRegras() {
  const lista = document.getElementById('lista-regras-auto');
  if (!lista) return;

  lista.innerHTML = REGRAS.map(r => `
    <div class="item-regra">
      <input type="checkbox" id="regra-${r.id}" ${r.ativa ? 'checked' : ''}
        onchange="toggleRegra('${r.id}', this.checked)">
      <label for="regra-${r.id}" class="nome-regra">${r.nome}</label>
      <span class="tag-tratamento ${r.tratamento === 'tarjar' ? 'tag-tarjar' : r.tratamento === 'descaracterizar' ? 'tag-descaracterizar' : 'tag-manter'}">
        ${r.tratamento === 'descaracterizar' ? 'Descarac.' : r.tratamento === 'tarjar' ? 'Tarjar' : 'Manter'}
      </span>
    </div>
  `).join('');
}

function toggleRegra(id, ativo) {
  if (ativo) App.regrasAtivas.add(id);
  else App.regrasAtivas.delete(id);
}

// ─── Utilitários ─────────────────────────────────────────────────────────────
function normalizarTexto(texto) {
  return texto
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '');
}

function nomeExibicaoPapel(papel) {
  const mapa = {
    investigado: 'Investigado',
    vitima: 'Vítima',
    testemunha: 'Testemunha',
    denunciante: 'Denunciante',
    terceiro: 'Terceiro',
    livre: 'Termo livre',
  };
  return mapa[papel] || papel;
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
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function exibirCarregando(ativo, msg = '') {
  const el = document.getElementById('indicador-carregando');
  if (!el) return;
  if (ativo) {
    el.textContent = msg;
    el.classList.remove('hidden');
  } else {
    el.classList.add('hidden');
  }
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
  el.className = `alerta alerta-${tipo}`;
  el.innerHTML = `<span class="alerta-icone">${tipo === 'erro' ? '❌' : tipo === 'aviso' ? '⚠️' : 'ℹ️'}</span><div>${escapeHtml(msg)}</div>`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 8000);
}

function exibirInfoSelecao() {
  let el = document.getElementById('info-selecao');
  if (!el) {
    el = document.createElement('div');
    el.id = 'info-selecao';
    document.body.appendChild(el);
  }
  el.textContent = 'Clique e arraste para selecionar uma área a tarjar';
  el.style.display = 'block';
}

function ocultarInfoSelecao() {
  const el = document.getElementById('info-selecao');
  if (el) el.style.display = 'none';
}
