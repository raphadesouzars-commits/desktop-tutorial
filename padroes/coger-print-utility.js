/**
 * COGER Print Utility
 * Funções de apoio para preparação de documentos para impressão.
 * Inclui: geração de referência, preenchimento de metadados, validação de page-break.
 */

/**
 * Gera uma referência única no formato INT-YYYYMMDD-XXXX
 * @returns {string} Referência única
 */
function generatePrintReference() {
  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const sequence = String(Math.floor(Math.random() * 10000)).padStart(4, '0');
  return `INT-${timestamp}-${sequence}`;
}

/**
 * Formata data para português (pt-BR)
 * @param {Date} date - Data a formatar
 * @returns {string} Data formatada (ex: "13 de julho de 2026")
 */
function formatDatePT(date) {
  return date.toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Formata hora para português (pt-BR)
 * @param {Date} date - Data/hora a formatar
 * @returns {string} Hora formatada (ex: "18:35")
 */
function formatTimePT(date) {
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Prepara o documento para impressão:
 * 1. Gera referência única
 * 2. Preenche campos de metadata no header/footer
 * 3. Limpa margens do body
 * 4. Dispara evento 'beforeprint'
 * @param {Object} options - Opções de configuração (opcional)
 *   - reference: string (se omitido, gera automaticamente)
 *   - documentTitle: string (título do documento para o header)
 */
function prepareForPrint(options = {}) {
  options = options || {};

  // 1. Gerar ou usar referência fornecida
  const reference = options.reference || generatePrintReference();

  // 2. Preencher campos de metadata
  const now = new Date();
  const dateStr = formatDatePT(now);
  const timeStr = formatTimePT(now);

  // Header
  const headerRef = document.getElementById('coger-print-ref');
  if (headerRef) headerRef.textContent = reference;

  const headerDate = document.getElementById('coger-print-date');
  if (headerDate) headerDate.textContent = dateStr;

  const headerTime = document.getElementById('coger-print-time');
  if (headerTime) headerTime.textContent = timeStr;

  // Footer
  const footerRef = document.getElementById('coger-print-footer-ref');
  if (footerRef) footerRef.textContent = reference;

  // 3. Garantir que margens do body estejam zeradas (será aplicado via CSS @media print)
  document.documentElement.style.margin = '0';
  document.body.style.margin = '0';

  // 4. Disparo de evento beforeprint (para navegadores que suportam)
  window.dispatchEvent(new Event('beforeprint'));

  return reference;
}

/**
 * Calcula o número total de páginas de impressão (aproximado).
 * Nota: Este é um cálculo heurístico; a precisão depende do navegador e do conteúdo.
 * @returns {number} Estimativa de páginas
 */
function estimatePrintPages() {
  const printPage = document.getElementById('printPage');
  if (!printPage) return 1;

  const height = printPage.scrollHeight;
  const pageHeightPx = 11 * 96; // A4 portrait: ~1050px em 96dpi

  return Math.ceil(height / pageHeightPx);
}

/**
 * Atualiza o contador de páginas no footer
 * (Requer que o footer tenha spans com classes .page-count)
 * @param {number} pageCount - Número total de páginas
 */
function updatePageCount(pageCount) {
  const pageCountEls = document.querySelectorAll('.page-count');
  pageCountEls.forEach(el => {
    el.textContent = pageCount;
  });
}

/**
 * Listener chamado quando o usuário clica no botão de imprimir
 * Exemplo de uso:
 * document.getElementById('printButton').addEventListener('click', onPrintButtonClick);
 */
function onPrintButtonClick(event) {
  event.preventDefault();

  // Preparar documento
  const reference = prepareForPrint({
    documentTitle: document.title
  });

  // Estimar e atualizar página count
  const estimatedPages = estimatePrintPages();
  updatePageCount(estimatedPages);

  // Abrir diálogo de impressão
  window.print();
}

/**
 * Valida se todos os elementos críticos de print estão presentes
 * @returns {Object} Resultado da validação
 *   - isValid: boolean
 *   - errors: string[]
 */
function validatePrintStructure() {
  const errors = [];

  if (!document.querySelector('.coger-print-header')) {
    errors.push('Missing .coger-print-header');
  }
  if (!document.querySelector('.coger-print-footer')) {
    errors.push('Missing .coger-print-footer');
  }
  if (!document.getElementById('coger-print-ref')) {
    errors.push('Missing #coger-print-ref in header');
  }
  if (!document.getElementById('coger-print-footer-ref')) {
    errors.push('Missing #coger-print-footer-ref in footer');
  }
  if (!document.getElementById('printPage')) {
    console.warn('Tip: No #printPage found; using [role="main"] as fallback');
  }

  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

/**
 * Inicialização padrão: executar quando o documento estiver pronto
 * Se o seu HTML já tiver um <button data-act="print">, use isto:
 *
 * document.addEventListener('DOMContentLoaded', initPrintSupport);
 *
 * Ou chame manualmente após setup completo.
 */
function initPrintSupport() {
  // Validar estrutura
  const validation = validatePrintStructure();
  if (!validation.isValid) {
    console.warn('Print structure validation errors:', validation.errors);
  }

  // Registrar listener de print button (se existir)
  const printButton = document.querySelector('[data-act="print"]');
  if (printButton) {
    printButton.addEventListener('click', onPrintButtonClick);
  }

  // Registrar listener de beforeprint
  window.addEventListener('beforeprint', function() {
    // Qualquer setup adicional pode ir aqui
  });

  // Registrar listener de afterprint
  window.addEventListener('afterprint', function() {
    // Qualquer cleanup pode ir aqui
  });

  console.log('COGER Print Support initialized');
}

// Exportar para uso modular (em contextos que suportam ES6 modules)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generatePrintReference,
    formatDatePT,
    formatTimePT,
    prepareForPrint,
    estimatePrintPages,
    updatePageCount,
    onPrintButtonClick,
    validatePrintStructure,
    initPrintSupport
  };
}
