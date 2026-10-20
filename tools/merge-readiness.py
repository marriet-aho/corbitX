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
rc_script = sub1(r'goLiveConfirmed: false', 'goLiveConfirmed: true', rc_script)
rc_script = rc_script.replace('["home","guides","journey","hub","coming"]', '["home","kjourney","guides","journey","hub","coming"]')
assert '"kjourney"' in rc_script
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
voice_script = KJ[vs:ve]
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
old = 'new IntersectionObserver(([e])=>$("#dock").classList.toggle("show",!e.isIntersecting),{threshold:.15}).observe($("#stage"));'
assert old in k_script
k_script = k_script.replace(old, 'let stageSeen=false;new IntersectionObserver(([e])=>{if(e.isIntersecting)stageSeen=true;$("#dock").classList.toggle("show",stageSeen&&!e.isIntersecting)},{threshold:.15}).observe($("#stage"));')
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
