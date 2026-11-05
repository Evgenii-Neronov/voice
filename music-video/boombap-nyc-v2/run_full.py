from pathlib import Path
import subprocess,json,time,re,concurrent.futures,threading
W=Path(__file__).resolve().parent;ROOT=W.parents[1];OUT=ROOT/'outputs/nyc-boombap-v2-1440p';BLENDER=W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'
OUT.mkdir(exist_ok=True);ranges=[(a,min(6079,a+506)) for a in range(1,6080,507)];start=time.time();state={};lock=threading.Lock()
def render(job):
 idx,(a,b)=job;dest=W/f'part-{idx:02d}.mp4';lp=W/f'full-{idx:02d}.log'
 with lock:state[idx]={'start':a,'end':b,'last':a-1,'state':'starting'}
 cmd=[str(BLENDER),'--gpu-backend','vulkan','-b',str(W/'film-v2.blend'),'-t','4','--python',str(W/'render_baked.py'),'--',str(a),str(b),str(dest),'100','eevee']
 with lp.open('w',encoding='utf8') as log:
  p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  while p.poll() is None:
   text=lp.read_text(errors='replace');matches=re.findall(r'Append frame (\d+)',text)
   with lock:state[idx].update(last=int(matches[-1]) if matches else a-1,state='rendering',pid=p.pid)
   time.sleep(5)
 if p.returncode:raise RuntimeError(f'Worker {idx} exit {p.returncode}; see {lp}')
 with lock:state[idx].update(last=b,state='complete')
 return dest
with concurrent.futures.ThreadPoolExecutor(3) as pool:
 fs=[pool.submit(render,j) for j in enumerate(ranges)]
 while not all(f.done() for f in fs):
  with lock:
   count=sum(max(0,x['last']-x['start']+1) for x in state.values());elapsed=time.time()-start
   report={'state':'rendering','frames':count,'total':6079,'seconds':round(elapsed,1),'fps':round(count/max(1,elapsed),3),'parts':dict(state)}
  (W/'status.json').write_text(json.dumps(report,indent=2));time.sleep(10)
 parts=[f.result() for f in fs]
(W/'parts.txt').write_text('\n'.join(f"file '{p.name}'" for p in parts),encoding='utf8')
cmd=['ffmpeg','-hide_banner','-y','-f','concat','-safe','0','-i','parts.txt','-i',str(ROOT/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3'),'-vf','ass=subtitles.ass','-t','253.283265','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-movflags','+faststart',str(OUT/'ADV-boombap-NYC-v2-1440p.mp4')]
with (W/'encode.log').open('w') as log:subprocess.run(cmd,cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
(W/'status.json').write_text(json.dumps({'state':'complete','frames':6079,'seconds':round(time.time()-start,1),'output':str(OUT/'ADV-boombap-NYC-v2-1440p.mp4')},indent=2))
print('COMPLETE',flush=True)
