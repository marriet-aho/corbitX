#!/usr/bin/env python3
"""Records every clip listed in preview/voice/clips.json that has no MP3 yet (voice af_heart via kokoro-onnx).
   node tools/list-clips.js && python3 tools/make-page-voice.py && python3 tools/merge-readiness.py"""
import json, os, subprocess, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KD = os.environ.get('KOKORO_DIR', '/tmp/kokoro')
out = os.path.join(ROOT, 'preview/voice/emily')
clips = json.load(open(os.path.join(ROOT, 'preview/voice/clips.json')))
k = Kokoro(os.path.join(KD, 'kokoro-v1.0.int8.onnx'), os.path.join(KD, 'voices-v1.0.bin'))
made = 0
for c in clips:
    f = os.path.join(out, c['name'] + '.mp3')
    if os.path.exists(f): continue
    a, sr = k.create(c['say'], voice='af_heart', speed=0.97, lang='en-us'); sf.write('/tmp/_v.wav', a, sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/_v.wav', '-b:a', '48k', '-ac', '1', f], check=True)
    made += 1; print(made, c['name'], round(len(a) / sr), 's', flush=True)
print('recorded', made, 'new clips; total', len(clips))
