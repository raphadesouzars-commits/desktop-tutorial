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
  const page = await browser.newPage({ viewport: { width: 1440, height: 3000 } });
  page.on('dialog', async (d) => { await d.accept(); });
  page.on('pageerror', (e) => console.log('  [pageerror]', e.message));
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/veritas.html')));
  await page.getByRole('button', { name: '+ Novo dossiê' }).click();
  await page.waitForSelector('.rfb-card__header');
  const numeroInput = page.locator('.rfb-field', { hasText: 'Nº do processo' }).locator('input').first();
  await numeroInput.fill(FIXTURE.processo.numero);
  await numeroInput.dispatchEvent('change');

  const relBtn = page.getByRole('button', { name: /relat[oó]rio|imprimir/i }).first();
  await relBtn.click();
  await page.waitForTimeout(300);

  const info = await page.evaluate(() => {
    const pp = document.getElementById('printPage');
    return {
      exists: !!pp,
      sectionCount: pp ? pp.querySelectorAll(':scope > div[style*="page-break-inside"]').length : 0,
      refFilled: pp ? (pp.querySelector('#coger-print-ref') || {}).textContent : null,
    };
  });
  console.log('Veritas printPage info:', JSON.stringify(info, null, 2));

  if (info.exists) {
    // dispara o clique real de "Imprimir / Salvar PDF" para exercitar prepareForPrint()
    // stub window.print() para não travar em headless
    await page.evaluate(() => { window.print = () => { window.__printCalled = true; }; });
    const btnCount = await page.getByRole('button', { name: /imprimir.*pdf/i }).count();
    console.log('botao imprimir count:', btnCount);
    await page.getByRole('button', { name: /imprimir.*pdf/i }).first().click();
    await page.waitForTimeout(200);
    const afterClick = await page.evaluate(() => ({
      printCalled: !!window.__printCalled,
      ref: (document.getElementById('coger-print-ref') || {}).textContent,
      date: (document.getElementById('coger-print-date') || {}).textContent,
    }));
    console.log('after click:', JSON.stringify(afterClick));

    const beforeWrite = await page.evaluate(() => ({
      printPageCount: document.querySelectorAll('#printPage').length,
      refCount: document.querySelectorAll('#coger-print-ref').length,
      ref: (document.getElementById('coger-print-ref') || {}).textContent,
    }));
    console.log('logo antes de escrever o html:', JSON.stringify(beforeWrite));
    fs.writeFileSync(path.join(OUT, 'veritas-printpage.html'), await page.evaluate(() => document.getElementById('printPage').outerHTML));
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(OUT, 'veritas-printpage.pdf'), format: 'A4', printBackground: true }).catch(e => console.log('pdf err:', e.message));
    await page.emulateMedia({ media: 'screen' });
    await page.screenshot({ path: path.join(OUT, 'veritas-printpage-dom.png'), fullPage: true }).catch(e => console.log('shot err', e.message));
  }
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
