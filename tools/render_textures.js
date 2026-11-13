// Renders each .tex element of tools/textures.html to frutiger/textures/<id>.png
// Usage: node tools/render_textures.js   (needs playwright with chromium)
const {chromium} = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const out = path.join(__dirname, '..', 'frutiger', 'textures');
  fs.mkdirSync(out, {recursive: true});
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport: {width: 2100, height: 1200}, deviceScaleFactor: 1});
  page.on('pageerror', e => console.log('PAGEERR', e.message));
  await page.goto('file://' + path.join(__dirname, 'textures.html'));
  await page.waitForFunction('document.title === "ready"');
  const els = await page.locator('.tex').all();
  for (const el of els) {
    const id = await el.getAttribute('id');
    await el.screenshot({path: path.join(out, id + '.png')});
    console.log(id);
  }
  await browser.close();
})();
