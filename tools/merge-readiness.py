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

# --- Readiness Centre edits: "Expected" go-live wording, no overall-readiness ring, expose data to Kukua's narrator
rc_script = sub1(r'CONFIG\.goLiveConfirmed\?"Confirmed go-live date":"Provisional date[^"]*"', '"Expected go-live date"', rc_script)
rc_script = rc_script.replace('${CONFIG.goLiveConfirmed?"confirmed":"provisional"} go-live date', 'expected go-live date')
assert 'Provisional date' not in rc_script and '?"confirmed":"provisional"' not in rc_script
for old in ['const overall=Math.round(CONFIG.workstreams.reduce((a,w)=>a+w[1],0)/CONFIG.workstreams.length);\n',
            '$("#overall").dataset.to=overall;\n',
            '  const r=e.target.querySelector("#ringFg");if(r)r.style.strokeDashoffset=502.65*(1-overall/100);\n']:
    assert old in rc_script, old
    rc_script = rc_script.replace(old, '')
assert 'overall' not in rc_script and 'ringFg' not in rc_script
rc_script += '\nwindow.CXJ_RC={CONFIG,POSTERS,CATS,PHASES,CAPS,FAQS,VIDEOS,QRC,UPDATES,DATES,CONTACTS,HUB,mq,GO,fmt,showPhase,showHub};\n'
r0 = rc_markup.index('<div class="ring-wrap">')
r1 = rc_markup.index('Overall ready</small></div>', r0)
r1 = rc_markup.index('</div>', r1 + len('Overall ready</small></div>')) + 6
rc_markup = rc_markup[:r0] + rc_markup[r1:]
assert 'Overall ready' not in rc_markup
rc_css += '\n.ready{grid-template-columns:1fr}\n.cx-reading{outline:3px solid rgba(242,106,27,.55);outline-offset:-5px;transition:outline-color .3s}\n'
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
mid = mid.replace('id="journey"', 'id="kjourney"').replace('href="#journey"', 'href="#kjourney"')
closing = closing.replace('href="#journey"', 'href="#kjourney"')
k_script = k_script.replace('#journey"', '#kjourney"')

# --- Kukua narration: read the whole page, in order, from the hero
def patch(old, new):
    global k_script
    assert k_script.count(old) == 1, old[:60]
    k_script = k_script.replace(old, new)
patch('V.paused=false;setSpeaking(false)}', 'V.paused=false;V.after=null;setSpeaking(false)}')
patch('a.onplay=()=>setSpeaking(true);a.onended=()=>setSpeaking(false);a.onerror=()=>setSpeaking(false);\n  a.play().catch(()=>setSpeaking(false));',
      'const fin=()=>{setSpeaking(false);const f=V.after;V.after=null;if(f)f()};\n  a.onplay=()=>setSpeaking(true);a.onended=fin;a.onerror=fin;\n  a.play().catch(()=>{setSpeaking(false);cancelTour()});')
patch('function narrate(text,audioUrl){', 'function narrate(text,audioUrl,fromTour){if(!fromTour)cancelTour();')
patch('if(speak){if(i===0)', 'if(speak&&!V.tour){if(i===0)')
patch('if(e.isIntersecting&&!seen.has(k)&&$("#dock").classList.contains("show")){', 'if(false){')
patch('V.enabled=true;V.muted=false;speakText(V.current,V.currentAudio);syncCtl();', 'V.enabled=true;V.muted=false;if(!V.touredOnce||V.tourDone){V.touredOnce=true;startTour(0)}else speakText(V.current,V.currentAudio);syncCtl();')
patch('function toggleMute(){V.muted=!V.muted;if(V.muted)stopVoice();syncCtl()}', 'function toggleMute(){V.muted=!V.muted;if(V.muted){cancelTour();stopVoice()}syncCtl()}')
patch('"Tap play to hear Kukua"', '"Tap play and I\'ll read the whole page"')
patch('new IntersectionObserver(([e])=>$("#dock").classList.toggle("show",!e.isIntersecting),{threshold:.15}).observe($("#stage"));', '$("#dock").classList.add("show");')
patch(':vh(text);', ':vh(sp(text));')
patch('if(e.isIntersecting&&!closedNarrated){closedNarrated=true;narrate(cm,msg("closing").AudioUrl)}', 'if(false){}')
patch('setTimeout(()=>narrate(msg("welcome").Text,msg("welcome").AudioUrl),reduced?0:1200);',
      'setTimeout(()=>{narrate(msg("welcome").Text,msg("welcome").AudioUrl,true);$("#dText").textContent="Tap play and I\'ll read this whole page to you, from the top."},reduced?0:1200);')
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
       + rc_a + '\n<div class="kx">\n' + hero + mid + '</div>\n' + rc_b
       + '\n<div class="kx">\n' + closing + '</div>\n' + rc_c
       + '\n<div class="kx">\n' + overlays + '</div>\n'
       + voice_script + '\n<script>' + wrap(k_script) + '</script>\n<script>' + wrap(rc_script) + '</script>\n</body>\n</html>\n')
open(OUT, 'w', encoding='utf8').write(doc)
print('written', OUT, len(doc) // 1024, 'KB; keyframes prefixed:', sorted(names))
