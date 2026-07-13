// Screenshot automation for the Suíte COGER manual (Veritas, Nexo Coger, Oitiva 360).
// Run with: NODE_PATH=/opt/node22/lib/node_modules /opt/node22/bin/node manual/screenshot.js
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const OUT = path.join(ROOT, 'manual/assets/screenshots');
fs.mkdirSync(OUT, { recursive: true });

const FIXTURE = require(path.join(ROOT, 'fixtures/pad-ficticio-001.json'));

function fileUrl(p) { return 'file://' + p; }

async function fieldInput(page, labelText, selector = 'input, select, textarea') {
  return page.locator('.rfb-field', { hasText: labelText }).locator(selector).first();
}

async function shot(target, filePath, opts = {}) {
  await target.screenshot({ path: filePath, ...opts });
  const size = fs.statSync(filePath).size;
  console.log(`  -> ${path.basename(filePath)} (${size} bytes)`);
  if (size < 5000) console.warn(`  !! WARNING: ${path.basename(filePath)} is suspiciously small`);
}

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('console', (msg) => { if (msg.type() === 'error') console.log('  [console error]', msg.text()); });
  page.on('pageerror', (err) => console.log('  [pageerror]', err.message));
  page.on('dialog', async (dialog) => {
    console.log('  [dialog]', dialog.type(), dialog.message().slice(0, 200));
    await dialog.accept();
  });

  try {
    await runVeritas(page);
  } catch (e) { console.error('VERITAS FAILED:', e); }

  try {
    await runNexo(page);
  } catch (e) { console.error('NEXO FAILED:', e); }

  try {
    await runOitiva(page);
  } catch (e) { console.error('OITIVA FAILED:', e); }

  await browser.close();
}

/* ==================== VERITAS ==================== */
async function runVeritas(page) {
  console.log('=== Veritas ===');
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/veritas.html')));
  await page.getByRole('button', { name: '+ Novo dossiê' }).click();
  await page.waitForSelector('.rfb-card__header');

  // Fill processo número so screenshots look real.
  const numeroInput = page.locator('.rfb-field', { hasText: 'Nº do processo' }).locator('input').first();
  await numeroInput.fill(FIXTURE.processo.numero);
  await numeroInput.dispatchEvent('change');

  // Open wizard (criar item)
  await page.getByRole('button', { name: '+ Adicionar item' }).click();
  await page.waitForSelector('.vdc-wizard-body');

  // Etapa 1 - Identificação
  const titulo = await fieldInput(page, 'Título/descrição', 'input');
  await titulo.fill(FIXTURE.provaInicialVeritas.titulo);
  const categoria = await fieldInput(page, 'Categoria', 'select');
  await categoria.selectOption(FIXTURE.provaInicialVeritas.categoria);
  const folha = await fieldInput(page, 'Nº/folha nos autos', 'input');
  await folha.fill('fls. 12-15');
  const vinculo = await fieldInput(page, 'Vinculado à matriz de apuração', 'input');
  await vinculo.fill('Fato F1 — ' + FIXTURE.fatos[0].titulo);
  const sigilo = await fieldInput(page, 'Sigilo/classificação', 'select');
  await sigilo.selectOption(FIXTURE.provaInicialVeritas.sigilo);
  await page.waitForTimeout(200);

  await shot(page, path.join(OUT, 'veritas-wizard-identificacao.png'), { fullPage: true });

  // Advance to Etapa 2 - Proveniência
  await page.getByRole('button', { name: 'Avançar →' }).click();
  await page.waitForTimeout(150);
  // choose "gerado_internamente"
  await page.locator('input[name="proveniencia"][value=""], input[name="proveniencia"]').first(); // noop guard
  const provRadio = page.locator('label.radio-option', { hasText: 'A) Gerado internamente' }).locator('input[type=radio]');
  await provRadio.check({ force: true });
  await page.waitForTimeout(150);
  const quemColetou = await fieldInput(page, 'Quem coletou', 'input');
  await quemColetou.fill('Secretário(a) da comissão');
  const contexto = await fieldInput(page, 'Contexto da coleta', 'input');
  await contexto.fill('Consulta a sistema interno durante diligência');
  const local = await fieldInput(page, 'Local/situação', 'input');
  await local.fill('Unidade de Teste — sede');
  await page.waitForTimeout(150);

  // Crop screenshot on the card body (proveniência step)
  const provCard = page.locator('.rfb-card').first();
  await shot(provCard, path.join(OUT, 'veritas-cadeia-custodia.png'));

  // Advance to Etapa 3 - Arquivos, attach a dummy file
  await page.getByRole('button', { name: 'Avançar →' }).click();
  await page.waitForTimeout(150);
  const descArquivo = page.locator('#novoArquivoDescricao');
  if (await descArquivo.count()) await descArquivo.fill('Extrato financeiro fictício nº 001/2026');
  const dummyFile = path.join('/tmp', 'dummy-veritas.txt');
  fs.writeFileSync(dummyFile, FIXTURE.provaInicialVeritas.conteudoFicticio);
  const fileInput = page.locator('#novoArquivoInput');
  if (await fileInput.count()) {
    await fileInput.setInputFiles(dummyFile);
    await page.getByRole('button', { name: 'Calcular hash e adicionar' }).click();
    await page.waitForTimeout(300);
  }

  // Advance to Etapa 4 and save
  await page.getByRole('button', { name: 'Avançar →' }).click();
  await page.waitForTimeout(150);
  await page.getByRole('button', { name: 'Salvar item' }).click();
  await page.waitForTimeout(300);

  // Should now be back at Processo view with item listed
  await page.waitForSelector('.vdc-item-row', { timeout: 5000 }).catch(() => {});
  await shot(page, path.join(OUT, 'veritas-consulta-listagem.png'), { fullPage: true });
}

/* ==================== NEXO COGER ==================== */
async function runNexo(page) {
  console.log('=== Nexo Coger ===');
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/nexo-coger.html')));
  await page.waitForSelector('#btnMenu');

  // Nexo Coger now opens on the "Dados do Processo" gate (1ª etapa) when there's no saved draft —
  // it blocks the rest of the app until "Número do processo" is filled. Clear it here so the rest
  // of this script (which drives #btnMenu etc.) isn't blocked by the fixed overlay.
  const gate = page.locator('#gate');
  if (await gate.isVisible().catch(() => false)) {
    const gateNumero = page.locator('#gateCard .field', { hasText: 'Número do processo' }).locator('input').first();
    await gateNumero.fill(FIXTURE.processo.numero);
    await page.click('#gateBtnContinuar');
    await page.waitForTimeout(200);
  }

  // Use built-in seed scenario "Carregar exemplo" to get a full fato-prova-norma map quickly.
  await page.click('#btnMenu');
  await page.waitForSelector('#menu.open');
  await page.click('#menu button[data-act="exemplo"]');
  await page.waitForTimeout(400);

  await shot(page, path.join(OUT, 'nexo-mapa-fato-prova-norma.png'), { fullPage: true });

  // Papel do depoente: open "+ Prova", set tipo = testemunhal
  await page.click('#btnAddProva');
  await page.waitForSelector('.modal, [class*="modal"]', { timeout: 5000 }).catch(() => {});
  // locate tipo select (first select in the modal, labeled "Tipo")
  const tipoSelect = page.locator('.field:has(label:text("Tipo")) select, .field label:text-is("Tipo")').first();
  // Fallback generic approach: find any select whose options include 'testemunhal'
  const allSelects = page.locator('select');
  const count = await allSelects.count();
  let tipoSet = false;
  for (let i = 0; i < count; i++) {
    const sel = allSelects.nth(i);
    const hasOpt = await sel.locator('option[value="testemunhal"]').count();
    if (hasOpt) {
      await sel.selectOption('testemunhal');
      tipoSet = true;
      break;
    }
  }
  if (!tipoSet) console.warn('  !! could not find tipo de prova select');
  await page.waitForTimeout(200);
  // Fill título prova
  const provaTituloField = page.locator('.field', { hasText: 'Título' }).locator('input').first();
  if (await provaTituloField.count()) await provaTituloField.fill(FIXTURE.depoente.identificacao + ' — depoimento');
  const deponenteField = page.locator('.field', { hasText: 'Deponente' }).locator('input').first();
  if (await deponenteField.count()) await deponenteField.fill(FIXTURE.depoente.identificacao);
  await page.waitForTimeout(200);

  // Zoom on the block containing "Papel do depoente"
  const papelBlock = page.locator('.field', { hasText: 'Papel do depoente' }).first();
  if (await papelBlock.count()) {
    // capture a bit more context: the whole detail block (parent)
    const detalheBlock = page.locator('.block', { hasText: 'Detalhes do tipo' }).first();
    const target = (await detalheBlock.count()) ? detalheBlock : papelBlock;
    await shot(target, path.join(OUT, 'nexo-papel-pessoa.png'));
  } else {
    console.warn('  !! Papel do depoente field not found');
  }

  // Close modal (Cancelar) to avoid polluting state, then attempt indiciação
  const cancelBtn = page.locator('button', { hasText: 'Cancelar' }).first();
  if (await cancelBtn.count()) await cancelBtn.click();
  await page.waitForTimeout(200);

  // Indiciação: the seed example has deliberate critical pendências, so generation will be blocked.
  // We try anyway and capture whatever state results (blocked alert or generation dialog).
  await page.click('#btnMenu');
  await page.waitForSelector('#menu.open');
  await page.click('#menu button[data-act="minuta"]');
  await page.waitForTimeout(400);
  // If a modal with checkboxes + "Data do documento" appeared, capture it.
  const minutaModal = page.locator('.modal', { hasText: 'Gerar minuta' });
  if (await minutaModal.count()) {
    await shot(page, path.join(OUT, 'nexo-indiciacao.png'), { fullPage: true });
  } else {
    console.warn('  !! Minuta modal did not open (likely blocked by pendências críticas) — building a clean minimal scenario instead.');
    await buildCleanIndiciacaoScenario(page);
  }
}

async function buildCleanIndiciacaoScenario(page) {
  // Any modal from the earlier "+ Prova" attempt may still be open — force-close via app API.
  await page.evaluate(() => { try { closeModal(); } catch (e) {} });
  await page.waitForTimeout(150);

  // Build a minimal, clean scenario directly on the app's `doc` object (same technique the
  // app's own "carregarExemplo" seed uses) — 1 acusado, 1 fato ativo with prova + enquadramento
  // (elemento subjetivo defined) + individualized conduct, so no critical pendências (P1/P2/P5/P8)
  // block indiciação. This is far more reliable than driving every nested modal via the UI.
  const fixture = FIXTURE;
  await page.evaluate((fx) => {
    doc = docVazio();
    doc.processo.numero = fx.processo.numero;
    doc.processo.objetoApuracao = fx.processo.objetoApuracao;
    doc.processo.comissao.presidente = { nome: 'Fulano de Tal', cargo: 'Auditor-Fiscal da RFB', matricula: '1234567' };
    doc.processo.comissao.portariaInstauracao = { numero: '123/2026', data: '2026-02-01' };

    const A1 = { id: genId('A'), nome: fx.acusado.nome, matricula: fx.acusado.matricula, cargo: fx.acusado.cargo,
      lotacao: fx.acusado.lotacao, qualificacaoComplementar: '',
      notificacaoPrevia: { realizada: true, data: '2026-02-10', refAutos: 'fls. 20' },
      interrogatorio: { status: 'pendente', data: '', refAutos: '', aposTodasAsProvas: null } };
    doc.acusados.push(A1);

    const P1 = { id: genId('P'), tipo: 'documental', titulo: fx.provaInicialVeritas.titulo,
      descricao: fx.provaInicialVeritas.conteudoFicticio,
      refAutos: { documento: 'Doc. 1', folhas: '12-15' }, hashVeritas: '', trechosSignificativos: [],
      contraditorio: { acusadoIntimado: true, refAutos: 'fls. 16' }, detalhe: {} };
    doc.provas.push(P1);

    const F1 = { id: genId('F'), titulo: fx.fatos[0].titulo,
      descricao: 'Descrição pormenorizada fictícia do fato F1, para fins de teste automatizado.',
      periodo: { inicio: '2026-01-01', fim: '2026-02-01' }, local: 'Unidade de Teste', dataCiencia: '2026-02-05',
      status: 'ativo', justificativaArquivamento: '', pautaEnviada: { em: null },
      condutas: [{ acusadoId: A1.id, descricaoConduta: 'processou pagamento sem cobertura contratual', modalidade: 'comissiva' }],
      provaIds: [P1.id],
      estadoProbatorio: { calculado: 'suficiente', override: null, justificativaOverride: '' },
      enquadramentos: [{ normaId: fx.fatos[0].normaId, elementoSubjetivo: 'dolo_direto', fundamentacao: 'Consciência e vontade de causar o dano ao erário.' }],
      multiplicidade: { classificacao: 'nao_classificada', principioAplicado: null, normaPrevalente: null, justificativa: '' },
      elementosBuscados: '' };
    doc.fatos.push(F1);
    doc.fatos.forEach((f, i) => f.ordem = i + 1);
    migra(doc);
    recomputaSeq();
    lens = 'todos'; isolatedFato = null; revisadas.clear();
    render();
  }, fixture);
  await page.waitForTimeout(300);

  // Now retry indiciação
  await page.click('#btnMenu');
  await page.waitForSelector('#menu.open');
  await page.click('#menu button[data-act="minuta"]');
  await page.waitForTimeout(400);
  const minutaModal = page.locator('.modal', { hasText: 'Gerar minuta' });
  if (await minutaModal.count()) {
    await shot(page, path.join(OUT, 'nexo-indiciacao.png'), { fullPage: true });
  } else {
    console.warn('  !! Still could not open a clean minuta dialog — capturing whatever is on screen for reference.');
    await shot(page, path.join(OUT, 'nexo-indiciacao-BLOCKED.png'), { fullPage: true });
  }
}

/* ==================== OITIVA 360 ==================== */
async function runOitiva(page) {
  console.log('=== Oitiva 360 ===');
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/oitiva-360.html')));
  // Oitiva 360 agora abre numa tela inicial (padrão uniforme da Suíte COGER) antes da Matriz de
  // Apuração. Sem estado salvo, "+ Novo processo" leva direto à Matriz (sem aviso).
  const telaInicialNovo = page.locator('#btn-inicial-novo');
  if (await telaInicialNovo.isVisible().catch(() => false)) {
    await telaInicialNovo.click();
  }
  await page.waitForSelector('#cartao-matriz');

  await page.fill('#campo-conduta', FIXTURE.fatos[1].titulo);
  await page.fill('#campo-investigado', FIXTURE.acusado.nome);
  await page.fill('#campo-elementos-disponiveis', 'Elementos já constantes dos autos: extrato financeiro fictício (F1).');
  await page.fill('#campo-hipotese', 'Hipótese fictícia: possível valimento do cargo em benefício próprio (F2).');
  // trigger blur/input handlers
  await page.locator('#campo-hipotese').dispatchEvent('change');
  await page.locator('#campo-hipotese').dispatchEvent('input');
  await page.waitForTimeout(300);

  await shot(page.locator('#cartao-matriz'), path.join(OUT, 'oitiva-matriz-apuracao.png'));

  // Adicionar depoente
  const addBtn = page.locator('#btn-add-depoente');
  await page.waitForTimeout(200);
  const disabled = await addBtn.isDisabled();
  if (disabled) {
    console.warn('  !! btn-add-depoente still disabled — matriz not detected as complete, retrying with keyboard events');
    for (const id of ['#campo-conduta', '#campo-investigado', '#campo-elementos-disponiveis', '#campo-hipotese']) {
      await page.click(id);
      await page.keyboard.press('End');
      await page.keyboard.type(' ');
      await page.keyboard.press('Backspace');
    }
    await page.waitForTimeout(300);
  }
  await addBtn.click();
  await page.waitForSelector('#dialogo-add-depoente[open]');
  await page.fill('#campo-identificacao-depoente', FIXTURE.depoente.identificacao);
  await page.fill('#campo-elementos-buscados-depoente', FIXTURE.depoente.elementosBuscados);
  await page.click('#btn-confirmar-add-depoente');
  await page.waitForTimeout(300);

  // Open the depoente wizard
  await page.click('[data-abrir-wizard]');
  await page.waitForSelector('#stepper-depoente:not([hidden])');
  await page.waitForTimeout(200);

  // Etapa 2: fill required fields (identificação already set), papel, infração
  await page.click('.etapa[data-etapa="2"]');
  await page.waitForTimeout(200);
  const depIdent = page.locator('#dep-identificacao');
  if (await depIdent.count()) {
    const val = await depIdent.inputValue();
    if (!val) await depIdent.fill(FIXTURE.depoente.identificacao);
  }
  const depElementos = page.locator('#dep-elementos-buscados');
  if (await depElementos.count()) {
    const val = await depElementos.inputValue();
    if (!val) await depElementos.fill(FIXTURE.depoente.elementosBuscados);
  }
  // papel = testemunha
  const papelRadio = page.locator('input[name="papel-depoente"][value="testemunha"]');
  if (await papelRadio.count()) await papelRadio.check({ force: true });
  // infração
  const infracaoSelect = page.locator('#dep-infracao');
  if (await infracaoSelect.count()) {
    const hasOpt = await infracaoSelect.locator(`option[value="${FIXTURE.depoente.infracaoPrincipal}"]`).count();
    if (hasOpt) await infracaoSelect.selectOption(FIXTURE.depoente.infracaoPrincipal);
  }
  await page.waitForTimeout(200);

  // Advance to Etapa 3 (Montagem do Roteiro) then Etapa 4 (Respostas)
  await page.click('#btn-wizard-avancar'); // -> etapa 3
  await page.waitForTimeout(300);
  await page.click('#btn-wizard-avancar'); // -> etapa 4
  await page.waitForTimeout(400);

  // Fill first N response textareas
  const respostas = page.locator('textarea[data-resposta-roteiro]');
  const n = await respostas.count();
  console.log(`  Etapa 4: ${n} pergunta(s) no roteiro`);
  const fillCount = Math.min(n, 3);
  for (let i = 0; i < fillCount; i++) {
    await respostas.nth(i).fill(FIXTURE.depoente.respostaPadrao);
    await respostas.nth(i).dispatchEvent('input');
  }
  await page.waitForTimeout(300);

  const respostasSection = page.locator('#wizard-etapa-4');
  await shot(respostasSection, path.join(OUT, 'oitiva-rodada-perguntas-respostas.png'));

  // Termo final — locate the "Termo de redução" card / textarea
  const termoTextarea = page.locator('#termo-texto');
  if (await termoTextarea.count()) {
    await termoTextarea.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    const termoCard = page.locator('.cartao', { has: page.locator('#termo-texto') }).first();
    const target = (await termoCard.count()) ? termoCard : termoTextarea;
    await shot(target, path.join(OUT, 'oitiva-termo-final.png'));
  } else {
    console.warn('  !! #termo-texto not found for termo final screenshot');
  }
}

main().catch((e) => { console.error(e); process.exit(1); });
