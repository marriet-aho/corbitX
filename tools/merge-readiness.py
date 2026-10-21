#!/usr/bin/env python3
"""Merges the Readiness Centre page (base: nav, hero, countdown, dashboard, gallery, timeline, hub) with Kukua's journey
(guide, highlights, journey, changes, tips, training, what's next, closing, dock + Ask Kukua + voice).
   python3 tools/merge-readiness.py"""
import re, os, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'preview')
RC = open(os.path.join(P, 'Corbit-X-Readiness-Centre.html'), encoding='utf8').read()
KJ = open(os.path.join(P, 'Corbit_X_Journey_standalone.html'), encoding='utf8').read()
OUT = os.path.join(P, 'Corbit_X_Readiness_Centre_Kukua.html')
GO_LIVE = '2027-02-08T00:00:00+00:00'   # countdown reaches zero when 8 Feb 2027 arrives (Ghana = GMT)

def sub1(pat, rep, s, flags=0):
    out, n = re.subn(pat, rep, s, count=1, flags=flags); assert n == 1, pat; return out

# ---------- Readiness Centre
rc_head = RC[:RC.index('<style>')]
rc_css = RC[RC.index('<style>') + 7:RC.index('</style>')]
b = RC.index('<body>') + 6
sc = RC.index('<script>', b)
rc_markup = RC[b:sc]
rc_script = RC[sc + 8:RC.index('</script>', sc)]
assert RC.count('<script>') == 1

dash = re.compile(r'[^{}]*\.eyebrow(?:::|:)before\s*\{[^}]*\}')
print('RC eyebrow dash rules removed:', len(dash.findall(rc_css)))
rc_css = dash.sub('', rc_css)
rc_script = sub1(r'goLive: "[^"]*"', 'goLive: "%s"' % GO_LIVE, rc_script)
rc_script = rc_script.replace('["home","guides","journey","hub","coming"]', '["home","kjourney","guides","journey","hub","coming"]')
assert '"kjourney"' in rc_script

# --- Readiness Centre edits: "Expected" go-live wording; no dashboard section; three labels removed; data exposed to Kukua's narrator
rc_script = sub1(r'CONFIG\.goLiveConfirmed\?"Confirmed go-live date":"Provisional date[^"]*"', '"Expected go-live date"', rc_script)
rc_script = rc_script.replace('${CONFIG.goLiveConfirmed?"confirmed":"provisional"} go-live date', 'expected go-live date')
assert 'Provisional date' not in rc_script and '?"confirmed":"provisional"' not in rc_script
# dashboard: moved into the "Highlights so far" section (no overall-readiness ring). Markup is pulled out of the page flow here
# and re-inserted right under the highlight numbers; its script stays as is.
d0, d1 = rc_markup.index('<!-- DASHBOARD -->'), rc_markup.index('<!-- CTA BAND -->')
dash_html = rc_markup[d0:d1]
rc_markup = rc_markup[:d0] + rc_markup[d1:]
r0 = dash_html.index('<div class="ring-wrap">')
r1 = dash_html.index('Overall ready</small></div>', r0)
r1 = dash_html.index('</div>', r1 + len('Overall ready</small></div>')) + 6
dash_html = dash_html[:r0] + dash_html[r1:]
assert 'Overall ready' not in dash_html
dash_html = dash_html.replace('<section class="dash">', '<section class="dash dash-hl" id="dashboard">', 1)
assert 'dash-hl' in dash_html
for old in ['const overall=Math.round(CONFIG.workstreams.reduce((a,w)=>a+w[1],0)/CONFIG.workstreams.length);\n',
            '$("#overall").dataset.to=overall;\n',
            '  const r=e.target.querySelector("#ringFg");if(r)r.style.strokeDashoffset=502.65*(1-overall/100);\n']:
    assert old in rc_script, old
    rc_script = rc_script.replace(old, '')
assert 'overall' not in rc_script and 'ringFg' not in rc_script
# "One Journey. One Platform. One Corbit X." band under the countdown: removed
c0, c1 = rc_markup.index('<!-- CTA BAND -->'), rc_markup.index('<!-- GALLERY -->')
rc_markup = rc_markup[:c0] + rc_markup[c1:]
assert 'One Platform' not in rc_markup
# the dashboard is built from the "Highlights so far" information (Kukua's Highlights list) instead of invented figures
for old in ['if(!CONFIG.dataIsIllustrative){$("#dataTag").textContent="Live programme data";$("#dataTag").classList.add("or")}\n']:
    assert old in rc_script; rc_script = rc_script.replace(old, '$("#dataTag").textContent="Highlights so far";$("#dataTag").classList.add("or");\n')
b0 = rc_script.index('$("#bars").innerHTML=')
b1 = rc_script.index('const A=CONFIG.announcement;')
rc_script = rc_script[:b0] + r"""const hlItems=[];(window.CXJ_HL||[]).forEach(g=>g.Items.forEach(i=>hlItems.push(i)));
$("#bars").innerHTML=hlItems.filter(i=>i.Bar).map(i=>`<div class="bar-row"><div class="bar-top"><span>${i.Label}</span><span><span class="count" data-to="${i.Value}">0</span>${i.Suffix||"%"}</span></div><div class="bar"><i data-w="${Math.min(100,i.Value)}"></i></div></div>`).join("");
$("#kpis").innerHTML=hlItems.filter(i=>!i.Bar).map(i=>`<div class="kpi"><b><span class="count" data-to="${i.Value}">0</span><span class="u">${i.Suffix||""}</span></b><small>${i.Label}</small></div>`).join("");
""" + rc_script[b1:]
for label in ('<span class="eyebrow reveal">Corbit X Transformation Programme</span>', '<span class="eyebrow">Poster gallery</span>', '<span class="eyebrow">Coming to Corbit X</span>'):
    assert rc_markup.count(label) == 1, label
    rc_markup = rc_markup.replace(label, '')

rc_script = sub1(r'if\(ms<=0\)\{\$\("#cdMsg"\)\.textContent="Corbit X is live\. Thank you for getting us here!";ms=0\}',
    'if(ms<=0){$("#cdMsg").textContent="Corbit X is live. Thank you for getting us here!";const h=document.querySelector(".cd-label h3");if(h)h.textContent="We are live!";ms=0;liveCelebrate()}', rc_script)
rc_script += r"""
/* ===== WE ARE LIVE: celebration pop-up when the countdown reaches zero (add ?cxlive to the page address to preview it) ===== */
let liveStop=false;
function liveConfetti(cv){
  if(matchMedia("(prefers-reduced-motion: reduce)").matches){cv.remove();return}
  const ctx=cv.getContext("2d"),col=["#F26A1B","#FF8A3D","#FFFFFF","#545557","#FDE3D0","#D4540A"];
  const fit=()=>{cv.width=cv.clientWidth;cv.height=cv.clientHeight};fit();
  const bits=Array.from({length:160},()=>({x:Math.random()*cv.width,y:-Math.random()*cv.height,w:6+Math.random()*8,h:10+Math.random()*10,vy:2+Math.random()*3.5,vx:-1+Math.random()*2,r:Math.random()*6,vr:-.2+Math.random()*.4,c:col[Math.floor(Math.random()*col.length)]}));
  const t0=performance.now();
  (function frame(t){
    if(liveStop||!cv.isConnected)return;
    ctx.clearRect(0,0,cv.width,cv.height);
    const fade=Math.max(0,1-Math.max(0,(t-t0-7000)/2500));
    bits.forEach(b=>{b.x+=b.vx;b.y+=b.vy;b.r+=b.vr;if(b.y>cv.height+20&&t-t0<6500){b.y=-20;b.x=Math.random()*cv.width}
      ctx.save();ctx.globalAlpha=fade;ctx.translate(b.x,b.y);ctx.rotate(b.r);ctx.fillStyle=b.c;ctx.fillRect(-b.w/2,-b.h/2,b.w,b.h);ctx.restore()});
    if(fade>0)requestAnimationFrame(frame)
  })(t0);
}
function liveCelebrate(force){
  const key="cxj-live-"+CONFIG.goLive;let seen=false;try{seen=!!localStorage.getItem(key)}catch(e){}
  if((seen&&!force)||document.getElementById("livePop"))return;
  try{localStorage.setItem(key,"1")}catch(e){}
  liveStop=false;
  const host=document.querySelector(".cxp")||document.body;
  const img=(document.querySelector(".hero-visual .disc img")||{}).src||"";
  const pop=document.createElement("div");pop.id="livePop";pop.className="live-pop";
  pop.setAttribute("role","dialog");pop.setAttribute("aria-modal","true");pop.setAttribute("aria-labelledby","liveTitle");
  pop.innerHTML='<canvas class="live-conf" aria-hidden="true"></canvas><div class="live-card"><div class="live-badge"><i></i>LIVE</div>'
    +(img?'<div class="live-disc"><span class="live-ring"></span><img src="'+img+'" alt=""></div>':'')
    +'<h2 id="liveTitle" class="display">We are <span class="o">live!</span></h2>'
    +'<p class="live-sub">Corbit X is live. Thank you, team, for getting us here.</p>'
    +'<p class="live-tag">Smile. Check. Serve.</p>'
    +'<button type="button" class="btn btn-primary live-go">Let&rsquo;s go</button></div>';
  host.appendChild(pop);
  requestAnimationFrame(()=>pop.classList.add("in"));
  const esc=e=>{if(e.key==="Escape")close()};
  const close=()=>{liveStop=true;pop.classList.remove("in");document.removeEventListener("keydown",esc);setTimeout(()=>pop.remove(),400)};
  document.addEventListener("keydown",esc);
  pop.querySelector(".live-go").addEventListener("click",close);
  pop.addEventListener("click",e=>{if(e.target===pop)close()});
  pop.querySelector(".live-go").focus();
  liveConfetti(pop.querySelector(".live-conf"));
  if(window.CXJ_SAY&&window.CXJ_LIVE_TEXT)try{window.CXJ_SAY(window.CXJ_LIVE_TEXT)}catch(e){}
}
window.CXJ_LIVE_PREVIEW=()=>liveCelebrate(true);
if(/[?&]cxlive\b/.test(location.search))setTimeout(()=>liveCelebrate(true),700);
"""
rc_script += '\nwindow.CXJ_RC={CONFIG,POSTERS,CATS,PHASES,CAPS,FAQS,VIDEOS,QRC,UPDATES,DATES,CONTACTS,HUB,mq,GO,fmt,showPhase,showHub};\n'
rc_css += """
.live-pop{position:fixed;inset:0;z-index:300;display:grid;place-items:center;padding:20px;background:rgba(44,44,46,.82);backdrop-filter:blur(6px);opacity:0;transition:opacity .45s var(--ease)}
.live-pop.in{opacity:1}
.live-conf{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.live-card{position:relative;max-width:560px;width:100%;text-align:center;background:#fff;border-radius:32px;padding:34px 34px 38px;box-shadow:0 40px 90px rgba(0,0,0,.4);transform:translateY(30px) scale(.9);transition:transform .6s cubic-bezier(.34,1.56,.64,1)}
.live-pop.in .live-card{transform:none}
.live-badge{display:inline-flex;align-items:center;gap:8px;background:var(--orange);color:#fff;font:800 14px var(--body);letter-spacing:.2em;padding:7px 16px 7px 12px;border-radius:999px}
.live-badge i{width:10px;height:10px;border-radius:50%;background:#fff;animation:livePulse 1.2s infinite}
.live-disc{position:relative;width:200px;height:200px;margin:18px auto 6px}
.live-disc img{position:relative;width:100%;height:100%;object-fit:cover;border-radius:50%;box-shadow:0 14px 36px rgba(242,106,27,.35)}
.live-ring{position:absolute;inset:-14px;border-radius:50%;border:6px solid rgba(242,106,27,.4);animation:liveRing 2s ease-out infinite}
.live-card h2{font-size:clamp(52px,9vw,84px);color:var(--ink);margin:6px 0 8px}
.live-sub{font-size:19px;color:var(--grey-700);margin-bottom:6px}
.live-tag{font:800 24px var(--display);text-transform:uppercase;letter-spacing:.04em;color:var(--orange-deep);margin-bottom:22px}
@keyframes livePulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.7)}}
@keyframes liveRing{0%{transform:scale(.92);opacity:.9}100%{transform:scale(1.18);opacity:0}}
@media (prefers-reduced-motion:reduce){.live-badge i,.live-ring{animation:none}.live-card{transition:none}}
"""
rc_css += """
.dash.dash-hl .ready{grid-template-columns:1fr;padding-bottom:72px}
.kx #highlights{display:none!important}
.dash-kukua{display:flex;align-items:center;gap:12px;margin:-4px 0 22px;padding:10px 14px;background:var(--orange-soft);border-radius:14px;font-size:15px;color:var(--grey-700)}
.dash-kukua img{width:42px;height:42px;border-radius:50%;border:2px solid var(--orange);flex:none;object-fit:cover}
.dash-kukua p{margin:0}
.dash-kukua .hearbtn{display:inline-flex;align-items:center;gap:5px;margin-left:6px;color:var(--orange-deep);font-weight:700;font-size:13px;cursor:pointer}
.dash-kukua .hearbtn svg{width:15px;height:15px}
.dock.wait{animation:dockHint 1.8s ease-in-out infinite}
@keyframes dockHint{0%,100%{box-shadow:0 0 0 0 rgba(242,106,27,.0)}50%{box-shadow:0 0 0 10px rgba(242,106,27,.28)}}
.cx-reading{outline:3px solid rgba(242,106,27,.55);outline-offset:-5px;transition:outline-color .3s}
button.cx-hear,.kx button.cx-hear{position:absolute;z-index:6;right:14px;bottom:14px;display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:999px;background:#fff;color:var(--orange-deep);border:1.5px solid var(--orange);font:700 13px var(--body);box-shadow:var(--shadow);cursor:pointer;transition:transform .2s,background .2s}
button.cx-hear:hover,.kx button.cx-hear:hover{background:var(--orange-soft);transform:translateY(-2px)}
button.cx-hear svg,.kx button.cx-hear svg{width:15px;height:15px;flex:none}
button.cx-hear.top,.kx button.cx-hear.top{top:92px;bottom:auto;right:20px}
button.cx-hear.sec,.kx button.cx-hear.sec{top:22px;bottom:auto;right:22px}
"""
fonts = re.search(r'<link href="https://fonts.googleapis.com/css2[^>]*>', KJ).group(0)
rc_head = sub1(r'<link href="https://fonts.googleapis.com/css2[^>]*>', fonts, rc_head)
rc_head = rc_head.replace('<title>Corbit X Readiness Centre</title>', '<title>Corbit X Readiness Centre</title>')
rc_markup = sub1(r'(<li><a href="#home">Home</a></li>)', r'\1\n      <li><a href="#kjourney">Kukua&rsquo;s Journey</a></li>', rc_markup)
a, b2 = rc_markup.index('<!-- GALLERY -->'), rc_markup.index('<!-- FINAL CTA -->')
rc_a, rc_b, rc_c = rc_markup[:a], rc_markup[a:b2], rc_markup[b2:]

# ---------- Kukua
ki = KJ.index('<style>\n:root')
k_css = KJ[ki + 7:KJ.index('</style>', ki)]
vs = KJ.index('<script>var CXJ_VOICE_DATA'); ve = KJ.index('</script>', vs) + 9
import glob, base64
vdir = os.path.join(P, 'voice', 'emily'); cj = os.path.join(P, 'voice', 'clips.json')
wanted = set(c['name'] for c in json.load(open(cj))) if os.path.exists(cj) else None
vd = {os.path.basename(f)[:-4]: 'data:audio/mpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode() for f in sorted(glob.glob(vdir + '/*.mp3')) if wanted is None or os.path.basename(f)[:-4] in wanted}
voice_script = '<script>var CXJ_VOICE_DATA=' + json.dumps(vd) + ';</script>'
print('voice clips embedded:', len(vd))
ms = KJ.index('<script>\n/* =====', ve)
k_script = KJ[ms + 8:KJ.index('</script>', ms)]
body0 = KJ.index('<div class="top">')
hero = KJ[KJ.index('<header class="hero" id="welcome">'):KJ.index('</header>', body0) + 9]
mid = KJ[KJ.index('<!-- ============ HIGHLIGHTS'):KJ.index('<!-- ============ CLOSING')]
closing = KJ[KJ.index('<!-- ============ CLOSING'):KJ.index('<!-- ============ NARRATOR DOCK')]
overlays = KJ[KJ.index('<!-- ============ NARRATOR DOCK'):vs]
closing = re.sub(r'<footer>.*?</footer>', '', closing, flags=re.S)

# hero becomes a normal section ("Meet Kukua"), renamed so it can't collide with the Readiness Centre hero
hero = hero.replace('<header class="hero" id="welcome">', '<section class="kwel" id="welcome">').replace('</header>', '</section>')
hero = hero.replace('wrap hero-grid', 'wrap kwel-grid').replace('class="hero-ctas"', 'class="kwel-ctas"')
hero = sub1(r'<h1 class="display">.*?</h1>', '<h2 class="display"><span class="ln"><span class="o">Meet Kukua</span></span><span class="ln"><span>Your Corbit X guide</span></span></h2>', hero, re.S)
hero = hero.replace('href="#journey"', 'href="#kjourney"')
mid = mid.replace('id="journey"', 'id="kjourney"').replace('<section class="next" id="next"', '<section class="next" id="knext"').replace('href="#journey"', 'href="#kjourney"')
closing = closing.replace('href="#journey"', 'href="#kjourney"')
j_ = mid.index('<!-- ============ JOURNEY')
mid_a, mid_b = mid[:j_], mid[j_:]
# Kukua's Highlights intro (avatar, text, "Hear Kukua") moves into the dashboard card
hl_src = mid[mid.index('id="highlights"'):mid.index('<!-- ============ JOURNEY')]
av_src = re.search(r'<div class="kline"><img class="av" src="([^"]+)"', hl_src).group(1)
hear_btn = re.search(r'<button class="hearbtn" data-hear="highlights">.*?</button>', hl_src, re.S).group(0)
kline = '<div class="dash-kukua"><img src="' + av_src + '" alt=""><p><span data-ktext="highlights"></span> ' + hear_btn + '</p></div>\n        '
assert '<div class="bars" id="bars">' in dash_html
dash_html = dash_html.replace('<div class="bars" id="bars">', kline + '<div class="bars" id="bars">', 1)

k_script = k_script.replace('#journey"', '#kjourney"')

# --- Kukua narration: read the whole page, in order, from the hero
def patch(old, new):
    global k_script
    assert k_script.count(old) == 1, old[:60]
    k_script = k_script.replace(old, new)
patch('const a=new Audio(audioUrl);V.audio=a;', 'const a=V.el||(V.el=new Audio());a.onended=a.onerror=a.onplay=null;a.pause();a.src=audioUrl;V.audio=a;')
patch('const POSTERS = {', 'window.CXJ_HL=LISTS.Highlights;\nconst POSTERS = {')
patch('V.paused=false;setSpeaking(false)}', 'V.paused=false;V.after=null;setSpeaking(false)}')
patch('a.onplay=()=>setSpeaking(true);a.onended=()=>setSpeaking(false);a.onerror=()=>setSpeaking(false);\n  a.play().catch(()=>setSpeaking(false));',
      'const fin=()=>{setSpeaking(false);const f=V.after;V.after=null;if(f)f()};\n  a.onplay=()=>setSpeaking(true);a.onended=fin;a.onerror=fin;\n  a.play().catch(e=>{setSpeaking(false);if(e&&e.name==="NotAllowedError"){cancelTour();if(window.CXJ_BLOCKED)window.CXJ_BLOCKED()}});')
patch('function narrate(text,audioUrl){', 'function narrate(text,audioUrl,fromTour){if(!fromTour)cancelTour();')
patch('if(speak){if(i===0)', 'if(speak&&!V.tour){if(i===0)')
patch('if(e.isIntersecting&&!seen.has(k)&&$("#dock").classList.contains("show")){', 'if(false){')
patch('V.enabled=true;V.muted=false;speakText(V.current,V.currentAudio);syncCtl();', 'V.enabled=true;V.muted=false;V.follow=true;if(!V.touredOnce){V.touredOnce=true;readCurrentSection()}else speakText(V.current,V.currentAudio);syncCtl();')
patch('function toggleMute(){V.muted=!V.muted;if(V.muted)stopVoice();syncCtl()}', 'function toggleMute(){V.muted=!V.muted;try{localStorage.setItem("cxj-muted",V.muted?"1":"0")}catch(e){}if(V.muted){cancelTour();stopVoice()}else{V.enabled=true;V.follow=true}syncCtl()}')
patch('"Tap play to hear Kukua"', '"Your browser needs one tap or click before it allows sound. Tap anywhere and I\'ll start reading"')
patch('new IntersectionObserver(([e])=>$("#dock").classList.toggle("show",!e.isIntersecting),{threshold:.15}).observe($("#stage"));', '$("#dock").classList.add("show");')
patch(':vh(text);', ':vh(sp(text));')
patch('if(e.isIntersecting&&!closedNarrated){closedNarrated=true;narrate(cm,msg("closing").AudioUrl)}', 'if(false){}')
patch('setTimeout(()=>narrate(msg("welcome").Text,msg("welcome").AudioUrl),reduced?0:1200);',
      'setTimeout(()=>{if(!V.enabled){V.current=msg("welcome").Text;V.currentAudio="";$("#bText").textContent=strip(msg("welcome").Text);if(!V.muted)$("#dText").textContent="Your browser needs one tap or click before it allows sound. Tap anywhere and I\'ll start reading."}},reduced?0:1200);')
k_script += '\n' + open(os.path.join(ROOT, 'tools', 'tour.js'), encoding='utf8').read()
for s_ in (hero, mid, closing, overlays): assert 'id="journey"' not in s_

# css: scope under .kx
k_css = re.sub(r'(^|\n)html\{[^}]*\}', r'\1', k_css)
k_css = k_css.replace('html{scroll-behavior:auto}', '')
k_css = dash.sub('', k_css)
k_css = k_css.replace(':root{', '&{', 1)
k_css = re.sub(r'(^|\n)body\{', r'\1&{', k_css, count=1)
k_css = k_css.replace('.hero h1', '.kwel h2').replace('.hero', '.kwel').replace('#journey', '#kjourney')
names = set(re.findall(r'@keyframes\s+([\w-]+)', k_css))
k_css = re.sub(r'@keyframes\s+([\w-]+)', lambda m: '@keyframes kx-' + m.group(1), k_css)
def fix_anim(m):
    return re.sub(r'(?<![\w-])(' + '|'.join(map(re.escape, sorted(names, key=len, reverse=True))) + r')(?![\w-])', r'kx-\1', m.group(0))
k_css = re.sub(r'animation(?:-name)?\s*:[^;}]*', fix_anim, k_css)
k_css += '\n.kwel{padding:84px 0 72px}\n'
open('/tmp/_k.scss', 'w').write('.kx{\n' + k_css + '\n}')
res = subprocess.run(['node', '-e', "process.stdout.write(require('sass').compile('/tmp/_k.scss',{style:'compressed'}).css)"], capture_output=True, text=True, cwd=os.path.join(ROOT, 'tools'))
assert res.returncode == 0, res.stderr
kx_css = res.stdout

def wrap(js): return '(function(){\n' + js + '\n})();'
doc = (rc_head + '<style>' + rc_css + '\n/* ===== Kukua (scoped under .kx) ===== */\n' + kx_css + '</style>\n</head>\n<body>'
       + rc_a + '\n<div class="kx">\n' + hero + mid_a + '</div>\n' + dash_html + '\n<div class="kx">\n' + mid_b + '</div>\n' + rc_b
       + '\n<div class="kx">\n' + closing + '</div>\n' + rc_c
       + '\n<div class="kx">\n' + overlays + '</div>\n'
       + voice_script + '\n<script>' + wrap(k_script) + '</script>\n<script>' + wrap(rc_script) + '</script>\n</body>\n</html>\n')
open(OUT, 'w', encoding='utf8').write(doc)
print('written', OUT, len(doc) // 1024, 'KB; keyframes prefixed:', sorted(names))

# =====================================================================================================
# SPFx export: the same page as a SharePoint web part. Content comes from lists (see portal/schema.json);
# voice clips are served from SiteAssets instead of being embedded.
# =====================================================================================================
SPD = os.path.join(ROOT, 'src', 'webparts', 'corbitXJourney', 'portal')
URI_RE = re.compile(r'data:image/[a-z+]+;base64,[A-Za-z0-9+/=]+')
assets, aindex = [], {}
def aid(uri):
    key = hashlib.md5(uri.encode()).hexdigest() if 'hashlib' in globals() else uri
    if key not in aindex: aindex[key] = len(assets); assets.append(uri)
    return aindex[key]
import hashlib
def tok(s): return URI_RE.sub(lambda m: '{{A%d}}' % aid(m.group(0)), s)
def jsa(s): return re.sub(r'"(' + URI_RE.pattern + r')"', lambda m: '__A[%d]' % aid(m.group(1)), s)

def scan_end(src, i):
    """index just after the bracketed value that starts at src[i] (string/template aware)"""
    depth, q = 0, None
    while i < len(src):
        c = src[i]
        if q:
            if c == '\\': i += 1
            elif c == q: q = None
        elif c in '"\'`': q = c
        elif c in '([{': depth += 1
        elif c in ')]}':
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    raise ValueError('unbalanced')
def swap_const(src, name, new):
    m = re.search(r'\bconst ' + re.escape(name) + r'\s*=\s*', src); assert m, name
    end = scan_end(src, m.end())
    if src[end] == ';': end += 1
    return src[:m.start()] + new + src[end:]

# ---- Kukua script (content now comes from the LISTS argument)
ksp = k_script
a0, a1 = ksp.index('const LISTS = {'), ksp.index('const POSTERS = {')
ksp = ksp[:a0] + 'window.CXJ_HL=LISTS.Highlights;\n' + ksp[a1:]
ksp = ksp.replace('const KHEAD=', 'Object.keys(POSTER_OVERRIDES||{}).forEach(k=>{const o=POSTER_OVERRIDES[k];if(POSTERS[k]&&o){if(o.title)POSTERS[k].title=o.title;if(o.img)POSTERS[k].img=o.img}});\nconst KHEAD=', 1)
assert 'const VOICE_BASE="voice/emily/";' in ksp
ksp = ksp.replace('const VOICE_BASE="voice/emily/";', 'const VOICE_BASE=(OPTS&&OPTS.voiceBase)||"voice/emily/";', 1)
ksp = jsa(ksp)

# ---- Readiness Centre script (content now comes from the RCDATA argument)
rsp = jsa(rc_script)
for name in ('CATS', 'POSTERS', 'PHASES', 'CAPS', 'FAQS', 'VIDEOS', 'QRC', 'UPDATES', 'CONTACTS', 'mq'):
    extra = 'CONFIG.currentPhase=Math.max(0,Math.min(Number(CONFIG.currentPhase)||0,PHASES.length-1));' if name == 'PHASES' else ''
    rsp = swap_const(rsp, name, 'const %s=RCDATA.%s;%s' % (name, name, extra))
rsp = swap_const(rsp, 'DATES',
    'const DATES=RCDATA.DATES.map(d=>{const t=addMonths(addDays(GO,d.Days),d.Months);'
    'const label=d.Fmt==="Week"?fmt(t,{day:"numeric",month:"short"})+" week":d.Fmt==="Full"?fmt(t,{day:"numeric",month:"short",year:"numeric"}):fmt(t,{weekday:"short",day:"numeric",month:"short"});'
    'return [label,d.Title,d.Body,!!d.Big]});')
m_ = re.search(r'\bconst CONFIG\s*=\s*', rsp); ce = scan_end(rsp, m_.end()); ce += 1 if rsp[ce] == ';' else 0
rsp = rsp[:ce] + '\n{const S=RCDATA.SETTINGS||{};if(S.AnnouncementTitle)CONFIG.announcement.title=S.AnnouncementTitle;if(S.AnnouncementBody)CONFIG.announcement.body=S.AnnouncementBody;if(/^\\d{4}-\\d{2}-\\d{2}/.test(S.AnnouncementDate||""))CONFIG.announcement.date=S.AnnouncementDate.slice(0,10);if(S.FiguresAreIllustrative!==undefined&&S.FiguresAreIllustrative!=="")CONFIG.dataIsIllustrative=/^(yes|true|1)$/i.test(S.FiguresAreIllustrative)}\nif(RCDATA.SETTINGS){if(RCDATA.SETTINGS.GoLive)CONFIG.goLive=RCDATA.SETTINGS.GoLive;if(RCDATA.SETTINGS.CurrentPhase!==undefined&&RCDATA.SETTINGS.CurrentPhase!=="")CONFIG.currentPhase=Number(RCDATA.SETTINGS.CurrentPhase)}' + rsp[ce:]
m_ = re.search(r'\bconst IMG\s*=\s*', rsp); ie = scan_end(rsp, m_.end()); ie += 1 if rsp[ie] == ';' else 0
rsp = rsp[:ie] + '\nObject.assign(IMG,RCDATA.IMG||{});' + rsp[ie:]

# ---- markup
page = '<div class="cxp">' + rc_a + '\n<div class="kx">\n' + hero + mid_a + '</div>\n' + dash_html + '\n<div class="kx">\n' + mid_b + '</div>\n' + rc_b + '\n<div class="kx">\n' + closing + '</div>\n' + rc_c + '\n<div class="kx">\n' + overlays + '</div>\n</div>'
page = tok(page)

# ---- css, scoped under .cxp
rcs = re.sub(r'(^|\n)html\{[^}]*\}', r'\1', rc_css).replace(':root{', '&{', 1)
rcs = re.sub(r'(^|\n)body\{', r'\1&{', rcs, count=1)
rcs = re.sub(r'html\{scroll-behavior:auto\}', '', rcs)
rcs += '\n.nav{position:sticky}\nsection,header,[id]{scroll-margin-top:84px}\n'
open('/tmp/_sp.scss', 'w').write('.cxp{\n' + rcs + '\n}\n.cxp{\n' + kx_css + '\n}')
res = subprocess.run(['node', '-e', "process.stdout.write(require('sass').compile('/tmp/_sp.scss',{style:'compressed'}).css)"], capture_output=True, text=True, cwd=os.path.join(ROOT, 'tools'))
assert res.returncode == 0, res.stderr
sp_css = res.stdout

def w(name, body): open(os.path.join(SPD, name), 'w', encoding='utf8').write(body)
HDR = '// GENERATED by tools/merge-readiness.py. Do not edit.\n'
w('portalCss.ts', HDR + 'export const PORTAL_CSS: string = ' + json.dumps(sp_css) + ';\n')
w('portalTemplate.ts', HDR + 'export const PORTAL_TEMPLATE: string = ' + json.dumps(page) + ';\n')
w('runPortal.ts', HDR + '// @ts-nocheck\n/* eslint-disable */\nexport function runPortal(LISTS: any, RCDATA: any, POSTER_OVERRIDES: any, __A: string[], OPTS: any): void {\n(function(){\n' + ksp + '\n})();\n(function(){\n' + rsp + '\n})();\nif (window.CXJ_SETUP) window.CXJ_SETUP();\n}\n')
rcd = json.load(open(os.path.join(ROOT, 'seed', 'rc-defaults.json')))
w('defaultRc.ts', HDR + '/* eslint-disable */\nexport const RC_DEFAULTS: any = ' + json.dumps(rcd, ensure_ascii=False, indent=1) + ';\n')
w('portalAssets.ts', HDR + 'export const PORTAL_ASSETS: string[] = ' + json.dumps(assets) + ';\n')
print('SPFx export: assets', len(assets), '| css', len(sp_css) // 1024, 'KB | template', len(page) // 1024, 'KB')
