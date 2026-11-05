from pathlib import Path
import json,shutil,zipfile,hashlib,subprocess,sys
W=Path(__file__).resolve().parent;ROOT=W.parents[1];O=ROOT/'outputs/nyc-boombap-v2-1440p'
status=json.loads((W/'status.json').read_text());validation=json.loads((O/'validation.json').read_text());assert status['state']=='complete';assert validation['full_decode']=='passed'
for name in ['scene-validation.json','subtitle-validation.json']:shutil.copy2(W/name,O/name)
production={'track':'07-minimax-trio-boombap-01.mp3','version':'NYC v2','video':validation['video'],'duration_seconds':validation['duration'],'native_resolution':[2560,1440],'fps':24,'frames':6079,'final_render_and_mux_seconds':status['seconds'],'renderer':'Blender 4.5.9 EEVEE / Vulkan, 24 samples, ray tracing enabled','shadow_fix':'Distant Streetlight and Streetlight.002 keep illumination but do not allocate shadow maps; performer key-light shadows remain enabled','editable_scene':'project/NYC-boombap-v2.blend','original_audio_preserved':True,'weights_committed':False,'lip_sync':'Locally recognized phonemes mapped to 15 visemes; approximate automatic articulation','passerby':'Reference-inspired approximation; calibrated 1.83m rest body height, excluding hat','limitations':validation['known_limits']}
(O/'production.json').write_text(json.dumps(production,ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(W/'README.md',O/'ASSET-SOURCES.md')
backup=O/'project/NYC-boombap-v2.blend1'
if backup.exists():
 target=W/'project-backup-before-delivery.blend'
 assert backup.resolve().is_relative_to(ROOT.resolve()) and target.resolve().is_relative_to(ROOT.resolve())
 if not target.exists():shutil.move(str(backup),str(target))
subprocess.run([sys.executable,str(W/'archive_project.py')],check=True,cwd=ROOT)
p=O/'editable-3D-project-v2.zip'
with zipfile.ZipFile(p,'a',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for name in ['validation.json','project-validation.json','scene-validation.json','subtitle-validation.json','production.json']:z.write(O/name,name)
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None;names=z.namelist()
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
(O/'archive-validation.json').write_text(json.dumps({'archive':p.name,'bytes':p.stat().st_size,'sha256':h.hexdigest(),'crc_check':'passed','entries':names},indent=2))
print('FINAL ARTIFACTS COMPLETE',flush=True)
