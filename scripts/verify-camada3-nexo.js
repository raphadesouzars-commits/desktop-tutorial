// Camada 3/4 — Nexo Coger: renderIndiciacao/renderIntimacao diretamente + inspeção de #printPage
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const OUT = path.join(ROOT, 'scripts/screenshots');
const FIXTURE = require(path.join(ROOT, 'fixtures/pad-ficticio-001.json'));

function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 3400 } });
  page.on('dialog', async (d) => { await d.accept(); });
  page.on('pageerror', (e) => console.log('  [pageerror]', e.message));

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

  const acusados = await page.evaluate(() => doc.acusados.map(a => ({ id: a.id, nome: a.nome })));
  console.log('Acusados:', acusados);

  // Render Nota de Indiciação diretamente para o primeiro acusado
  const info = await page.evaluate((acId) => {
    renderIndiciacao(acId, doc);
    const pp = document.getElementById('printPage');
    return {
      exists: !!pp,
      innerTextSample: pp ? pp.innerText.slice(0, 500) : null,
      sectionCount: pp ? pp.querySelectorAll(':scope > div[style*="page-break-inside"]').length : 0,
      hasTable: pp ? !!pp.querySelector('table') : false,
      fullHTMLLength: pp ? pp.outerHTML.length : 0,
    };
  }, acusados[0].id);
  console.log('Nota de Indiciação render info:', JSON.stringify(info, null, 2));

  if (info.exists) {
    fs.writeFileSync(path.join(OUT, 'nexo-coger-nota-indiciacao.html'), await page.evaluate(() => document.getElementById('printPage').outerHTML));
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(OUT, 'nexo-coger-nota-indiciacao.pdf'), format: 'A4', printBackground: true }).catch(e => console.log('pdf err (headed context?):', e.message));
    await page.emulateMedia({ media: 'screen' });
    await page.screenshot({ path: path.join(OUT, 'nexo-coger-nota-indiciacao-dom.png'), fullPage: true }).catch(e => console.log('shot err', e.message));
  }

  // Fechar o painel de impressão antes de reabrir o menu (senão intercepta cliques)
  await page.evaluate(() => { if (typeof closePrint === 'function') closePrint(); });
  await page.waitForTimeout(200);

  // Try Termo de Intimação too
  await page.click('#btnMenu');
  await page.waitForSelector('#menu.open');
  const infoIntimacao = await page.evaluate((acId) => {
    try {
      const st = { tipo: 'esclarecimento_fato', alvoId: null, dest: {}, prazoDias: 5, texto: 'Solicito esclarecimento sobre o fato apurado.', dataDoc: new Date().toISOString().slice(0,10), numero: '12/2026', sufixo: 'CI', momento: 'final' };
      if (typeof renderIntimacao === 'function') {
        renderIntimacao(st, acId);
      }
      const pp = document.getElementById('printPage');
      return {
        exists: !!pp,
        innerTextSample: pp ? pp.innerText.slice(0, 400) : null,
        sectionCount: pp ? pp.querySelectorAll(':scope > div[style*="page-break-inside"]').length : 0,
        error: null,
      };
    } catch (e) {
      return { error: e.message, stack: e.stack };
    }
  }, acusados[0].id);
  console.log('Termo de Intimação render info:', JSON.stringify(infoIntimacao, null, 2));

  if (infoIntimacao.exists) {
    fs.writeFileSync(path.join(OUT, 'nexo-coger-termo-intimacao.html'), await page.evaluate(() => document.getElementById('printPage').outerHTML));
    await page.screenshot({ path: path.join(OUT, 'nexo-coger-termo-intimacao-dom.png'), fullPage: true }).catch(e => console.log('shot err', e.message));
  }

  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
