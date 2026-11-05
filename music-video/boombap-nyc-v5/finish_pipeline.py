from pathlib import Path
import subprocess,time,json,sys,os
W=Path(__file__).resolve().parent;PY=sys.executable;B=W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'
def state(s):
 (W/'pipeline-status.json').write_text(json.dumps({'state':s,'time':time.time()}));print(s,flush=True)
state('Waiting for approved dance render')
while not (W/'render-11.log').exists() or 'Blender quit' not in (W/'render-11.log').read_text(errors='replace'):time.sleep(5)
state('Rendering second bird-whistle shot')
with (W/'render-14.log').open('w') as f:
 subprocess.run([str(B),'-b',str(W/'sets/lab.blend'),'--gpu-backend','vulkan','--python',str(W/'render_shot.py'),'--','14','full'],stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
state('Waiting for grounded street shots')
indices=[s['index'] for s in json.loads((W/'edit-plan.json').read_text()) if s['scene']=='street']
while True:
 good=True
 for i in indices:
  p=W/f'status-{i:02d}.json'
  if not p.exists() or json.loads(p.read_text()).get('returncode')!=0:good=False
 if good:break
 time.sleep(10)
for script in ['assemble.py','verify.py','package_project.py']:
 state(script)
 with (W/(script+'.log')).open('w') as f:subprocess.run([PY,'-X','utf8',str(W/script)],stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
state('Complete')
