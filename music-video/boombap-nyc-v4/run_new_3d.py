from pathlib import Path
import json,subprocess,time,re,threading,concurrent.futures,os,shutil
W=Path(__file__).resolve().parent;B=Path(os.environ.get('BLENDER_EXE') or shutil.which('blender') or str(W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'));PLAN=json.loads((W/'edit-plan.json').read_text());jobs=[s for s in PLAN if s['scene'] not in ['street','graffiti']];state={};lock=threading.Lock();begin=time.time()
def run(s):
 i=s['index'];log=W/f'render-{i:02d}.log'
 with lock:state[i]={'frames':s['frames'],'last':0,'scene':s['scene']}
 with log.open('w') as f:
  p=subprocess.Popen([str(B),'--gpu-backend','vulkan','-b',str(W/'sets'/f"{s['scene']}.blend"),'-t','4','--python',str(W/'render_shot.py'),'--',str(i),'full'],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  while p.poll() is None:
   m=re.findall(r'Append frame (\d+)',log.read_text(errors='replace'))
   with lock:state[i]['last']=int(m[-1]) if m else 0
   time.sleep(4)
 assert p.returncode==0,f'Shot {i} failed'
 with lock:state[i].update(last=s['frames'],complete=True)
with concurrent.futures.ThreadPoolExecutor(2) as pool:
 fs=[pool.submit(run,s) for s in jobs]
 while not all(f.done() for f in fs):
  with lock:r={'state':'rendering','frames':sum(v['last'] for v in state.values()),'total':sum(s['frames'] for s in jobs),'seconds':time.time()-begin,'shots':dict(state)}
  (W/'render-status.json').write_text(json.dumps(r,indent=2));time.sleep(5)
 [f.result() for f in fs]
(W/'render-status.json').write_text(json.dumps({'state':'complete','seconds':time.time()-begin,'frames':sum(s['frames'] for s in jobs)},indent=2));print('3D COMPLETE',flush=True)
