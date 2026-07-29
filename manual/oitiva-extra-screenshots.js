// Extra screenshots for the Oitiva 360 audit complement (lista de depoentes, Kit de Incidentes, Cartão de Mesa).
// Run with: NODE_PATH=/opt/node22/lib/node_modules /opt/node22/bin/node manual/oitiva-extra-screenshots.js (or wherever placed)
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const OUT = path.join(ROOT, 'manual/assets/screenshots');
fs.mkdirSync(OUT, { recursive: true });

const FIXTURE = require(path.join(ROOT, 'fixtures/pad-ficticio-001.json'));

function fileUrl(p) { return 'file://' + p; }

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

  console.log('=== Oitiva 360 — extra screenshots ===');
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/oitiva-360.html')));
  await page.waitForSelector('#cartao-matriz');

  // Preencher a Matriz de Apuração (obrigatória para habilitar "Adicionar depoente")
  await page.fill('#campo-conduta', FIXTURE.fatos[1].titulo);
  await page.fill('#campo-investigado', FIXTURE.acusado.nome);
  await page.fill('#campo-elementos-disponiveis', 'Elementos já constantes dos autos: extrato financeiro fictício (F1).');
  await page.fill('#campo-hipotese', 'Hipótese fictícia: possível valimento do cargo em benefício próprio (F2).');
  await page.locator('#campo-hipotese').dispatchEvent('input');
  await page.locator('#campo-hipotese').dispatchEvent('change');
  await page.waitForTimeout(300);

  const addBtn = page.locator('#btn-add-depoente');
  if (await addBtn.isDisabled()) {
    for (const id of ['#campo-conduta', '#campo-investigado', '#campo-elementos-disponiveis', '#campo-hipotese']) {
      await page.click(id);
      await page.keyboard.press('End');
      await page.keyboard.type(' ');
      await page.keyboard.press('Backspace');
    }
    await page.waitForTimeout(300);
  }

  // ---- Adicionar 2 depoentes de exemplo ----
  async function adicionarDepoente(identificacao, elementosBuscados) {
    await addBtn.click();
    await page.waitForSelector('#dialogo-add-depoente[open]');
    await page.fill('#campo-identificacao-depoente', identificacao);
    await page.fill('#campo-elementos-buscados-depoente', elementosBuscados);
    await page.click('#btn-confirmar-add-depoente');
    await page.waitForTimeout(250);
  }

  await adicionarDepoente('T-01', FIXTURE.depoente.elementosBuscados);
  await adicionarDepoente('T-02 — Colega de setor', 'Confirmar rotina de acesso ao sistema no período apurado.');

  // Dar um "papel" ao primeiro depoente para a coluna Papel/Infração aparecerem preenchidas na lista.
  await page.click('[data-abrir-wizard]');
  await page.waitForSelector('#stepper-depoente:not([hidden])');
  await page.waitForTimeout(200);
  await page.click('.etapa[data-etapa="2"]');
  await page.waitForTimeout(200);
  const papelRadio = page.locator('input[name="papel-depoente"][value="testemunha"]');
  if (await papelRadio.count()) await papelRadio.check({ force: true });
  const infracaoSelect = page.locator('#dep-infracao');
  if (await infracaoSelect.count()) {
    const hasOpt = await infracaoSelect.locator(`option[value="${FIXTURE.depoente.infracaoPrincipal}"]`).count();
    if (hasOpt) await infracaoSelect.selectOption(FIXTURE.depoente.infracaoPrincipal);
  }
  await page.waitForTimeout(200);

  // Avançar para gerar roteiro (status vira "Roteiro pronto") — captura fica mais realista.
  await page.click('#btn-wizard-avancar'); // -> etapa 3
  await page.waitForTimeout(300);

  // Voltar para a tela do processo (fechar wizard) para fotografar a lista de depoentes.
  const fecharBtn = page.locator('#btn-fechar-wizard, [data-fechar-wizard], #btn-voltar-processo');
  if (await fecharBtn.count()) {
    await fecharBtn.first().click();
  } else {
    // Fallback: chamar fecharWizard() diretamente via API global exposta pelo app.
    await page.evaluate(() => { try { fecharWizard(); } catch (e) {} });
  }
  await page.waitForSelector('#tela-processo:not([hidden])', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(300);

  await shot(page, path.join(OUT, 'oitiva-lista-depoentes.png'), { fullPage: true });

  // ---- Kit de Incidentes (equivalente ao "kit de situações") — painel lateral nas Etapas 3/4 ----
  await page.click('[data-abrir-wizard]');
  await page.waitForSelector('#stepper-depoente:not([hidden])');
  await page.waitForTimeout(200);
  await page.click('.etapa[data-etapa="3"]');
  await page.waitForTimeout(300);
  const kitPanel = page.locator('#kit-incidentes-conteudo');
  if (await kitPanel.count()) {
    // Expandir alguns grupos <details> para o conteúdo aparecer na screenshot.
    await page.evaluate(() => {
      document.querySelectorAll('#kit-incidentes-conteudo details').forEach((d, i) => { if (i < 3) d.open = true; });
    });
    await page.waitForTimeout(200);
    const kitCard = page.locator('#kit-incidentes-conteudo').locator('xpath=ancestor::*[self::aside or contains(@class,"cartao")][1]');
    const target = (await kitCard.count()) ? kitCard.first() : kitPanel;
    await shot(target, path.join(OUT, 'oitiva-kit-situacoes.png'));
  } else {
    console.warn('  !! #kit-incidentes-conteudo not found — Kit de Incidentes screenshot skipped');
  }

  // ---- Cartão de Mesa (impressão isolada do Kit de Incidentes) ----
  // window.print() abre diálogo nativo do SO — em vez disso, montamos a área de impressão via as
  // mesmas funções do app e capturamos o HTML diretamente, forçando display:block (mesma regra do
  // @media print).
  await page.click('.etapa[data-etapa="4"]');
  await page.waitForTimeout(300);
  const cartaoMesaBtn = page.locator('#btn-imprimir-cartao-mesa');
  if (await cartaoMesaBtn.count()) {
    // montarAreaImpressaoCartaoMesa() é interna ao IIFE do app (não exposta em window) — em vez de
    // chamá-la diretamente, neutralizamos window.print() e deixamos o handler do próprio botão
    // (que já roda montarAreaImpressaoCartaoMesa() + prepararAreaImpressaoParaImpressao()) montar o
    // HTML normalmente; depois só forçamos display:block em #area-impressao (mesma regra do @media print).
    await page.evaluate(() => { window.print = () => {}; });
    await cartaoMesaBtn.click();
    await page.waitForTimeout(200);
    await page.evaluate(() => {
      const area = document.getElementById('area-impressao');
      area.style.display = 'block';
      area.style.position = 'static';
      area.style.width = '900px';
      area.style.margin = '20px auto';
      area.style.border = '1px solid #ccc';
      area.style.padding = '16px';
      area.style.color = '#1A2740';
      area.style.background = '#fff';
    });
    await page.waitForTimeout(200);
    const area = page.locator('#area-impressao');
    await shot(area, path.join(OUT, 'oitiva-cartao-mesa.png'));
  } else {
    console.warn('  !! #btn-imprimir-cartao-mesa not found — Cartão de Mesa screenshot skipped');
  }

  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
