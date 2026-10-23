'use strict';
const path = require('path');
const { chromium } = require('playwright');
const ROOT = '/home/user/desktop-tutorial';
function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', (e) => console.log('  [pageerror]', e.message));
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/nexo-par.html')));
  await page.waitForTimeout(300);

  // sem dados: nao deve ter Continuar
  let btns = await page.locator('#inicioCard button').allTextContents();
  console.log('estado vazio - botoes:', btns);

  // simula dados existentes
  await page.evaluate(() => {
    doc.processo.numero = '10000.000000/2026-00';
    doc.fatos.push({id:'F1'}); doc.provas.push({id:'P1'}); doc.acusados.push({id:'A1', tipo:'pj'});
    render(); abrirInicio();
  });
  await page.waitForTimeout(200);
  btns = await page.locator('#inicioCard button').allTextContents();
  console.log('estado com dados - botoes:', btns);
  await page.screenshot({ path: path.join(ROOT, 'scripts/screenshots/nexo-par-tela-inicial-continuar.png'), fullPage: true });

  await browser.close();
}
main().catch((e) => { console.error('FATAL', e); process.exit(1); });
