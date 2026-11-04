"""Check actual PCM splices, hashes and independent short speech excerpts locally."""
import os,json,hashlib,sys
from pathlib import Path
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1]; sys.stdout.reconfigure(encoding='utf-8'); w=R/'work/editable'; root=R/'results/editable/modular'
a,sr=sf.read(root/'01-original-beat.wav'); b,_=sf.read(root/'02-beat-patch.wav'); c,_=sf.read(root/'03-line-retake.wav')
assert np.array_equal(a[:10*sr],b[:10*sr]) and np.array_equal(a[20*sr:],b[20*sr:])
assert np.array_equal(a[:int(32.5*sr)],c[:int(32.5*sr)]) and np.array_equal(a[int(37.5*sr):],c[int(37.5*sr):])
for x in [a,b,c]: assert np.isfinite(x).all() and np.max(np.abs(x))<1
m=json.loads((root/'manifest.json').read_text(encoding='utf-8')); m['validated']['actual_pcm24_unchanged_outside_edit']=True; (root/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
d=R/'.venvs/qwen/Lib/site-packages/torch/lib'; os.environ['PATH']=str(d)+os.pathsep+os.environ['PATH']; handle=os.add_dll_directory(str(d))
from faster_whisper import WhisperModel
model=WhisperModel(str(R/'models/asr-whisper-small'),device='cuda',compute_type='float16',local_files_only=True,cpu_threads=4)
checks=[('f5-greeting',root/'greeting.wav',None,None),('f5-changed-line',root/'changed-line.wav',None,None),('f5-ezhi',root/'ezhi-one.wav',None,None)]
mini=R/'results/productions/editable-minimax-01/full.wav'; checks += [('minimax-greeting',mini,0,4),('minimax-changed-line',mini,71,77),('minimax-ezhi',mini,131.1,132.85)]
if '--natural-only' in sys.argv: checks=[('f5-natural-line',w/'phrases/changed-line-take-2026110566.wav',None,None)]
rows=[]
for name,path,start,end in checks:
 if start is not None:
  x,s=sf.read(path,always_2d=True); path=w/(name+'-check.wav'); sf.write(path,x[int(start*s):int(end*s)].mean(axis=1),s)
 segs,_=model.transcribe(str(path),language='ru',beam_size=3,condition_on_previous_text=False,vad_filter=False); text=' '.join(t.text for t in segs); rows.append({'clip':name,'automatic_transcript':text}); print(name,text,flush=True)
(R/'results/editable'/('natural-check.json' if '--natural-only' in sys.argv else 'checks.json')).write_text(json.dumps({'local_asr':'faster-whisper-small CUDA','not_human_listening':True,'pcm_splice_checks_passed':True,'clips':rows},ensure_ascii=False,indent=2),encoding='utf-8')
