import { chromium } from 'playwright';
const [,, file = '_puppet_harness.html', out = '_puppet_shot.png', w = '1200', h = '900'] = process.argv;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +w, height: +h } });
p.on('console', m => console.log('PAGE', m.type(), ':', m.text()));
p.on('pageerror', e => console.log('PAGE EXCEPTION:', e.message));
await p.goto('file:///D:/Axolotto_2026/axolotto/docs/prototipos/' + file);
await p.waitForTimeout(3000);
const info = await p.evaluate(() => {
  const c = document.querySelector('canvas');
  return c ? { w: c.width, h: c.height, css: getComputedStyle(c).display } : 'no canvas';
});
console.log('CANVAS:', JSON.stringify(info));
await p.screenshot({ path: 'D:/Axolotto_2026/axolotto/docs/prototipos/' + out });
await b.close();
console.log('OK');
