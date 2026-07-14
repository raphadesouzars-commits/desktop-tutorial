// Verificação visual — Nexo PAR redesenhado (padrão Integritas)
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const OUT = path.join(ROOT, 'scripts/screenshots');
const FIXTURE = require(path.join(ROOT, 'fixtures/par-ficticio-001.json'));

function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 3400 } });
  page.on('dialog', async (d) => { await d.accept(); });
  page.on('pageerror', (e) => console.log('  [pageerror]', e.message));

  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/nexo-par.html')));
  await page.waitForSelector('#btnMenu');
  const inicio = page.locator('#inicio');
  if (await inicio.isVisible().catch(() => false)) {
    await page.click('#inicio .inicio-acoes button.primary');
    await page.waitForTimeout(200);
  }
  const gate = page.locator('#gate');
  if (await gate.isVisible().catch(() => false)) {
    const gateNumero = page.locator('#gateCard .field', { hasText: 'Número do processo' }).locator('input').first();
    await gateNumero.fill(FIXTURE.processo ? FIXTURE.processo.numero : '00190.100000/2026-00');
    await page.click('#gateBtnContinuar');
    await page.waitForTimeout(200);
  }
  await page.click('#btnMenu');
  await page.waitForSelector('#menu.open');
  const exemploBtn = page.locator('#menu button[data-act="exemplo"]');
  if (await exemploBtn.count()) {
    await exemploBtn.click();
    await page.waitForTimeout(400);
  }

  const acusados = await page.evaluate(() => (typeof doc !== 'undefined' && doc.acusados) ? doc.acusados.map(a => ({ id: a.id, nome: a.razaoSocial || a.nome })) : []);
  console.log('Acusados/entes:', acusados);

  if (!acusados.length) {
    console.log('Nenhum ente carregado pelo exemplo — abortando verificação visual (sem dado de teste).');
    await browser.close();
    return;
  }

  const info = await page.evaluate((acId) => {
    renderIndiciacao(acId, '2026-07-14');
    const pp = document.getElementById('printPage');
    return {
      exists: !!pp,
      sectionCount: pp ? pp.querySelectorAll(':scope > div[style*="page-break-inside"]').length : 0,
      hasTable: pp ? !!pp.querySelector('table') : false,
      innerTextSample: pp ? pp.innerText.slice(0, 300) : null,
    };
  }, acusados[0].id);
  console.log('Nota de Indiciação PAR render info:', JSON.stringify(info, null, 2));

  if (info.exists) {
    fs.writeFileSync(path.join(OUT, 'nexo-par-nota-indiciacao.html'), await page.evaluate(() => document.getElementById('printPage').outerHTML));
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(OUT, 'nexo-par-nota-indiciacao.pdf'), format: 'A4', printBackground: true }).catch(e => console.log('pdf err:', e.message));
    await page.emulateMedia({ media: 'screen' });
    await page.screenshot({ path: path.join(OUT, 'nexo-par-nota-indiciacao-dom.png'), fullPage: true }).catch(e => console.log('shot err', e.message));
  }

  await browser.close();
}
main().catch((e) => { console.error('FATAL', e); process.exit(1); });
