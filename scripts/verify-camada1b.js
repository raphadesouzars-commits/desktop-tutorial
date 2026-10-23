// Camada 1 (parte B): screenshot inicial (tela não-branca) + presença de #printPage capability
'use strict';
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const ROOT = '/home/user/desktop-tutorial';
const OUT = path.join(ROOT, 'scripts/screenshots');
const TOOLS = [
  { name: 'veritas', file: 'ferramentas/veritas.html' },
  { name: 'nexo-coger', file: 'ferramentas/nexo-coger.html' },
  { name: 'nexo-par', file: 'ferramentas/nexo-par.html' },
  { name: 'oitiva-360', file: 'ferramentas/oitiva-360.html' },
];

function fileUrl(p) { return 'file://' + p; }

async function main() {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const tool of TOOLS) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on('dialog', async (d) => { await d.accept(); });
    await page.goto(fileUrl(path.join(ROOT, tool.file)), { waitUntil: 'load' });
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT, `${tool.name}-inicial.png`) });
    const size = fs.statSync(path.join(OUT, `${tool.name}-inicial.png`)).size;
    console.log(tool.name, 'screenshot size:', size, 'bytes');
    await page.close();
  }
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
