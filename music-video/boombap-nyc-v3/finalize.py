from pathlib import Path
import json,shutil,subprocess,sys,hashlib,zipfile
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-v3-1440p'
s=json.loads((W/'status.json').read_text());v=json.loads((O/'validation.json').read_text());assert s['state']=='complete' and v['full_decode']=='passed'
for name in ['motion-validation.json','lighting-v1.json','beats.json','subtitle-validation.json']:shutil.copy2(W/name,O/name)
p={'version':'NYC v3','video':v['video'],'render_and_mux_seconds':s['seconds'],'changes':['Continuous quaternion keyframes on all three performers','Independent beat-linked listener movement','No passerby or NY cap lettering','V1 light/world/exposure restored','144px yellow bottom-centred subtitle margin'],'original_audio':True,'resolution':[2560,1440],'fps':24,'frames':6079,'preview_review':'12-second preliminary moving preview and 15-second final opening temporal contact sheets; final sampled frames reviewed; not a claim of full playback','limits':v['known_limits']}
(O/'production.json').write_text(json.dumps(p,indent=2));shutil.copy2(W/'README.md',O/'ASSET-SOURCES.md')
subprocess.run([sys.executable,str(W/'archive_project.py')],cwd=W.parents[1],check=True)
zpath=O/'editable-3D-project-v3.zip'
with zipfile.ZipFile(zpath,'a',zipfile.ZIP_DEFLATED) as z:
 for name in ['validation.json','project-validation.json','motion-validation.json','lighting-v1.json','beats.json','subtitle-validation.json','production.json']:z.write(O/name,name)
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
h=hashlib.sha256()
with zpath.open('rb') as f:
 for b in iter(lambda:f.read(4194304),b''):h.update(b)
(O/'archive-validation.json').write_text(json.dumps({'file':zpath.name,'bytes':zpath.stat().st_size,'sha256':h.hexdigest(),'crc_check':'passed'},indent=2));print('Final artifacts verified')
