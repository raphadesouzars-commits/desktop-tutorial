'use strict';
const path = require('path');
const { chromium } = require('playwright');
const ROOT = '/home/user/desktop-tutorial';
function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1600 } });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/veritas.html')));
  await page.waitForTimeout(300);

  await page.evaluate(() => { window.print = () => { window.__printCalled = true; }; App.irParaRelatorio(); });
  await page.waitForTimeout(300);

  const btn = page.locator('button[onclick*="prepareForPrint"]');
  console.log('btn count:', await btn.count());
  await btn.click();
  await page.waitForTimeout(300);

  const info = await page.evaluate(() => {
    const pp = document.getElementById('printPage');
    return {
      exists: !!pp,
      printCalled: !!window.__printCalled,
      hasRefLabel: pp ? pp.innerHTML.includes('Referência') : null,
      dateFilled: pp ? (pp.querySelector('#coger-print-date')||{}).textContent : null,
    };
  });
  console.log('info:', JSON.stringify(info));
  console.log('pageerrors:', errs);
  await page.screenshot({ path: path.join(ROOT, 'scripts/screenshots/veritas-sem-referencia.png'), fullPage: true });
  await browser.close();
}
main().catch((e) => { console.error('FATAL', e); process.exit(1); });
