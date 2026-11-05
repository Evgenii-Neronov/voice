from pathlib import Path
import hashlib,json,importlib.metadata as md
w=Path('work/nyc-boombap-v2');m=Path('I:/VOICE/voice/models/lipsync/wav2vec2-espeak')
report={'python_packages':{k:md.version(k) for k in ['torch','transformers','numpy','scipy','soundfile']},'model':{'id':'facebook/wav2vec2-xlsr-53-espeak-cv-ft','license':'Apache-2.0','path':str(m)},'files':[]}
for p in list((w/'assets').rglob('*'))+list(m.glob('*')):
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
  report['files'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
(w/'dependencies.json').write_text(json.dumps(report,indent=2))
print(report['python_packages']);print('assets',len(report['files']))
