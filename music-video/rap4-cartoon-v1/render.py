import argparse,subprocess,math,time,json
from pathlib import Path
import art
W=Path(__file__).resolve().parent;O=(W/'renders') if (W/'PROJECT.txt').exists() else W.parents[1]/'outputs/rap4-cartoon-1440p';O.mkdir(parents=True,exist_ok=True);TRACK='I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3'
if (W/'audio/track.mp3').exists():TRACK=str(W/'audio/track.mp3')
p=argparse.ArgumentParser();p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,default=273.188571);p.add_argument('--name',default='ADV-rap4-cartoon-1440p');a=p.parse_args();out=O/(a.name+'.mp4');start=time.time();n=math.ceil(a.duration*12)
cmd=['ffmpeg','-hide_banner','-y','-f','rawvideo','-pix_fmt','bgra','-s','2560x1440','-r','12','-i','pipe:0','-ss',str(a.start),'-i',TRACK,'-vf',f'setpts=PTS+{a.start}/TB,ass=subtitles.ass,setpts=PTS-{a.start}/TB,fps=24','-t',str(a.duration),'-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-movflags','+faststart',str(out)]
with (W/(a.name+'.log')).open('w') as log:
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,cwd=W,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  art.init()
  for i in range(n):
   im=art.frame(a.start+i/12);proc.stdin.write(im.tobytes())
   if i%48==0:(W/(a.name+'-status.json')).write_text(json.dumps({'state':'rendering','drawings':i,'total':n,'seconds':round(time.time()-start,2)}))
 finally:proc.stdin.close()
 rc=proc.wait();assert rc==0,rc
(W/(a.name+'-status.json')).write_text(json.dumps({'state':'complete','drawings':n,'seconds':round(time.time()-start,2),'output':str(out)},indent=2));print('COMPLETE',out.name,round(time.time()-start,2),flush=True)
