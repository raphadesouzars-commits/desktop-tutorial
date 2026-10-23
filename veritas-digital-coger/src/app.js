(function () {
"use strict";

/* ============================================================
   Utilitários
   ============================================================ */
function uid() { return crypto.randomUUID(); }
function nowIso() { return new Date().toISOString(); }
function fmtDT(iso) {
  if (!iso) return "—";
  var d = new Date(iso);
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
function fmtBytes(n) {
  if (n === 0) return "0 B";
  if (!n) return "—";
  var u = ["B", "KB", "MB", "GB"], i = 0;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return n.toFixed(i === 0 ? 0 : 1) + " " + u[i];
}
function escapeHtml(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}
function get(obj, path) {
  return path.split(".").reduce(function (o, k) { return (o === null || o === undefined) ? undefined : o[k]; }, obj);
}
function set(obj, path, value) {
  var parts = path.split(".");
  var last = parts.pop();
  var target = parts.reduce(function (o, k) { if (!(k in o)) o[k] = {}; return o[k]; }, obj);
  target[last] = value;
}
function stableStringify(obj) {
  function sort(o) {
    if (Array.isArray(o)) return o.map(sort);
    if (o && typeof o === "object") {
      var out = {};
      Object.keys(o).sort().forEach(function (k) { out[k] = sort(o[k]); });
      return out;
    }
    return o;
  }
  return JSON.stringify(sort(obj));
}
function bufToHex(buf) {
  return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
}
async function sha256Hex(arrayBufferOrString) {
  var buf = typeof arrayBufferOrString === "string"
    ? new TextEncoder().encode(arrayBufferOrString)
    : arrayBufferOrString;
  var digest = await crypto.subtle.digest("SHA-256", buf);
  return bufToHex(digest);
}
async function hashFile(file) {
  var buf = await file.arrayBuffer();
  return sha256Hex(buf);
}
async function hashDossieMetadata(dossie) {
  var copy = JSON.parse(JSON.stringify(dossie));
  copy.hashDoDossie = "";
  return sha256Hex(stableStringify(copy));
}

/* ============================================================
   Catálogo de conteúdo — dicas, textos fixos, listas
   ============================================================ */
var CATALOGO = {
  epigrafe: { texto: "Toda prova, antes de provar, deve ser provada.", autor: "Iacoviello" },
  disclaimerCurto: "Ferramenta de apoio à decisão. Não realiza perícia técnica, não valida assinatura digital ICP-Brasil e não substitui laudo pericial formal.",
  disclaimerLongo: "Veritas Digital - Coger é uma ferramenta de apoio à decisão para as unidades da Corregedoria da RFB — investigação, parecer técnico e comissões de PAD/sindicância. Documenta a consistência interna e a continuidade de elementos de prova digitais e documentais, mas não realiza perícia técnica formal, não valida assinatura digital ICP-Brasil e não substitui laudo pericial quando a autenticidade de um elemento for seriamente contestada. O carimbo de data/hora registrado é o relógio do sistema local do usuário — não é um selo de tempo com autoridade certificadora. A avaliação do caso concreto é sempre da unidade responsável.",
  fundamentacao: "A cadeia de custódia tem disciplina legal expressa apenas no processo penal (art. 158-A a 158-F do CPP, Lei 13.964/2019). No PAD, sua aplicação decorre por analogia e principiologia — verdade real, devido processo, ampla defesa — reforçada pela intercambialidade doutrinária de provas entre PAD e processo penal (compartilhamento de interceptações e dados de operações conjuntas). Esta ferramenta não sugere vinculação normativa direta ao CPP.",
  dicas: {
    dica_integralidade: "Cuidado: decisões não devem se fundamentar em prints de tela, áudios isolados ou trechos sem contexto. Se este é um extrato parcial, registre por que o conteúdo integral não foi anexado e avalie a necessidade de complementação.",
    dica_custodia_externa: "A partir daqui você documenta a <strong>cadeia externa</strong>: o que aconteceu antes do recebimento pela Coger não está sob seu controle direto. Registre com precisão a origem e o hash declarado — é essa comparação que sustenta a continuidade da prova.",
    dica_carimbo_local: "O carimbo de data/hora é o relógio deste computador, não um selo de tempo com autoridade certificadora. Tem valor para mostrar consistência interna do arquivo, não para provar o instante exato de forma inatacável.",
    dica_fishing: "Mantenha o objeto da apuração determinado: fato, pessoa e meios de prova. Evite incorporar elementos coletados sem relação direta com a hipótese investigativa em curso.",
    dica_privacidade_consentimento: "Ao registrar mensagens ou gravações, observe as normas de privacidade aplicáveis e, quando pertinente, documente se houve consentimento na colaboração de quem forneceu o material.",
    dica_prejuizo: "Uma divergência ou lacuna formal na cadeia de custódia não gera nulidade automática. Registre o ocorrido com precisão e avalie se há prejuízo concreto e demonstrável para a acusação ou para a defesa — esse é o critério que prevalece, não a falha formal isolada em si.",
    dica_pericia: "Se a autenticidade deste elemento for seriamente contestada, esta ferramenta não substitui perícia formal. Ela documenta a cadeia até este ponto; a partir daqui, avalie a necessidade de exame pericial.",
    dica_lacre_fisico: "Documentos físicos e dispositivos (HD, celular, mídia removível) não têm hash — a integridade deles se sustenta pelo lacre. Registre o nº do lacre, sua condição no recebimento/coleta e o local de guarda física; use \"Registrar evento &rarr; Conferência do lacre\" sempre que o objeto for reaberto ou transferido."
  }
};

var CATEGORIAS = {
  print_sistema: "Print de sistema", documento_financeiro: "Documento financeiro",
  comunicacao: "Comunicação (e-mail/mensagem)", foto_video: "Foto/vídeo",
  laudo_pericia: "Laudo/perícia", oficio: "Ofício", decisao_judicial: "Decisão judicial",
  documento_fisico: "Documento físico", dispositivo_fisico: "Dispositivo/mídia física (HD, celular, pendrive etc.)",
  outro: "Outro"
};
var ELEMENTO_FISICO_TIPOS = {
  documento_fisico: "Documento físico (papel)", hd_armazenamento: "HD/dispositivo de armazenamento",
  celular_smartphone: "Celular/smartphone", midia_removivel: "Mídia removível (pendrive, CD/DVD)", outro: "Outro"
};
var CONDICAO_LACRE = { intacto: "Íntegro", rompido: "Rompido", nao_lacrado: "Não lacrado" };
var SIGILO = { publico: "Público nos autos", acesso_restrito: "Acesso restrito", sigiloso: "Sigiloso" };
var PROVENIENCIA_TIPOS = {
  gerado_internamente: "A) Gerado internamente",
  recebido_hash_oficial: "B) Recebido com hash oficial",
  extraido_sistema_trilha: "C) Extraído de sistema com trilha própria"
};
var NATUREZA_COMPARTILHAMENTO = {
  mandado: "Mandado", oficio: "Ofício", decisao_compartilhamento: "Decisão de compartilhamento de prova",
  operacao_conjunta: "Operação conjunta"
};
var STATUS_ITEM = { ativo: "Ativo", substituido: "Substituído", contestado: "Contestado", descartado: "Descartado" };
var RESULTADO = { confere: "Confere", diverge: "Diverge", nao_aplicavel: "Não aplicável" };
var EVENTO_TIPOS = {
  item_identificado: { label: "Item (pacote) identificado como elemento de prova", escopo: "item" },
  hash_declarado_recebido: { label: "Hash declarado recebido", escopo: "arquivo" },
  hash_local_calculado: { label: "Hash local calculado", escopo: "arquivo" },
  descricao_registrada: { label: "Descrição/contexto registrado", escopo: "misto" },
  arquivo_adicionado: { label: "Arquivo adicionado ao item", escopo: "arquivo" },
  transferencia_custodia: { label: "Transferência de custódia", escopo: "item" },
  enviado_pericia: { label: "Enviado para perícia formal", escopo: "arquivo" },
  conferencia_rodada: { label: "Conferência de integridade rodada", escopo: "item" },
  conferencia_arquivo: { label: "Conferência de integridade (arquivo)", escopo: "arquivo" },
  conferencia_lacre: { label: "Conferência do lacre", escopo: "item" },
  status_alterado: { label: "Status alterado", escopo: "item" },
  item_descartado: { label: "Item descartado", escopo: "item" }
};

/* ============================================================
   Estado
   ============================================================ */
var STORAGE_KEY = "veritas-digital-coger:dossie";
var DB = { dossie: null };
var UI = { view: "inicio", wizardStep: 1, draftItem: null, editingField: null, conferencia: null, modal: null };

function novoItemDraft() {
  return {
    id: uid(), titulo: "", categoria: "", folhaAutos: "", vinculoMatriz: "",
    sigilo: "acesso_restrito", conteudoIntegral: true, justificativaExtrato: "",
    proveniencia: {
      tipo: "", modoHashDeclarado: "por_arquivo", hashDeclaradoPacote: "", algoritmoDeclarado: "SHA-256",
      processoJudicialOrigem: "", orgaoExpedidor: "", naturezaCompartilhamento: "", nomeOperacao: "",
      dataOficio: "", dataRecebimento: "", numeroOficio: "",
      quemColetou: "", contextoColeta: "", localSituacao: "",
      sistemaOrigem: "", idDocumentoOrigem: "", processoOrigem: "", usuarioExtraiu: "", dataHoraExtracao: "",
      elementoFisico: elementoFisicoVazio()
    },
    arquivos: [],
    responsavelRegistro: "", custodianteAtual: "", status: "ativo", resultadoAgregado: "nao_aplicavel",
    itemSubstitutoId: null, fundamentacaoContestacao: "", observacoes: "", linhaDoTempoItem: []
  };
}

function membroVazio() { return { nome: "", cargo: "", matricula: "" }; }
function elementoFisicoVazio() {
  return { presente: false, tipo: "", numeroLacre: "", descricaoLacre: "", condicaoLacre: "intacto", localGuarda: "", responsavelGuarda: "" };
}
function novoDossie() {
  return {
    versaoFerramenta: "1.0", versaoEsquema: "2.0", hashDoDossie: "",
    processo: {
      id: uid(), numero: "", portaria: "", secaoResponsavel: "",
      comissao: { presidente: membroVazio(), secretario: membroVazio(), vogais: [] },
      criadoEm: nowIso(), atualizadoEm: nowIso()
    },
    itens: []
  };
}
function migrarMembro(m) {
  if (!m) return membroVazio();
  if (typeof m === "string") return { nome: m, cargo: "", matricula: "" };
  return { nome: m.nome || "", cargo: m.cargo || "", matricula: m.matricula || "" };
}
function migrarDossie(d) {
  if (!d) return d;
  if (d.processo) {
    if (d.processo.secaoResponsavel === undefined) d.processo.secaoResponsavel = "";
    if (d.processo.comissao) {
      var c = d.processo.comissao;
      c.presidente = migrarMembro(c.presidente);
      c.secretario = migrarMembro(c.secretario);
      c.vogais = (c.vogais || []).map(migrarMembro);
    }
  }
  (d.itens || []).forEach(function (it) {
    if (it.proveniencia && !it.proveniencia.elementoFisico) it.proveniencia.elementoFisico = elementoFisicoVazio();
  });
  return d;
}

/* ============================================================
   Persistência
   ============================================================ */
async function persistir() {
  if (!DB.dossie) return;
  DB.dossie.processo.atualizadoEm = nowIso();
  DB.dossie.hashDoDossie = await hashDossieMetadata(DB.dossie);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(DB.dossie));
}
function carregarLocal() {
  var raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (e) { return null; }
}

/* ============================================================
   Toast
   ============================================================ */
function toast(msg, type) {
  var wrap = document.querySelector(".vdc-toast-wrap");
  if (!wrap) { wrap = document.createElement("div"); wrap.className = "vdc-toast-wrap"; document.body.appendChild(wrap); }
  var el = document.createElement("div");
  el.className = "vdc-toast" + (type ? " vdc-toast--" + type : "");
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(function () { el.remove(); }, 4200);
}

/* ============================================================
   Dica contextual
   ============================================================ */
function dica(id) {
  var txt = CATALOGO.dicas[id];
  if (!txt) return "";
  return '<div class="vdc-tip"><span class="vdc-tip__icon">&#128161;</span><div>' + txt + "</div></div>";
}

/* ============================================================
   Cálculo de agregados
   ============================================================ */
function piorResultado(resultados) {
  if (resultados.indexOf("diverge") !== -1) return "diverge";
  if (resultados.length === 0) return "nao_aplicavel";
  if (resultados.every(function (r) { return r === "confere"; })) return "confere";
  return "nao_aplicavel";
}
function recalcularAgregadoItem(item) {
  var resultados = item.arquivos.map(function (a) { return a.resultadoComparacao; });
  var ef = item.proveniencia.elementoFisico;
  if (ef && ef.presente && ef.condicaoLacre === "rompido") resultados.push("diverge");
  item.resultadoAgregado = piorResultado(resultados);
}
function statusIconClasse(item) {
  if (item.status === "descartado") return "vdc-status-icon--none";
  if (item.resultadoAgregado === "diverge") return "vdc-status-icon--warn";
  if (item.resultadoAgregado === "confere") return "vdc-status-icon--ok";
  return "vdc-status-icon--none";
}
function statusIconGlifo(item) {
  if (item.resultadoAgregado === "diverge") return "⚠";
  if (item.resultadoAgregado === "confere") return "✓";
  return "—";
}

/* ============================================================
   Eventos de linha do tempo (append-only)
   ============================================================ */
function novoEvento(tipo, dataOverrides) {
  var base = { evento: tipo, dataHora: nowIso(), responsavel: "", resultado: "", observacao: "" };
  return Object.assign(base, dataOverrides || {});
}
function registrarEventoItem(item, tipo, overrides) {
  item.linhaDoTempoItem.push(novoEvento(tipo, overrides));
}
function registrarEventoArquivo(arquivo, tipo, overrides) {
  arquivo.linhaDoTempoArquivo.push(novoEvento(tipo, overrides));
}

/* ============================================================
   Renderização — roteador principal
   ============================================================ */
var appEl;
function render() {
  appEl = appEl || document.getElementById("app");
  var html = "";
  if (!DB.dossie) {
    html = viewInicio();
  } else if (UI.view === "itemWizard") {
    html = viewItemWizard();
  } else if (UI.view === "itemDetalhe") {
    html = viewItemDetalhe(UI.editingField);
  } else if (UI.view === "conferencia") {
    html = viewConferencia();
  } else if (UI.view === "relatorio") {
    html = viewRelatorio();
  } else {
    html = viewProcesso();
  }
  appEl.innerHTML = html + (UI.modal ? renderModal() : "");
  updateTopbar();
}
function updateTopbar() {
  var el = document.getElementById("topbar-status-text");
  if (!el) return;
  if (!DB.dossie) { el.textContent = "nenhum dossiê carregado"; return; }
  el.textContent = (DB.dossie.processo.numero || "processo sem número") + " · " + DB.dossie.itens.length + " item(ns)";
}

/* ============================================================
   Tela inicial
   ============================================================ */
function viewInicio() {
  return '' +
  '<div class="vdc-page">' +
    '<div class="vdc-epigraph">&ldquo;' + escapeHtml(CATALOGO.epigrafe.texto) + '&rdquo;<small>' + escapeHtml(CATALOGO.epigrafe.autor) + '</small></div>' +
    '<div class="rfb-card"><div class="rfb-card__body" style="text-align:center;display:flex;flex-direction:column;gap:16px;align-items:center;">' +
      '<div class="rfb-eyebrow">Coger/RFB — Divisão de Processos (Dproc)</div>' +
      '<h1 class="rfb-h1" style="font-size:28px;">Veritas Digital - Coger</h1>' +
      '<p class="rfb-body rfb-body--muted" style="max-width:560px;">Cadeia de custódia dos elementos de prova digitais e documentais juntados ao processo — da coleta/recebimento ao relatório final. Uso transversal às unidades da Corregedoria: investigação, parecer técnico e comissões de PAD/sindicância.</p>' +
      '<div class="vdc-actions">' +
        '<button class="rfb-btn rfb-btn--primary" onclick="App.criarDossie()">+ Novo dossiê</button>' +
        '<label class="rfb-btn rfb-btn--secondary" style="cursor:pointer;">Importar dossiê (.json)<input type="file" accept=".json,application/json" style="display:none" onchange="App.importarArquivo(event)"></label>' +
      '</div>' +
      '<div class="rfb-alert rfb-alert--info" style="text-align:left;max-width:640px;"><div><div class="rfb-alert__title">Fundamentação doutrinária</div><div class="rfb-alert__msg">' + escapeHtml(CATALOGO.fundamentacao) + '</div></div></div>' +
      '<div class="rfb-body--small rfb-body--muted" style="max-width:640px;">' + escapeHtml(CATALOGO.disclaimerLongo) + '</div>' +
    '</div></div>' +
  '</div>';
}

/* ============================================================
   Tela do Processo
   ============================================================ */
function viewProcesso() {
  var p = DB.dossie.processo;
  var itensHtml = DB.dossie.itens.length === 0
    ? '<div class="vdc-empty-state"><div class="rfb-h3">Nenhum item cadastrado</div><div class="rfb-body--muted">Adicione o primeiro elemento de prova do processo.</div></div>'
    : '<div class="rfb-table-wrap"><table class="rfb-table"><thead><tr><th></th><th>Título</th><th>Categoria</th><th>Proveniência</th><th>Arquivos</th><th>Custodiante</th><th>Status</th><th>Fls.</th><th></th></tr></thead><tbody>' +
      DB.dossie.itens.map(function (it) {
        return '<tr class="vdc-item-row" onclick="App.abrirItem(\'' + it.id + '\')" title="Abrir e editar item">' +
          '<td><span class="vdc-status-icon ' + statusIconClasse(it) + '" title="' + RESULTADO[it.resultadoAgregado] + '">' + statusIconGlifo(it) + '</span></td>' +
          '<td>' + escapeHtml(it.titulo || "(sem título)") + (it.sigilo !== "publico" ? ' <span class="rfb-badge rfb-badge--neutral">' + SIGILO[it.sigilo] + '</span>' : '') + '</td>' +
          '<td>' + (CATEGORIAS[it.categoria] || "—") + '</td>' +
          '<td>' + (PROVENIENCIA_TIPOS[it.proveniencia.tipo] || "—").replace(/^[A-C]\) /, '') + '</td>' +
          '<td>' + it.arquivos.length + '</td>' +
          '<td>' + escapeHtml(it.custodianteAtual || "—") + '</td>' +
          '<td><span class="rfb-badge rfb-badge--' + statusBadgeCor(it.status) + '">' + STATUS_ITEM[it.status] + '</span></td>' +
          '<td>' + escapeHtml(it.folhaAutos || "—") + '</td>' +
          '<td class="vdc-edit-affordance" title="Abrir e editar item">&#9998;</td>' +
        '</tr>';
      }).join("") + '</tbody></table></div>';

  return '' +
  '<div class="vdc-page">' +
    '<div class="vdc-epigraph">&ldquo;' + escapeHtml(CATALOGO.epigrafe.texto) + '&rdquo;<small>' + escapeHtml(CATALOGO.epigrafe.autor) + '</small></div>' +
    '<div class="rfb-card"><div class="rfb-card__header"><span class="rfb-card__title">Dados do processo</span>' +
      '<div class="vdc-actions no-print">' +
        '<label class="rfb-btn rfb-btn--secondary rfb-btn--sm" style="cursor:pointer;">Importar<input type="file" accept=".json,application/json" style="display:none" onchange="App.importarArquivo(event)"></label>' +
        '<button class="rfb-btn rfb-btn--secondary rfb-btn--sm" onclick="App.exportarDossie()">Exportar .json</button>' +
        '<button class="rfb-btn rfb-btn--ghost rfb-btn--sm" onclick="App.abrirModal(\'reiniciar\', {})">Reiniciar</button>' +
      '</div>' +
    '</div><div class="rfb-card__body">' +
      '<div class="vdc-grid-3">' +
        '<div class="rfb-field"><label class="rfb-label">Nº do processo</label><input class="rfb-input" value="' + escapeHtml(p.numero) + '" onchange="App.setProcesso(\'numero\', this.value)"></div>' +
        '<div class="rfb-field"><label class="rfb-label">Portaria</label><input class="rfb-input" value="' + escapeHtml(p.portaria) + '" onchange="App.setProcesso(\'portaria\', this.value)"></div>' +
        '<div class="rfb-field"><label class="rfb-label">Seção/unidade responsável</label><input class="rfb-input" value="' + escapeHtml(p.secaoResponsavel || "") + '" onchange="App.setProcesso(\'secaoResponsavel\', this.value)" placeholder="Investigação, parecer técnico ou comissão"></div>' +
      '</div>' +
      '<div class="rfb-divider"></div>' +
      membroCampoHtml("Presidente da comissão", "presidente", p.comissao.presidente) +
      membroCampoHtml("Secretário(a)", "secretario", p.comissao.secretario) +
      '<div class="rfb-field"><label class="rfb-label">Vogais</label>' +
        '<div class="vdc-lista-vogais">' +
          (p.comissao.vogais.length ? '<div class="vdc-cabecalho-vogais"><span>Nome</span><span>Cargo</span><span>Matrícula</span><span></span></div>' : '') +
          p.comissao.vogais.map(function (v, i) {
            return '<div class="vdc-linha-vogal">' +
              '<input class="rfb-input" placeholder="Nome" value="' + escapeHtml(v.nome) + '" onchange="App.setVogalCampo(' + i + ', \'nome\', this.value)">' +
              '<input class="rfb-input" placeholder="Cargo" value="' + escapeHtml(v.cargo) + '" onchange="App.setVogalCampo(' + i + ', \'cargo\', this.value)">' +
              '<input class="rfb-input" placeholder="Matrícula" value="' + escapeHtml(v.matricula) + '" onchange="App.setVogalCampo(' + i + ', \'matricula\', this.value)">' +
              '<button type="button" class="vdc-close-btn" title="Remover vogal" onclick="App.removerVogal(' + i + ')">&times;</button>' +
            '</div>';
          }).join("") +
        '</div>' +
        '<button type="button" class="rfb-btn rfb-btn--secondary rfb-btn--sm" style="margin-top:8px;" onclick="App.adicionarVogal()">+ Adicionar vogal</button>' +
      '</div>' +
      '<div class="rfb-help" style="margin-top:10px;">hashDoDossie: <code style="font-family:var(--rfb-font-mono);">' + (DB.dossie.hashDoDossie || "—") + '</code> · atualizado em ' + fmtDT(p.atualizadoEm) + '</div>' +
    '</div></div>' +

    '<div class="vdc-section-head no-print">' +
      '<span class="rfb-h3">Itens (elementos de prova)</span>' +
      '<div class="vdc-actions">' +
        '<button class="rfb-btn rfb-btn--secondary" onclick="App.irParaConferencia()">Conferência Geral</button>' +
        '<button class="rfb-btn rfb-btn--secondary" onclick="App.irParaRelatorio()">Relatório</button>' +
        '<button class="rfb-btn rfb-btn--primary" onclick="App.criarItem()">+ Adicionar item</button>' +
      '</div>' +
    '</div>' +
    itensHtml +
  '</div>';
}
function statusBadgeCor(status) {
  return { ativo: "success", substituido: "info", contestado: "warning", descartado: "neutral" }[status] || "neutral";
}
function membroCampoHtml(label, papel, membro) {
  return '<div class="rfb-field" style="margin-top:12px;"><label class="rfb-label">' + label + '</label>' +
    '<div class="vdc-grid-3">' +
      '<div><label class="rfb-label vdc-rotulo-campo">Nome</label><input class="rfb-input" value="' + escapeHtml(membro.nome) + '" onchange="App.setMembro(\'' + papel + '\', \'nome\', this.value)"></div>' +
      '<div><label class="rfb-label vdc-rotulo-campo">Cargo</label><input class="rfb-input" value="' + escapeHtml(membro.cargo) + '" onchange="App.setMembro(\'' + papel + '\', \'cargo\', this.value)"></div>' +
      '<div><label class="rfb-label vdc-rotulo-campo">Matrícula</label><input class="rfb-input" value="' + escapeHtml(membro.matricula) + '" onchange="App.setMembro(\'' + papel + '\', \'matricula\', this.value)"></div>' +
    '</div></div>';
}

/* ============================================================
   Wizard de cadastro de item
   ============================================================ */
var WIZARD_STEPS = ["Identificação", "Proveniência", "Arquivos", "Linha do tempo"];
function stepBarHtml(current, doneUntil) {
  return '<div class="step-bar no-print">' + WIZARD_STEPS.map(function (label, i) {
    var n = i + 1;
    var cls = n === current ? "active" : (n < current ? "done" : "");
    return '<div class="step-item ' + cls + '" onclick="App.irParaStep(' + n + ')"><span class="step-num">' + (n < current ? "✓" : n) + '</span>' + label + '</div>';
  }).join("") + '</div>';
}

function viewItemWizard() {
  var d = UI.draftItem;
  var body = "";
  if (UI.wizardStep === 1) body = stepIdentificacao(d);
  else if (UI.wizardStep === 2) body = stepProveniencia(d);
  else if (UI.wizardStep === 3) body = stepArquivos(d);
  else body = stepLinhaDoTempoResumo(d);

  return '' +
  '<div class="vdc-page">' +
    '<div class="vdc-section-head"><span class="rfb-h2">Cadastro de item</span><button class="rfb-btn rfb-btn--ghost rfb-btn--sm no-print" onclick="App.cancelarWizard()">Cancelar</button></div>' +
    '<div class="rfb-card">' + stepBarHtml(UI.wizardStep) +
      '<div class="rfb-card__body vdc-wizard-body">' + body + '</div>' +
      '<div class="rfb-card__footer no-print">' +
        (UI.wizardStep > 1 ? '<button class="rfb-btn rfb-btn--secondary" onclick="App.irParaStep(' + (UI.wizardStep - 1) + ')">&larr; Voltar</button>' : '<span></span>') +
        (UI.wizardStep < 4
          ? '<button class="rfb-btn rfb-btn--primary" onclick="App.avancarStep()">Avançar &rarr;</button>'
          : '<button class="rfb-btn rfb-btn--accent" onclick="App.salvarItem()">Salvar item</button>') +
      '</div>' +
    '</div>' +
  '</div>';
}

function stepIdentificacao(d) {
  var integralRadios = ['sim', 'nao'].map(function (v) {
    var checked = (v === 'sim') === !!d.conteudoIntegral;
    return '<label class="radio-option' + (checked ? ' selected' : '') + '"><input type="radio" name="integral" ' + (checked ? 'checked' : '') + ' onchange="App.setDraft(\'conteudoIntegral\', ' + (v === 'sim') + ')"> ' + (v === 'sim' ? 'Sim — conteúdo integral' : 'Não — extrato/trecho parcial') + '</label>';
  }).join("");
  return '' +
    dica('dica_fishing') +
    '<div class="vdc-grid-2" style="margin-top:14px;">' +
      '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Título/descrição</label><input class="rfb-input" value="' + escapeHtml(d.titulo) + '" oninput="App.setDraftQuiet(\'titulo\', this.value)" placeholder="Ex.: Extrato bancário — conta XXXX, período 01/2023 a 12/2023"></div>' +
      '<div class="rfb-field"><label class="rfb-label">Categoria</label><select class="rfb-select" onchange="App.setDraft(\'categoria\', this.value)">' +
        '<option value="">Selecione…</option>' + Object.keys(CATEGORIAS).map(function (k) { return '<option value="' + k + '"' + (d.categoria === k ? ' selected' : '') + '>' + CATEGORIAS[k] + '</option>'; }).join("") + '</select></div>' +
      '<div class="rfb-field"><label class="rfb-label">Nº/folha nos autos <span class="rfb-label__hint">opcional</span></label><input class="rfb-input" value="' + escapeHtml(d.folhaAutos) + '" oninput="App.setDraftQuiet(\'folhaAutos\', this.value)"></div>' +
      '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Vinculado à matriz de apuração</label><input class="rfb-input" value="' + escapeHtml(d.vinculoMatriz) + '" oninput="App.setDraftQuiet(\'vinculoMatriz\', this.value)" placeholder="Fato/hipótese que este elemento sustenta"></div>' +
      '<div class="rfb-field"><label class="rfb-label">Sigilo/classificação</label><select class="rfb-select" onchange="App.setDraft(\'sigilo\', this.value)">' +
        Object.keys(SIGILO).map(function (k) { return '<option value="' + k + '"' + (d.sigilo === k ? ' selected' : '') + '>' + SIGILO[k] + '</option>'; }).join("") + '</select></div>' +
    '</div>' +
    (d.categoria === 'comunicacao' ? '<div style="margin-top:14px;">' + dica('dica_privacidade_consentimento') + '</div>' : '') +
    '<div class="rfb-field" style="margin-top:16px;"><label class="rfb-label">Extrato ou conteúdo integral?</label>' + integralRadios + '</div>' +
    (!d.conteudoIntegral ? (
      '<div class="rfb-field" style="margin-top:8px;"><label class="rfb-label">Justificativa <span class="rfb-label__hint">obrigatória</span></label><textarea class="rfb-textarea" rows="2" oninput="App.setDraftQuiet(\'justificativaExtrato\', this.value)">' + escapeHtml(d.justificativaExtrato) + '</textarea></div>' +
      '<div style="margin-top:10px;">' + dica('dica_integralidade') + '</div>'
    ) : "");
}

function stepProveniencia(d) {
  var opts = [
    { v: "gerado_internamente", label: "A) Gerado internamente", sub: "Print, PDF exportado, foto de diligência — a ferramenta gera o hash no momento da coleta." },
    { v: "recebido_hash_oficial", label: "B) Recebido com hash oficial", sub: "PJe, ofício de compartilhamento, operação conjunta — a comissão declara o hash da origem." },
    { v: "extraido_sistema_trilha", label: "C) Extraído de sistema com trilha própria", sub: "Extração ativa pela própria Coger, com acesso institucional." }
  ];
  var radios = opts.map(function (o) {
    var checked = d.proveniencia.tipo === o.v;
    return '<label class="radio-option' + (checked ? ' selected' : '') + '"><input type="radio" name="proveniencia" ' + (checked ? 'checked' : '') + ' onchange="App.setDraft(\'proveniencia.tipo\', \'' + o.v + '\')"><div><div style="font-weight:600;">' + o.label + '</div><div class="rfb-body--small rfb-body--muted">' + o.sub + '</div></div></label>';
  }).join("");

  var extra = "";
  if (d.proveniencia.tipo === "gerado_internamente") {
    extra = '<div class="vdc-grid-2" style="margin-top:14px;">' +
      campoDraft("Quem coletou", "proveniencia.quemColetou", d.proveniencia.quemColetou) +
      campoDraft("Contexto da coleta", "proveniencia.contextoColeta", d.proveniencia.contextoColeta, "Diligência, atendimento, consulta a sistema…") +
      campoDraft("Local/situação", "proveniencia.localSituacao", d.proveniencia.localSituacao) +
    '</div>';
  } else if (d.proveniencia.tipo === "recebido_hash_oficial") {
    extra = '<div style="margin-top:14px;">' + dica('dica_custodia_externa') + '</div>' +
      '<div class="vdc-grid-2" style="margin-top:14px;">' +
        campoDraft("Processo judicial de origem", "proveniencia.processoJudicialOrigem", d.proveniencia.processoJudicialOrigem) +
        campoDraft("Órgão expedidor", "proveniencia.orgaoExpedidor", d.proveniencia.orgaoExpedidor) +
        selectCampo("Natureza do compartilhamento", "proveniencia.naturezaCompartilhamento", d.proveniencia.naturezaCompartilhamento, NATUREZA_COMPARTILHAMENTO) +
        campoDraft("Nome/codinome da operação", "proveniencia.nomeOperacao", d.proveniencia.nomeOperacao) +
        campoDraft("Data do ofício/decisão", "proveniencia.dataOficio", d.proveniencia.dataOficio, null, "date") +
        campoDraft("Data de recebimento pela Coger", "proveniencia.dataRecebimento", d.proveniencia.dataRecebimento, null, "date") +
        campoDraft("Nº do ofício/expediente", "proveniencia.numeroOficio", d.proveniencia.numeroOficio) +
      '</div>' +
      '<div class="rfb-field" style="margin-top:14px;"><label class="rfb-label">Modo do hash declarado pela origem</label>' +
        '<label class="radio-option' + (d.proveniencia.modoHashDeclarado === "por_arquivo" ? " selected" : "") + '"><input type="radio" name="modoHash" ' + (d.proveniencia.modoHashDeclarado === "por_arquivo" ? "checked" : "") + ' onchange="App.setDraft(\'proveniencia.modoHashDeclarado\', \'por_arquivo\')"> Hash declarado individualmente por arquivo</label>' +
        '<label class="radio-option' + (d.proveniencia.modoHashDeclarado === "pacote" ? " selected" : "") + '"><input type="radio" name="modoHash" ' + (d.proveniencia.modoHashDeclarado === "pacote" ? "checked" : "") + ' onchange="App.setDraft(\'proveniencia.modoHashDeclarado\', \'pacote\')"> Hash único do pacote compactado</label>' +
      '</div>' +
      (d.proveniencia.modoHashDeclarado === "pacote"
        ? '<div class="vdc-grid-2" style="margin-top:10px;">' + campoDraft("Hash declarado do pacote", "proveniencia.hashDeclaradoPacote", d.proveniencia.hashDeclaradoPacote) + campoDraft("Algoritmo declarado", "proveniencia.algoritmoDeclarado", d.proveniencia.algoritmoDeclarado) + '</div>' +
          '<div class="rfb-alert rfb-alert--warning" style="margin-top:10px;"><div><div class="rfb-alert__msg">Modo pacote: a comparação por arquivo individual não é aplicável — cada arquivo é conferido, na Conferência Geral, contra o hash local originalmente registrado (consistência interna), não contra o hash do pacote.</div></div></div>'
        : '');
  } else if (d.proveniencia.tipo === "extraido_sistema_trilha") {
    extra = '<div class="vdc-grid-2" style="margin-top:14px;">' +
      campoDraft("Sistema de origem", "proveniencia.sistemaOrigem", d.proveniencia.sistemaOrigem, "PJe, e-CAC, outro") +
      campoDraft("ID do documento no sistema de origem", "proveniencia.idDocumentoOrigem", d.proveniencia.idDocumentoOrigem) +
      campoDraft("Nº do processo de origem", "proveniencia.processoOrigem", d.proveniencia.processoOrigem) +
      campoDraft("Usuário que extraiu", "proveniencia.usuarioExtraiu", d.proveniencia.usuarioExtraiu) +
      campoDraft("Data/hora da extração", "proveniencia.dataHoraExtracao", d.proveniencia.dataHoraExtracao, null, "datetime-local") +
    '</div>';
  }
  return radios + extra + (d.proveniencia.tipo ? elementoFisicoBlocoHtml(d) : "");
}
function elementoFisicoBlocoHtml(d) {
  var ef = d.proveniencia.elementoFisico;
  return '<div class="rfb-divider"></div>' +
    '<label class="rfb-check"><input type="checkbox" ' + (ef.presente ? "checked" : "") + ' onchange="App.setDraft(\'proveniencia.elementoFisico.presente\', this.checked)"> Este item inclui um elemento físico (documento físico, HD, celular, mídia removível etc.), além do(s) arquivo(s) digital(is)?</label>' +
    (ef.presente ? '<div style="margin-top:12px;">' + dica('dica_lacre_fisico') +
      '<div class="vdc-grid-3" style="margin-top:12px;">' +
        selectCampo("Tipo de elemento físico", "proveniencia.elementoFisico.tipo", ef.tipo, ELEMENTO_FISICO_TIPOS) +
        campoDraft("Nº do lacre", "proveniencia.elementoFisico.numeroLacre", ef.numeroLacre) +
        selectCampo("Condição do lacre", "proveniencia.elementoFisico.condicaoLacre", ef.condicaoLacre, CONDICAO_LACRE) +
      '</div>' +
      '<div class="vdc-grid-2" style="margin-top:12px;">' +
        campoDraft("Descrição do lacre (cor/característica)", "proveniencia.elementoFisico.descricaoLacre", ef.descricaoLacre) +
        campoDraft("Local de guarda física", "proveniencia.elementoFisico.localGuarda", ef.localGuarda) +
        campoDraft("Responsável pela guarda física", "proveniencia.elementoFisico.responsavelGuarda", ef.responsavelGuarda) +
      '</div>' +
    '</div>' : "");
}
function campoDraft(label, path, value, placeholder, type) {
  return '<div class="rfb-field"><label class="rfb-label">' + label + '</label><input class="rfb-input" type="' + (type || "text") + '" value="' + escapeHtml(value || "") + '" oninput="App.setDraftQuiet(\'' + path + '\', this.value)"' + (placeholder ? ' placeholder="' + placeholder + '"' : '') + '></div>';
}
function selectCampo(label, path, value, options) {
  return '<div class="rfb-field"><label class="rfb-label">' + label + '</label><select class="rfb-select" onchange="App.setDraft(\'' + path + '\', this.value)"><option value="">Selecione…</option>' +
    Object.keys(options).map(function (k) { return '<option value="' + k + '"' + (value === k ? ' selected' : '') + '>' + options[k] + '</option>'; }).join("") + '</select></div>';
}

function stepArquivos(d) {
  var isB = d.proveniencia.tipo === "recebido_hash_oficial";
  var porArquivo = isB && d.proveniencia.modoHashDeclarado === "por_arquivo";
  var cards = d.arquivos.map(function (a, idx) { return arquivoCardHtml(a, idx, null); }).join("");
  return '' +
    (d.proveniencia.tipo === "" ? '<div class="rfb-alert rfb-alert--warning"><div><div class="rfb-alert__msg">Defina a proveniência (etapa anterior) antes de adicionar arquivos.</div></div></div>' : '') +
    '<div class="rfb-stack rfb-gap-3">' + cards + '</div>' +
    '<div class="vdc-file-drop no-print" style="margin-top:14px;">' +
      '<div style="margin-bottom:10px;">+ Adicionar arquivo ao item</div>' +
      '<div class="vdc-grid-2" style="text-align:left;max-width:520px;margin:0 auto;">' +
        '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Descrição do arquivo no pacote</label><input class="rfb-input" id="novoArquivoDescricao" placeholder="Ex.: extrato bancário, print de conversa…"></div>' +
        (porArquivo ? '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Hash declarado pela origem (deste arquivo)</label><input class="rfb-input" id="novoArquivoHashDeclarado" placeholder="sha256…"></div>' : '') +
        '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Arquivo</label><input class="rfb-input" type="file" id="novoArquivoInput"></div>' +
      '</div>' +
      '<button class="rfb-btn rfb-btn--primary rfb-btn--sm" style="margin-top:8px;" onclick="App.adicionarArquivoDraft()">Calcular hash e adicionar</button>' +
      (d.proveniencia.tipo !== "" ? '<div style="margin-top:12px;">' + dica('dica_carimbo_local') + '</div>' : '') +
    '</div>' +
    (d.arquivos.length === 0
      ? (d.proveniencia.elementoFisico.presente
          ? '<div class="rfb-help" style="margin-top:8px;">Elemento físico marcado na Proveniência — arquivo digital é opcional aqui (ex.: foto do objeto lacrado).</div>'
          : '<div class="rfb-help--error" style="margin-top:8px;">É necessário ao menos um arquivo para salvar o item.</div>')
      : '');
}
function arquivoCardHtml(a, idx, itemId) {
  var resBadge = a.resultadoComparacao === "confere" ? '<span class="rfb-badge rfb-badge--success">Confere</span>' :
    a.resultadoComparacao === "diverge" ? '<span class="rfb-badge rfb-badge--danger">Diverge</span>' :
    '<span class="rfb-badge rfb-badge--neutral">Não aplicável</span>';
  return '<div class="vdc-file-card">' +
    '<div class="vdc-file-card__head"><span class="vdc-file-card__name">' + escapeHtml(a.descricao || "(sem descrição)") + '</span>' + resBadge + '</div>' +
    '<div class="vdc-file-meta">' +
      '<div>Arquivo: ' + escapeHtml(a.nomeArquivo) + '</div>' +
      '<div>Tamanho: ' + fmtBytes(a.tamanho) + ' · ' + escapeHtml(a.tipoMime || "tipo desconhecido") + '</div>' +
      '<div>Carimbo local: ' + fmtDT(a.carimboLocal) + '</div>' +
      '<div>Hash local: <code>' + a.hashLocal + '</code></div>' +
      (a.hashDeclarado ? '<div>Hash declarado: <code>' + escapeHtml(a.hashDeclarado) + '</code></div>' : '') +
    '</div>' +
  '</div>';
}

function stepLinhaDoTempoResumo(d) {
  var eventos = eventosMesclados(d);
  return '' +
    '<div class="vdc-grid-2">' +
      '<div class="rfb-field"><label class="rfb-label">Responsável pelo registro na ferramenta</label><input class="rfb-input" value="' + escapeHtml(d.responsavelRegistro) + '" oninput="App.setDraftQuiet(\'responsavelRegistro\', this.value)"></div>' +
      '<div class="rfb-field"><label class="rfb-label">Custodiante atual</label><input class="rfb-input" value="' + escapeHtml(d.custodianteAtual) + '" oninput="App.setDraftQuiet(\'custodianteAtual\', this.value)" placeholder="Quem responde pelo item agora"></div>' +
    '</div>' +
    '<div class="rfb-field" style="margin-top:10px;"><label class="rfb-label">Observações livres</label><textarea class="rfb-textarea" rows="2" oninput="App.setDraftQuiet(\'observacoes\', this.value)">' + escapeHtml(d.observacoes) + '</textarea></div>' +
    '<div class="rfb-divider"></div>' +
    '<div class="rfb-h3" style="margin-bottom:8px;">Prévia da linha do tempo (gerada ao salvar)</div>' +
    (eventos.length ? '<div class="vdc-timeline">' + eventos.map(timelineEventHtml).join("") + '</div>' : '<div class="rfb-body--muted rfb-body--small">Os eventos automáticos (identificação, cálculo de hash) serão gerados ao salvar o item.</div>');
}
function eventosMesclados(item) {
  var evs = item.linhaDoTempoItem.map(function (e) { return Object.assign({}, e, { escopo: "item" }); });
  item.arquivos.forEach(function (a) {
    (a.linhaDoTempoArquivo || []).forEach(function (e) { evs.push(Object.assign({}, e, { escopo: "arquivo", arquivoNome: a.descricao || a.nomeArquivo })); });
  });
  evs.sort(function (x, y) { return new Date(x.dataHora) - new Date(y.dataHora); });
  return evs;
}
function timelineEventHtml(e) {
  var tipo = EVENTO_TIPOS[e.evento] || { label: e.evento };
  return '<div class="vdc-timeline-event"><div class="vdc-timeline-event__dot' + (e.escopo === "arquivo" ? " vdc-timeline-event__dot--arquivo" : "") + '"></div>' +
    '<div class="vdc-timeline-event__body">' +
      '<div class="vdc-timeline-event__title">' + tipo.label + (e.arquivoNome ? " — " + escapeHtml(e.arquivoNome) : "") + '</div>' +
      '<div class="vdc-timeline-event__meta">' + fmtDT(e.dataHora) + (e.responsavel ? " · " + escapeHtml(e.responsavel) : "") + (e.resultado ? " · " + (RESULTADO[e.resultado] || CONDICAO_LACRE[e.resultado] || e.resultado) : "") + '</div>' +
      (e.observacao ? '<div class="vdc-timeline-event__obs">' + escapeHtml(e.observacao) + '</div>' : '') +
    '</div></div>';
}

/* ============================================================
   Detalhe de item existente
   ============================================================ */
function findItem(id) { return DB.dossie.itens.find(function (i) { return i.id === id; }); }

function viewItemDetalhe(itemId) {
  var it = findItem(itemId);
  if (!it) { UI.view = "processo"; return viewProcesso(); }
  var eventos = eventosMesclados(it);
  var isB = it.proveniencia.tipo === "recebido_hash_oficial";
  var porArquivo = isB && it.proveniencia.modoHashDeclarado === "por_arquivo";

  return '' +
  '<div class="vdc-page">' +
    '<div class="vdc-section-head no-print"><button class="rfb-btn rfb-btn--ghost rfb-btn--sm" onclick="App.voltarProcesso()">&larr; Voltar</button>' +
      '<div class="vdc-actions"><button class="rfb-btn rfb-btn--secondary rfb-btn--sm" onclick="App.abrirModal(\'evento\', {itemId:\'' + it.id + '\'})">+ Registrar evento</button></div>' +
    '</div>' +

    '<div class="rfb-card"><div class="rfb-card__header"><span class="rfb-card__title">' + escapeHtml(it.titulo) + '</span>' +
      '<span class="rfb-badge rfb-badge--' + statusBadgeCor(it.status) + '">' + STATUS_ITEM[it.status] + '</span></div>' +
      '<div class="rfb-card__body">' +
        '<div class="vdc-grid-3">' +
          campo("Título/descrição", "titulo", it.titulo) +
          selectCampoDetalhe("Categoria", "categoria", it.categoria, CATEGORIAS) +
          campo("Nº/folha nos autos", "folhaAutos", it.folhaAutos) +
          campo("Vinculado à matriz de apuração", "vinculoMatriz", it.vinculoMatriz) +
          selectCampoDetalhe("Sigilo/classificação", "sigilo", it.sigilo, SIGILO) +
          campo("Custodiante atual", "custodianteAtual", it.custodianteAtual) +
        '</div>' +
        (it.conteudoIntegral ? '' : '<div style="margin-top:12px;"><span class="rfb-badge rfb-badge--warning">Extrato parcial</span> <span class="rfb-body--small rfb-body--muted">' + escapeHtml(it.justificativaExtrato) + '</span></div>') +
        (it.status === "contestado" ? '<div class="rfb-alert rfb-alert--warning" style="margin-top:12px;"><div><div class="rfb-alert__title">Contestado</div><div class="rfb-alert__msg">' + escapeHtml(it.fundamentacaoContestacao || "—") + '</div></div></div>' + dica('dica_pericia') : '') +
      '</div></div>' +

    '<div class="rfb-card"><div class="rfb-card__header"><span class="rfb-card__title">Proveniência</span></div><div class="rfb-card__body">' +
      '<div class="rfb-badge rfb-badge--info" style="margin-bottom:12px;">' + PROVENIENCIA_TIPOS[it.proveniencia.tipo] + '</div>' +
      provenienciaResumoHtml(it) +
    '</div></div>' +

    '<div class="rfb-card"><div class="rfb-card__header"><span class="rfb-card__title">Arquivos (' + it.arquivos.length + ')</span></div><div class="rfb-card__body">' +
      '<div class="rfb-stack rfb-gap-3">' + it.arquivos.map(function (a) { return arquivoCardHtml(a, 0, it.id); }).join("") + '</div>' +
      '<div class="vdc-file-drop no-print" style="margin-top:14px;">' +
        '<div style="margin-bottom:10px;">+ Adicionar arquivo ao item</div>' +
        '<div class="vdc-grid-2" style="text-align:left;max-width:520px;margin:0 auto;">' +
          '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Descrição do arquivo no pacote</label><input class="rfb-input" id="detArquivoDescricao"></div>' +
          (porArquivo ? '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Hash declarado pela origem</label><input class="rfb-input" id="detArquivoHashDeclarado"></div>' : '') +
          '<div class="rfb-field" style="grid-column:span 2;"><label class="rfb-label">Arquivo</label><input class="rfb-input" type="file" id="detArquivoInput"></div>' +
        '</div>' +
        '<button class="rfb-btn rfb-btn--primary rfb-btn--sm" style="margin-top:8px;" onclick="App.adicionarArquivoExistente(\'' + it.id + '\')">Calcular hash e adicionar</button>' +
      '</div>' +
    '</div></div>' +

    '<div class="rfb-card"><div class="rfb-card__header"><span class="rfb-card__title">Linha do tempo</span></div><div class="rfb-card__body">' +
      (eventos.length ? '<div class="vdc-timeline">' + eventos.map(timelineEventHtml).join("") + '</div>' : '<div class="rfb-body--muted">Sem eventos.</div>') +
    '</div></div>' +
  '</div>';
}
function selectCampoDetalhe(label, field, value, options) {
  return '<div class="rfb-field"><label class="rfb-label">' + label + '</label><select class="rfb-select" onchange="App.salvarCampoItem(\'' + field + '\', this.value)">' +
    Object.keys(options).map(function (k) { return '<option value="' + k + '"' + (value === k ? ' selected' : '') + '>' + options[k] + '</option>'; }).join("") + '</select></div>';
}
function campo(label, field, value) {
  return '<div class="rfb-field"><label class="rfb-label">' + label + '</label><input class="rfb-input" value="' + escapeHtml(value || "") + '" onchange="App.salvarCampoItem(\'' + field + '\', this.value)"></div>';
}
function provenienciaResumoHtml(it) {
  var p = it.proveniencia, rows = [];
  if (p.tipo === "gerado_internamente") {
    rows = [["Quem coletou", p.quemColetou], ["Contexto", p.contextoColeta], ["Local/situação", p.localSituacao]];
  } else if (p.tipo === "recebido_hash_oficial") {
    rows = [["Processo judicial de origem", p.processoJudicialOrigem], ["Órgão expedidor", p.orgaoExpedidor],
      ["Natureza", NATUREZA_COMPARTILHAMENTO[p.naturezaCompartilhamento] || p.naturezaCompartilhamento], ["Operação", p.nomeOperacao],
      ["Data do ofício", p.dataOficio], ["Data de recebimento", p.dataRecebimento], ["Nº do ofício", p.numeroOficio],
      ["Modo do hash declarado", p.modoHashDeclarado === "pacote" ? "Pacote compactado" : "Por arquivo"]];
    if (p.modoHashDeclarado === "pacote") rows.push(["Hash declarado do pacote", p.hashDeclaradoPacote], ["Algoritmo", p.algoritmoDeclarado]);
  } else if (p.tipo === "extraido_sistema_trilha") {
    rows = [["Sistema de origem", p.sistemaOrigem], ["ID do documento", p.idDocumentoOrigem], ["Processo de origem", p.processoOrigem], ["Usuário que extraiu", p.usuarioExtraiu], ["Data/hora da extração", p.dataHoraExtracao]];
  }
  var html = '<div class="vdc-file-meta">' + rows.map(function (r) { return '<div><strong>' + r[0] + ':</strong> ' + escapeHtml(r[1] || "—") + '</div>'; }).join("") + '</div>';
  html += elementoFisicoResumoHtml(p.elementoFisico);
  return html;
}
function elementoFisicoResumoHtml(ef) {
  if (!ef || !ef.presente) return "";
  var corCondicao = ef.condicaoLacre === "rompido" ? "danger" : (ef.condicaoLacre === "intacto" ? "success" : "neutral");
  return '<div class="rfb-divider"></div>' +
    '<div class="rfb-badge rfb-badge--' + corCondicao + '" style="margin-bottom:8px;">&#128274; Lacre ' + (CONDICAO_LACRE[ef.condicaoLacre] || "—") + '</div>' +
    '<div class="vdc-file-meta">' +
      '<div><strong>Tipo de elemento físico:</strong> ' + escapeHtml(ELEMENTO_FISICO_TIPOS[ef.tipo] || "—") + '</div>' +
      '<div><strong>Nº do lacre:</strong> ' + escapeHtml(ef.numeroLacre || "—") + '</div>' +
      '<div><strong>Descrição do lacre:</strong> ' + escapeHtml(ef.descricaoLacre || "—") + '</div>' +
      '<div><strong>Local de guarda física:</strong> ' + escapeHtml(ef.localGuarda || "—") + '</div>' +
      '<div><strong>Responsável pela guarda física:</strong> ' + escapeHtml(ef.responsavelGuarda || "—") + '</div>' +
    '</div>';
}

/* ============================================================
   Modal — registrar evento
   ============================================================ */
function renderModal() {
  if (!UI.modal) return "";
  if (UI.modal.tipo === "evento") return renderModalEvento();
  if (UI.modal.tipo === "importarChoice") return renderModalImportChoice();
  if (UI.modal.tipo === "reiniciar") return renderModalReiniciar();
  return "";
}
var EVENTO_TIPO_OPTIONS = [
  ["transferencia_custodia", "Transferência de custódia"],
  ["enviado_pericia", "Enviado para perícia formal"],
  ["status_alterado", "Status alterado"],
  ["item_descartado", "Item descartado"],
  ["descricao_registrada", "Descrição/contexto registrado"]
];
function renderModalEvento() {
  var it = findItem(UI.modal.itemId);
  var c = UI.modal.campos;
  var opcoesTipo = EVENTO_TIPO_OPTIONS.slice();
  if (it.proveniencia.elementoFisico && it.proveniencia.elementoFisico.presente) opcoesTipo.push(["conferencia_lacre", "Conferência do lacre"]);
  var selectTipo = '<select class="rfb-select" id="evTipo" onchange="App.mudarTipoEvento(this.value)">' +
    opcoesTipo.map(function (o) { return '<option value="' + o[0] + '"' + (c.tipo === o[0] ? " selected" : "") + '>' + o[1] + "</option>"; }).join("") + "</select>";
  return '<div class="vdc-modal-overlay" onclick="if(event.target===this) App.fecharModal()"><div class="vdc-modal">' +
    '<div class="vdc-modal__head"><span class="rfb-h3">Registrar evento</span><button class="vdc-close-btn" onclick="App.fecharModal()">&times;</button></div>' +
    '<div class="vdc-modal__body">' +
      '<div class="rfb-field"><label class="rfb-label">Tipo de evento</label>' + selectTipo + '</div>' +
      '<div id="evExtraFields">' + buildEventoExtraFieldsHtml(it, c) + '</div>' +
      '<div class="rfb-field"><label class="rfb-label">Responsável</label><input class="rfb-input" id="evResponsavel"></div>' +
      '<div class="rfb-field"><label class="rfb-label">Observação</label><textarea class="rfb-textarea" rows="2" id="evObservacao"></textarea></div>' +
    '</div>' +
    '<div class="vdc-modal__foot"><button class="rfb-btn rfb-btn--secondary" onclick="App.fecharModal()">Cancelar</button><button class="rfb-btn rfb-btn--primary" onclick="App.confirmarEvento()">Registrar</button></div>' +
  '</div></div>';
}
function buildEventoExtraFieldsHtml(it, c) {
  var html = "";
  if (c.tipo === "transferencia_custodia") {
    html = '<div class="rfb-field"><label class="rfb-label">Novo custodiante</label><input class="rfb-input" id="evNovoCustodiante"></div>';
  } else if (c.tipo === "enviado_pericia") {
    html = '<div class="rfb-field"><label class="rfb-label">Arquivo</label><select class="rfb-select" id="evArquivo">' +
      it.arquivos.map(function (a) { return '<option value="' + a.id + '">' + escapeHtml(a.descricao || a.nomeArquivo) + '</option>'; }).join("") + '</select></div>';
  } else if (c.tipo === "status_alterado") {
    html = '<div class="rfb-field"><label class="rfb-label">Novo status</label><select class="rfb-select" id="evNovoStatus" onchange="App.mudarNovoStatusEvento(this.value)">' +
      Object.keys(STATUS_ITEM).map(function (k) { return '<option value="' + k + '"' + (c.novoStatus === k ? " selected" : "") + '>' + STATUS_ITEM[k] + "</option>"; }).join("") + '</select></div>';
    if (c.novoStatus === "substituido") html += '<div class="rfb-field"><label class="rfb-label">Referência ao item substituto</label><input class="rfb-input" id="evItemSubstituto"></div>';
    if (c.novoStatus === "contestado") html += '<div class="rfb-field"><label class="rfb-label">Fundamentação da contestação <span class="rfb-label__hint">obrigatória</span></label><textarea class="rfb-textarea" rows="2" id="evFundamentacao"></textarea></div>';
  } else if (c.tipo === "item_descartado") {
    html = '<div class="rfb-field"><label class="rfb-label">Justificativa <span class="rfb-label__hint">obrigatória</span></label><textarea class="rfb-textarea" rows="2" id="evJustificativa"></textarea></div>';
  } else if (c.tipo === "descricao_registrada") {
    html = '<div class="rfb-field"><label class="rfb-label">Escopo</label><select class="rfb-select" id="evEscopo" onchange="App.mudarEscopoEvento(this.value)">' +
      '<option value="item"' + (c.escopo === "item" ? " selected" : "") + '>Item (pacote)</option>' +
      '<option value="arquivo"' + (c.escopo === "arquivo" ? " selected" : "") + '>Arquivo</option></select></div>';
    if (c.escopo === "arquivo") {
      html += '<div class="rfb-field"><label class="rfb-label">Arquivo</label><select class="rfb-select" id="evArquivo">' +
        it.arquivos.map(function (a) { return '<option value="' + a.id + '">' + escapeHtml(a.descricao || a.nomeArquivo) + '</option>'; }).join("") + '</select></div>';
    }
    html += '<div class="rfb-field"><label class="rfb-label">Texto</label><textarea class="rfb-textarea" rows="2" id="evTexto"></textarea></div>';
  } else if (c.tipo === "conferencia_lacre") {
    html = '<div class="rfb-field"><label class="rfb-label">Condição do lacre nesta conferência</label><select class="rfb-select" id="evCondicaoLacre">' +
      Object.keys(CONDICAO_LACRE).map(function (k) { return '<option value="' + k + '"' + (it.proveniencia.elementoFisico.condicaoLacre === k ? " selected" : "") + '>' + CONDICAO_LACRE[k] + "</option>"; }).join("") + '</select></div>';
  }
  return html;
}
function renderModalImportChoice() {
  return '<div class="vdc-modal-overlay"><div class="vdc-modal">' +
    '<div class="vdc-modal__head"><span class="rfb-h3">Importar dossiê</span></div>' +
    '<div class="vdc-modal__body"><p class="rfb-body">Você tem um dossiê aberto com ' + DB.dossie.itens.length + ' item(ns). A importação nunca mescla dossiês — o dossiê atual será substituído nesta sessão.</p>' +
    (UI.modal.hashDivergente ? '<div class="rfb-alert rfb-alert--danger"><div><div class="rfb-alert__title">Atenção</div><div class="rfb-alert__msg">O hashDoDossie do arquivo importado não confere com o conteúdo — possível indício de alteração externa do arquivo.</div></div></div>' : '') +
    '</div>' +
    '<div class="vdc-modal__foot"><button class="rfb-btn rfb-btn--secondary" onclick="App.fecharModal()">Cancelar</button><button class="rfb-btn rfb-btn--primary" onclick="App.confirmarImportacao()">Substituir e importar</button></div>' +
  '</div></div>';
}
function renderModalReiniciar() {
  var d = DB.dossie;
  return '<div class="vdc-modal-overlay" onclick="if(event.target===this) App.fecharModal()"><div class="vdc-modal">' +
    '<div class="vdc-modal__head"><span class="rfb-h3">Reiniciar dossiê</span><button class="vdc-close-btn" onclick="App.fecharModal()">&times;</button></div>' +
    '<div class="vdc-modal__body">' +
      '<p class="rfb-body">Este dossiê (' + escapeHtml(d.processo.numero || "sem número") + ') tem ' + d.itens.length + ' item(ns) e está salvo neste navegador — reabrir o navegador continuaria carregando-o automaticamente.</p>' +
      '<p class="rfb-body">Reiniciar apaga o dossiê deste navegador (localStorage) e volta à tela inicial, para começar um novo ou importar outro. <strong>Exporte o .json antes, se ainda precisar destes dados.</strong></p>' +
      '<div class="rfb-alert rfb-alert--warning"><div><div class="rfb-alert__msg">Esta ação não pode ser desfeita — o dossiê só será recuperável se você tiver exportado o .json antes.</div></div></div>' +
    '</div>' +
    '<div class="vdc-modal__foot">' +
      '<button class="rfb-btn rfb-btn--secondary" onclick="App.fecharModal()">Cancelar</button>' +
      '<button class="rfb-btn rfb-btn--secondary" onclick="App.exportarDossie()">Exportar .json antes</button>' +
      '<button class="rfb-btn rfb-btn--danger" onclick="App.confirmarReiniciar()">Reiniciar mesmo assim</button>' +
    '</div>' +
  '</div></div>';
}

/* ============================================================
   Conferência Geral
   ============================================================ */
function viewConferencia() {
  var itens = DB.dossie.itens.filter(function (i) { return i.status !== "descartado"; });
  if (itens.length === 0) return '<div class="vdc-page"><button class="rfb-btn rfb-btn--ghost" onclick="App.voltarProcesso()">&larr; Voltar</button><div class="vdc-empty-state">Nenhum item ativo para conferir.</div></div>';

  return '<div class="vdc-page">' +
    '<div class="vdc-section-head"><span class="rfb-h2">Conferência Geral</span><button class="rfb-btn rfb-btn--ghost rfb-btn--sm no-print" onclick="App.voltarProcesso()">&larr; Voltar</button></div>' +
    '<div class="rfb-body--muted rfb-body--small">Recarregue cada arquivo original para recalcular o hash e comparar contra a referência registrada. Proveniência B (por arquivo) compara contra o hash declarado pela origem; demais casos comparam contra o hash local originalmente registrado.</div>' +
    itens.map(conferenciaItemHtml).join("") +
  '</div>';
}
function conferenciaItemHtml(it) {
  return '<div class="rfb-card"><div class="rfb-card__header"><span class="rfb-card__title">' + escapeHtml(it.titulo) + '</span>' +
    '<span class="rfb-badge rfb-badge--' + statusBadgeCor(it.status) + '">' + STATUS_ITEM[it.status] + '</span></div>' +
    '<div class="rfb-card__body"><div class="rfb-stack rfb-gap-3">' +
      it.arquivos.map(function (a) { return conferenciaArquivoHtml(it, a); }).join("") +
    '</div></div>' +
    '<div class="rfb-card__footer"><button class="rfb-btn rfb-btn--accent rfb-btn--sm" onclick="App.concluirConferenciaItem(\'' + it.id + '\')">Concluir conferência do item</button></div>' +
  '</div>';
}
function conferenciaArquivoHtml(it, a) {
  var resBadge = a.resultadoComparacao === "confere" ? '<span class="rfb-badge rfb-badge--success">Confere</span>' :
    a.resultadoComparacao === "diverge" ? '<span class="rfb-badge rfb-badge--danger">Diverge</span>' :
    '<span class="rfb-badge rfb-badge--neutral">Não aplicável</span>';
  return '<div class="vdc-file-card">' +
    '<div class="vdc-file-card__head"><span class="vdc-file-card__name">' + escapeHtml(a.descricao || a.nomeArquivo) + '</span>' + resBadge + '</div>' +
    '<div class="vdc-file-meta"><div>Hash de referência: <code>' + referenciaHash(it, a) + '</code></div></div>' +
    '<div class="rfb-row rfb-gap-2" style="align-items:center;">' +
      '<input class="rfb-input" type="file" id="conf_' + a.id + '" style="max-width:320px;">' +
      '<button class="rfb-btn rfb-btn--secondary rfb-btn--sm" onclick="App.conferirArquivo(\'' + it.id + '\', \'' + a.id + '\')">Conferir</button>' +
    '</div>' +
  '</div>';
}
function referenciaHash(it, a) {
  var isB = it.proveniencia.tipo === "recebido_hash_oficial";
  var porArquivo = isB && it.proveniencia.modoHashDeclarado === "por_arquivo";
  return porArquivo ? (a.hashDeclarado || "—") : a.hashLocal;
}

/* ============================================================
   Relatório
   ============================================================ */
function membroResumoHtml(label, m) {
  if (!m || !m.nome) return "<div><b>" + label + ":</b> —</div>";
  var partes = [escapeHtml(m.nome)];
  if (m.cargo) partes.push(escapeHtml(m.cargo));
  if (m.matricula) partes.push("mat. " + escapeHtml(m.matricula));
  return "<div><b>" + label + ":</b> " + partes.join(" — ") + "</div>";
}
function itemHashCelulaHtml(it) {
  if (it.arquivos.length === 0) return "—";
  return '<div class="impresso-hash">' + it.arquivos.map(function (a) {
    return (it.arquivos.length > 1 ? '<small>' + escapeHtml(a.descricao || a.nomeArquivo) + ':</small> ' : '') + a.hashLocal;
  }).join("<br>") + '</div>';
}
function viewRelatorio() {
  var d = DB.dossie, p = d.processo;
  var temSigilo = d.itens.some(function (i) { return i.sigilo !== "publico"; });
  return '<div class="vdc-page">' +
    '<div class="vdc-actions no-print"><button class="rfb-btn rfb-btn--ghost rfb-btn--sm" onclick="App.voltarProcesso()">&larr; Voltar</button><button class="rfb-btn rfb-btn--primary rfb-btn--sm" onclick="window.print()">Imprimir / Salvar PDF</button></div>' +
    '<div class="rfb-card vdc-relatorio"><div class="rfb-card__body">' +

      '<div class="impresso-topo"><div class="impresso-marca">Receita Federal <span>·</span> Corregedoria</div></div>' +
      '<div class="impresso-titulo">Veritas Digital - Coger</div>' +
      '<div class="impresso-subtitulo">Relatório de Cadeia de Custódia · Investigação, pareceres e comissões</div>' +
      '<div class="impresso-epigrafe">&ldquo;' + escapeHtml(CATALOGO.epigrafe.texto) + '&rdquo; — ' + escapeHtml(CATALOGO.epigrafe.autor) + '</div>' +

      '<div class="impresso-refs">' +
        '<span><b>Processo nº</b> ' + escapeHtml(p.numero || "—") + '</span>' +
        '<span><b>Portaria</b> ' + escapeHtml(p.portaria || "—") + '</span>' +
        '<span><b>Seção/unidade</b> ' + escapeHtml(p.secaoResponsavel || "—") + '</span>' +
        '<span><b>Gerado em</b> ' + fmtDT(nowIso()) + '</span>' +
      '</div>' +

      '<div class="impresso-infobox">' +
        membroResumoHtml("Presidente", p.comissao.presidente) +
        membroResumoHtml("Secretário(a)", p.comissao.secretario) +
        (p.comissao.vogais.length ? p.comissao.vogais.map(function (v, i) { return membroResumoHtml("Vogal " + (i + 1), v); }).join("") : "<div><b>Vogais:</b> —</div>") +
        '<div class="divisor"></div>' +
        '<div class="linha"><div><div class="rotulo">hashDoDossie</div><span style="font-family:var(--rfb-font-mono);font-size:10.5px;">' + d.hashDoDossie + '</span></div></div>' +
      '</div>' +

      (temSigilo ? '<div class="impresso-alerta">Atenção — conteúdo classificado: este relatório contém itens de acesso restrito e/ou sigilosos. Trate a divulgação e o compartilhamento conforme a classificação de cada item.</div>' : '') +

      '<h3 class="impresso-secao">1. Itens (elementos de prova)</h3>' +
      '<div class="rfb-table-wrap"><table class="rfb-table"><thead><tr><th>Item</th><th>Categoria</th><th>Proveniência</th><th>Arquivos</th><th>Hash</th><th>Status</th><th>Fls.</th></tr></thead><tbody>' +
        d.itens.map(function (it) {
          var ef = it.proveniencia.elementoFisico;
          var provCel = (PROVENIENCIA_TIPOS[it.proveniencia.tipo] || "—") +
            (ef && ef.presente ? '<br><span class="rfb-badge rfb-badge--' + (ef.condicaoLacre === "rompido" ? "danger" : "success") + '" style="margin-top:4px;">&#128274; Lacre ' + (ef.numeroLacre ? "nº " + escapeHtml(ef.numeroLacre) + " — " : "") + (CONDICAO_LACRE[ef.condicaoLacre] || "") + '</span>' : "");
          return '<tr><td>' + escapeHtml(it.titulo) + '</td><td>' + (CATEGORIAS[it.categoria] || "—") + '</td><td>' + provCel + '</td>' +
            '<td>' + it.arquivos.length + '</td><td>' + itemHashCelulaHtml(it) + '</td><td>' + STATUS_ITEM[it.status] + '</td><td>' + escapeHtml(it.folhaAutos || "—") + '</td></tr>';
        }).join("") + '</tbody></table></div>' +

      '<h3 class="impresso-secao">2. Apêndice — linha do tempo detalhada</h3>' +
        d.itens.map(function (it) {
          var evs = eventosMesclados(it);
          return '<div class="vdc-report-item-block"><div style="font-weight:600;margin-bottom:6px;">' + escapeHtml(it.titulo) + '</div>' +
            '<div class="vdc-timeline">' + (evs.length ? evs.map(timelineEventHtml).join("") : '<div class="rfb-body--small rfb-body--muted">Sem eventos.</div>') + '</div></div>';
        }).join("") +

      '<div class="impresso-rodape">' +
        '<div class="disclaimer"><strong>Fundamentação doutrinária:</strong> ' + escapeHtml(CATALOGO.fundamentacao) + '<br><br>' + escapeHtml(CATALOGO.disclaimerLongo) + '</div>' +
        '<div class="linha-final"><span>Veritas Digital - Coger · Ferramentas Coger · RFB</span><span>' + escapeHtml(p.numero || "sem número") + '</span></div>' +
      '</div>' +
    '</div></div>' +
  '</div>';
}

/* ============================================================
   API pública — App
   ============================================================ */
window.App = {
  render: render,

  criarDossie: function () {
    DB.dossie = novoDossie();
    UI.view = "processo";
    persistir().then(render);
  },
  importarArquivo: function (evt) {
    var file = evt.target.files[0];
    if (!file) return;
    var reader = new FileReader();
    reader.onload = async function () {
      var parsed;
      try { parsed = JSON.parse(reader.result); } catch (e) { toast("Arquivo .json inválido.", "danger"); return; }
      if (parsed.versaoEsquema !== "2.0") { toast("Versão de esquema não suportada: " + parsed.versaoEsquema, "danger"); return; }
      var hashCalc = await hashDossieMetadata(parsed);
      var hashDivergente = parsed.hashDoDossie && hashCalc !== parsed.hashDoDossie;
      if (DB.dossie && DB.dossie.itens.length > 0) {
        UI.modal = { tipo: "importarChoice", parsed: parsed, hashDivergente: hashDivergente };
        render();
      } else {
        App._finalizarImportacao(parsed, hashDivergente);
      }
    };
    reader.readAsText(file);
    evt.target.value = "";
  },
  confirmarImportacao: function () {
    var m = UI.modal;
    App._finalizarImportacao(m.parsed, m.hashDivergente);
  },
  confirmarReiniciar: function () {
    localStorage.removeItem(STORAGE_KEY);
    DB.dossie = null;
    UI.modal = null;
    UI.view = "inicio";
    render();
    toast("Dossiê apagado deste navegador. Comece um novo ou importe um .json.", "success");
  },
  _finalizarImportacao: function (parsed, hashDivergente) {
    DB.dossie = migrarDossie(parsed);
    UI.modal = null;
    UI.view = "processo";
    persistir().then(function () {
      render();
      toast(hashDivergente ? "Dossiê importado — hashDoDossie divergente, verifique a origem do arquivo." : "Dossiê importado com sucesso.", hashDivergente ? "danger" : "success");
    });
  },
  exportarDossie: function () {
    persistir().then(function () {
      var blob = new Blob([JSON.stringify(DB.dossie, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "dossie-" + (DB.dossie.processo.numero || "veritas-digital-coger").replace(/[^\w.-]+/g, "_") + ".json";
      document.body.appendChild(a); a.click(); a.remove();
      toast("Dossiê exportado.", "success");
    });
  },

  setProcesso: function (path, value) { set(DB.dossie.processo, path, value); persistir().then(updateTopbar); },
  setMembro: function (papel, sub, value) { DB.dossie.processo.comissao[papel][sub] = value; persistir(); },
  adicionarVogal: function () { DB.dossie.processo.comissao.vogais.push(membroVazio()); persistir().then(render); },
  removerVogal: function (i) { DB.dossie.processo.comissao.vogais.splice(i, 1); persistir().then(render); },
  setVogalCampo: function (i, sub, value) { DB.dossie.processo.comissao.vogais[i][sub] = value; persistir(); },

  voltarProcesso: function () { UI.view = "processo"; UI.editingField = null; render(); },
  abrirItem: function (id) { UI.view = "itemDetalhe"; UI.editingField = id; render(); },
  irParaConferencia: function () { UI.view = "conferencia"; render(); },
  irParaRelatorio: function () { UI.view = "relatorio"; render(); },

  criarItem: function () { UI.draftItem = novoItemDraft(); UI.wizardStep = 1; UI.view = "itemWizard"; render(); },
  cancelarWizard: function () { UI.draftItem = null; UI.view = "processo"; render(); },
  setDraft: function (path, value) { set(UI.draftItem, path, value); render(); },
  setDraftQuiet: function (path, value) { set(UI.draftItem, path, value); },
  irParaStep: function (n) { if (n < UI.wizardStep || App._validarStep(UI.wizardStep)) { UI.wizardStep = n; render(); } },
  avancarStep: function () { if (App._validarStep(UI.wizardStep)) { UI.wizardStep++; render(); } },
  _validarStep: function (step) {
    var d = UI.draftItem;
    if (step === 1) {
      if (!d.titulo.trim()) { toast("Informe o título/descrição.", "danger"); return false; }
      if (!d.categoria) { toast("Selecione a categoria.", "danger"); return false; }
      if (!d.conteudoIntegral && !d.justificativaExtrato.trim()) { toast("Justificativa obrigatória para extrato parcial.", "danger"); return false; }
    }
    if (step === 2) {
      if (!d.proveniencia.tipo) { toast("Selecione o tipo de proveniência.", "danger"); return false; }
    }
    if (step === 3) {
      if (d.arquivos.length === 0 && !d.proveniencia.elementoFisico.presente) { toast("Adicione ao menos um arquivo (ou marque o elemento físico na Proveniência).", "danger"); return false; }
    }
    return true;
  },

  adicionarArquivoDraft: async function () {
    var input = document.getElementById("novoArquivoInput");
    var file = input.files[0];
    if (!file) { toast("Selecione um arquivo.", "danger"); return; }
    var descricao = document.getElementById("novoArquivoDescricao").value;
    var hashDeclaradoEl = document.getElementById("novoArquivoHashDeclarado");
    var hashDeclarado = hashDeclaradoEl ? hashDeclaradoEl.value.trim() : "";
    var arquivo = await App._construirArquivo(file, descricao, hashDeclarado, UI.draftItem.proveniencia);
    UI.draftItem.arquivos.push(arquivo);
    render();
    toast("Arquivo adicionado.", "success");
  },
  adicionarArquivoExistente: async function (itemId) {
    var it = findItem(itemId);
    var input = document.getElementById("detArquivoInput");
    var file = input.files[0];
    if (!file) { toast("Selecione um arquivo.", "danger"); return; }
    var descricao = document.getElementById("detArquivoDescricao").value;
    var hashDeclaradoEl = document.getElementById("detArquivoHashDeclarado");
    var hashDeclarado = hashDeclaradoEl ? hashDeclaradoEl.value.trim() : "";
    var arquivo = await App._construirArquivo(file, descricao, hashDeclarado, it.proveniencia);
    it.arquivos.push(arquivo);
    registrarEventoItem(it, "descricao_registrada", { responsavel: it.responsavelRegistro, observacao: "Arquivo adicionado ao pacote: " + (descricao || file.name) });
    recalcularAgregadoItem(it);
    persistir().then(render);
    toast("Arquivo adicionado ao item.", "success");
  },
  _construirArquivo: async function (file, descricao, hashDeclarado, proveniencia) {
    var hashLocal = await hashFile(file);
    var isB = proveniencia.tipo === "recebido_hash_oficial";
    var porArquivo = isB && proveniencia.modoHashDeclarado === "por_arquivo";
    var resultado = "nao_aplicavel";
    if (porArquivo && hashDeclarado) resultado = (hashLocal.toLowerCase() === hashDeclarado.toLowerCase()) ? "confere" : "diverge";
    var arquivo = {
      id: uid(), descricao: descricao || "", nomeArquivo: file.name, tamanho: file.size, tipoMime: file.type || "aplicação/octeto",
      hashLocal: hashLocal, algoritmoLocal: "SHA-256", hashDeclarado: porArquivo ? hashDeclarado : "",
      resultadoComparacao: resultado, carimboLocal: nowIso(), linhaDoTempoArquivo: []
    };
    registrarEventoArquivo(arquivo, "arquivo_adicionado", { responsavel: "", observacao: descricao || file.name });
    registrarEventoArquivo(arquivo, "hash_local_calculado", { resultado: resultado === "nao_aplicavel" ? "" : resultado });
    if (porArquivo && hashDeclarado) registrarEventoArquivo(arquivo, "hash_declarado_recebido", { resultado: resultado });
    return arquivo;
  },

  salvarItem: function () {
    if (!App._validarStep(1) || !App._validarStep(2) || !App._validarStep(3)) return;
    var d = UI.draftItem;
    registrarEventoItem(d, "item_identificado", { responsavel: d.responsavelRegistro, observacao: d.titulo });
    recalcularAgregadoItem(d);
    DB.dossie.itens.push(d);
    UI.draftItem = null;
    UI.view = "itemDetalhe";
    UI.editingField = d.id;
    persistir().then(render);
    toast("Item salvo.", "success");
  },

  salvarCampoItem: function (field, value) {
    var it = findItem(UI.editingField);
    if (field === "categoria" && value === "" ) return;
    set(it, field, value);
    persistir().then(render);
  },

  abrirModal: function (tipo, payload) {
    UI.modal = Object.assign({ tipo: tipo }, payload);
    if (tipo === "evento") UI.modal.campos = { tipo: "transferencia_custodia", novoStatus: "ativo", escopo: "item" };
    render();
  },
  fecharModal: function () { UI.modal = null; render(); },
  _refrescarExtraFields: function () {
    var it = findItem(UI.modal.itemId);
    document.getElementById("evExtraFields").innerHTML = buildEventoExtraFieldsHtml(it, UI.modal.campos);
  },
  mudarTipoEvento: function (v) { UI.modal.campos.tipo = v; App._refrescarExtraFields(); },
  mudarNovoStatusEvento: function (v) { UI.modal.campos.novoStatus = v; App._refrescarExtraFields(); },
  mudarEscopoEvento: function (v) { UI.modal.campos.escopo = v; App._refrescarExtraFields(); },
  confirmarEvento: function () {
    var tipo = UI.modal.campos.tipo;
    var responsavel = document.getElementById("evResponsavel").value;
    var observacao = document.getElementById("evObservacao").value;
    var it = findItem(UI.modal.itemId);

    if (tipo === "transferencia_custodia") {
      var novo = document.getElementById("evNovoCustodiante").value;
      if (!novo.trim()) { toast("Informe o novo custodiante.", "danger"); return; }
      it.custodianteAtual = novo;
      registrarEventoItem(it, "transferencia_custodia", { responsavel: responsavel, observacao: observacao || ("Novo custodiante: " + novo) });
    } else if (tipo === "enviado_pericia") {
      var arqId = document.getElementById("evArquivo").value;
      var arq = it.arquivos.find(function (a) { return a.id === arqId; });
      registrarEventoArquivo(arq, "enviado_pericia", { responsavel: responsavel, observacao: observacao });
    } else if (tipo === "status_alterado") {
      var novoStatus = document.getElementById("evNovoStatus").value;
      if (novoStatus === "contestado") {
        var fund = document.getElementById("evFundamentacao").value;
        if (!fund.trim()) { toast("Fundamentação da contestação é obrigatória.", "danger"); return; }
        it.fundamentacaoContestacao = fund;
      }
      if (novoStatus === "substituido") { it.itemSubstitutoId = document.getElementById("evItemSubstituto").value || null; }
      it.status = novoStatus;
      registrarEventoItem(it, "status_alterado", { responsavel: responsavel, resultado: novoStatus, observacao: observacao });
    } else if (tipo === "item_descartado") {
      var just = document.getElementById("evJustificativa").value;
      if (!just.trim()) { toast("Justificativa é obrigatória para descarte.", "danger"); return; }
      it.status = "descartado";
      registrarEventoItem(it, "item_descartado", { responsavel: responsavel, observacao: just });
    } else if (tipo === "descricao_registrada") {
      var escopo = document.getElementById("evEscopo").value;
      var texto = document.getElementById("evTexto").value;
      if (escopo === "arquivo") {
        var arqId2 = document.getElementById("evArquivo").value;
        var arq2 = it.arquivos.find(function (a) { return a.id === arqId2; });
        registrarEventoArquivo(arq2, "descricao_registrada", { responsavel: responsavel, observacao: texto || observacao });
      } else {
        registrarEventoItem(it, "descricao_registrada", { responsavel: responsavel, observacao: texto || observacao });
      }
    } else if (tipo === "conferencia_lacre") {
      var condicaoLacre = document.getElementById("evCondicaoLacre").value;
      it.proveniencia.elementoFisico.condicaoLacre = condicaoLacre;
      registrarEventoItem(it, "conferencia_lacre", { responsavel: responsavel, resultado: condicaoLacre, observacao: observacao });
      recalcularAgregadoItem(it);
    }
    UI.modal = null;
    persistir().then(render);
    toast("Evento registrado.", "success");
  },

  conferirArquivo: async function (itemId, arquivoId) {
    var it = findItem(itemId);
    var a = it.arquivos.find(function (x) { return x.id === arquivoId; });
    var input = document.getElementById("conf_" + arquivoId);
    var file = input.files[0];
    if (!file) { toast("Selecione um arquivo para conferir.", "danger"); return; }
    var hashRecalculado = await hashFile(file);
    var referencia = referenciaHash(it, a);
    var resultado = referencia && referencia !== "—" ? (hashRecalculado.toLowerCase() === referencia.toLowerCase() ? "confere" : "diverge") : "nao_aplicavel";
    a.resultadoComparacao = resultado;
    registrarEventoArquivo(a, "conferencia_arquivo", { responsavel: "", resultado: resultado, observacao: resultado === "diverge" ? "Divergência encontrada na conferência — ver princípio do prejuízo." : "" });
    persistir().then(render);
    if (resultado === "diverge") { toast("Divergência encontrada em " + (a.descricao || a.nomeArquivo), "danger"); }
    else toast("Arquivo conferido: " + RESULTADO[resultado], "success");
  },
  concluirConferenciaItem: function (itemId) {
    var it = findItem(itemId);
    recalcularAgregadoItem(it);
    registrarEventoItem(it, "conferencia_rodada", { resultado: it.resultadoAgregado });
    persistir().then(render);
    var msg = it.resultadoAgregado === "diverge" ? "Conferência concluída com divergência — " + it.titulo : "Conferência concluída.";
    toast(msg, it.resultadoAgregado === "diverge" ? "danger" : "success");
    if (it.resultadoAgregado === "diverge") {
      setTimeout(function () {
        var wrap = document.querySelector(".vdc-toast-wrap");
        var el = document.createElement("div");
        el.className = "vdc-toast";
        el.innerHTML = CATALOGO.dicas.dica_prejuizo;
        wrap.appendChild(el);
        setTimeout(function () { el.remove(); }, 7000);
      }, 300);
    }
  }
};

/* ============================================================
   Bootstrap
   ============================================================ */
document.addEventListener("DOMContentLoaded", function () {
  var saved = carregarLocal();
  if (saved) { DB.dossie = migrarDossie(saved); UI.view = "processo"; }
  render();
});

})();
