/**
 * Tarjamento Coger — Ferramenta de Tarjamento Automático de PDF
 * Corregedoria da Receita Federal do Brasil
 */
'use strict';

// Versão da aplicação. Confira no console (F12) que esta é a versão carregada.
const VERSAO_APP = 'v10';
console.info(`%cTarjamento Coger ${VERSAO_APP} carregado`, 'color:#1a3a5c;font-weight:bold');

// ─── Estado global ────────────────────────────────────────────────────────────
const App = {
  etapaAtual: 1,
  pdfBytes: null, pdfNome: '', pdfDoc: null,
  totalPaginas: 0, paginaAtual: 1,
  escala: 1.5,

  contexto: { julgado: 'nao', assedio: false },
  termos: [],
  regrasAtivas: new Set(),

  // Map<pagina, Marcacao[]>
  marcacoesPorPagina: new Map(),
  // Map<pagina, { indice: IndiceItem[], textoPlano: string }>
  textoPorPagina: new Map(),

  modoSelecao: false,
  ocrDisponivel: false,     // true se Tesseract carregou
  ocrLinguagem: 'por',      // língua usada no OCR
};

// ─── Regras de detecção automática ───────────────────────────────────────────
const REGRAS = [
  {
    id: 'cpf', nome: 'CPF',
    // OCR pode dividir "567-09" em dois tokens: "567" + "-09" → espaço antes do hífen.
    // [\s.,\-]{0,2} cobre " -", "-", ".", " " entre o último grupo de 3 e os 2 finais.
    regex: /(?<!\d)\d{3}[\s.,]?\d{3}[\s.,]?\d{3}[\s.,\-]{0,2}\d{2}(?!\d)/g,
    tratamento: 'descaracterizar', ativa: true,
  },
  {
    id: 'cnpj', nome: 'CNPJ',
    regex: /(?<!\d)\d{2}[\s.,]?\d{3}[\s.,]?\d{3}[\s\/]?\d{4}[\s\-]?\d{2}(?!\d)/g,
    tratamento: 'tarjar', ativa: false,
  },
  {
    id: 'rg', nome: 'RG / Identidade',
    regex: /(?:R\.?G\.?|Identidade|C[eé]dula)[:\s#nNºo°]*([0-9]{1,2}[\s.]?[0-9]{3}[\s.]?[0-9]{3}[\s\-]?[0-9A-Za-z])/gi,
    tratamento: 'tarjar', ativa: true,
  },
  {
    id: 'matricula', nome: 'Matrícula / SIAPE',
    regex: /(?:matr[íi]cula|SIAPE)[:\s#nNºo°]*([0-9]{6,8})/gi,
    tratamento: 'tarjar', ativa: true,
  },
  {
    id: 'conta', nome: 'Conta Bancária / Agência',
    regex: /(?:ag[eê]ncia|conta(?:\s+corrente|\s+poupan[çc]a)?)[:\s#nNºo°]*([0-9]{3,6}[\s\-]?[0-9X])/gi,
    tratamento: 'tarjar', ativa: true,
  },
  {
    id: 'nascimento', nome: 'Data de Nascimento',
    regex: /(?:nasc(?:ido|eu|imento)?(?:\s+em)?|data\s+de\s+nascimento)[:\s]*([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})/gi,
    tratamento: 'tarjar', ativa: true,
  },
  {
    id: 'email', nome: 'E-mail',
    regex: /\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b/g,
    tratamento: 'tarjar', ativa: true,
    filtro: m => !m.toLowerCase().includes('@receita.fazenda.gov.br') && !m.toLowerCase().includes('@rfb.gov.br'),
  },
  {
    id: 'telefone', nome: 'Telefone',
    regex: /\(?\d{2}\)?\s?(?:9\s?)?\d{4}[\s\-]?\d{4}/g,
    tratamento: 'tarjar', ativa: true,
  },
  {
    id: 'endereco', nome: 'Endereço Residencial',
    regex: /(?:Rua|Av\.|Avenida|Travessa|Alameda|Estrada|R\.)\s+[A-Za-zÀ-ú\s]{3,40},?\s*n[°º]?\s*[0-9]+/gi,
    tratamento: 'tarjar', ativa: true,
  },
  {
    id: 'saude', nome: 'Palavras-chave de Saúde',
    regex: /\b(CID[\s\-]?[A-Z][0-9]+|atestado\s+m[eé]dico|laudo\s+m[eé]dico|afastamento\s+por|diagn[oó]stico|gestante|gravidez|licen[çc]a[\s\-]sa[úu]de|sa[úu]de\s+mental|transtorno|depress[aão]+|ansiedade)\b/gi,
    tratamento: 'tarjar', ativa: true,
  },
];

const IDENT_INDIRETOS = [
  /\bcargo\b/i, /\blota[çc][aã]o\b/i, /\bsetor\b/i, /\bunidade\b/i,
  /\d{1,2}\/\d{1,2}\/\d{2,4}/, /\bn[°º\.]\s*proc/i, /\bfilia[çc][aã]o\b/i,
];

// ─── Detecção heurística de nomes próprios ────────────────────────────────────
// Palavras/siglas que aparecem em maiúsculas mas NÃO são nomes de pessoas.
const BLOCKLIST_NOMES = new Set([
  'MINISTERIO','SECRETARIA','DEPARTAMENTO','COORDENACAO','DIVISAO','GERENCIA',
  'RECEITA','FEDERAL','BRASIL','FAZENDA','TRIBUTARIA','TRIBUTARIO',
  'TRIBUNAL','SUPERIOR','JUSTICA','CORTE','SUPREMO','PLENO','TURMA',
  'PROCESSO','RELATORIO','PORTARIA','RESOLUCAO','INSTRUCAO','NORMATIVA',
  'REPRESENTACAO','FUNCIONAL','ADMINISTRATIVA','ADMINISTRATIVO','ADMINISTRATIVOS',
  'PROCURADORIA','ADVOCACIA','GERAL','UNIAO','NACIONAL','ESPECIAL',
  'ESTADO','MUNICIPIO','PREFEITURA','CAMARA','SENADO','CONGRESSO',
  'JANEIRO','FEVEREIRO','MARCO','ABRIL','MAIO','JUNHO',
  'JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO',
  'SEGUNDA','TERCA','QUARTA','QUINTA','SEXTA','SABADO','DOMINGO',
  'CONTRIBUINTE','SERVIDOR','SERVIDORA','FUNCIONARIO','FUNCIONARIA',
  'INVESTIGADO','INVESTIGADA','AUDITORA','AUDITOR','TECNICO','TECNICA',
  'CAPITULO','SECAO','ARTIGO','PARAGRAFO','INCISO','ALINEA',
  'CONFIDENCIAL','SIGILOSO','RESTRITO','PUBLICO','PRIVADO',
  'OBJETO','ASSUNTO','EMENTA','CONCLUSAO','INTRODUCAO','CONSIDERACOES',
  'COGER','RFB','CGU','TCU','STF','STJ','TST','TRF','TRT','CNJ',
  'IRPF','IRPJ','DIRF','DCTF','SEFAZ','SEFIN','SPED','ECF','ECD',
  'DELEGACIA','REGIONAL','FISCAL','ADUANEIRA','ESPECIAL','REPRE',
  'COM','SEM','SOB','POR','PARA','QUE','NAO','SIM','MAS','ATE',
  'TOTAL','VALOR','DATA','HORA','LOCAL','TIPO','FORMA','MODO',
  'NUMERO','CODIGO','CHAVE','SENHA','REGISTRO','DOCUMENTO','FOLHA',
]);

// Regex: 1–6 palavras em MAIÚSCULAS (incluindo nome sozinho com ≥5 chars).
// {0,5} permite palavra única; o filtro de comprimento e blocklist filtra falsos positivos.
const RE_NOMES_CAPS = /\b([A-ZÁÉÍÓÚÂÊÔÃÕÀÜÇ]{2,}(?:\s+(?:DE|DO|DA|DOS|DAS|E|[A-ZÁÉÍÓÚÂÊÔÃÕÀÜÇ]{2,})){0,5})\b/g;

function detectarNomesProvaveis(pagina, texto, indice, marcacoes) {
  const PARTICULAS = new Set(['DE','DO','DA','DOS','DAS','E']);
  const re = new RegExp(RE_NOMES_CAPS.source, RE_NOMES_CAPS.flags);
  let m;
  while ((m = re.exec(texto)) !== null) {
    const seq = m[1];
    const palavras = seq.split(/\s+/);
    const substantivas = palavras.filter(p => !PARTICULAS.has(p));
    if (substantivas.length === 0) continue;
    // Palavra única: exigir ≥5 chars para reduzir falsos positivos (siglas, abreviaturas)
    if (substantivas.length === 1 && substantivas[0].length < 5) continue;
    // Múltiplas palavras: ao menos 2 substantivas
    if (substantivas.length > 1 && substantivas.filter(p => p.length >= 2).length < 2) continue;

    // Normalizar (sem acentos) para comparar com blocklist
    const normalizadas = substantivas.map(p =>
      p.normalize('NFD').replace(/[̀-ͯ]/g, '')
    );
    // Skip se TODAS as palavras substantivas estiverem na blocklist
    if (normalizadas.every(p => BLOCKLIST_NOMES.has(p))) continue;

    bboxesDoMatch(m.index, m.index + seq.length, indice).forEach(bbox => {
      // Evitar duplicatas: pular se já houver marcação com bbox sobreposto
      const sobrepoe = marcacoes.some(mk =>
        mk.pagina === pagina &&
        mk.bbox.x < bbox.x + bbox.largura &&
        mk.bbox.x + mk.bbox.largura > bbox.x &&
        mk.bbox.y < bbox.y + bbox.altura &&
        mk.bbox.y + mk.bbox.altura > bbox.y
      );
      if (sobrepoe) return;

      marcacoes.push({
        id: gerarId(), pagina, texto: seq, bbox,
        origem: 'Sugestão automática: possível nome próprio',
        tipo: 'tarjar', estado: 'sugerido', fonteRegra: 'nome_proprio',
      });
    });
  }
}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  REGRAS.forEach(r => { if (r.ativa) App.regrasAtivas.add(r.id); });
  configurarUpload();
  configurarFormularioEtapa2();
  configurarBotoesNavegacao();
  renderizarListaRegras();
  verificarTesseract();
});

async function verificarTesseract() {
  if (typeof Tesseract === 'undefined') {
    document.getElementById('status-ocr').innerHTML =
      '⚠️ OCR não disponível (Tesseract.js não carregado). PDFs escaneados: use seleção manual.';
    document.getElementById('status-ocr').className = 'alerta alerta-aviso';
    document.getElementById('status-ocr').classList.remove('hidden');
    return;
  }
  App.ocrDisponivel = true;
}

// ─── ETAPA 1: Upload ──────────────────────────────────────────────────────────
function configurarUpload() {
  const area = document.getElementById('area-upload');
  const input = document.getElementById('input-arquivo');
  area.addEventListener('click', () => input.click());
  area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('drag-over'); });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault(); area.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) processarArquivo(e.dataTransfer.files[0]);
  });
  input.addEventListener('change', e => { if (e.target.files[0]) processarArquivo(e.target.files[0]); });
}

async function processarArquivo(file) {
  if (!file.name.toLowerCase().endsWith('.pdf') && !file.type.includes('pdf')) {
    mostrarAlerta('erro', 'Selecione um arquivo PDF.'); return;
  }
  try {
    const bytes = await new Promise((res, rej) => {
      const r = new FileReader();
      r.onload = e => res(e.target.result);
      r.onerror = rej;
      r.readAsArrayBuffer(file);
    });
    App.pdfBytes = new Uint8Array(bytes);
    App.pdfNome = file.name;
    // standardFontDataUrl/cMapUrl são ESSENCIAIS para PDFs que usam fontes
    // padrão NÃO embutidas (comum em relatórios do eCAC/Portal IRPF-JAVA).
    // Sem isso, o PDF.js renderiza o texto em posição vertical incorreta e as
    // tarjas (calculadas pelas métricas corretas do texto) ficam desalinhadas.
    // São apenas arquivos estáticos de fonte — nenhum dado do PDF é enviado.
    App.pdfDoc = await pdfjsLib.getDocument({
      data: App.pdfBytes,
      standardFontDataUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/standard_fonts/',
      cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/cmaps/',
      cMapPacked: true,
    }).promise;
    App.totalPaginas = App.pdfDoc.numPages;

    document.getElementById('nome-arquivo').textContent = file.name;
    document.getElementById('paginas-arquivo').textContent = `${App.totalPaginas} página(s)`;
    document.getElementById('tamanho-arquivo').textContent = formatarTamanho(file.size);
    document.getElementById('info-arquivo').classList.add('visivel');
    document.getElementById('btn-avancar-etapa1').disabled = false;
  } catch (err) {
    let msg = 'Não foi possível abrir o PDF.';
    if (typeof pdfjsLib === 'undefined') msg = 'PDF.js não carregado. Verifique a conexão e recarregue.';
    else if (err?.name === 'PasswordException') msg = 'PDF protegido por senha.';
    else if (err?.name === 'InvalidPDFException') msg = 'Arquivo inválido ou corrompido.';
    mostrarAlerta('erro', msg);
  }
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
  ].forEach(([btn, papel, lista]) =>
    document.getElementById(btn).addEventListener('click', () => adicionarTermoPapel(papel, lista)));

  document.querySelectorAll('input[name="julgado"]').forEach(el =>
    el.addEventListener('change', () => { App.contexto.julgado = el.value; atualizarTagInvestigado(); }));
  document.querySelectorAll('input[name="assedio"]').forEach(el =>
    el.addEventListener('change', () => { App.contexto.assedio = el.value === 'sim'; }));
}

function atualizarTagInvestigado() {
  const tag = document.getElementById('tag-investigado');
  if (!tag) return;
  const manter = App.contexto.julgado === 'sancionado';
  tag.textContent = manter ? 'Manter' : 'Tarjar';
  tag.className = 'tag-tratamento ' + (manter ? 'tag-manter' : 'tag-tarjar');
}

function tratamentoPorPapel(papel) {
  return (papel === 'investigado' && App.contexto.julgado === 'sancionado') ? 'manter' : 'tarjar';
}

function adicionarTermoPapel(papel, listaId) {
  const div = document.createElement('div');
  div.className = 'item-termo';
  div.innerHTML = `
    <input type="text" placeholder="Nome ou termo exato..." class="input-termo" data-papel="${papel}">
    <select class="select-busca" title="Tipo de busca">
      <option value="exata">Palavra exata</option>
      <option value="substring">Substring</option>
    </select>
    <button class="btn-remover-termo" onclick="this.closest('.item-termo').remove()">✕</button>`;
  document.getElementById(listaId).appendChild(div);
  div.querySelector('.input-termo').focus();
}

function coletarTermosFormulario() {
  App.termos = [];
  document.querySelectorAll('.input-termo').forEach(input => {
    const papel = input.dataset.papel;
    const busca = input.closest('.item-termo').querySelector('.select-busca').value;
    input.value.split(',').map(t => t.trim()).filter(Boolean).forEach(termo => {
      App.termos.push({ termo, papel, tratamento: tratamentoPorPapel(papel), buscaExata: busca === 'exata' });
    });
  });
}

// ─── ETAPA 3: Pré-processamento ───────────────────────────────────────────────
// OCR_SCALE: escala usada para renderizar o canvas passado ao Tesseract.
// As coordenadas do Tesseract estão nessa escala e precisam ser divididas por
// OCR_SCALE para converter para o espaço de coordenadas scale=1.0 do PDF.js.
// 2.5 (~225 DPI) melhora o reconhecimento de números (CPF) e nomes em scans.
const OCR_SCALE = 2.5;

async function executarPreProcessamento() {
  coletarTermosFormulario();
  App.marcacoesPorPagina.clear();
  App.textoPorPagina.clear();

  document.getElementById('barra-progresso-container').style.display = 'block';
  atualizarProgresso(0, 'Iniciando...');

  // ── Inicializar Tesseract worker ──────────────────────────────────────────
  let worker = null;
  if (App.ocrDisponivel) {
    atualizarProgresso(2, 'Carregando dados de OCR (português) — aguarde...');
    try {
      worker = await Tesseract.createWorker('por', 1, {
        logger: m => {
          if (m.status === 'loading tesseract core') atualizarProgresso(3, 'Carregando Tesseract...');
          if (m.status === 'loading language traineddata') atualizarProgresso(5, 'Baixando dados de idioma (por) — pode levar alguns segundos...');
          if (m.status === 'initializing tesseract') atualizarProgresso(8, 'Inicializando OCR...');
        },
      });
      App.ocrLinguagem = 'por';
    } catch (errPor) {
      // fallback para inglês — números (CPF, tel etc.) são detectados normalmente
      try {
        worker = await Tesseract.createWorker('eng', 1, { logger: () => {} });
        App.ocrLinguagem = 'eng';
        mostrarAlerta('aviso', 'OCR iniciado em modo inglês (dados do português indisponíveis). Números como CPF ainda serão detectados. Textos em português podem ter menor precisão.');
      } catch (errEng) {
        worker = null;
        mostrarAlerta('aviso', 'OCR não foi possível inicializar. Documentos escaneados não terão detecção automática — use a seleção manual na Etapa 4 para marcar as áreas sensíveis.');
      }
    }
  }

  // ── Processar páginas ─────────────────────────────────────────────────────
  for (let p = 1; p <= App.totalPaginas; p++) {
    const pct = 10 + Math.round(((p - 1) / App.totalPaginas) * 85);
    atualizarProgresso(pct, `Analisando página ${p} de ${App.totalPaginas}...`);

    const page = await App.pdfDoc.getPage(p);
    const viewport1 = page.getViewport({ scale: 1.0 });

    // Índice de itens com rastreamento de offset de caractere no textoPlano.
    // Cada item: { x, y, largura, altura, charStart, charEnd }
    // Todos os valores x/y/largura/altura estão em coordenadas de scale=1.0.
    const indice = [];
    let textoPlano = '';

    // ── Extrair texto nativo (PDF com texto) ─────────────────────────────────
    const tc = await page.getTextContent();
    tc.items.forEach(item => {
      if (!item.str) return;
      // Transformar coordenadas: PDF (Y↑) → canvas (Y↓)
      const tx = pdfjsLib.Util.transform(viewport1.transform, item.transform);
      const x = tx[4];
      // tx[5] = posição Y do baseline no canvas.
      // A altura do item em PDF user space corresponde a ~escala 1 px por pt.
      // Subtraímos para obter o TOPO da caixa de texto.
      const altReal = Math.abs(item.height) || 12;
      const y = tx[5] - altReal;
      const larg = Math.abs(item.width) || 8;

      const charStart = textoPlano.length;
      textoPlano += item.str;
      const charEnd = textoPlano.length;
      textoPlano += ' '; // separador não-rastreado

      indice.push({ x, y, largura: larg, altura: altReal + 2, charStart, charEnd });
    });

    // ── OCR se a página for escaneada (pouco/nenhum texto nativo) ────────────
    const temTextoNativo = textoPlano.trim().replace(/\s+/g, '').length > 20;
    let usouOCR = false;

    if (!temTextoNativo && worker) {
      atualizarProgresso(pct + 2, `OCR na página ${p}/${App.totalPaginas}...`);
      try {
        // Renderizar página em canvas de alta resolução para o OCR
        const vpOcr = page.getViewport({ scale: OCR_SCALE });
        const cvOcr = document.createElement('canvas');
        cvOcr.width = Math.round(vpOcr.width);
        cvOcr.height = Math.round(vpOcr.height);
        const ctxOcr = cvOcr.getContext('2d');
        ctxOcr.fillStyle = '#ffffff';
        ctxOcr.fillRect(0, 0, cvOcr.width, cvOcr.height);
        await page.render({ canvasContext: ctxOcr, viewport: vpOcr }).promise;

        const resultado = await worker.recognize(cvOcr);

        resultado.data.words.forEach(word => {
          const txt = word.text?.trim();
          if (!txt || word.confidence < 20) return; // ignorar palavras de baixa confiança

          // CONVERSÃO CRÍTICA: coordenadas do Tesseract estão no espaço do canvas OCR
          // (scale=OCR_SCALE). Dividir por OCR_SCALE converte para espaço scale=1.0.
          const x       = word.bbox.x0 / OCR_SCALE;
          const largura = (word.bbox.x1 - word.bbox.x0) / OCR_SCALE;
          const altReal = (word.bbox.y1 - word.bbox.y0) / OCR_SCALE;
          // Padding vertical de ~18% da altura: a caixa do Tesseract é justa aos
          // glifos; expandir garante cobertura total de acentos e descidas (g, p, ç).
          const padV    = altReal * 0.18;
          const y       = word.bbox.y0 / OCR_SCALE - padV;
          const altura  = altReal + padV * 2;

          const charStart = textoPlano.length;
          textoPlano += txt;
          const charEnd = textoPlano.length;
          textoPlano += ' ';

          indice.push({ x, y, largura, altura, charStart, charEnd, deOcr: true });
        });
        usouOCR = true;
      } catch (e) {
        console.warn(`OCR falhou na página ${p}:`, e);
      }
    }

    App.textoPorPagina.set(p, { indice, textoPlano });

    const marcacoes = [];
    detectarPadroesAutomaticos(p, textoPlano, indice, marcacoes);
    detectarTermosCadastrados(p, textoPlano, indice, marcacoes);
    detectarNomesProvaveis(p, textoPlano, indice, marcacoes);
    App.marcacoesPorPagina.set(p, marcacoes);
  }

  if (worker) { try { await worker.terminate(); } catch (_) {} }

  atualizarProgresso(97, 'Verificando identificação indireta...');
  verificarIdentificacaoIndireta();
  atualizarProgresso(100, 'Concluído!');

  const total = [...App.marcacoesPorPagina.values()].reduce((s, m) => s + m.filter(x => x.estado !== 'sugerido').length, 0);
  const sugeridos = [...App.marcacoesPorPagina.values()].reduce((s, m) => s + m.filter(x => x.estado === 'sugerido').length, 0);
  document.getElementById('stat-marcacoes').textContent = sugeridos > 0 ? `${total} (+${sugeridos} nomes a revisar)` : total;
  document.getElementById('stat-paginas').textContent = App.totalPaginas;

  setTimeout(() => {
    document.getElementById('barra-progresso-container').style.display = 'none';
    document.getElementById('resultados-processamento').classList.remove('hidden');
    document.getElementById('nav-etapa3').style.display = 'flex';
    if (total === 0) {
      mostrarAlerta('aviso', 'Nenhuma marcação detectada automaticamente. Se o documento for escaneado, verifique se o OCR funcionou. Use a Etapa 4 → "Selecionar área" para marcar manualmente as regiões sensíveis.');
    }
  }, 400);
}

// ─── Mapeamento texto→bbox via índice de offsets ──────────────────────────────
// Encontra os itens cujo intervalo [charStart, charEnd] sobrepõe [matchStart, matchEnd]
// e os AGRUPA POR LINHA (pela coordenada Y). Retorna UMA caixa por linha.
//
// Para PDFs com texto nativo, um item pode ser uma linha inteira. Usar o bbox
// completo do item quando o match é apenas uma parte dele gera caixas muito largas.
// A solução é calcular um sub-bbox PROPORCIONAL: se o match cobre K% dos caracteres
// do item, a largura da caixa é K% da largura do item, posicionada proporcionalmente.
// Para itens OCR (deOcr:true), cada palavra já é seu próprio item → usar bbox completo.
function bboxesDoMatch(matchStart, matchEnd, indice) {
  const participantes = indice.filter(it =>
    it.charEnd > matchStart && it.charStart < matchEnd
  );
  if (participantes.length === 0) return [];

  // Calcular sub-bbox proporcional por item.
  const participantesComSub = participantes.map(it => {
    if (it.deOcr) return { ...it, subX: it.x, subW: it.largura };
    const itemLen = it.charEnd - it.charStart;
    if (itemLen === 0) return { ...it, subX: it.x, subW: it.largura };
    // Fração do item coberta pelo match
    const mStart = Math.max(matchStart, it.charStart) - it.charStart;
    const mEnd   = Math.min(matchEnd,   it.charEnd)   - it.charStart;
    const subX = it.x + (mStart / itemLen) * it.largura;
    const subW = Math.max(4, ((mEnd - mStart) / itemLen) * it.largura);
    return { ...it, subX, subW };
  });

  // Agrupar por linha: itens cujo centro vertical está próximo pertencem à mesma linha.
  const linhas = [];
  participantesComSub
    .slice()
    .sort((a, b) => a.y - b.y)
    .forEach(it => {
      const cy = it.y + it.altura / 2;
      let linha = linhas.find(L => Math.abs(L.cy - cy) < Math.max(L.alturaMax, it.altura) * 0.7);
      if (!linha) { linha = { cy, alturaMax: it.altura, itens: [] }; linhas.push(linha); }
      linha.itens.push(it);
      linha.alturaMax = Math.max(linha.alturaMax, it.altura);
    });

  const P = 3; // padding em px para cobertura completa
  return linhas.map(L => {
    const x    = Math.min(...L.itens.map(i => i.subX));
    const y    = Math.min(...L.itens.map(i => i.y));
    const xMax = Math.max(...L.itens.map(i => i.subX + i.subW));
    const yMax = Math.max(...L.itens.map(i => i.y + i.altura));
    return { x: x - P, y: y - P, largura: (xMax - x) + P * 2, altura: (yMax - y) + P * 2 };
  });
}

// ─── Detecção de padrões automáticos ─────────────────────────────────────────
function detectarPadroesAutomaticos(pagina, texto, indice, marcacoes) {
  REGRAS.forEach(regra => {
    if (!App.regrasAtivas.has(regra.id)) return;
    const re = new RegExp(regra.regex.source, regra.regex.flags);
    let m;
    while ((m = re.exec(texto)) !== null) {
      if (regra.filtro && !regra.filtro(m[0])) continue;
      bboxesDoMatch(m.index, m.index + m[0].length, indice).forEach(bbox => {
        marcacoes.push({
          id: gerarId(), pagina, texto: m[0], bbox,
          origem: `Regra automática: ${regra.nome}`,
          tipo: regra.tratamento, estado: 'incluido', fonteRegra: regra.id,
        });
      });
    }
  });
}

// ─── Detecção de termos cadastrados ──────────────────────────────────────────
function detectarTermosCadastrados(pagina, texto, indice, marcacoes) {
  App.termos.forEach(termo => {
    if (termo.tratamento === 'manter') return;

    // Normalizar para busca case-insensitive e sem acentos
    const tNorm = normalizarTexto(termo.termo);
    const xNorm = normalizarTexto(texto);

    // A normalização preserva os comprimentos de string (apenas remove diacríticos),
    // então pos em xNorm == pos em texto original.
    let idx = 0;
    while (idx <= xNorm.length - tNorm.length) {
      const pos = xNorm.indexOf(tNorm, idx);
      if (pos === -1) break;

      // Verificar palavra exata (não faz parte de palavra maior)
      if (termo.buscaExata) {
        const ant = pos > 0 ? xNorm[pos - 1] : ' ';
        const dep = pos + tNorm.length < xNorm.length ? xNorm[pos + tNorm.length] : ' ';
        if (/[a-z0-9àáâãäéêíóõôúüçñ]/i.test(ant) || /[a-z0-9àáâãäéêíóõôúüçñ]/i.test(dep)) {
          idx = pos + 1; continue;
        }
      }

      bboxesDoMatch(pos, pos + tNorm.length, indice).forEach(bbox => {
        marcacoes.push({
          id: gerarId(), pagina,
          texto: texto.slice(pos, pos + termo.termo.length) || termo.termo,
          bbox,
          origem: `Termo cadastrado: ${nomeExibicaoPapel(termo.papel)} — ${termo.termo}`,
          tipo: termo.tratamento, estado: 'incluido', fonteTermo: termo,
        });
      });
      idx = pos + tNorm.length;
    }
  });
}

// ─── Alerta de identificação indireta ────────────────────────────────────────
function verificarIdentificacaoIndireta() {
  const alertas = [];
  App.textoPorPagina.forEach(({ textoPlano }, pagina) => {
    const hits = IDENT_INDIRETOS.filter(re => re.test(textoPlano));
    if (hits.length < 3) return;
    const marcPag = App.marcacoesPorPagina.get(pagina) || [];
    const temNome = marcPag.some(m => m.fonteTermo &&
      ['vitima', 'testemunha', 'investigado'].includes(m.fonteTermo.papel) && m.estado === 'incluido');
    if (!temNome) alertas.push(pagina);
  });
  if (alertas.length > 0) {
    const el = document.getElementById('alertas-indiretos');
    if (el) {
      el.innerHTML = alertas.map(p => `
        <div class="alerta alerta-aviso">
          <span class="alerta-icone">⚠️</span>
          <div><strong>Pág. ${p}:</strong> Identificadores indiretos detectados (cargo, data, lotação etc.) — pode identificar a pessoa mesmo sem o nome. Revise.</div>
        </div>`).join('');
      el.classList.remove('hidden');
    }
  }
}

// ─── ETAPA 4: Revisão visual ──────────────────────────────────────────────────
let renderTask = null;

async function inicializarRevisao() {
  App.paginaAtual = 1;
  // Propagar alertas de identificação indireta para etapa 4
  const a3 = document.getElementById('alertas-indiretos');
  const a4 = document.getElementById('alertas-indiretos-revisao');
  if (a3 && a4 && a3.innerHTML.trim()) { a4.innerHTML = a3.innerHTML; a4.classList.remove('hidden'); }
  await renderizarPaginaRevisao(1);
  atualizarPainelMarcacoes();
  configurarSelecaoManual();
}

async function renderizarPaginaRevisao(numPagina) {
  if (renderTask) { try { renderTask.cancel(); } catch (_) {} renderTask = null; }

  const page = await App.pdfDoc.getPage(numPagina);
  const canvasPdf = document.getElementById('canvas-pdf');
  const overlay   = document.getElementById('overlay-marcacoes');
  const viewport  = page.getViewport({ scale: App.escala });

  // Definir dimensões internas de ambos os canvas identicamente
  canvasPdf.width = overlay.width = Math.round(viewport.width);
  canvasPdf.height = overlay.height = Math.round(viewport.height);

  // Guardar escala para uso nos cálculos de overlay e geração final
  App._escalaRevisao = App.escala;

  const ctxPdf = canvasPdf.getContext('2d');
  ctxPdf.fillStyle = '#fff';
  ctxPdf.fillRect(0, 0, canvasPdf.width, canvasPdf.height);

  renderTask = page.render({ canvasContext: ctxPdf, viewport });
  await renderTask.promise;
  renderTask = null;

  desenharOverlay(numPagina);
  atualizarNavPaginas();
}

// Desenha as marcações no canvas overlay.
// As bboxes estão em coordenadas scale=1.0.
// Multiplicamos pela escala de revisão para obter coordenadas no canvas de display.
function desenharOverlay(numPagina) {
  const overlay = document.getElementById('overlay-marcacoes');
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);

  const E = App._escalaRevisao; // fator de escala: bbox(scale=1) → canvas pixels

  (App.marcacoesPorPagina.get(numPagina) || []).forEach(m => {
    if (m.estado !== 'incluido' && m.estado !== 'sugerido') return;
    const x = m.bbox.x * E, y = m.bbox.y * E;
    const w = m.bbox.largura * E, h = m.bbox.altura * E;

    if (m.estado === 'sugerido') {
      ctx.save();
      ctx.setLineDash([5, 3]);
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);
      ctx.restore();
      return;
    }

    if (m.tipo === 'tarjar') {
      ctx.fillStyle = 'rgba(220,38,38,0.40)';
      ctx.strokeStyle = '#dc2626';
    } else {
      ctx.fillStyle = 'rgba(217,119,6,0.40)';
      ctx.strokeStyle = '#d97706';
    }
    ctx.fillRect(x, y, w, h);
    ctx.lineWidth = 1.5;
    ctx.strokeRect(x, y, w, h);
  });
}

function atualizarPainelMarcacoes() {
  const lista  = document.getElementById('lista-marcacoes-painel');
  const marcas = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  const incl   = marcas.filter(m => m.estado === 'incluido').length;
  const suger  = marcas.filter(m => m.estado === 'sugerido').length;
  const cnt    = document.getElementById('contador-marcacoes-painel');
  if (cnt) cnt.textContent = suger > 0 ? `${incl} tarj. + ${suger} sugerido(s)` : `${incl}/${marcas.filter(m=>m.estado!=='sugerido').length}`;

  const confirmadas = marcas.filter(m => m.estado !== 'sugerido');
  const sugeridas   = marcas.filter(m => m.estado === 'sugerido');

  if (confirmadas.length === 0 && sugeridas.length === 0) {
    lista.innerHTML = '<p style="color:#6b7280;padding:12px;font-size:12px;text-align:center">Nenhuma marcação nesta página</p>';
    return;
  }

  const renderConfirmada = m => {
    const ok = m.estado === 'incluido';
    return `
      <div class="item-marcacao ${ok ? '' : 'removida'}" id="marcacao-${m.id}">
        <div class="texto-marcacao">${escapeHtml(m.texto)}</div>
        <div class="origem-marcacao">${escapeHtml(m.origem)}</div>
        <div class="acoes-marcacao">
          ${ok ? `
            <button class="btn-marcacao btn-tipo-tarjar ${m.tipo==='tarjar'?'ativo':''}"
              onclick="alterarTipo('${m.id}','tarjar')">■ Tarjar</button>
            <button class="btn-marcacao btn-tipo-descarac ${m.tipo==='descaracterizar'?'ativo':''}"
              onclick="alterarTipo('${m.id}','descaracterizar')">▒ Descarac.</button>
            <button class="btn-marcacao btn-remover-marcacao"
              onclick="removerMarcacao('${m.id}')">✕ Remover</button>
          ` : `
            <button class="btn-marcacao btn-restaurar-marcacao"
              onclick="restaurarMarcacao('${m.id}')">↺ Restaurar</button>
          `}
        </div>
      </div>`;
  };

  const renderSugerida = m => `
    <div class="item-marcacao sugerido" id="marcacao-${m.id}">
      <div class="texto-marcacao">${escapeHtml(m.texto)}</div>
      <div class="origem-marcacao">${escapeHtml(m.origem)}</div>
      <div class="acoes-marcacao">
        <button class="btn-marcacao btn-confirmar-sugestao"
          onclick="confirmarSugestao('${m.id}')">✓ Tarjar</button>
        <button class="btn-marcacao btn-ignorar-sugestao"
          onclick="ignorarSugestao('${m.id}')">✗ Ignorar</button>
      </div>
    </div>`;

  let html = confirmadas.map(renderConfirmada).join('');
  if (sugeridas.length > 0) {
    html += `<div class="secao-sugestoes">
      <div class="titulo-sugestoes">⚠️ Possíveis nomes próprios — revise e decida:</div>
      ${sugeridas.map(renderSugerida).join('')}
    </div>`;
  }
  lista.innerHTML = html;
}

function getMarca(id) { return (App.marcacoesPorPagina.get(App.paginaAtual)||[]).find(m=>m.id===id); }

function alterarTipo(id, tipo) {
  const m = getMarca(id); if (!m) return;
  m.tipo = tipo; desenharOverlay(App.paginaAtual); atualizarPainelMarcacoes();
}
function removerMarcacao(id) {
  const m = getMarca(id); if (!m) return;
  m.estado = 'removido'; desenharOverlay(App.paginaAtual); atualizarPainelMarcacoes();
}
function restaurarMarcacao(id) {
  const m = getMarca(id); if (!m) return;
  m.estado = 'incluido'; desenharOverlay(App.paginaAtual); atualizarPainelMarcacoes();
}
function confirmarSugestao(id) {
  const m = getMarca(id); if (!m) return;
  m.estado = 'incluido'; desenharOverlay(App.paginaAtual); atualizarPainelMarcacoes();
}
function ignorarSugestao(id) {
  const m = getMarca(id); if (!m) return;
  m.estado = 'ignorado'; desenharOverlay(App.paginaAtual); atualizarPainelMarcacoes();
}

function atualizarNavPaginas() {
  document.getElementById('num-pagina-atual').textContent = App.paginaAtual;
  document.getElementById('total-paginas-revisao').textContent = App.totalPaginas;
  document.getElementById('btn-pagina-anterior').disabled = App.paginaAtual <= 1;
  document.getElementById('btn-proxima-pagina').disabled  = App.paginaAtual >= App.totalPaginas;
}

// ─── Seleção manual no canvas ─────────────────────────────────────────────────
function configurarSelecaoManual() {
  const canvas = document.getElementById('canvas-pdf');
  const container = document.getElementById('painel-canvas');
  let arrastando = false, ox = 0, oy = 0;
  let selDiv = null;

  // Converte posição de evento (CSS px) para coordenadas de bbox (scale=1.0)
  function evtParaBbox(e) {
    const rect = canvas.getBoundingClientRect();
    // displayScale: relação entre pixels internos do canvas e pixels CSS exibidos
    const displayScale = canvas.width / rect.width;
    const cx = (e.clientX - rect.left) * displayScale;
    const cy = (e.clientY - rect.top)  * displayScale;
    return { cx, cy };
  }

  canvas.addEventListener('mousedown', e => {
    if (!App.modoSelecao) return;
    arrastando = true;
    const rect = canvas.getBoundingClientRect();
    ox = e.clientX - rect.left;
    oy = e.clientY - rect.top;
    if (!selDiv) {
      selDiv = document.createElement('div');
      selDiv.style.cssText = 'position:absolute;border:2px solid #2563eb;background:rgba(37,99,235,0.12);pointer-events:none';
      container.appendChild(selDiv);
    }
    selDiv.style.left = ox + 'px';
    selDiv.style.top  = oy + 'px';
    selDiv.style.width = selDiv.style.height = '0';
    selDiv.style.display = 'block';
  });

  canvas.addEventListener('mousemove', e => {
    if (!arrastando || !selDiv) return;
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left, cy = e.clientY - rect.top;
    selDiv.style.left   = Math.min(ox, cx) + 'px';
    selDiv.style.top    = Math.min(oy, cy) + 'px';
    selDiv.style.width  = Math.abs(cx - ox) + 'px';
    selDiv.style.height = Math.abs(cy - oy) + 'px';
  });

  canvas.addEventListener('mouseup', e => {
    if (!arrastando) return;
    arrastando = false;
    if (selDiv) selDiv.style.display = 'none';

    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left, cy = e.clientY - rect.top;
    const w = Math.abs(cx - ox), h = Math.abs(cy - oy);
    if (w < 5 || h < 5) return;

    // displayScale: quantos pixels internos do canvas por pixel CSS
    const ds = canvas.width / rect.width;
    // Converter de CSS px → canvas px → bbox scale=1.0
    const bboxPdf = {
      x:       Math.min(ox, cx) * ds / App._escalaRevisao,
      y:       Math.min(oy, cy) * ds / App._escalaRevisao,
      largura: w * ds / App._escalaRevisao,
      altura:  h * ds / App._escalaRevisao,
    };
    adicionarMarcacaoManual(bboxPdf);
  });
}

function adicionarMarcacaoManual(bbox) {
  const tipo = confirm('Clique OK para TARJAR (bloco preto)\nClique Cancelar para DESCARACTERIZAR (máscara parcial)')
    ? 'tarjar' : 'descaracterizar';
  const marcas = App.marcacoesPorPagina.get(App.paginaAtual) || [];
  marcas.push({
    id: gerarId(), pagina: App.paginaAtual, texto: '[Seleção manual]',
    bbox, origem: 'Marcação manual', tipo, estado: 'incluido',
  });
  App.marcacoesPorPagina.set(App.paginaAtual, marcas);
  desenharOverlay(App.paginaAtual);
  atualizarPainelMarcacoes();
  // Desativar modo seleção
  App.modoSelecao = false;
  document.getElementById('canvas-pdf').classList.remove('modo-selecao');
  document.getElementById('btn-selecao-manual').textContent = '✏️ Selecionar área';
  const info = document.getElementById('info-selecao');
  if (info) info.style.display = 'none';
}

// ─── ETAPA 5: Geração do PDF final ────────────────────────────────────────────
async function gerarPDFFinal() {
  if (!window.jspdf) {
    mostrarAlerta('erro', 'jsPDF não carregado. Verifique a conexão e recarregue.'); return;
  }
  const { jsPDF } = window.jspdf;

  document.getElementById('barra-progresso-container').style.display = 'block';
  atualizarProgresso(0, 'Preparando...');

  // DPI de 150 ≈ escala 2.083 sobre pontos PDF (72 dpi base).
  // Para o documento de teste (scan 150 DPI, 1240×1754 px, página 595×842 pt),
  // ESCALA_FINAL ≈ 2.083 produz canvas de 1240×1754 px — coincide com o scan original.
  const ESCALA_FINAL = 150 / 72; // ≈ 2.083

  try {
    const doc = new jsPDF({ unit: 'pt', compress: true });
    let primeira = true;

    for (let p = 1; p <= App.totalPaginas; p++) {
      atualizarProgresso(
        Math.round((p / App.totalPaginas) * 94),
        `Rasterizando página ${p} de ${App.totalPaginas}...`
      );

      const page = await App.pdfDoc.getPage(p);
      const vp   = page.getViewport({ scale: ESCALA_FINAL });

      const cv  = document.createElement('canvas');
      cv.width  = Math.round(vp.width);
      cv.height = Math.round(vp.height);
      const ctx = cv.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, cv.width, cv.height);
      await page.render({ canvasContext: ctx, viewport: vp }).promise;

      // Aplicar marcações no canvas (nível de pixel).
      // estado 'sugerido' e 'ignorado' NÃO são aplicados — somente 'incluido'.
      // Ordem: tarjar primeiro, descaracterizar por último — garante que a
      // descaracterização (CPF com asteriscos) nunca fique coberta por uma tarja.
      const marcacoesAtivas = (App.marcacoesPorPagina.get(p) || [])
        .filter(m => m.estado === 'incluido')
        .sort((a, b) => (a.tipo === 'descaracterizar' ? 1 : 0) - (b.tipo === 'descaracterizar' ? 1 : 0));

      marcacoesAtivas.forEach(m => {
        // bbox está em coordenadas scale=1.0.
        // Multiplicamos por ESCALA_FINAL para obter coordenadas do canvas final.
        const x = Math.floor(m.bbox.x * ESCALA_FINAL);
        const y = Math.floor(m.bbox.y * ESCALA_FINAL);
        const w = Math.ceil(m.bbox.largura  * ESCALA_FINAL);
        const h = Math.ceil(m.bbox.altura   * ESCALA_FINAL);

        if (m.tipo === 'tarjar') {
          ctx.fillStyle = '#000000';
          ctx.fillRect(x, y, w, h);
        } else if (m.tipo === 'descaracterizar') {
          aplicarDescaracterizacaoCPF(ctx, x, y, w, h);
        }
      });

      // Dimensões em pontos para o jsPDF (invertendo a escala)
      const largPt = cv.width  / ESCALA_FINAL;
      const altPt  = cv.height / ESCALA_FINAL;

      if (!primeira) {
        doc.addPage([largPt, altPt]);
      } else {
        doc.internal.pageSize.width  = largPt;
        doc.internal.pageSize.height = altPt;
        primeira = false;
      }
      doc.addImage(cv.toDataURL('image/jpeg', 0.92), 'JPEG', 0, 0, largPt, altPt);
    }

    atualizarProgresso(100, 'Gerando download...');
    const nomeBase = App.pdfNome.replace(/\.pdf$/i, '');
    // A versão entra no nome do arquivo: serve de diagnóstico para confirmar
    // qual build gerou a saída (ex.: "..._tarjado_v8.pdf").
    const nomeOut  = `${nomeBase}_tarjado_${VERSAO_APP}.pdf`;
    doc.save(nomeOut);
    document.getElementById('nome-arquivo-gerado').textContent = nomeOut;
    document.getElementById('barra-progresso-container').style.display = 'none';
    avancarEtapa(5);
  } catch (err) {
    console.error(err);
    mostrarAlerta('erro', 'Erro ao gerar PDF: ' + err.message);
    document.getElementById('barra-progresso-container').style.display = 'none';
  }
}

// Descaracterização de CPF: oculta os 3 primeiros e os 2 últimos dígitos,
// deixando os dígitos centrais visíveis (***.456.789-**).
//
// Usa frações FIXAS da largura da caixa (30% à esquerda, 28% à direita) em vez de
// calcular a posição exata de cada dígito. Isso é robusto: a caixa do OCR pode
// incluir pontuação extra (ex.: a vírgula em "134.068.028-93,"), o que deslocaria
// um cálculo proporcional e deixaria um dígito exposto. Cobrir frações fixas e
// generosas garante que NENHUM dígito sensível vaze — sempre prioriza o sigilo.
function aplicarDescaracterizacaoCPF(ctx, x, y, w, h) {
  const leftW  = Math.ceil(w * 0.30);   // cobre os 3 primeiros dígitos + ponto
  const rightX = Math.floor(w * 0.72);  // início da faixa direita
  const rightW = w - rightX + 1;        // cobre 2 últimos dígitos + eventual vírgula

  ctx.fillStyle = '#000000';
  ctx.fillRect(x, y, leftW, h);
  ctx.fillRect(x + rightX, y, rightW, h);

  const fs = Math.max(7, Math.min(Math.round(h * 0.7), 13));
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${fs}px monospace`;
  ctx.textBaseline = 'middle';
  ctx.fillText('***', x + 2, y + h / 2);
  ctx.fillText('**',  x + rightX + 2, y + h / 2);
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
    if (App.paginaAtual > 1) { App.paginaAtual--; await renderizarPaginaRevisao(App.paginaAtual); atualizarPainelMarcacoes(); }
  });
  document.getElementById('btn-proxima-pagina').addEventListener('click', async () => {
    if (App.paginaAtual < App.totalPaginas) { App.paginaAtual++; await renderizarPaginaRevisao(App.paginaAtual); atualizarPainelMarcacoes(); }
  });

  document.getElementById('btn-selecao-manual').addEventListener('click', () => {
    App.modoSelecao = !App.modoSelecao;
    const canvas = document.getElementById('canvas-pdf');
    const btn = document.getElementById('btn-selecao-manual');
    const info = document.getElementById('info-selecao') || criarInfoSelecao();
    if (App.modoSelecao) {
      canvas.classList.add('modo-selecao');
      btn.textContent = '✕ Cancelar seleção';
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

function criarInfoSelecao() {
  const el = document.createElement('div');
  el.id = 'info-selecao';
  el.textContent = 'Clique e arraste para selecionar a área a tarjar';
  document.body.appendChild(el);
  return el;
}

function avancarEtapa(num) {
  const ant = document.querySelector(`.step[data-step="${App.etapaAtual}"]`);
  if (ant) { ant.classList.remove('ativa'); ant.classList.add('concluida'); }
  App.etapaAtual = num;
  document.querySelectorAll('.step').forEach(s => s.classList.remove('ativa'));
  const nova = document.querySelector(`.step[data-step="${num}"]`);
  if (nova) nova.classList.add('ativa');
  document.querySelectorAll('.etapa-secao').forEach(s => s.classList.add('hidden'));
  const sec = document.getElementById(`etapa-${num}`);
  if (sec) sec.classList.remove('hidden');
  window.scrollTo(0, 0);
}

function renderizarListaRegras() {
  const lista = document.getElementById('lista-regras-auto');
  if (!lista) return;
  lista.innerHTML = REGRAS.map(r => `
    <div class="item-regra">
      <input type="checkbox" id="regra-${r.id}" ${r.ativa?'checked':''}
        onchange="toggleRegra('${r.id}',this.checked)">
      <label for="regra-${r.id}" class="nome-regra">${r.nome}</label>
      <span class="tag-tratamento ${r.tratamento==='tarjar'?'tag-tarjar':'tag-descaracterizar'}">
        ${r.tratamento==='descaracterizar'?'Descarac.':'Tarjar'}
      </span>
    </div>`).join('');
}

function toggleRegra(id, ativo) {
  if (ativo) App.regrasAtivas.add(id); else App.regrasAtivas.delete(id);
}

// ─── Utilitários ─────────────────────────────────────────────────────────────
function normalizarTexto(t) {
  return String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
}
function nomeExibicaoPapel(p) {
  return { investigado:'Investigado', vitima:'Vítima', testemunha:'Testemunha',
           denunciante:'Denunciante', terceiro:'Terceiro', livre:'Termo livre' }[p] || p;
}
function gerarId() { return Math.random().toString(36).slice(2) + Date.now().toString(36); }
function formatarTamanho(b) {
  return b < 1024 ? b+' B' : b < 1048576 ? (b/1024).toFixed(1)+' KB' : (b/1048576).toFixed(1)+' MB';
}
function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function atualizarProgresso(pct, label) {
  const f = document.getElementById('barra-progresso-fill'), l = document.getElementById('progresso-label');
  if (f) f.style.width = pct + '%';
  if (l) l.textContent = label;
}
function mostrarAlerta(tipo, msg) {
  const el = document.getElementById('alerta-global');
  if (!el) return;
  const ic = { erro:'❌', aviso:'⚠️', info:'ℹ️', sucesso:'✅' };
  el.className = `alerta alerta-${tipo}`;
  el.innerHTML = `<span class="alerta-icone">${ic[tipo]||'ℹ️'}</span><div>${msg}</div>`;
  el.classList.remove('hidden');
  if (tipo !== 'erro') setTimeout(() => el.classList.add('hidden'), 12000);
}
