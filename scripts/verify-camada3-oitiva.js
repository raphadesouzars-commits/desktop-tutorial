// Camada 3 — Oitiva 360: fluxo completo do wizard até Etapa 4, depois "Imprimir termo"
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
  const page = await browser.newPage({ viewport: { width: 1440, height: 3600 } });
  const errs = [];
  page.on('dialog', async (d) => { await d.accept(); });
  page.on('pageerror', (e) => { errs.push(e.message); console.log('  [pageerror]', e.message); });

  await page.goto(fileUrl(path.join(ROOT, 'ferramentas/oitiva-360.html')));
  const telaInicialNovo = page.locator('#btn-inicial-novo');
  if (await telaInicialNovo.isVisible().catch(() => false)) {
    await telaInicialNovo.click();
  }
  await page.waitForSelector('#cartao-matriz');

  await page.fill('#campo-conduta', FIXTURE.fatos[1].titulo);
  await page.fill('#campo-investigado', FIXTURE.acusado.nome);
  await page.fill('#campo-elementos-disponiveis', 'Elementos já constantes dos autos: extrato financeiro fictício (F1).');
  await page.fill('#campo-hipotese', 'Hipótese fictícia: possível valimento do cargo em benefício próprio (F2).');
  await page.locator('#campo-hipotese').dispatchEvent('change');
  await page.locator('#campo-hipotese').dispatchEvent('input');
  await page.waitForTimeout(300);

  const addBtn = page.locator('#btn-add-depoente');
  await page.waitForTimeout(200);
  if (await addBtn.isDisabled()) {
    for (const id of ['#campo-conduta', '#campo-investigado', '#campo-elementos-disponiveis', '#campo-hipotese']) {
      await page.click(id);
      await page.keyboard.press('End');
      await page.keyboard.type(' ');
      await page.keyboard.press('Backspace');
    }
    await page.waitForTimeout(300);
  }
  await addBtn.click();
  await page.waitForSelector('#dialogo-add-depoente[open]');
  await page.fill('#campo-identificacao-depoente', FIXTURE.depoente.identificacao);
  await page.fill('#campo-elementos-buscados-depoente', FIXTURE.depoente.elementosBuscados);
  await page.click('#btn-confirmar-add-depoente');
  await page.waitForTimeout(300);

  await page.click('[data-abrir-wizard]');
  await page.waitForSelector('#stepper-depoente:not([hidden])');
  await page.waitForTimeout(200);

  await page.click('.etapa[data-etapa="2"]');
  await page.waitForTimeout(200);
  const depIdent = page.locator('#dep-identificacao');
  if (await depIdent.count()) {
    const val = await depIdent.inputValue();
    if (!val) await depIdent.fill(FIXTURE.depoente.identificacao);
  }
  const depElementos = page.locator('#dep-elementos-buscados');
  if (await depElementos.count()) {
    const val = await depElementos.inputValue();
    if (!val) await depElementos.fill(FIXTURE.depoente.elementosBuscados);
  }
  const papelRadio = page.locator('input[name="papel-depoente"][value="testemunha"]');
  if (await papelRadio.count()) await papelRadio.check({ force: true });
  const infracaoSelect = page.locator('#dep-infracao');
  if (await infracaoSelect.count()) {
    const hasOpt = await infracaoSelect.locator(`option[value="${FIXTURE.depoente.infracaoPrincipal}"]`).count();
    if (hasOpt) await infracaoSelect.selectOption(FIXTURE.depoente.infracaoPrincipal);
  }
  await page.waitForTimeout(200);

  await page.click('#btn-wizard-avancar'); // -> etapa 3
  await page.waitForTimeout(300);
  await page.click('#btn-wizard-avancar'); // -> etapa 4
  await page.waitForTimeout(400);

  const respostas = page.locator('textarea[data-resposta-roteiro]');
  const n = await respostas.count();
  console.log(`Etapa 4: ${n} pergunta(s) no roteiro`);
  const fillCount = Math.min(n, 3);
  for (let i = 0; i < fillCount; i++) {
    await respostas.nth(i).fill(FIXTURE.depoente.respostaPadrao + ' (resposta de teste nº ' + i + ')');
    await respostas.nth(i).dispatchEvent('input');
  }
  await page.waitForTimeout(300);

  // Now click "Imprimir termo" — this calls montarAreaImpressaoTermo(d) + CogerPrint.prepareForPrint() + prepararAreaImpressaoParaImpressao() + window.print()
  // window.print() will hang in headless without a handler; stub it first.
  await page.evaluate(() => { window.print = () => { window.__printCalled = true; }; });

  const btnImprimirTermo = page.locator('#btn-imprimir-termo');
  const btnExists = await btnImprimirTermo.count();
  console.log('btn-imprimir-termo exists:', btnExists);
  if (btnExists) {
    await btnImprimirTermo.click();
    await page.waitForTimeout(300);
  }

  const info = await page.evaluate(() => {
    const pp = document.getElementById('printPage');
    return {
      printCalled: !!window.__printCalled,
      exists: !!pp,
      cogerPrintExists: typeof window.CogerPrint === 'object',
      refFilled: pp ? (pp.querySelector('#coger-print-ref') || {}).textContent : null,
      refCount: document.querySelectorAll('#coger-print-ref').length,
      sectionCount: pp ? pp.querySelectorAll(':scope > div[style*="page-break-inside"]').length : 0,
      qaItemCount: pp ? pp.innerHTML.split('P1.').length - 1 + (pp.querySelectorAll('div').length ? 0 : 0) : 0,
      areaImpressaoParentIsBody: (() => {
        const ai = document.getElementById('area-impressao');
        return ai ? ai.parentElement === document.body : null;
      })(),
    };
  });
  console.log('Oitiva termo (fluxo real) info:', JSON.stringify(info, null, 2));

  if (info.exists) {
    const html = await page.evaluate(() => document.getElementById('printPage').outerHTML);
    fs.writeFileSync(path.join(OUT, 'oitiva-360-termo-real.html'), html);
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(OUT, 'oitiva-360-termo-real.pdf'), format: 'A4', printBackground: true }).catch((e) => console.log('pdf err', e.message));
    await page.screenshot({ path: path.join(OUT, 'oitiva-360-termo-real.png'), fullPage: true }).catch((e) => console.log('shot err', e.message));
    await page.emulateMedia({ media: 'screen' });
  }
  fs.writeFileSync(path.join(ROOT, 'scripts/camada3-oitiva-report.json'), JSON.stringify({ info, errs }, null, 2));

  await browser.close();
}
main().catch((e) => { console.error('FATAL', e); process.exit(1); });
