#!/usr/bin/env python3
"""
SigPlan injection script - adapts bundled HTML to multiuser system
"""
import json
import re

# Read source
print("Reading source file...")
with open('/root/.claude/uploads/b5099e84-d270-589a-afd0-502f259ecc59/360a8cf5-Sistema_de_Gerenciamento_de_Planos_de_Trabalho__Dproc1.html', encoding='utf-8') as f:
    outer_content = f.read()

# Extract the template JSON to get actual HTML
template_marker = '<script type="__bundler/template">'
template_start = outer_content.find(template_marker)
template_content_start = template_start + len(template_marker)
template_end = outer_content.find('</script>', template_content_start)

template_json = outer_content[template_content_start:template_end].strip()
actual_html = json.loads(template_json)
print(f"Actual HTML size: {len(actual_html)} chars")

# ─────────────────────────────────────────────────────────────────────
# 1. Add .oculto CSS class to <style> (before </style>)
# ─────────────────────────────────────────────────────────────────────
oculto_css = "\n.oculto { display: none !important; }\n"
# Find the last </style> before </head>
head_end = actual_html.find('</head>')
last_style_end = actual_html.rfind('</style>', 0, head_end)
if last_style_end >= 0:
    actual_html = actual_html[:last_style_end] + oculto_css + actual_html[last_style_end:]
    print("Added .oculto CSS")
    # Recalculate head position
    head_end = actual_html.find('</head>')

# ─────────────────────────────────────────────────────────────────────
# 2. Add MSAL script before </head>
# ─────────────────────────────────────────────────────────────────────
msal_script = """
  <!-- Microsoft Authentication Library -->
  <script src="https://alcdn.msauth.net/browser/2.38.3/js/msal-browser.min.js"></script>
"""
actual_html = actual_html[:head_end] + msal_script + actual_html[head_end:]
print("Added MSAL script tag")

# ─────────────────────────────────────────────────────────────────────
# 3. Modify the landing screen HTML
#    - Remove or hide the "Carregar Plano" button
#    - Keep "Novo Plano de Trabalho" but note it's now handled by SigPlan
# ─────────────────────────────────────────────────────────────────────
# We'll just add a note - the rendering will be handled by JS
# The file-input-json for loading is still there but the landing card buttons
# will be replaced by the JS-driven tela-comissao-inicio screen

# ─────────────────────────────────────────────────────────────────────
# 4. Add all new JavaScript before </script> of the main script
# ─────────────────────────────────────────────────────────────────────
# Find the main script tag in actual_html
script_tag_pos = actual_html.find('<script>\n// ════')
if script_tag_pos < 0:
    script_tag_pos = actual_html.rfind('<script>')
print(f"Main script tag at: {script_tag_pos}")

# Find the end of the main script
script_end_pos = actual_html.find('</script>', script_tag_pos)
print(f"Main script end at: {script_end_pos}")

# The new JS code to inject
new_js_code = r"""

// ════════════════════════════════════════
//   CONFIGURAÇÃO SIGPLAN
// ════════════════════════════════════════

const MODO_DEV = true; // Mudar para false antes de publicar em produção

const SIGPLAN_CONFIG = {
  clientId: "AGUARDANDO_TI",
  tenantId: "AGUARDANDO_TI",
  sharePointSiteUrl: "https://rfbgov.sharepoint.com/sites/Gabinete/Coger",
  bibliotecaNome: "SigPlan"
};

const msalConfig = {
  auth: {
    clientId: SIGPLAN_CONFIG.clientId,
    authority: `https://login.microsoftonline.com/${SIGPLAN_CONFIG.tenantId}`,
    redirectUri: window.location.origin + window.location.pathname
  },
  cache: { cacheLocation: "sessionStorage", storeAuthStateInCookie: false }
};

const GRAPH_SCOPES = ["User.Read", "Sites.ReadWrite.All"];

let usuarioAtual = { nome: null, email: null, perfil: null, token: null };
let sharePointIds = { siteId: null, driveId: null };

const PERFIS = {
  COMISSAO: "comissao",
  GESTOR_APROVADOR: "gestor-aprovador",
  GESTOR_CONSULTA: "gestor-consulta",
  ADMINISTRADOR: "administrador"
};

const STATUS = {
  RASCUNHO: "Rascunho",
  AGUARDANDO: "Aguardando Aprovação",
  APROVADO: "Aprovado",
  DEVOLVIDO: "Devolvido",
  REVISAO: "Revisão Solicitada"
};

// ════════════════════════════════════════
//   MODO DEV — DADOS FICTÍCIOS
// ════════════════════════════════════════

const DEV_MOCK = {
  usuarioLogado: null,
  usuarios: [
    { email: "admin@rfb.gov.br", nome: "Administrador Teste", perfil: "administrador", ativo: true, cadastradoEm: "2026-01-01T00:00:00Z" },
    { email: "gestor.aprovador@rfb.gov.br", nome: "Gestor Aprovador Teste", perfil: "gestor-aprovador", ativo: true, cadastradoEm: "2026-01-01T00:00:00Z" },
    { email: "gestor.consulta@rfb.gov.br", nome: "Gestor Consulta Teste", perfil: "gestor-consulta", ativo: true, cadastradoEm: "2026-01-01T00:00:00Z" },
    { email: "comissao1@rfb.gov.br", nome: "Membro Comissão 1", perfil: "comissao", ativo: true, cadastradoEm: "2026-01-01T00:00:00Z" },
    { email: "comissao2@rfb.gov.br", nome: "Membro Comissão 2", perfil: "comissao", ativo: true, cadastradoEm: "2026-01-01T00:00:00Z" }
  ],
  processos: [
    { numero: "10830.720001/2026-01", tipo: "PAD", membros: ["comissao1@rfb.gov.br", "comissao2@rfb.gov.br"], cadastradoEm: "2026-01-10T10:00:00Z", cadastradoPor: "admin@rfb.gov.br" },
    { numero: "10830.720002/2026-02", tipo: "PAR", membros: ["comissao1@rfb.gov.br"], cadastradoEm: "2026-02-15T10:00:00Z", cadastradoPor: "admin@rfb.gov.br" }
  ],
  planos: {
    "10830.720001/2026-01": {
      _sigplan: { versao: "2.0", status: "Aguardando Aprovação", numeroProcesso: "10830.720001/2026-01", tipoProcesso: "PAD", criadoPor: "comissao1@rfb.gov.br", criadoEm: "2026-06-01T10:00:00Z", atualizadoPor: "comissao1@rfb.gov.br", atualizadoEm: "2026-06-08T14:00:00Z", aprovadoPor: null, aprovadoEm: null, comentarioGestor: null, justificativaRevisao: null, versaoNumero: 1 },
      dados: {}
    },
    "10830.720002/2026-02": {
      _sigplan: { versao: "2.0", status: "Devolvido", numeroProcesso: "10830.720002/2026-02", tipoProcesso: "PAR", criadoPor: "comissao1@rfb.gov.br", criadoEm: "2026-05-20T10:00:00Z", atualizadoPor: "gestor.aprovador@rfb.gov.br", atualizadoEm: "2026-06-05T16:30:00Z", aprovadoPor: null, aprovadoEm: null, comentarioGestor: "Favor completar a fase de instrução.", justificativaRevisao: null, versaoNumero: 1 },
      dados: {}
    }
  }
};

function exibirTelaLoginDev() {
  const overlay = document.createElement("div");
  overlay.id = "dev-login-overlay";
  overlay.style.cssText = `
    position:fixed; top:0; left:0; width:100%; height:100%;
    background:rgba(0,0,0,0.85); z-index:99999; display:flex;
    align-items:center; justify-content:center; font-family:sans-serif;
  `;
  overlay.innerHTML = `
    <div style="background:#fff; padding:40px; border-radius:12px; width:420px; box-shadow:0 8px 32px rgba(0,0,0,0.3);">
      <div style="text-align:center; margin-bottom:24px;">
        <h2 style="margin:0; color:#1a1a2e;">SigPlan</h2>
        <p style="margin:8px 0 0; color:#888; font-size:13px;">Sistema de Planos de Trabalho</p>
        <div style="display:inline-block; margin-top:10px; padding:4px 12px; background:#fff3cd; border:1px solid #ffc107; border-radius:20px; font-size:12px; color:#856404;">
          ⚠ MODO DESENVOLVIMENTO — dados fictícios
        </div>
      </div>
      <label style="display:block; margin-bottom:8px; font-weight:600; color:#333; font-size:14px;">Selecione o usuário para simular:</label>
      <select id="dev-user-select" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; font-size:14px; margin-bottom:20px;">
        <option value="">-- Selecione --</option>
        <option value="admin@rfb.gov.br">Administrador Teste (admin@rfb.gov.br)</option>
        <option value="gestor.aprovador@rfb.gov.br">Gestor Aprovador (gestor.aprovador@rfb.gov.br)</option>
        <option value="gestor.consulta@rfb.gov.br">Gestor Consulta (gestor.consulta@rfb.gov.br)</option>
        <option value="comissao1@rfb.gov.br">Membro Comissão 1 (comissao1@rfb.gov.br)</option>
        <option value="comissao2@rfb.gov.br">Membro Comissão 2 (comissao2@rfb.gov.br)</option>
      </select>
      <button id="dev-login-btn" style="width:100%; padding:12px; background:#0078d4; color:#fff; border:none; border-radius:6px; font-size:15px; font-weight:600; cursor:pointer;">
        Entrar
      </button>
      <p style="margin-top:16px; font-size:12px; color:#aaa; text-align:center;">
        Processos disponíveis: 10830.720001/2026-01 (PAD) · 10830.720002/2026-02 (PAR)
      </p>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById("dev-login-btn").addEventListener("click", () => {
    const email = document.getElementById("dev-user-select").value;
    if (!email) { alert("Selecione um usuário."); return; }
    const usuario = DEV_MOCK.usuarios.find(u => u.email === email);
    if (!usuario) { alert("Usuário não encontrado."); return; }
    DEV_MOCK.usuarioLogado = usuario;
    usuarioAtual.email = usuario.email;
    usuarioAtual.nome = usuario.nome;
    usuarioAtual.perfil = usuario.perfil;
    usuarioAtual.token = "dev-token-mock";
    overlay.remove();
    roteiarPorPerfil();
  });
}

function devCarregarUsuarios() {
  return { _sigplan_config: true, usuarios: DEV_MOCK.usuarios };
}
function devSalvarUsuarios(dados) {
  DEV_MOCK.usuarios = dados.usuarios;
}
function devCarregarProcessos() {
  return { _sigplan_config: true, processos: DEV_MOCK.processos };
}
function devSalvarProcessos(dados) {
  DEV_MOCK.processos = dados.processos;
}
function devCarregarPlano(numero) {
  return DEV_MOCK.planos[numero] || null;
}
function devSalvarPlano(numero, payload) {
  DEV_MOCK.planos[numero] = payload;
}
function devListarPlanos() {
  return Object.values(DEV_MOCK.planos).map(p => p._sigplan);
}

// ════════════════════════════════════════
//   AUTENTICAÇÃO SIGPLAN
// ════════════════════════════════════════

async function inicializarSigPlan() {
  if (MODO_DEV) {
    exibirTelaLoginDev();
    return;
  }
  try {
    exibirLoader(true, "Verificando autenticação...");
    const msalInstance = new msal.PublicClientApplication(msalConfig);
    window._msalInstance = msalInstance;
    await msalInstance.handleRedirectPromise();
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length === 0) {
      await msalInstance.loginRedirect({ scopes: GRAPH_SCOPES });
      return;
    }
    const tokenResponse = await msalInstance.acquireTokenSilent({ scopes: GRAPH_SCOPES, account: accounts[0] });
    usuarioAtual.token = tokenResponse.accessToken;
    await carregarDadosUsuario();
  } catch (erro) {
    if (erro.name === "InteractionRequiredAuthError") {
      await window._msalInstance.acquireTokenRedirect({ scopes: GRAPH_SCOPES });
    } else {
      exibirErroFatal("Falha na autenticação. Recarregue a página.");
    }
  } finally {
    exibirLoader(false);
  }
}

async function carregarDadosUsuario() {
  exibirLoader(true, "Identificando usuário...");
  const dadosMicrosoft = await chamarGraphAPI("https://graph.microsoft.com/v1.0/me?$select=displayName,mail,userPrincipalName");
  usuarioAtual.nome = dadosMicrosoft.displayName;
  usuarioAtual.email = dadosMicrosoft.mail || dadosMicrosoft.userPrincipalName;
  await obterIdsSharePoint();
  const cadastro = await obterCadastroUsuario(usuarioAtual.email);
  if (!cadastro) {
    exibirErroFatal(`Seu usuário (${usuarioAtual.email}) não está cadastrado no SigPlan. Entre em contato com o administrador do sistema.`);
    return;
  }
  usuarioAtual.perfil = cadastro.perfil;
  exibirLoader(false);
  roteiarPorPerfil();
}

function roteiarPorPerfil() {
  switch (usuarioAtual.perfil) {
    case PERFIS.ADMINISTRADOR: renderizarPainelAdministrador(); break;
    case PERFIS.GESTOR_APROVADOR:
    case PERFIS.GESTOR_CONSULTA: renderizarPainelGestor(); break;
    case PERFIS.COMISSAO: renderizarTelaComissao(); break;
    default: exibirErroFatal("Perfil de usuário não reconhecido.");
  }
}

async function chamarGraphAPI(url, metodo = "GET", corpo = null) {
  if (MODO_DEV) throw new Error("Graph API não disponível em MODO_DEV");
  const msalInstance = window._msalInstance;
  if (msalInstance) {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      try {
        const tokenResponse = await msalInstance.acquireTokenSilent({ scopes: GRAPH_SCOPES, account: accounts[0] });
        usuarioAtual.token = tokenResponse.accessToken;
      } catch (e) { /* usa token atual */ }
    }
  }
  const opcoes = {
    method: metodo,
    headers: { "Authorization": `Bearer ${usuarioAtual.token}`, "Content-Type": "application/json" }
  };
  if (corpo !== null) {
    opcoes.body = typeof corpo === "string" ? corpo : JSON.stringify(corpo);
    if (typeof corpo === "string") opcoes.headers["Content-Type"] = "text/plain";
  }
  const resp = await fetch(url, opcoes);
  if (resp.status === 204) return null;
  if (!resp.ok) {
    const erro = await resp.json().catch(() => ({}));
    throw new Error(`Graph API ${resp.status}: ${erro.error?.message || resp.statusText}`);
  }
  return resp.json();
}

async function obterIdsSharePoint() {
  if (MODO_DEV || sharePointIds.siteId) return;
  const site = await chamarGraphAPI(`https://graph.microsoft.com/v1.0/sites/rfbgov.sharepoint.com:/sites/Gabinete/Coger`);
  sharePointIds.siteId = site.id;
  const drives = await chamarGraphAPI(`https://graph.microsoft.com/v1.0/sites/${sharePointIds.siteId}/drives`);
  const biblioteca = drives.value.find(d => d.name === SIGPLAN_CONFIG.bibliotecaNome);
  if (!biblioteca) throw new Error(`Biblioteca "${SIGPLAN_CONFIG.bibliotecaNome}" não encontrada no SharePoint.`);
  sharePointIds.driveId = biblioteca.id;
}

// ════════════════════════════════════════
//   GESTÃO DE USUÁRIOS
// ════════════════════════════════════════

async function carregarUsuarios() {
  if (MODO_DEV) return devCarregarUsuarios();
  try {
    const resp = await fetch(
      `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root:/usuarios.json:/content`,
      { headers: { "Authorization": `Bearer ${usuarioAtual.token}` } }
    );
    if (resp.status === 404) return { usuarios: [] };
    return await resp.json();
  } catch { return { usuarios: [] }; }
}

async function salvarUsuarios(dadosUsuarios) {
  const payload = { ...dadosUsuarios, atualizadoEm: new Date().toISOString(), atualizadoPor: usuarioAtual.email };
  if (MODO_DEV) { devSalvarUsuarios(payload); return; }
  await chamarGraphAPI(
    `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root:/usuarios.json:/content`,
    "PUT", JSON.stringify(payload, null, 2)
  );
}

async function obterCadastroUsuario(email) {
  const dados = await carregarUsuarios();
  return dados.usuarios.find(u => u.email === email && u.ativo !== false) || null;
}

async function adicionarUsuario(email, nome, perfil) {
  if (!Object.values(PERFIS).includes(perfil)) throw new Error(`Perfil inválido: ${perfil}`);
  const dados = await carregarUsuarios();
  if (dados.usuarios.find(u => u.email === email)) throw new Error(`Usuário ${email} já está cadastrado.`);
  dados.usuarios.push({ email, nome, perfil, ativo: true, cadastradoEm: new Date().toISOString() });
  await salvarUsuarios(dados);
}

async function alterarPerfilUsuario(email, novoPerfil) {
  const dados = await carregarUsuarios();
  const usuario = dados.usuarios.find(u => u.email === email);
  if (!usuario) throw new Error(`Usuário ${email} não encontrado.`);
  if (usuario.perfil === PERFIS.ADMINISTRADOR) {
    const admins = dados.usuarios.filter(u => u.perfil === PERFIS.ADMINISTRADOR && u.ativo);
    if (admins.length <= 1 && novoPerfil !== PERFIS.ADMINISTRADOR)
      throw new Error("Não é possível remover o último administrador do sistema.");
  }
  usuario.perfil = novoPerfil;
  await salvarUsuarios(dados);
}

async function desativarUsuario(email) {
  const dados = await carregarUsuarios();
  const usuario = dados.usuarios.find(u => u.email === email);
  if (!usuario) throw new Error(`Usuário ${email} não encontrado.`);
  const admins = dados.usuarios.filter(u => u.perfil === PERFIS.ADMINISTRADOR && u.ativo);
  if (usuario.perfil === PERFIS.ADMINISTRADOR && admins.length <= 1)
    throw new Error("Não é possível desativar o último administrador do sistema.");
  usuario.ativo = false;
  await salvarUsuarios(dados);
}

// ════════════════════════════════════════
//   GESTÃO DE PROCESSOS
// ════════════════════════════════════════

async function carregarProcessos() {
  if (MODO_DEV) return devCarregarProcessos();
  try {
    const resp = await fetch(
      `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root:/processos.json:/content`,
      { headers: { "Authorization": `Bearer ${usuarioAtual.token}` } }
    );
    if (resp.status === 404) return { processos: [] };
    return await resp.json();
  } catch { return { processos: [] }; }
}

async function salvarProcessos(dadosProcessos) {
  const payload = { ...dadosProcessos, atualizadoEm: new Date().toISOString() };
  if (MODO_DEV) { devSalvarProcessos(payload); return; }
  await chamarGraphAPI(
    `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root:/processos.json:/content`,
    "PUT", JSON.stringify(payload, null, 2)
  );
}

async function cadastrarProcesso(numero, tipo, membros) {
  const dados = await carregarProcessos();
  if (dados.processos.find(p => p.numero === numero)) throw new Error(`Processo ${numero} já está cadastrado.`);
  dados.processos.push({ numero, tipo, membros, cadastradoEm: new Date().toISOString(), cadastradoPor: usuarioAtual.email });
  await salvarProcessos(dados);
}

async function atualizarMembrosProcesso(numero, novosMembros) {
  const dados = await carregarProcessos();
  const processo = dados.processos.find(p => p.numero === numero);
  if (!processo) throw new Error(`Processo ${numero} não encontrado.`);
  processo.membros = novosMembros;
  processo.atualizadoEm = new Date().toISOString();
  processo.atualizadoPor = usuarioAtual.email;
  await salvarProcessos(dados);
}

async function obterProcessosDoUsuario(email) {
  const dados = await carregarProcessos();
  return dados.processos.filter(p => p.membros.includes(email));
}

async function verificarAcessoAoProcesso(email, numero) {
  const dados = await carregarProcessos();
  const processo = dados.processos.find(p => p.numero === numero);
  return processo?.membros.includes(email) || false;
}

// ════════════════════════════════════════
//   PERSISTÊNCIA DE PLANOS (SHAREPOINT)
// ════════════════════════════════════════

function montarPayloadPlano(dadosPlano, status, infoExtra = {}) {
  return {
    _sigplan: {
      versao: "2.0",
      status,
      numeroProcesso: dadosPlano.cabecalho?.numero || dadosPlano['f-num'] || dadosPlano.numero || "",
      tipoProcesso: dadosPlano.tipo || "",
      criadoPor: infoExtra.criadoPor || usuarioAtual.email,
      criadoEm: infoExtra.criadoEm || new Date().toISOString(),
      atualizadoPor: usuarioAtual.email,
      atualizadoEm: new Date().toISOString(),
      aprovadoPor: infoExtra.aprovadoPor || null,
      aprovadoEm: infoExtra.aprovadoEm || null,
      comentarioGestor: infoExtra.comentarioGestor || null,
      justificativaRevisao: infoExtra.justificativaRevisao || null,
      versaoNumero: infoExtra.versaoNumero || 1
    },
    dados: dadosPlano
  };
}

function gerarNomeArquivo(numeroProcesso) {
  return `plano_${numeroProcesso.replace(/[^a-zA-Z0-9\-_]/g, "_")}.json`;
}

async function salvarPlano(dadosPlano, status, infoExtra = {}) {
  const numero = dadosPlano.cabecalho?.numero || dadosPlano['f-num'] || dadosPlano.numero || "";
  const payload = montarPayloadPlano(dadosPlano, status, infoExtra);
  if (MODO_DEV) {
    devSalvarPlano(numero, payload);
    exibirToast(`[DEV] Plano salvo localmente — ${status}`, "sucesso");
    return;
  }
  const nomeArquivo = gerarNomeArquivo(numero);
  await chamarGraphAPI(
    `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root:/${nomeArquivo}:/content`,
    "PUT", JSON.stringify(payload, null, 2)
  );
}

async function carregarPlanoPorNumero(numeroProcesso) {
  if (MODO_DEV) return devCarregarPlano(numeroProcesso);
  const nomeArquivo = gerarNomeArquivo(numeroProcesso);
  const resp = await fetch(
    `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root:/${nomeArquivo}:/content`,
    { headers: { "Authorization": `Bearer ${usuarioAtual.token}` } }
  );
  if (resp.status === 404) return null;
  if (!resp.ok) throw new Error(`Erro ao carregar plano: ${resp.status}`);
  const payload = await resp.json();
  if (!payload._sigplan || payload._sigplan.versao !== "2.0")
    throw new Error("Arquivo inválido. Não é um plano SigPlan.");
  return payload;
}

async function verificarPlanoExistente(numeroProcesso) {
  const payload = await carregarPlanoPorNumero(numeroProcesso);
  return payload !== null;
}

async function listarTodosOsPlanos() {
  if (MODO_DEV) return devListarPlanos();
  const itens = await chamarGraphAPI(`https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/root/children`);
  const arquivosPlanos = itens.value.filter(item => item.name.startsWith("plano_") && item.name.endsWith(".json"));
  const planos = await Promise.all(arquivosPlanos.map(async item => {
    try {
      const resp = await fetch(
        `https://graph.microsoft.com/v1.0/drives/${sharePointIds.driveId}/items/${item.id}/content`,
        { headers: { "Authorization": `Bearer ${usuarioAtual.token}` } }
      );
      const payload = await resp.json();
      return payload._sigplan;
    } catch { return null; }
  }));
  return planos.filter(Boolean);
}

// ════════════════════════════════════════
//   CICLO DE STATUS
// ════════════════════════════════════════

async function salvarRascunho() {
  await executarComFeedback(async () => {
    const dadosPlano = coletarDadosPlanoAtual();
    const payloadAtual = await carregarPlanoPorNumero(dadosPlano.cabecalho?.numero || dadosPlano['f-num'] || dadosPlano.numero);
    await salvarPlano(dadosPlano, STATUS.RASCUNHO, {
      criadoPor: payloadAtual?._sigplan?.criadoPor,
      criadoEm: payloadAtual?._sigplan?.criadoEm,
      versaoNumero: payloadAtual?._sigplan?.versaoNumero || 1
    });
  }, "Rascunho salvo com sucesso.", "Erro ao salvar rascunho");
}

async function enviarParaAprovacao() {
  const confirmado = await exibirModalConfirmacao("Enviar para Aprovação", "O plano será enviado ao gestor para aprovação. Deseja continuar?");
  if (!confirmado) return;
  await executarComFeedback(async () => {
    const dadosPlano = coletarDadosPlanoAtual();
    const numero = dadosPlano.cabecalho?.numero || dadosPlano['f-num'] || dadosPlano.numero;
    const payloadAtual = await carregarPlanoPorNumero(numero);
    await salvarPlano(dadosPlano, STATUS.AGUARDANDO, {
      criadoPor: payloadAtual?._sigplan?.criadoPor,
      criadoEm: payloadAtual?._sigplan?.criadoEm,
      versaoNumero: payloadAtual?._sigplan?.versaoNumero || 1
    });
    bloquearEdicao(STATUS.AGUARDANDO);
  }, "Plano enviado para aprovação.", "Erro ao enviar plano");
}

async function solicitarRevisao(justificativa) {
  if (!justificativa || justificativa.trim().length < 10) {
    exibirToast("Informe uma justificativa com pelo menos 10 caracteres.", "erro");
    return;
  }
  await executarComFeedback(async () => {
    const dadosPlano = coletarDadosPlanoAtual();
    const numero = dadosPlano.cabecalho?.numero || dadosPlano['f-num'] || dadosPlano.numero;
    const payloadAtual = await carregarPlanoPorNumero(numero);
    await salvarPlano(dadosPlano, STATUS.REVISAO, {
      criadoPor: payloadAtual._sigplan.criadoPor,
      criadoEm: payloadAtual._sigplan.criadoEm,
      aprovadoPor: payloadAtual._sigplan.aprovadoPor,
      aprovadoEm: payloadAtual._sigplan.aprovadoEm,
      justificativaRevisao: justificativa,
      versaoNumero: (payloadAtual._sigplan.versaoNumero || 1) + 1
    });
    desbloquearEdicao();
    fecharModalSigplan();
  }, "Revisão solicitada.", "Erro ao solicitar revisão");
}

async function aprovarPlano(numeroProcesso, comentario = "") {
  await executarComFeedback(async () => {
    const payload = await carregarPlanoPorNumero(numeroProcesso);
    await salvarPlano(payload.dados, STATUS.APROVADO, {
      criadoPor: payload._sigplan.criadoPor,
      criadoEm: payload._sigplan.criadoEm,
      aprovadoPor: usuarioAtual.nome,
      aprovadoEm: new Date().toISOString(),
      comentarioGestor: comentario,
      versaoNumero: payload._sigplan.versaoNumero
    });
    fecharModalSigplan();
    await renderizarPainelGestor();
  }, `Processo ${numeroProcesso} aprovado.`, "Erro ao aprovar plano");
}

async function devolverPlano(numeroProcesso, comentario) {
  if (!comentario || comentario.trim().length < 10) {
    exibirToast("Informe o motivo da devolução (mínimo 10 caracteres).", "erro");
    return;
  }
  await executarComFeedback(async () => {
    const payload = await carregarPlanoPorNumero(numeroProcesso);
    await salvarPlano(payload.dados, STATUS.DEVOLVIDO, {
      criadoPor: payload._sigplan.criadoPor,
      criadoEm: payload._sigplan.criadoEm,
      comentarioGestor: comentario,
      versaoNumero: payload._sigplan.versaoNumero
    });
    fecharModalSigplan();
    await renderizarPainelGestor();
  }, `Processo ${numeroProcesso} devolvido para a comissão.`, "Erro ao devolver plano");
}

// ════════════════════════════════════════
//   RENDERIZAÇÃO — TELA COMISSÃO
// ════════════════════════════════════════

function renderizarTelaComissao() {
  document.getElementById("tela-gestor")?.classList.add("oculto");
  document.getElementById("tela-admin")?.classList.add("oculto");
  // Hide original landing
  const telaLanding = document.getElementById("tela-landing");
  if (telaLanding) telaLanding.style.display = "none";

  let telaComissao = document.getElementById("tela-comissao-inicio");
  if (!telaComissao) {
    telaComissao = document.createElement("div");
    telaComissao.id = "tela-comissao-inicio";
    document.body.appendChild(telaComissao);
  }
  telaComissao.classList.remove("oculto");
  telaComissao.innerHTML = `
    <div id="barra-usuario" style="background:#0078d4;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:16px;font-family:sans-serif;">
      <strong>SigPlan</strong>
      <span style="flex:1">${usuarioAtual.nome}</span>
      <span style="background:rgba(255,255,255,0.2);padding:4px 10px;border-radius:12px;font-size:12px;">Comissão</span>
      <button onclick="sairSigplan()" style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff;padding:6px 14px;border-radius:6px;cursor:pointer;">Sair</button>
    </div>
    <div style="max-width:700px;margin:60px auto;font-family:sans-serif;padding:0 20px;">
      <h2 style="text-align:center;color:#1a1a2e;margin-bottom:40px;">Planos de Trabalho</h2>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
        <div style="border:1px solid #e0e0e0;border-radius:12px;padding:28px;text-align:center;background:#f8f9ff;">
          <h3 style="margin:0 0 12px;color:#0078d4;">Novo Plano de Trabalho</h3>
          <p style="color:#666;font-size:14px;margin:0 0 20px;">Iniciar o registro de um novo processo.</p>
          <button onclick="iniciarNovoPlano()" style="background:#0078d4;color:#fff;border:none;padding:10px 24px;border-radius:6px;cursor:pointer;font-size:14px;">Iniciar</button>
        </div>
        <div style="border:1px solid #e0e0e0;border-radius:12px;padding:28px;text-align:center;background:#f8f9ff;">
          <h3 style="margin:0 0 12px;color:#0078d4;">Retomar Plano Existente</h3>
          <p style="color:#666;font-size:14px;margin:0 0 12px;">Buscar pelo número do processo.</p>
          <input type="text" id="input-busca-processo" placeholder="Ex: 10830.720001/2026-01" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;margin-bottom:12px;font-size:13px;">
          <button onclick="buscarPlanoExistente()" style="background:#0078d4;color:#fff;border:none;padding:10px 24px;border-radius:6px;cursor:pointer;font-size:14px;">Buscar</button>
        </div>
      </div>
      ${MODO_DEV ? `<div style="margin-top:32px;padding:16px;background:#fff3cd;border:1px solid #ffc107;border-radius:8px;font-size:13px;color:#856404;">
        <strong>MODO DEV ativo</strong> — Usuário: ${usuarioAtual.email}<br>
        Processos disponíveis: <em>10830.720001/2026-01</em> e <em>10830.720002/2026-02</em>
      </div>` : ""}
    </div>
  `;
}

async function iniciarNovoPlano() {
  document.getElementById("tela-comissao-inicio")?.classList.add("oculto");
  const telaLanding = document.getElementById("tela-landing");
  if (telaLanding) telaLanding.style.display = "none";
  const telaInicio = document.getElementById("tela-inicio");
  if (telaInicio) telaInicio.style.display = "flex";
  adicionarBotoesAcaoComissao();
}

async function buscarPlanoExistente(numero) {
  const numeroProcesso = numero || document.getElementById("input-busca-processo")?.value.trim();
  if (!numeroProcesso) { exibirToast("Informe o número do processo.", "erro"); return; }
  await executarComFeedback(async () => {
    const autorizado = await verificarAcessoAoProcesso(usuarioAtual.email, numeroProcesso);
    if (!autorizado) { exibirToast("Processo não encontrado ou você não tem acesso a ele.", "erro"); return; }
    const payload = await carregarPlanoPorNumero(numeroProcesso);
    if (!payload) { exibirToast("Nenhum plano encontrado para este número.", "info"); return; }
    document.getElementById("tela-comissao-inicio")?.classList.add("oculto");
    const telaLanding = document.getElementById("tela-landing");
    if (telaLanding) telaLanding.style.display = "none";
    const telaInicio = document.getElementById("tela-inicio");
    if (telaInicio) telaInicio.style.display = "flex";
    adicionarBotoesAcaoComissao();
    if (typeof carregarPlanoNaInterface === "function") carregarPlanoNaInterface(payload);
    aplicarEstadoDeStatus(payload._sigplan.status);
  }, "", "Erro ao buscar plano");
}

function adicionarBotoesAcaoComissao() {
  if (document.getElementById("sigplan-action-buttons")) return;
  const container = document.createElement("div");
  container.id = "sigplan-action-buttons";
  container.style.cssText = "position:fixed;bottom:20px;right:20px;display:flex;flex-direction:column;gap:10px;z-index:1000;";
  container.innerHTML = `
    <div id="badge-status" class="oculto" style="text-align:center;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600;"></div>
    <button class="btn-salvar-rascunho" onclick="salvarRascunho()" style="background:#0078d4;color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">↓ Salvar Rascunho</button>
    <button class="btn-enviar-aprovacao oculto" onclick="enviarParaAprovacao()" style="background:#28a745;color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">✓ Enviar para Aprovação</button>
    <button id="btn-solicitar-revisao" class="oculto" onclick="abrirModalRevisao()" style="background:#fd7e14;color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">✎ Solicitar Revisão</button>
  `;
  document.body.appendChild(container);
}

function abrirModalRevisao() {
  exibirModalSigplan({
    titulo: "Solicitar Revisão do Plano",
    conteudo: `
      <p>Informe o motivo pelo qual está solicitando revisão do plano aprovado:</p>
      <textarea id="justificativa-revisao" rows="4" style="width:100%;box-sizing:border-box;" placeholder="Justificativa (mínimo 10 caracteres)..."></textarea>
    `,
    botoes: [
      { texto: "Confirmar", classe: "btn-sucesso", acao: () => solicitarRevisao(document.getElementById("justificativa-revisao").value) },
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

// ════════════════════════════════════════
//   RENDERIZAÇÃO — PAINEL GESTOR
// ════════════════════════════════════════

async function renderizarPainelGestor() {
  document.getElementById("tela-comissao-inicio")?.classList.add("oculto");
  document.getElementById("tela-admin")?.classList.add("oculto");
  const telaLanding = document.getElementById("tela-landing");
  if (telaLanding) telaLanding.style.display = "none";
  const telaInicio = document.getElementById("tela-inicio");
  if (telaInicio) telaInicio.style.display = "none";

  let telaGestor = document.getElementById("tela-gestor");
  if (!telaGestor) {
    telaGestor = document.createElement("div");
    telaGestor.id = "tela-gestor";
    document.body.appendChild(telaGestor);
  }
  telaGestor.classList.remove("oculto");
  telaGestor.innerHTML = `
    <div style="background:#0078d4;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:16px;font-family:sans-serif;">
      <strong>SigPlan — Painel do Gestor</strong>
      <span style="flex:1"></span>
      <span id="nome-gestor-logado" style="font-size:14px;">${usuarioAtual.nome}</span>
      <span id="badge-perfil-gestor" style="background:rgba(255,255,255,0.2);padding:4px 10px;border-radius:12px;font-size:12px;">
        ${usuarioAtual.perfil === PERFIS.GESTOR_APROVADOR ? "Gestor Aprovador" : "Gestor Consulta"}
      </span>
      <button onclick="sairSigplan()" style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:#fff;padding:6px 14px;border-radius:6px;cursor:pointer;">Sair</button>
    </div>
    <div style="padding:24px;font-family:sans-serif;">
      <div id="filtros-gestor" style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
        <select id="filtro-status" style="padding:8px;border:1px solid #ddd;border-radius:6px;">
          <option value="">Todos os status</option>
          <option value="Aguardando Aprovação">Aguardando Aprovação</option>
          <option value="Revisão Solicitada">Revisão Solicitada</option>
          <option value="Aprovado">Aprovado</option>
          <option value="Devolvido">Devolvido</option>
          <option value="Rascunho">Rascunho</option>
        </select>
        <select id="filtro-tipo" style="padding:8px;border:1px solid #ddd;border-radius:6px;">
          <option value="">PAD e PAR</option>
          <option value="PAD">PAD</option>
          <option value="PAR">PAR</option>
        </select>
        <input type="text" id="filtro-numero" placeholder="Buscar por número..." style="padding:8px;border:1px solid #ddd;border-radius:6px;min-width:200px;">
        <button onclick="renderizarPainelGestor()" style="padding:8px 16px;background:#0078d4;color:#fff;border:none;border-radius:6px;cursor:pointer;">Atualizar</button>
      </div>
      <table id="tabela-planos" style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead>
          <tr style="background:#f5f5f5;">
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Nº do Processo</th>
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Tipo</th>
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Status</th>
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Atualizado por</th>
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Atualizado em</th>
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Versão</th>
            <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Ações</th>
          </tr>
        </thead>
        <tbody id="corpo-tabela-planos"></tbody>
      </table>
      ${MODO_DEV ? `<div style="margin-top:20px;padding:12px;background:#fff3cd;border:1px solid #ffc107;border-radius:6px;font-size:12px;color:#856404;">MODO DEV — dados fictícios em memória</div>` : ""}
    </div>
  `;

  exibirLoader(true, "Carregando planos...");
  let planos = await listarTodosOsPlanos();
  exibirLoader(false);

  const filtroStatus = document.getElementById("filtro-status")?.value || "";
  const filtroTipo = document.getElementById("filtro-tipo")?.value || "";
  const filtroNumero = document.getElementById("filtro-numero")?.value.toLowerCase() || "";
  if (filtroStatus) planos = planos.filter(p => p.status === filtroStatus);
  if (filtroTipo) planos = planos.filter(p => p.tipoProcesso === filtroTipo);
  if (filtroNumero) planos = planos.filter(p => p.numeroProcesso.toLowerCase().includes(filtroNumero));

  const prioridade = { [STATUS.REVISAO]: 0, [STATUS.AGUARDANDO]: 1, [STATUS.DEVOLVIDO]: 2, [STATUS.RASCUNHO]: 3, [STATUS.APROVADO]: 4 };
  planos.sort((a, b) => (prioridade[a.status] ?? 5) - (prioridade[b.status] ?? 5));

  const corStatus = {
    "Revisão Solicitada": { bg: "#fd7e14", text: "#fff" },
    "Aguardando Aprovação": { bg: "#f0ad4e", text: "#000" },
    "Devolvido": { bg: "#dc3545", text: "#fff" },
    "Rascunho": { bg: "#6c757d", text: "#fff" },
    "Aprovado": { bg: "#28a745", text: "#fff" }
  };

  const tbody = document.getElementById("corpo-tabela-planos");
  if (planos.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="padding:20px;text-align:center;color:#888;">Nenhum plano encontrado.</td></tr>`;
    return;
  }

  for (const plano of planos) {
    const tr = document.createElement("tr");
    const ehAprovador = usuarioAtual.perfil === PERFIS.GESTOR_APROVADOR || usuarioAtual.perfil === PERFIS.ADMINISTRADOR;
    const podeAgir = ehAprovador && [STATUS.AGUARDANDO, STATUS.REVISAO].includes(plano.status);
    const cor = corStatus[plano.status] || { bg: "#6c757d", text: "#fff" };
    tr.style.borderBottom = "1px solid #eee";
    tr.innerHTML = `
      <td style="padding:10px;">${plano.numeroProcesso}</td>
      <td style="padding:10px;">${plano.tipoProcesso}</td>
      <td style="padding:10px;"><span style="background:${cor.bg};color:${cor.text};padding:3px 10px;border-radius:12px;font-size:12px;">${plano.status}</span></td>
      <td style="padding:10px;">${plano.atualizadoPor}</td>
      <td style="padding:10px;">${new Date(plano.atualizadoEm).toLocaleDateString("pt-BR")}</td>
      <td style="padding:10px;">v${plano.versaoNumero}</td>
      <td style="padding:10px;">
        ${podeAgir ? `
          <button onclick="abrirModalAprovacao('${plano.numeroProcesso}')" style="background:#28a745;color:#fff;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;font-size:12px;margin-right:4px;">Aprovar</button>
          <button onclick="abrirModalDevolucao('${plano.numeroProcesso}')" style="background:#dc3545;color:#fff;border:none;padding:5px 10px;border-radius:4px;cursor:pointer;font-size:12px;">Devolver</button>
        ` : `<span style="color:#aaa;font-size:12px;">—</span>`}
      </td>
    `;
    tbody.appendChild(tr);
  }
}

async function abrirModalAprovacao(numeroProcesso) {
  const payload = await carregarPlanoPorNumero(numeroProcesso);
  const meta = payload._sigplan;
  exibirModalSigplan({
    titulo: `Aprovar — ${numeroProcesso}`,
    conteudo: `
      <p><strong>Tipo:</strong> ${meta.tipoProcesso}</p>
      <p><strong>Versão:</strong> v${meta.versaoNumero}</p>
      ${meta.justificativaRevisao ? `<p><strong>Justificativa de revisão:</strong> ${meta.justificativaRevisao}</p>` : ""}
      <label>Comentário (opcional):</label>
      <textarea id="comentario-aprovacao" rows="3" style="width:100%;box-sizing:border-box;margin-top:4px;"></textarea>
    `,
    botoes: [
      { texto: "Confirmar Aprovação", classe: "btn-sucesso", acao: () => aprovarPlano(numeroProcesso, document.getElementById("comentario-aprovacao").value) },
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

async function abrirModalDevolucao(numeroProcesso) {
  exibirModalSigplan({
    titulo: `Devolver — ${numeroProcesso}`,
    conteudo: `
      <label>Motivo da devolução (obrigatório):</label>
      <textarea id="comentario-devolucao" rows="4" style="width:100%;box-sizing:border-box;margin-top:4px;" placeholder="Descreva o que deve ser corrigido ou complementado..."></textarea>
    `,
    botoes: [
      { texto: "Confirmar Devolução", classe: "btn-perigo", acao: () => devolverPlano(numeroProcesso, document.getElementById("comentario-devolucao").value) },
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

// ════════════════════════════════════════
//   RENDERIZAÇÃO — PAINEL ADMINISTRADOR
// ════════════════════════════════════════

async function renderizarPainelAdministrador() {
  document.getElementById("tela-comissao-inicio")?.classList.add("oculto");
  document.getElementById("tela-gestor")?.classList.add("oculto");
  const telaLanding = document.getElementById("tela-landing");
  if (telaLanding) telaLanding.style.display = "none";
  const telaInicio = document.getElementById("tela-inicio");
  if (telaInicio) telaInicio.style.display = "none";

  let telaAdmin = document.getElementById("tela-admin");
  if (!telaAdmin) {
    telaAdmin = document.createElement("div");
    telaAdmin.id = "tela-admin";
    document.body.appendChild(telaAdmin);
  }
  telaAdmin.classList.remove("oculto");
  telaAdmin.innerHTML = `
    <div style="background:#1a1a2e;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:16px;font-family:sans-serif;">
      <strong>SigPlan — Administrador</strong>
      <span style="flex:1"></span>
      <span id="nome-admin-logado" style="font-size:14px;">${usuarioAtual.nome}</span>
      <span style="background:rgba(255,255,255,0.15);padding:4px 10px;border-radius:12px;font-size:12px;">Administrador</span>
      <button onclick="sairSigplan()" style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.3);color:#fff;padding:6px 14px;border-radius:6px;cursor:pointer;">Sair</button>
    </div>
    <div style="font-family:sans-serif;">
      <div style="display:flex;border-bottom:2px solid #e0e0e0;">
        <button onclick="mostrarAbaAdmin('usuarios')" id="aba-btn-usuarios" style="padding:14px 28px;background:#0078d4;color:#fff;border:none;cursor:pointer;font-size:14px;font-weight:600;">Usuários</button>
        <button onclick="mostrarAbaAdmin('processos')" id="aba-btn-processos" style="padding:14px 28px;background:#f5f5f5;border:none;cursor:pointer;font-size:14px;">Processos</button>
        <button onclick="mostrarAbaAdmin('planos')" id="aba-btn-planos" style="padding:14px 28px;background:#f5f5f5;border:none;cursor:pointer;font-size:14px;">Planos</button>
      </div>
      <div id="conteudo-aba-admin" style="padding:24px;"></div>
    </div>
    ${MODO_DEV ? `<div style="margin:0 24px 20px;padding:12px;background:#fff3cd;border:1px solid #ffc107;border-radius:6px;font-size:12px;color:#856404;">MODO DEV — dados fictícios em memória</div>` : ""}
  `;

  await carregarAbaUsuarios();
}

function mostrarAbaAdmin(aba) {
  ["usuarios","processos","planos"].forEach(a => {
    const btn = document.getElementById(`aba-btn-${a}`);
    if (btn) { btn.style.background = a === aba ? "#0078d4" : "#f5f5f5"; btn.style.color = a === aba ? "#fff" : "#333"; btn.style.fontWeight = a === aba ? "600" : "normal"; }
  });
  if (aba === "usuarios") carregarAbaUsuarios();
  else if (aba === "processos") carregarAbaProcessos();
  else if (aba === "planos") { usuarioAtual._adminVerPlanos = true; renderizarPainelGestor(); }
}

async function carregarAbaUsuarios() {
  const dados = await carregarUsuarios();
  const container = document.getElementById("conteudo-aba-admin");
  if (!container) return;
  container.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h3 style="margin:0;">Usuários Cadastrados</h3>
      <button onclick="abrirModalAdicionarUsuario()" style="background:#0078d4;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;">+ Adicionar Usuário</button>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <thead><tr style="background:#f5f5f5;">
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Nome</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">E-mail</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Perfil</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Status</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Ações</th>
      </tr></thead>
      <tbody>
        ${dados.usuarios.map(u => `
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:10px;">${u.nome}</td>
            <td style="padding:10px;">${u.email}</td>
            <td style="padding:10px;">${u.perfil}</td>
            <td style="padding:10px;"><span style="background:${u.ativo ? '#28a745' : '#6c757d'};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">${u.ativo ? 'Ativo' : 'Inativo'}</span></td>
            <td style="padding:10px;">
              <button onclick="abrirModalEditarPerfil('${u.email}')" style="background:#f0ad4e;color:#000;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;margin-right:4px;">Editar</button>
              ${u.ativo ? `<button onclick="confirmarDesativarUsuario('${u.email}')" style="background:#dc3545;color:#fff;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;">Desativar</button>` : ''}
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function carregarAbaProcessos() {
  const dados = await carregarProcessos();
  const container = document.getElementById("conteudo-aba-admin");
  if (!container) return;
  container.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h3 style="margin:0;">Processos Cadastrados</h3>
      <button onclick="abrirModalNovoProcesso()" style="background:#0078d4;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;">+ Novo Processo</button>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <thead><tr style="background:#f5f5f5;">
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Número</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Tipo</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Membros</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Cadastrado em</th>
        <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd;">Ações</th>
      </tr></thead>
      <tbody>
        ${dados.processos.map(p => `
          <tr style="border-bottom:1px solid #eee;">
            <td style="padding:10px;">${p.numero}</td>
            <td style="padding:10px;">${p.tipo}</td>
            <td style="padding:10px;font-size:12px;">${p.membros.join(", ")}</td>
            <td style="padding:10px;">${new Date(p.cadastradoEm).toLocaleDateString("pt-BR")}</td>
            <td style="padding:10px;">
              <button onclick="abrirModalEditarMembros('${p.numero}')" style="background:#f0ad4e;color:#000;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;">Editar Membros</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function abrirModalAdicionarUsuario() {
  exibirModalSigplan({
    titulo: "Adicionar Usuário",
    conteudo: `
      <div style="display:flex;flex-direction:column;gap:12px;">
        <div><label style="display:block;margin-bottom:4px;font-weight:600;">E-mail institucional</label>
        <input type="email" id="novo-usuario-email" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;"></div>
        <div><label style="display:block;margin-bottom:4px;font-weight:600;">Nome completo</label>
        <input type="text" id="novo-usuario-nome" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;"></div>
        <div><label style="display:block;margin-bottom:4px;font-weight:600;">Perfil</label>
        <select id="novo-usuario-perfil" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;">
          <option value="comissao">Comissão</option>
          <option value="gestor-aprovador">Gestor Aprovador</option>
          <option value="gestor-consulta">Gestor Consulta</option>
          <option value="administrador">Administrador</option>
        </select></div>
      </div>
    `,
    botoes: [
      { texto: "Adicionar", classe: "btn-sucesso", acao: async () => {
        const email = document.getElementById("novo-usuario-email").value.trim();
        const nome = document.getElementById("novo-usuario-nome").value.trim();
        const perfil = document.getElementById("novo-usuario-perfil").value;
        await executarComFeedback(async () => { await adicionarUsuario(email, nome, perfil); fecharModalSigplan(); await carregarAbaUsuarios(); }, "Usuário adicionado.", "Erro");
      }},
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

async function abrirModalEditarPerfil(email) {
  const dados = await carregarUsuarios();
  const usuario = dados.usuarios.find(u => u.email === email);
  exibirModalSigplan({
    titulo: `Editar Perfil — ${email}`,
    conteudo: `
      <label style="display:block;margin-bottom:8px;font-weight:600;">Novo perfil para ${usuario?.nome}:</label>
      <select id="edit-perfil-select" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;">
        <option value="comissao" ${usuario?.perfil==="comissao"?"selected":""}>Comissão</option>
        <option value="gestor-aprovador" ${usuario?.perfil==="gestor-aprovador"?"selected":""}>Gestor Aprovador</option>
        <option value="gestor-consulta" ${usuario?.perfil==="gestor-consulta"?"selected":""}>Gestor Consulta</option>
        <option value="administrador" ${usuario?.perfil==="administrador"?"selected":""}>Administrador</option>
      </select>
    `,
    botoes: [
      { texto: "Salvar", classe: "btn-sucesso", acao: async () => {
        const novoPerfil = document.getElementById("edit-perfil-select").value;
        await executarComFeedback(async () => { await alterarPerfilUsuario(email, novoPerfil); fecharModalSigplan(); await carregarAbaUsuarios(); }, "Perfil alterado.", "Erro");
      }},
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

async function confirmarDesativarUsuario(email) {
  const confirmado = await exibirModalConfirmacaoSigplan("Desativar Usuário", `Deseja desativar o acesso de ${email}?`);
  if (!confirmado) return;
  await executarComFeedback(async () => { await desativarUsuario(email); await carregarAbaUsuarios(); }, "Usuário desativado.", "Erro ao desativar");
}

async function abrirModalNovoProcesso() {
  exibirModalSigplan({
    titulo: "Cadastrar Novo Processo",
    conteudo: `
      <div style="display:flex;flex-direction:column;gap:12px;">
        <div><label style="display:block;margin-bottom:4px;font-weight:600;">Número do Processo</label>
        <input type="text" id="novo-processo-numero" placeholder="Ex: 10830.720003/2026-03" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;"></div>
        <div><label style="display:block;margin-bottom:4px;font-weight:600;">Tipo</label>
        <select id="novo-processo-tipo" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;">
          <option value="PAD">PAD</option><option value="PAR">PAR</option>
        </select></div>
        <div><label style="display:block;margin-bottom:4px;font-weight:600;">Membros (e-mails, um por linha)</label>
        <textarea id="novo-processo-membros" rows="4" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;" placeholder="membro1@rfb.gov.br&#10;membro2@rfb.gov.br"></textarea></div>
      </div>
    `,
    botoes: [
      { texto: "Cadastrar", classe: "btn-sucesso", acao: async () => {
        const numero = document.getElementById("novo-processo-numero").value.trim();
        const tipo = document.getElementById("novo-processo-tipo").value;
        const membros = document.getElementById("novo-processo-membros").value.split("\n").map(e => e.trim()).filter(Boolean);
        await executarComFeedback(async () => { await cadastrarProcesso(numero, tipo, membros); fecharModalSigplan(); await carregarAbaProcessos(); }, "Processo cadastrado.", "Erro");
      }},
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

async function abrirModalEditarMembros(numero) {
  const dados = await carregarProcessos();
  const processo = dados.processos.find(p => p.numero === numero);
  exibirModalSigplan({
    titulo: `Membros — ${numero}`,
    conteudo: `
      <label style="display:block;margin-bottom:8px;font-weight:600;">Membros (e-mails, um por linha):</label>
      <textarea id="edit-membros-lista" rows="5" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;">${processo?.membros.join("\n") || ""}</textarea>
    `,
    botoes: [
      { texto: "Salvar", classe: "btn-sucesso", acao: async () => {
        const membros = document.getElementById("edit-membros-lista").value.split("\n").map(e => e.trim()).filter(Boolean);
        await executarComFeedback(async () => { await atualizarMembrosProcesso(numero, membros); fecharModalSigplan(); await carregarAbaProcessos(); }, "Membros atualizados.", "Erro");
      }},
      { texto: "Cancelar", classe: "btn-secundario", acao: fecharModalSigplan }
    ]
  });
}

// ════════════════════════════════════════
//   ESTADO DO EDITOR
// ════════════════════════════════════════

function aplicarEstadoDeStatus(status) {
  atualizarBadgeStatus(status);
  const podeEditar = [STATUS.RASCUNHO, STATUS.DEVOLVIDO, STATUS.REVISAO].includes(status);
  if (podeEditar) desbloquearEdicao(); else bloquearEdicao(status);
}

function bloquearEdicao(status) {
  document.querySelectorAll("#tela-inicio input, #tela-inicio select, #tela-inicio textarea").forEach(el => { el.disabled = true; });
  document.querySelector(".btn-salvar-rascunho")?.classList.add("oculto");
  document.querySelector(".btn-enviar-aprovacao")?.classList.add("oculto");
  if (status === STATUS.APROVADO) document.getElementById("btn-solicitar-revisao")?.classList.remove("oculto");
}

function desbloquearEdicao() {
  document.querySelectorAll("#tela-inicio input, #tela-inicio select, #tela-inicio textarea").forEach(el => { el.disabled = false; });
  document.querySelector(".btn-salvar-rascunho")?.classList.remove("oculto");
  document.querySelector(".btn-enviar-aprovacao")?.classList.remove("oculto");
  document.getElementById("btn-solicitar-revisao")?.classList.add("oculto");
}

function atualizarBadgeStatus(status) {
  const cores = {
    [STATUS.RASCUNHO]: { bg: "#6c757d", text: "#fff" },
    [STATUS.AGUARDANDO]: { bg: "#f0ad4e", text: "#000" },
    [STATUS.APROVADO]: { bg: "#28a745", text: "#fff" },
    [STATUS.DEVOLVIDO]: { bg: "#dc3545", text: "#fff" },
    [STATUS.REVISAO]: { bg: "#fd7e14", text: "#fff" }
  };
  const badge = document.getElementById("badge-status");
  if (badge) {
    const cor = cores[status] || { bg: "#6c757d", text: "#fff" };
    badge.textContent = status;
    badge.style.backgroundColor = cor.bg;
    badge.style.color = cor.text;
    badge.classList.remove("oculto");
  }
}

// ════════════════════════════════════════
//   UTILITÁRIOS DE UI
// ════════════════════════════════════════

function exibirToast(mensagem, tipo) {
  tipo = tipo || "sucesso";
  const cores = { sucesso: "#28a745", erro: "#dc3545", info: "#0078d4" };
  const toastEl = document.createElement("div");
  toastEl.style.cssText = `position:fixed;bottom:80px;right:20px;background:${cores[tipo]||"#333"};color:#fff;padding:12px 20px;border-radius:8px;font-family:sans-serif;font-size:14px;z-index:99998;box-shadow:0 4px 12px rgba(0,0,0,0.3);max-width:350px;`;
  toastEl.textContent = mensagem;
  document.body.appendChild(toastEl);
  setTimeout(() => toastEl.remove(), 4000);
}

function exibirLoader(visivel, mensagem) {
  mensagem = mensagem || "Aguarde...";
  let overlay = document.getElementById("loader-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "loader-overlay";
    overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,255,255,0.8);z-index:99997;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:sans-serif;";
    overlay.innerHTML = `<div style="width:40px;height:40px;border:4px solid #e0e0e0;border-top-color:#0078d4;border-radius:50%;animation:spin 0.8s linear infinite;"></div><p id="loader-mensagem" style="margin-top:16px;color:#555;"></p>`;
    const style = document.createElement("style");
    style.textContent = "@keyframes spin{to{transform:rotate(360deg)}}";
    document.head.appendChild(style);
    document.body.appendChild(overlay);
  }
  const msgEl = document.getElementById("loader-mensagem");
  if (msgEl) msgEl.textContent = mensagem;
  overlay.style.display = visivel ? "flex" : "none";
}

async function executarComFeedback(operacao, mensagemSucesso, mensagemErro) {
  try {
    exibirLoader(true);
    await operacao();
    if (mensagemSucesso) exibirToast(mensagemSucesso, "sucesso");
  } catch (erro) {
    console.error(erro);
    exibirToast(`${mensagemErro}: ${erro.message}`, "erro");
  } finally {
    exibirLoader(false);
  }
}

function exibirModalSigplan(config) {
  fecharModalSigplan();
  const overlay = document.createElement("div");
  overlay.id = "sigplan-modal-overlay";
  overlay.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:99996;display:flex;align-items:center;justify-content:center;font-family:sans-serif;";
  const botoesBtns = (config.botoes || []).map((b, i) => {
    const bg = b.classe === "btn-sucesso" ? "#28a745" : b.classe === "btn-perigo" ? "#dc3545" : "#6c757d";
    return `<button data-acao="${i}" style="background:${bg};color:#fff;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;font-size:14px;">${b.texto}</button>`;
  }).join(" ");
  overlay.innerHTML = `
    <div style="background:#fff;padding:28px;border-radius:12px;width:500px;max-width:90vw;box-shadow:0 8px 32px rgba(0,0,0,0.3);">
      <h3 style="margin:0 0 16px;">${config.titulo}</h3>
      <div style="margin-bottom:20px;">${config.conteudo}</div>
      <div style="display:flex;gap:10px;justify-content:flex-end;">${botoesBtns}</div>
    </div>
  `;
  overlay.querySelectorAll("button[data-acao]").forEach(btn => {
    btn.addEventListener("click", () => config.botoes[parseInt(btn.dataset.acao)].acao());
  });
  document.body.appendChild(overlay);
}

function fecharModalSigplan() {
  document.getElementById("sigplan-modal-overlay")?.remove();
}

function exibirModalConfirmacaoSigplan(titulo, mensagem) {
  return new Promise(resolve => {
    exibirModalSigplan({
      titulo,
      conteudo: `<p>${mensagem}</p>`,
      botoes: [
        { texto: "Confirmar", classe: "btn-sucesso", acao: () => { fecharModalSigplan(); resolve(true); } },
        { texto: "Cancelar", classe: "btn-secundario", acao: () => { fecharModalSigplan(); resolve(false); } }
      ]
    });
  });
}

// Keep exibirModalConfirmacao as alias for backward compat
const exibirModalConfirmacao = exibirModalConfirmacaoSigplan;

function exibirErroFatal(mensagem) {
  exibirLoader(false);
  document.body.innerHTML = `
    <div style="text-align:center;padding:60px;font-family:sans-serif;">
      <h2>SigPlan</h2>
      <p style="color:#dc3545;">${mensagem}</p>
      <button onclick="location.reload()" style="padding:10px 24px;background:#0078d4;color:#fff;border:none;border-radius:6px;cursor:pointer;">Tentar novamente</button>
    </div>
  `;
}

function sairSigplan() {
  if (MODO_DEV) { location.reload(); return; }
  if (window._msalInstance) window._msalInstance.logout();
  else location.reload();
}

// Wrapper to get current plan data
function coletarDadosPlanoAtual() {
  if (typeof coletarCabecalho === "function") {
    const cab = coletarCabecalho();
    return { cabecalho: cab, numero: cab['f-num'] || '', tipo: typeof tipo !== 'undefined' ? tipo : '', fluxo: typeof fluxo !== 'undefined' ? fluxo : null };
  }
  if (typeof coletarDadosPlano === "function") return coletarDadosPlano();
  if (typeof serializarPlano === "function") return serializarPlano();
  const numero = document.querySelector("[name='numero'], #numero-processo, #f-num")?.value || "";
  return { cabecalho: { 'f-num': numero }, numero, tipo: typeof tipo !== 'undefined' ? tipo : '' };
}

// ════════════════════════════════════════
//   INICIALIZAÇÃO — chamar ao carregar
// ════════════════════════════════════════
// inicializarSigPlan() é chamado no DOMContentLoaded abaixo

"""

# Insert new JS right after the <script> opening tag of the main script
insert_pos = script_tag_pos + len('<script>')
actual_html = actual_html[:insert_pos] + new_js_code + actual_html[insert_pos:]
print("Injected new JavaScript code")

# Recalculate positions after insertion
script_end_pos = actual_html.rfind('</script>')
print(f"New script end at: {script_end_pos}")

# ─────────────────────────────────────────────────────────────────────
# 5. Modify DOMContentLoaded in the actual HTML to call inicializarSigPlan()
# ─────────────────────────────────────────────────────────────────────
# The landing already has its own initialization, we just need to add
# inicializarSigPlan() call after the bundler unpacks (or add a DOMContentLoaded)
# We'll add it at the end of the main script (before </script>)
init_call = """
// SigPlan initialization
document.addEventListener('DOMContentLoaded', function() {
  // Wait a tick for the rest of the script to be ready
  setTimeout(inicializarSigPlan, 0);
});
"""

# Insert before the last </script>
actual_html = actual_html[:script_end_pos] + init_call + actual_html[script_end_pos:]
print("Added inicializarSigPlan() DOMContentLoaded call")

# ─────────────────────────────────────────────────────────────────────
# 6. Re-serialize template and replace in outer HTML
# ─────────────────────────────────────────────────────────────────────
print("Re-serializing template...")
new_template_json = json.dumps(actual_html, ensure_ascii=False)
# CRITICAL: escape </script> inside the JSON string so it doesn't prematurely close
# the outer <script type="__bundler/template"> tag
# Use <\/script> which is safe in JSON strings and browsers parse correctly
new_template_json = new_template_json.replace('</script>', '<\\/script>')
print(f"</script> occurrences in template JSON after escaping: {new_template_json.count('</script>')}")

# Replace template in outer content
new_outer = (
    outer_content[:template_content_start] +
    "\n" + new_template_json + "\n" +
    outer_content[template_end:]
)

print(f"New outer content size: {len(new_outer)}")

with open('/home/user/desktop-tutorial/sigplan.html', 'w', encoding='utf-8') as f:
    f.write(new_outer)

print("Written to /home/user/desktop-tutorial/sigplan.html")
print("DONE!")
