'use strict';
const path = require('path');
const { chromium } = require('playwright');
const ROOT = '/home/user/desktop-tutorial';
function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', (e) => console.log('  [pageerror]', e.message));
  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/Integritas.html')));
  await page.waitForTimeout(500);

  const btnNova = page.locator('#ti-nova');
  const btnImportar = page.locator('#ti-importar');
  console.log('tela inicial visivel:', await btnNova.count() > 0 && await btnImportar.count() > 0);

  await page.screenshot({ path: path.join(ROOT, 'scripts/screenshots/integritas-tela-inicial.png'), fullPage: true });

  await btnNova.click();
  await page.waitForTimeout(300);
  const formVisible = await page.locator('#pi-proc').count();
  console.log('formulario de identificacao apareceu apos clique:', formVisible > 0);

  await browser.close();
}
main().catch((e) => { console.error('FATAL', e); process.exit(1); });
