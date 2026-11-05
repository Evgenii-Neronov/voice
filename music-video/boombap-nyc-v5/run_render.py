import subprocess,concurrent.futures,json,time,os
from pathlib import Path
W=Path(__file__).resolve().parent;B=Path(os.environ.get('BLENDER_EXE',str(W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe')));plan=json.loads((W/'edit-plan.json').read_text())
def run(sh):
 i=sh['index'];kind=sh['scene'];scene=W/'street-v5.blend' if kind=='street' else W/'sets'/f'{kind}.blend';script=W/('render_street.py' if kind=='street' else 'render_shot.py');t=time.time()
 with (W/f'render-{i:02d}.log').open('w') as log:
  p=subprocess.run([str(B),'-b',str(scene),'--gpu-backend','vulkan','--python',str(script),'--',str(i),'full'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 result={'index':i,'returncode':p.returncode,'seconds':time.time()-t};(W/f'status-{i:02d}.json').write_text(json.dumps(result));print(result,flush=True)
 if p.returncode:raise RuntimeError(result)
if __name__=='__main__':
 selected=[s for s in plan if s['scene']=='street']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,selected))
 print('STREET COMPLETE',flush=True)
