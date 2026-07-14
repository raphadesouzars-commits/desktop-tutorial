// Rodada 13 — Camada 1: Integridade Estrutural
// Run with: NODE_PATH=/opt/node22/lib/node_modules /opt/node22/bin/node scripts/verify-camada1.js
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const TOOLS = [
  { name: 'Veritas', file: 'ferramentas/veritas.html' },
  { name: 'Nexo Coger', file: 'ferramentas/nexo-coger.html' },
  { name: 'Nexo PAR', file: 'ferramentas/nexo-par.html' },
  { name: 'Oitiva 360', file: 'ferramentas/oitiva-360.html' },
];

function fileUrl(p) { return 'file://' + p; }

const report = {};

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

  for (const tool of TOOLS) {
    console.log(`\n=== ${tool.name} ===`);
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const consoleErrors = [];
    const pageErrors = [];
    const networkRequests = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', (err) => pageErrors.push(err.message));
    page.on('request', (req) => {
      // file:// requests for the page itself and same-dir resources are fine;
      // we're checking for actual network fetches (http/https).
      const url = req.url();
      if (url.startsWith('http://') || url.startsWith('https://')) {
        networkRequests.push(url);
      }
    });
    page.on('dialog', async (dialog) => { await dialog.accept(); });

    let loadOk = true;
    let loadError = null;
    try {
      await page.goto(fileUrl(path.join(ROOT, tool.file)), { waitUntil: 'load', timeout: 30000 });
      await page.waitForTimeout(1000); // let init() finish, async validations, etc.
    } catch (e) {
      loadOk = false;
      loadError = e.message;
    }

    // Check body has content (not blank screen)
    let bodyText = '';
    let hasPrintPageCapable = false;
    try {
      bodyText = await page.evaluate(() => document.body.innerText.slice(0, 200));
    } catch (e) { /* ignore */ }

    // Check window.CogerPrint exists (indicates the print module loaded without throwing)
    let cogerPrintExists = false;
    try {
      cogerPrintExists = await page.evaluate(() => typeof window.CogerPrint === 'object' && typeof window.CogerPrint.prepareForPrint === 'function');
    } catch (e) { /* ignore */ }

    // Check CSS variables resolve on :root
    let cssVars = {};
    try {
      cssVars = await page.evaluate(() => {
        const cs = getComputedStyle(document.documentElement);
        return {
          navy900: cs.getPropertyValue('--coger-print-navy-900').trim(),
          gold500: cs.getPropertyValue('--coger-print-gold-500').trim(),
        };
      });
    } catch (e) { /* ignore */ }

    report[tool.name] = {
      loadOk,
      loadError,
      consoleErrors,
      pageErrors,
      externalNetworkRequests: networkRequests,
      bodySample: bodyText,
      cogerPrintExists,
      cssVars,
    };

    console.log('  loadOk:', loadOk, loadError || '');
    console.log('  consoleErrors:', consoleErrors.length, consoleErrors.slice(0, 5));
    console.log('  pageErrors:', pageErrors.length, pageErrors.slice(0, 5));
    console.log('  externalNetworkRequests:', networkRequests.length, networkRequests.slice(0, 5));
    console.log('  cogerPrintExists:', cogerPrintExists);
    console.log('  cssVars:', JSON.stringify(cssVars));

    await page.close();
  }

  await browser.close();

  fs.writeFileSync(path.join(ROOT, 'scripts/camada1-report.json'), JSON.stringify(report, null, 2));
  console.log('\n\nReport written to scripts/camada1-report.json');
}

main().catch((e) => { console.error('FATAL:', e); process.exit(1); });
