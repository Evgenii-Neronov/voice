import subprocess,concurrent.futures,json,time,os
from pathlib import Path
W=Path(__file__).resolve().parent;B=Path(os.environ.get('BLENDER_EXE',str(W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe')));plan=json.loads((W/'edit-plan.json').read_text())
def valid(sh):
 p=W/'shots'/f"{sh['index']:02d}.mp4"
 if not p.exists():return False
 try:
  d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,width','-of','json',str(p)],stderr=subprocess.DEVNULL))['streams'][0];return int(d['nb_frames'])==sh['frames'] and d['width']==2560
 except Exception:return False
def run(sh):
 i=sh['index'];kind=sh['scene'];t=time.time()
 if not valid(sh):
  scene=W/'street-v6.blend' if kind=='street' else W/'sets'/f'{kind}.blend';script=W/('render_street.py' if kind=='street' else 'render_shot.py')
  with (W/f'render-{i:02d}.log').open('w') as log:subprocess.run([str(B),'-b',str(scene),'--gpu-backend','vulkan','--python',str(script),'--',str(i),'full'],stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 assert valid(sh),i
 r={'index':i,'returncode':0,'seconds':time.time()-t};(W/f'status-{i:02d}.json').write_text(json.dumps(r));print(r,flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,plan))
 print('ALL SHOTS COMPLETE',flush=True)
