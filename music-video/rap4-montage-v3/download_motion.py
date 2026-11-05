from pathlib import Path
import urllib.request,json,time,hashlib
W=Path(__file__).resolve().parent;D=Path('I:/VOICE/voice/models/motion/aistplusplus');D.mkdir(parents=True,exist_ok=True);p=D/'keypoints3d.zip'
u='https://github.com/google/aistplusplus_dataset/releases/download/v1.0/keypoints3d.zip'
if not p.exists():
 with urllib.request.urlopen(u+'?download=1&v=20261105',timeout=60) as r, (D/'keypoints3d.partial').open('wb') as f:
  size=0
  while b:=r.read(1048576):
   f.write(b);size+=len(b)
   if size%10485760==0:print('Downloaded MB',size//1048576,flush=True)
 (D/'keypoints3d.partial').replace(p)
h=hashlib.sha256()
with p.open('rb') as f:
 while b:=f.read(4194304):h.update(b)
(W/'dataset-download.json').write_text(json.dumps({'source':u,'path':str(p),'bytes':p.stat().st_size,'sha256':h.hexdigest(),'license':'CC BY4.0 for annotations; original video not used'},indent=2));print('COMPLETE',flush=True)
