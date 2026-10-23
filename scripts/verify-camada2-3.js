// Rodada 13 — Camada 2 (smoke funcional pós-refactor) + Camada 3 (captura de #printPage/impressão)
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const OUT = path.join(ROOT, 'scripts/screenshots');
const FIXTURE = require(path.join(ROOT, 'fixtures/pad-ficticio-001.json'));

function fileUrl(p) { return 'file://' + p; }

async function fieldInput(page, labelText, selector = 'input, select, textarea') {
  return page.locator('.rfb-field', { hasText: labelText }).locator(selector).first();
}

async function shot(target, filePath, opts = {}) {
  await target.screenshot({ path: filePath, ...opts });
  const size = fs.statSync(filePath).size;
  console.log(`  -> ${path.basename(filePath)} (${size} bytes)`);
}

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const results = {};

  // ============ VERITAS ============
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    page.on('dialog', async (d) => { await d.accept(); });
    console.log('=== Veritas: smoke + impressão ===');
    await page.goto(fileUrl(path.join(ROOT, 'ferramentas/veritas.html')));
    await page.getByRole('button', { name: '+ Novo dossiê' }).click();
    await page.waitForSelector('.rfb-card__header');
    const numeroInput = page.locator('.rfb-field', { hasText: 'Nº do processo' }).locator('input').first();
    await numeroInput.fill(FIXTURE.processo.numero);
    await numeroInput.dispatchEvent('change');

    // trigger print view directly (viewRelatorio) if exposed
    const hasViewRelatorio = await page.evaluate(() => typeof viewRelatorio === 'function').catch(() => false);
    console.log('  viewRelatorio function exists:', hasViewRelatorio);

    // Find and click a "relatório"/"imprimir" button if present at this stage
    const relBtn = page.getByRole('button', { name: /relat[oó]rio|imprimir/i }).first();
    if (await relBtn.count()) {
      await relBtn.click().catch(() => {});
      await page.waitForTimeout(300);
    }
    const printPageExists = await page.evaluate(() => !!document.getElementById('printPage')).catch(() => false);
    console.log('  #printPage found after triggering relatório:', printPageExists);
    await shot(page, path.join(OUT, 'veritas-smoke.png'), { fullPage: true });
    results.veritas = { errs, printPageExists };
    await page.close();
  } catch (e) {
    results.veritas = { fatal: e.message };
    console.error('VERITAS SMOKE FAILED:', e.message);
  }

  // ============ NEXO COGER ============
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    page.on('dialog', async (d) => { await d.accept(); });
    console.log('=== Nexo Coger: smoke + minuta de indiciação ===');
    await page.goto(fileUrl(path.join(ROOT, 'ferramentas/nexo-coger.html')));
    await page.waitForSelector('#btnMenu');

    const inicio = page.locator('#inicio');
    if (await inicio.isVisible().catch(() => false)) {
      await page.click('#inicio .inicio-actions button.primary');
      await page.waitForTimeout(200);
    }
    const gate = page.locator('#gate');
    if (await gate.isVisible().catch(() => false)) {
      const gateNumero = page.locator('#gateCard .field', { hasText: 'Número do processo' }).locator('input').first();
      await gateNumero.fill(FIXTURE.processo.numero);
      await page.click('#gateBtnContinuar');
      await page.waitForTimeout(200);
    }

    await page.click('#btnMenu');
    await page.waitForSelector('#menu.open');
    await page.click('#menu button[data-act="exemplo"]');
    await page.waitForTimeout(400);

    // Try to open "Gerar minuta" flow (menu closes after each action — reopen it)
    await page.click('#btnMenu');
    await page.waitForSelector('#menu.open');
    const gerarBtn = page.locator('#menu button[data-act="minuta"]');
    if (await gerarBtn.count()) {
      await gerarBtn.click();
      await page.waitForTimeout(300);
      // Modal should show a list; click "Visualizar / Imprimir" on first, or if single id auto-renders
      const visualizarBtn = page.locator('button', { hasText: 'Visualizar / Imprimir' }).first();
      if (await visualizarBtn.count()) {
        await visualizarBtn.click();
        await page.waitForTimeout(300);
      }
    }

    const printPageExists = await page.evaluate(() => !!document.getElementById('printPage')).catch(() => false);
    console.log('  #printPage found after Gerar minuta flow:', printPageExists);
    if (printPageExists) {
      await page.evaluate(() => window.CogerPrint && window.CogerPrint.prepareForPrint());
      await page.waitForTimeout(200);
      await page.pdf ? null : null; // pdf only works headless chromium via page.pdf, but page created headed? check
    }
    await shot(page, path.join(OUT, 'nexo-coger-smoke.png'), { fullPage: true });
    // Full print-page screenshot if visible
    const printPageLocator = page.locator('#printPage');
    if (await printPageLocator.count()) {
      await shot(printPageLocator, path.join(OUT, 'nexo-coger-printpage.png'));
    }
    results.nexoCoger = { errs, printPageExists };
    await page.close();
  } catch (e) {
    results.nexoCoger = { fatal: e.message };
    console.error('NEXO COGER SMOKE FAILED:', e.message);
  }

  // ============ OITIVA 360 ============
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    page.on('dialog', async (d) => { await d.accept(); });
    console.log('=== Oitiva 360: smoke + termo ===');
    await page.goto(fileUrl(path.join(ROOT, 'ferramentas/oitiva-360.html')));
    await page.waitForTimeout(500);

    // "Tela inicial" -> "+ Novo processo" pattern (like others)
    const novoBtn = page.locator('button', { hasText: /novo processo|começar|iniciar/i }).first();
    if (await novoBtn.count()) {
      await novoBtn.click().catch(() => {});
      await page.waitForTimeout(200);
    }
    await shot(page, path.join(OUT, 'oitiva-360-smoke-tela1.png'), { fullPage: true });
    results.oitiva = { errs, note: 'smoke only — full wizard flow requires deeper interaction, not automated here' };
    await page.close();
  } catch (e) {
    results.oitiva = { fatal: e.message };
    console.error('OITIVA SMOKE FAILED:', e.message);
  }

  await browser.close();
  fs.writeFileSync(path.join(ROOT, 'scripts/camada2-3-report.json'), JSON.stringify(results, null, 2));
  console.log('\nDone. Report at scripts/camada2-3-report.json');
}

main().catch((e) => { console.error('FATAL', e); process.exit(1); });
