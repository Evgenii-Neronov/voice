import argparse,json,math,subprocess,time
from pathlib import Path
import film_art
W=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--start',type=float,default=8);p.add_argument('--end',type=float,default=249);p.add_argument('--name',default='illustrated-middle');a=p.parse_args()
n=round((a.end-a.start)*24);begin=time.time()
cmd=['ffmpeg','-hide_banner','-y','-f','rawvideo','-pix_fmt','bgra','-s','2560x1440','-r','24','-i','pipe:0','-an','-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0','-pix_fmt','yuv420p','-movflags','+faststart',str(W/(a.name+'.mp4'))]
with (W/(a.name+'.log')).open('w') as log:
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  for i in range(n):
   proc.stdin.write(film_art.frame(a.start+i/24).tobytes())
   if i%72==0:(W/(a.name+'-status.json')).write_text(json.dumps({'state':'rendering','frame':i,'total':n,'seconds':time.time()-begin}))
 finally:proc.stdin.close()
 assert proc.wait()==0,'See encoder log'
(W/(a.name+'-status.json')).write_text(json.dumps({'state':'complete','frames':n,'seconds':time.time()-begin},indent=2))
print('COMPLETE',a.name,flush=True)
