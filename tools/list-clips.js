// node tools/list-clips.js  -> preview/voice/clips.json : every clip Kukua can speak on the merged page
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(__dirname, '../preview/Corbit_X_Readiness_Centre_Kukua.html'));
  await p.waitForTimeout(1500);
  const clips = await p.evaluate(() => window.CXJ_CLIPS());
  fs.writeFileSync(path.resolve(__dirname, '../preview/voice/clips.json'), JSON.stringify(clips, null, 1));
  const words = clips.reduce((n, c) => n + c.say.split(/\s+/).length, 0);
  console.log('clips:', clips.length, 'words:', words, '~minutes:', Math.round(words / 150), errs.length ? 'ERRORS ' + errs : 'no errors');
  await b.close();
})();
