from pathlib import Path
import skia,numpy as np,math,json,subprocess,time
W=Path(__file__).resolve().parent;PLAN=json.loads((W/'edit-plan.json').read_text())
def col(h,a=255):h=h.lstrip('#');return skia.ColorSetARGB(a,int(h[:2],16),int(h[2:4],16),int(h[4:],16))
def paint(h,width=0,a=255):
 p=skia.Paint(Color=col(h,a),AntiAlias=True)
 if width:p.setStyle(skia.Paint.kStroke_Style);p.setStrokeWidth(width);p.setStrokeCap(skia.Paint.kRound_Cap);p.setStrokeJoin(skia.Paint.kRound_Join)
 return p
def line(c,pts,h,w,progress=1,offset=(0,0),alpha=255):
 if progress<=0:return
 end=max(2,min(len(pts),round(len(pts)*progress)));p=skia.Path();p.moveTo(pts[0][0]+offset[0],pts[0][1]+offset[1])
 for x,y in pts[1:end]:p.lineTo(x+offset[0],y+offset[1])
 c.drawPath(p,paint(h,w,alpha))
def path(seed):
 rng=np.random.default_rng(seed);pts=[]
 for j in range(9):
  phase=j*.39;xy=[]
  for u in np.linspace(0,1,200):
   x=400+1700*u+110*math.sin(u*math.tau*1.5+phase);y=620+220*math.sin(u*math.tau*2+phase)+j*20-80
   xy.append((x,y))
  pts.append((xy,70-j*3,['#d5ab48','#246778','#ae5d3e','#d4c7a3'][j%4],j*.055))
 # Rings suggest exchange/circular time, with an imperfect sprayed contour.
 for j in range(3):
  xy=[]
  for a in np.linspace(-.6,math.tau-.6,220):
   r=190+j*12+12*math.sin(a*3+j);xy.append((730+j*500+r*math.cos(a),620+r*.7*math.sin(a)))
  pts.append((xy,20,['#eee1bc','#233c48','#caaa50'][j],.16+j*.07))
 # Angular branches grow from the organic strokes, without spelling a word.
 for j in range(8):
  x=480+j*210;y=500+70*math.sin(j);xy=[(x,790),(x+35,y+80),(x+130,y),(x+190,y-190)]
  dense=[]
  for a,b in zip(xy,xy[1:]):dense.extend([(a[0]+u*(b[0]-a[0]),a[1]+u*(b[1]-a[1])) for u in np.linspace(0,1,40)])
  pts.append((dense,9,'#e5d4a8',.3+j*.025))
 return pts
PATHS=path(318)
def base():
 rng=np.random.default_rng(18);noise=np.clip(rng.normal(0,3,(720,1280,1))+np.array([36,40,43]),0,255).astype(np.uint8);arr=np.concatenate([noise,np.full((720,1280,1),255,np.uint8)],axis=2)
 return skia.Image.fromarray(arr,colorType=skia.ColorType.kRGBA_8888_ColorType)
BASE=base()
FONT=skia.Font(skia.Typeface.MakeFromFile(str(W.parent/'nyc-boombap-v2/assets/RubikWetPaint-Regular.ttf')),220)
WORD='ЭКВИВАЛЕНТ'
WIDTH=FONT.measureText(WORD);X=(2560-WIDTH)/2

def frame(u,variant):
 s=skia.Surface(2560,1440);c=s.getCanvas();c.clear(col('#24282b'));c.drawImageRect(BASE,skia.Rect.MakeWH(2560,1440))
 # Broad painted branches become the underline of the final lettering.
 for j,(pts,w,h,delay) in enumerate(PATHS[:5]):
  pts=[(x,920+(y-620)*.28) for x,y in pts]
  prog=float(np.clip(u/.5-j*.06,0,1));line(c,pts,'#101b22',w*.45+12,prog,(8,10));line(c,pts,h,w*.45,prog)
 # Staggered rising letter masks grow into a readable word; hold final 30%.
 x=X
 for j,ch in enumerate(WORD):
  advance=FONT.measureText(ch);v=float(np.clip((u-j*.028)/.4,0,1));v=v*v*(3-2*v)
  c.save();c.clipRect(skia.Rect.MakeLTRB(x-20,820-330*v,x+advance+30,850))
  outline=paint('#101b22',22);c.drawString(ch,x+9,790,FONT,outline)
  c.drawString(ch,x,778,FONT,paint('#ead49c',12));c.drawString(ch,x,778,FONT,paint('#c89137'))
  c.restore();x+=advance
 return s.makeImageSnapshot()
if __name__=='__main__':
 (W/'shots').mkdir(exist_ok=True)
 for sh in PLAN:
  if sh['scene']!='graffiti':continue
  dest=W/'shots'/f"{sh['index']:02d}.mp4";n=sh['frames'];cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s','2560x1440','-r','24','-i','pipe:0','-an','-c:v','h264_nvenc','-preset','p5','-cq','18','-pix_fmt','yuv420p',str(dest)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  for i in range(n):p.stdin.write(frame(i/(n-1),sh['index']).tobytes())
  p.stdin.close();assert p.wait()==0;print('Graffiti',sh['index'],'complete',flush=True)
