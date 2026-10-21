// node tools/dump-rc.js -> seed/rc-defaults.json : the Readiness Centre's built-in content (read from the merged page)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, '../preview/Corbit_X_Readiness_Centre_Kukua.html'));
  await p.waitForLoadState('load'); await p.waitForTimeout(1200);
  const d = await p.evaluate(() => { const r = window.CXJ_RC; return { CATS: r.CATS, POSTERS: r.POSTERS, PHASES: r.PHASES, CAPS: r.CAPS, FAQS: r.FAQS, VIDEOS: r.VIDEOS, QRC: r.QRC, UPDATES: r.UPDATES, CONTACTS: r.CONTACTS, mq: r.mq, CONFIG: { goLive: r.CONFIG.goLive, currentPhase: r.CONFIG.currentPhase, workstreams: r.CONFIG.workstreams, kpis: r.CONFIG.kpis, announcement: r.CONFIG.announcement, dataIsIllustrative: r.CONFIG.dataIsIllustrative }, DATES: r.DATES }; });
  const dates = [ // label/format and offset for each key date (offsets are from the go-live date)
    { Days: -7, Months: 0, Fmt: 'Week' }, { Days: -1, Months: 0, Fmt: 'Day' }, { Days: 0, Months: 0, Fmt: 'Day' }, { Days: 3, Months: 0, Fmt: 'Day' }, { Days: 0, Months: 6, Fmt: 'Full' }];
  const out = { CATS: d.CATS, POSTERS: d.POSTERS, PHASES: d.PHASES, CAPS: d.CAPS, FAQS: d.FAQS, VIDEOS: d.VIDEOS, QRC: d.QRC, UPDATES: d.UPDATES, CONTACTS: d.CONTACTS, mq: d.mq,
    SETTINGS: { GoLive: d.CONFIG.goLive, CurrentPhase: String(d.CONFIG.currentPhase), AnnouncementTitle: d.CONFIG.announcement.title, AnnouncementBody: d.CONFIG.announcement.body, AnnouncementDate: d.CONFIG.announcement.date },
    DATES: d.DATES.map((x, i) => Object.assign({ Title: x[1], Body: x[2], Big: !!x[3] }, dates[i])) };
  fs.writeFileSync(path.resolve(__dirname, '../seed/rc-defaults.json'), JSON.stringify(out, null, 1));
  console.log('rc defaults:', Object.keys(out).map(k => k + ':' + (Array.isArray(out[k]) ? out[k].length : 'obj')).join(' '));
  await b.close();
})();
