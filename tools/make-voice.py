#!/usr/bin/env python3
"""Records every line Kukua speaks that has no recording yet (neural voice af_heart, needs kokoro-onnx + model files in $KOKORO_DIR)."""
import json, os, subprocess, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KD = os.environ.get('KOKORO_DIR', '/tmp/kokoro')
D = json.load(open(os.path.join(ROOT, 'seed/defaults.json')))
texts = {}
for m in D['KukuaMessages']: texts[m['Key']] = m['Text']
for i, s in enumerate(sorted(D['JourneyStages'], key=lambda x: x['Order'])): texts['stage%d' % (i + 1)] = s['KukuaSays']
extra = [m['Text'] for m in D['SectionIntros']] + [s['PanelKukua'] for s in D['JourneyStages'] if s.get('PanelKukua')] \
      + [f['KukuaCommentary'] for f in D['FeaturedGuides']] + ["That video is coming soon. Keep an eye on this space!"]
hasher = "const vh=t=>{let h=5381;for(let i=0;i<t.length;i++)h=((h<<5)+h+t.charCodeAt(i))|0;return 't'+(h>>>0).toString(16)};console.log(JSON.stringify(JSON.parse(require('fs').readFileSync(0,'utf8')).map(vh)))"
names = json.loads(subprocess.run(['node', '-e', hasher], input=json.dumps(extra), capture_output=True, text=True, check=True).stdout)
for n, t in zip(names, extra): texts.setdefault(n, t)
out = os.path.join(ROOT, 'preview/voice/emily'); os.makedirs(out, exist_ok=True)
k = Kokoro(os.path.join(KD, 'kokoro-v1.0.int8.onnx'), os.path.join(KD, 'voices-v1.0.bin'))
made = 0
for n, t in texts.items():
    f = os.path.join(out, n + '.mp3')
    if os.path.exists(f): continue
    a, sr = k.create(t, voice='af_heart', speed=0.97, lang='en-us'); sf.write('/tmp/_v.wav', a, sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/_v.wav', '-b:a', '64k', '-ac', '1', f], check=True); made += 1
json.dump(texts, open(os.path.join(ROOT, 'seed/voice/voice-script.json'), 'w'), ensure_ascii=False, indent=1)
print('recorded', made, 'new; total', len(texts))
