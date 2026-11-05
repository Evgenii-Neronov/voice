from pathlib import Path
import json,zipfile,hashlib,shutil
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/rap4-cartoon-1440p';P=O/'project'
v=json.loads((O/'validation.json').read_text());s=json.loads((W/'ADV-rap4-cartoon-1440p-status.json').read_text());assert v['full_decode']=='passed' and s['state']=='complete'
for name in ['README.md','BRIEF.md','dependencies.json','project-validation.json','audio-manifest.json']:
 shutil.copy2(W/name,O/('TECHNICAL.md' if name=='README.md' else name))
production={'version':'Rap4 cartoon v1','render_seconds':s['seconds'],'drawings':s['drawings'],'duration':v['duration'],'video_sha256':v['sha256'],'quality_control':'Full decode, audio correlation, subtitle dash checks, moving previews and18 final sampled frames','camera_fix':'Camera centre clamped inside background extents at every zoom; final render regenerated','source_audio_unchanged':True,'reference_image_uploaded':False}
(O/'production.json').write_text(json.dumps(production,indent=2))
for name in ['validation.json','production.json','project-validation.json']:shutil.copy2(O/name,P/name)
zpath=O/'editable-cartoon-project.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for f in P.rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and 'renders' not in f.parts:z.write(f,f.relative_to(P))
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
h=hashlib.sha256(zpath.read_bytes()).hexdigest();(O/'archive-validation.json').write_text(json.dumps({'archive':zpath.name,'bytes':zpath.stat().st_size,'sha256':h,'crc_check':'passed'},indent=2));print('Project archive complete',zpath.stat().st_size)
