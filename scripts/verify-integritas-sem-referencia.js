'use strict';
const path = require('path');
const { chromium } = require('playwright');
const ROOT = '/home/user/desktop-tutorial';
function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const context = await browser.newContext();
  const page = await context.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/Integritas.html')));
  await page.waitForTimeout(300);

  await page.evaluate(() => {
    hist = [{id:'res-sem-ilicito', ch:null, justs:[{fund:'',prob:'',pag:''}]}];
    SESSION.conduta = 'Conduta ficticia de teste';
    SESSION.processo = '10000.000000/2026-00';
    showReport();
  });
  await page.waitForTimeout(300);

  const popupPromise = context.waitForEvent('page');
  await page.click('#bpr');
  const popup = await popupPromise;
  await popup.waitForLoadState('domcontentloaded');
  const html = await popup.content();
  console.log('popup tem "Referência":', html.includes('Referência'));
  console.log('popup tem "INT-":', html.includes('INT-'));
  console.log('pageerrors:', errs);
  await popup.screenshot({ path: path.join(ROOT, 'scripts/screenshots/integritas-relatorio-sem-referencia.png'), fullPage: true });
  await browser.close();
}
main().catch((e) => { console.error('FATAL', e); process.exit(1); });
