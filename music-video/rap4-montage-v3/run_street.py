from pathlib import Path
import subprocess,time,json,re,concurrent.futures,threading,os,shutil
W=Path(__file__).resolve().parent;B=Path(os.environ.get('BLENDER_EXE') or shutil.which('blender') or str(W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'));R=W/'render_part.py';state={};lock=threading.Lock();start=time.time()
def render(job):
 name,a,b=job;p=W/(name+'.mp4');log=W/(name+'.log')
 with log.open('w') as f:
  proc=subprocess.Popen([str(B),'-b',str(W/'street-no-graffiti.blend'),'-t','4','--python',str(R),'--',str(a),str(b),str(p),'100'],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  while proc.poll() is None:
   m=re.findall(r'Append frame (\d+)',log.read_text(errors='replace'))
   with lock:state[name]={'last':int(m[-1]) if m else a-1,'start':a,'end':b}
   time.sleep(4)
 if proc.returncode:raise RuntimeError(name)
 with lock:state[name]={'last':b,'start':a,'end':b,'complete':True}
with concurrent.futures.ThreadPoolExecutor(2) as pool:
 fs=[pool.submit(render,x) for x in [('street-opening',1,96),('street-outro',2989,3279)]]
 while not all(f.done() for f in fs):
  with lock:r={'state':'rendering','seconds':time.time()-start,'parts':dict(state)}
  (W/'street-status.json').write_text(json.dumps(r,indent=2));time.sleep(6)
 [f.result() for f in fs]
(W/'street-status.json').write_text(json.dumps({'state':'complete','seconds':time.time()-start},indent=2))
