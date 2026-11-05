from pathlib import Path
import subprocess,json,time,re,concurrent.futures,threading,sys
W=Path(__file__).resolve().parent;ROOT=W.parents[1];OUT=ROOT/'outputs/rap4-cartoon-v2-1440p';OUT.mkdir(exist_ok=True);BLENDER=W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'
preview='--preview' in sys.argv
ranges=[(1,121)] if preview else [(a,min(3279,a+359)) for a in range(1,3280,360)]
state={};lock=threading.Lock();start=time.time()
def render(job):
 idx,(a,b)=job;dest=W/(f'preview-silent.mp4' if preview else f'part-{idx:02d}.mp4');lp=W/(f'preview.log' if preview else f'full-{idx:02d}.log')
 with lock:state[idx]={'start':a,'end':b,'last':a-1,'state':'rendering'}
 with lp.open('w',encoding='utf8') as log:
  p=subprocess.Popen([str(BLENDER),'--gpu-backend','vulkan','-b',str(W/'evening-isometric.blend'),'-t','4','--python',str(W/'render_part.py'),'--',str(a),str(b),str(dest),'50' if preview else '100'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
  while p.poll() is None:
   matches=re.findall(r'Append frame (\d+)',lp.read_text(errors='replace'))
   with lock:state[idx]['last']=int(matches[-1]) if matches else a-1
   time.sleep(4)
 if p.returncode:raise RuntimeError(f'{lp}: exit {p.returncode}')
 with lock:state[idx].update(last=b,state='complete')
 return dest
with concurrent.futures.ThreadPoolExecutor(1 if preview else 2) as pool:
 fs=[pool.submit(render,j) for j in enumerate(ranges)]
 while not all(f.done() for f in fs):
  with lock:report={'state':'rendering','frames':sum(max(0,v['last']-v['start']+1) for v in state.values()),'total':sum(b-a+1 for a,b in ranges),'seconds':round(time.time()-start,1),'parts':dict(state)}
  (W/('preview-status.json' if preview else 'status.json')).write_text(json.dumps(report,indent=2));time.sleep(6)
 parts=[f.result() for f in fs]
concat=W/('preview-parts.txt' if preview else 'parts.txt');concat.write_text('\n'.join(f"file '{p.name}'" for p in parts),encoding='utf8')
audio='I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3';dest=OUT/('opening-preview.mp4' if preview else 'ADV-rap4-evening-isometric-1440p.mp4')
vf='scale=2560:1440,ass=subtitles.ass,scale=1280:720,fps=24' if preview else 'ass=subtitles.ass,fps=24'
with (W/'encode.log').open('w') as log:subprocess.run(['ffmpeg','-hide_banner','-y','-f','concat','-safe','0','-i',str(concat),'-i',audio,'-vf',vf,'-t','10.083333' if preview else '273.188571','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-movflags','+faststart',str(dest)],cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
(W/('preview-status.json' if preview else 'status.json')).write_text(json.dumps({'state':'complete','seconds':round(time.time()-start,1),'output':str(dest)},indent=2));print('COMPLETE',flush=True)
