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
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('dialog', async (d) => { await d.accept(); });
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
      hasCogerHeader: pp ? !!pp.querySelector('.coger-print-header') : false,
      hasCogerFooter: pp ? !!pp.querySelector('.coger-print-footer') : false,
      sectionTitles: pp ? Array.from(pp.querySelectorAll('.coger-print-section-title')).map(e => e.textContent) : [],
      refFilled: pp ? (pp.querySelector('#coger-print-ref') || {}).textContent : null,
    };
  });
  console.log('Veritas printPage info:', JSON.stringify(info, null, 2));
  if (info.exists) {
    fs.writeFileSync(path.join(OUT, 'veritas-printpage.html'), await page.evaluate(() => document.getElementById('printPage').outerHTML));
    await page.locator('#printPage').screenshot({ path: path.join(OUT, 'veritas-printpage-dom.png') }).catch(e => console.log('shot err', e.message));
  }
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
