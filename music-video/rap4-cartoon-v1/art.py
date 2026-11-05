"""Original local 2D vector cartoon artwork and deterministic puppet animation."""
from pathlib import Path
import skia,numpy as np,math,re,json,functools
W=Path(__file__).resolve().parent
WIDTH,HEIGHT=2560,1440;INK='#29252b'
def color(h,alpha=255):
 h=h.lstrip('#');return skia.ColorSetARGB(alpha,int(h[0:2],16),int(h[2:4],16),int(h[4:6],16))
def paint(h,stroke=0,alpha=255):
 p=skia.Paint(AntiAlias=True,Color=color(h,alpha));
 if stroke:p.setStyle(skia.Paint.kStroke_Style);p.setStrokeWidth(stroke);p.setStrokeJoin(skia.Paint.kRound_Join);p.setStrokeCap(skia.Paint.kRound_Cap)
 return p
@functools.lru_cache(4096)
def svg(d):
 a=re.findall(r'[MLCQZ]|[-+]?(?:\d*\.\d+|\d+)',d);p=skia.Path();i=0
 while i<len(a):
  cmd=a[i];i+=1
  n={'M':2,'L':2,'C':6,'Q':4,'Z':0}[cmd];v=list(map(float,a[i:i+n]));i+=n
  if cmd=='M':p.moveTo(*v)
  elif cmd=='L':p.lineTo(*v)
  elif cmd=='C':p.cubicTo(*v)
  elif cmd=='Q':p.quadTo(*v)
  else:p.close()
 return p
def shape(c,d,fill,stroke=INK,sw=4):
 p=svg(d) if isinstance(d,str) else d
 if fill:c.drawPath(p,paint(fill))
 if stroke:c.drawPath(p,paint(stroke,sw))
def poly(c,pts,fill,stroke=INK,sw=4):
 p=skia.Path();p.moveTo(*pts[0]);[p.lineTo(*v) for v in pts[1:]];p.close();shape(c,p,fill,stroke,sw)
def line(c,pts,col=INK,sw=3,alpha=255):
 p=skia.Path();p.moveTo(*pts[0]);[p.lineTo(*v) for v in pts[1:]];c.drawPath(p,paint(col,sw,alpha))
def rect(c,x,y,w,h,fill,stroke=INK,sw=4,r=0):
 rr=skia.Rect.MakeXYWH(x,y,w,h)
 if r:
  if fill:c.drawRoundRect(rr,r,r,paint(fill))
  if stroke:c.drawRoundRect(rr,r,r,paint(stroke,sw))
 else:
  if fill:c.drawRect(rr,paint(fill))
  if stroke:c.drawRect(rr,paint(stroke,sw))
def oval(c,x,y,rx,ry,fill,stroke=INK,sw=3,alpha=255):
 r=skia.Rect.MakeLTRB(x-rx,y-ry,x+rx,y+ry)
 if fill:c.drawOval(r,paint(fill,alpha=alpha))
 if stroke:c.drawOval(r,paint(stroke,sw,alpha))
def txt(c,text,x,y,size,col,font='arialbd.ttf',stroke=False):
 face=skia.Typeface.MakeFromFile(str(W/'assets/RubikWetPaint-Regular.ttf'));f=skia.Font(face,size)
 if stroke:c.drawString(text,x+4,y+5,f,paint(INK,6))
 c.drawString(text,x,y,f,paint(col))
def background(canvas=None):
 s=skia.Surface(WIDTH,HEIGHT);c=canvas if canvas is not None else s.getCanvas();c.clear(color('#d5c9aa'))
 # Hand-inked brownstones, warm brick and broad cool shadows.
 rect(c,0,20,2560,805,'#ac7058',None)
 rng=np.random.default_rng(142)
 for row in range(26):
  y=25+row*28
  for j in range(-1,32):
   x=j*86+(43 if row%2 else 0);shade=['#a76652','#ae745c','#b77b5f','#995d50'][rng.integers(4)]
   rect(c,x+3,y+3,80,23,shade,None);line(c,[(x+3,y+26),(x+82,y+26)],'#d4a782',1.7)
   if rng.random()<.3:line(c,[(x+10,y+10),(x+35,y+8)],'#8b584c',1)
 rect(c,0,760,2560,270,'#b9aa8f',None)
 for y in [820,885,950,1015]:line(c,[(0,y),(2560,y-4)],'#81796c',2)
 for y in [780,850,920,990]:
  for x in range(-100,2600,260):line(c,[(x,y),(x+2,y+55)],'#8c806d',2)
 for x in [20,650,1290,1950,2500]:
  rect(c,x,0,17,1020,'#704f48',None);line(c,[(x+18,0),(x+18,1020)],'#d7b38e',2)
 rect(c,0,18,2560,45,'#e5d4af');rect(c,0,65,2560,13,'#786b62',None)
 rect(c,0,418,2560,24,'#e1cba6');rect(c,0,444,2560,13,'#806b5a',None)
 def window(x,y,w=195,h=235):
  rect(c,x-14,y-14,w+28,h+30,'#e6d2aa');rect(c,x,y,w,h,'#3e5056',sw=5)
  poly(c,[(x+7,y+7),(x+w-7,y+7),(x+w-7,y+h-8),(x+7,y+h-8)],'#42555b',None)
  for yy in range(int(y+18),int(y+h),16):line(c,[(x+7,yy),(x+w-7,yy)],'#293d46',2)
  line(c,[(x+w*.5,y),(x+w*.5,y+h)],'#baae91',6);line(c,[(x,y+h*.55),(x+w,y+h*.55)],'#c7b795',6)
  poly(c,[(x+7,y+8),(x+w*.42,y+8),(x+w*.42,y+h-7),(x+7,y+h-7)],'#718482',None)
  rect(c,x-23,y+h+9,w+46,20,'#e6d1ab');poly(c,[(x-23,y+h+29),(x+w+23,y+h+29),(x+w+4,y+h+41),(x-9,y+h+41)],'#7d7162',None)
 for x in [90,390,760,1070,1430,1740,2110,2390]:window(x,130,160 if x==2390 else 185,220)
 for x in [80,400,1435,1770,2125]:window(x,505,195,235)
 # Doors and stoops are drawn as overlapping planes, not a flat photo.
 for x in [835,2350]:
  rect(c,x-15,490,240,430,'#ded0af');rect(c,x,500,210,400,'#5b4e45',sw=5)
  rect(c,x+32,537,146,145,'#263b43');rect(c,x+32,710,146,140,'#4b403b');line(c,[(x+170,745),(x+170,802)],'#d8c493',5)
  for i in range(5):
   yy=900+i*24;poly(c,[(x-25-i*14,yy),(x+240+i*14,yy),(x+254+i*14,yy+24),(x-39-i*14,yy+24)],'#a19580');line(c,[(x-30-i*14,yy+3),(x+240+i*14,yy+3)],'#d5c6a7',3)
  for side in [-1,1]:
   xx=x-24 if side<0 else x+240;line(c,[(xx,855),(xx+side*70,1015)],'#29373a',9)
   for i in range(5):line(c,[(xx+side*i*15,856+i*34),(xx+side*i*15,920+i*24)],'#29373a',5)
 # Long architectural shadow and pavement planes.
 shadow=svg('M 0 80 L 540 80 L 810 1020 L 0 1020 Z');c.drawPath(shadow,paint('#292733',alpha=48))
 # Repaint shadow translucent so linework remains visible.
 # Above shadow is replaced by a semitransparent overlay in the composed artwork.
 # Sidewalk and road.
 poly(c,[(0,1010),(2560,1010),(2560,1150),(0,1150)],'#b4afa0');rect(c,0,1150,2560,290,'#777c79',None)
 rect(c,0,1090,2560,60,'#918d80');line(c,[(0,1092),(2560,1092)],'#d3c8ac',4)
 for x in range(-100,2700,300):line(c,[(x,1012),(x-60,1090)],'#7d7c71',2)
 for x in [100,800,1640,2190]:line(c,[(x,1260),(x+110,1245),(x+170,1260),(x+370,1244)],'#535e60',2)
 for i in range(500):
  x,y=rng.uniform(0,2560),rng.uniform(1155,1440);line(c,[(x,y),(x+rng.uniform(2,10),y-1)],'#9a9c8d',1,100)
 # Small stoop fence.
 for x in range(45,650,75):line(c,[(x,900),(x,1020)],'#26383b',6)
 line(c,[(25,920),(670,920)],'#26383b',7)
 # Parked bicycle, all visible behind the listener.
 for x in [350,590]:
  oval(c,x,1010,84,84,'#7d837b','#28363a',10);oval(c,x,1010,76,76,'#a5aa9a','#d2c3a2',3)
  for a in np.linspace(0,2*np.pi,18,endpoint=False):line(c,[(x,1010),(x+73*np.cos(a),1010+73*np.sin(a))],'#526664',1.8)
  oval(c,x,1010,9,9,'#d0bca0')
 line(c,[(350,1010),(415,885),(480,1010),(350,1010),(525,885),(590,1010)],'#322c32',13)
 line(c,[(350,1010),(415,885),(480,1010),(350,1010),(525,885),(590,1010)],'#a24639',7)
 line(c,[(415,885),(525,885)],'#a24639',9);line(c,[(415,885),(405,856)],'#343333',7);rect(c,375,842,63,15,'#302e30',r=6)
 line(c,[(525,885),(538,844),(570,839)],'#30383b',8);line(c,[(480,1010),(504,1025),(520,1025)],'#30383b',5)
 # Tape boombox on the sidewalk.
 rect(c,2045,938,300,115,'#555c5d',sw=5,r=9);rect(c,2070,953,250,82,'#363f43',sw=3,r=4)
 for x in [2103,2287]:
  oval(c,x,994,34,34,'#88908a','#202c31',5);oval(c,x,994,25,25,'#343e43','#aeb4a4',2);oval(c,x,994,9,9,'#657774',None)
 rect(c,2156,975,75,39,'#b1b8a5',sw=3,r=3);rect(c,2171,984,45,15,'#4d5d60',sw=2,r=2)
 line(c,[(2100,936),(2100,918),(2275,918),(2275,936)],'#27353a',7);line(c,[(2308,939),(2370,800)],'#36494b',3)
 for x in range(2160,2240,15):rect(c,x,928,9,6,'#d0bda0',sw=1)
 # ADV is the sole scene lettering, keeping the accepted visual motif.
 c.save();c.translate(2090,870);c.rotate(-8);txt(c,'ADV',0,0,102,'#e5b343',stroke=True);c.restore()
 for x,h in [(2120,26),(2195,18),(2280,32)]:line(c,[(x,875),(x+1,875+h)],'#34303a',4)
 return s.makeImageSnapshot()

# Skin, garment and hair palettes, individually designed rather than recoloured copies.
PALETTES={'lead':('#b8794c','#895438','#e7b830','#b77c25','#25323d'), 'hood':('#b48b70','#8b6654','#b3b6b0','#7c8a87','#4b5c62'),'blue':('#825336','#573a31','#66858d','#425d69','#424951'),'ezhi':('#dab798','#b38570','#717780','#4b525f','#3b414b')}
def hand(c,x,y,ang,skin,shadow,gesture):
 c.save();c.translate(x,y);c.rotate(ang)
 # Open palm with separate rounded fingers; relaxed hands curl slightly.
 if gesture:
  shape(c,'M -13 8 Q -23 -1 -29 -8 Q -31 -14 -26 -16 L -14 -9 L -18 -36 Q -18 -43 -13 -42 L -7 -18 L -7 -44 Q -6 -49 -1 -45 L 2 -19 L 5 -43 Q 8 -48 11 -41 L 10 -17 L 17 -34 Q 21 -37 22 -30 L 17 -5 Q 16 12 5 20 L -8 20 Z',skin,sw=2.8)
 else:
  shape(c,'M -12 -8 Q -24 -17 -26 -9 Q -24 -2 -17 3 L -14 23 Q -8 31 1 29 L 13 22 Q 18 14 14 -3 Q 10 -16 -12 -8 Z',skin,sw=2.8)
  for x0 in [-5,2,9]:line(c,[(x0,2),(x0+1,18)],shadow,1.7)
 c.restore()
def mouth(c,v,amp):
 # Stylized visemes: closed lips, narrow consonants, open A/E and rounded O/U.
 if amp<.035 or v in [0,1]:shape(c,'M -17 0 Q 0 6 18 -1',None,INK,2.8);return
 h=3+amp*(18 if v in [10,11,12] else 11);w=12 if v in [13,14] else 21
 oval(c,0,2,w,h,'#432b2d',INK,2.7)
 if v not in [13,14]:shape(c,f'M {-w+3} -2 Q 0 2 {w-3} -2 L {w-5} 4 Q 0 7 {-w+5} 4 Z','#f2dfb8',None)
 if h>11:oval(c,1,h*.64,10,3.4,'#b67165',None)
def face(c,kind,t,v,amp,angle=0):
 skin,shade,cloth,dark,pants=PALETTES[kind];ez=kind=='ezhi'
 c.save();c.translate(0,-540);c.rotate(angle);sx=1.12 if ez else 1;c.scale(sx,1)
 if kind=='hood':shape(c,'M -59 73 Q -84 25 -64 -55 Q -46 -87 0 -88 Q 54 -81 66 -32 Q 78 38 52 78 Z','#9ca7a3',sw=4)
 # Ears, neck and asymmetric face planes.
 oval(c,-48,0,11,22,skin,sw=3);oval(c,48,0,11,22,skin,sw=3)
 shape(c,'M -25 48 L -27 85 Q 0 101 30 78 L 24 43 Z',skin,sw=3)
 shape(c,'M -47 -42 Q -45 -75 -7 -78 Q 31 -80 46 -49 L 48 12 Q 44 51 18 68 Q -6 77 -31 56 Q -47 40 -49 11 Z',skin,sw=3.5)
 shape(c,'M 27 -64 Q 48 -42 47 11 Q 41 45 18 61 L 27 35 L 22 17 L 33 -2 Z',shade,None)
 shape(c,'M -39 12 Q -28 21 -19 20',None,shade,2);shape(c,'M -35 -44 Q -13 -56 2 -48',None,'#efd1a6' if kind!='blue' else '#a7754b',4)
 # Hair / black cap / lowered hood.
 if kind=='lead':
  shape(c,'M -50 -37 Q -58 -83 -19 -94 Q 25 -102 47 -72 L 49 -41 Q 8 -57 -50 -37 Z','#33383b',sw=4)
  shape(c,'M -49 -38 Q -18 -58 47 -45 Q 81 -47 88 -35 Q 64 -21 16 -28 Q -17 -31 -49 -26 Z','#33383b',sw=4)
  shape(c,'M -29 -78 Q -18 -87 1 -88',None,'#646967',3)
 elif ez:
  shape(c,'M -49 -18 L -51 -49 Q -53 -85 -14 -96 Q 25 -105 48 -78 L 47 -28 L 32 -48 L 22 -54 Q 9 -58 -2 -35 L 0 -67 Q -24 -49 -45 -44 Z','#46423f',sw=3)
  for a in range(6):shape(c,f'M {-38+a*9} -68 Q {-15+a*7} -92 {34+a*2} -77',None,'#99958b',2)
  shape(c,'M -46 -33 L -40 -9',None,'#b2a798',3)
 else:
  shape(c,'M -49 -21 L -46 -52 Q -18 -80 16 -70 Q 44 -63 47 -28 L 30 -45 Q -1 -53 -36 -39 L -39 -12 Z','#383431' if kind=='blue' else '#52453c',sw=3)
 # Brows and lids; blink independently.
 blink=abs((t+{'lead':0,'hood':.8,'blue':1.9,'ezhi':.3}[kind])%4.9-.14)<.065
 for side in [-1,1]:
  x=side*23;ey=-12
  shape(c,f'M {x-13} {ey-12} Q {x} {ey-18} {x+13} {ey-12}',None,'#423b34',4.5)
  if blink:shape(c,f'M {x-13} {ey} Q {x} {ey+4} {x+13} {ey}',None,INK,2.5)
  else:
   shape(c,f'M {x-13} {ey} Q {x} {ey-9} {x+13} {ey} Q {x} {ey+8} {x-13} {ey} Z','#e8dfc6',sw=2)
   oval(c,x+2,ey,4,6,'#303b39',None);oval(c,x+3,ey-2,1.4,1.4,'#f8efd3',None)
 shape(c,'M 2 -11 L -4 12 Q 2 18 12 12',None,shade,3)
 if ez:
  # Box spectacles with doubled temples, plus full short beard and moustache.
  for x in [-43,5]:rect(c,x,-24,39,29,None,'#303b47',3.5,r=7)
  line(c,[(-4,-12),(5,-12)],'#303b47',3.5);line(c,[(-43,-15),(-57,-23)],'#303b47',4);line(c,[(44,-15),(54,-22)],'#303b47',3)
  shape(c,'M -43 21 L -34 37 Q -31 64 -7 74 Q 20 78 37 50 L 43 18 L 31 28 L 18 34 Q 4 27 -13 35 L -28 32 Z','#5c4c43',sw=2.5)
  shape(c,'M -20 28 Q 0 18 23 29 L 18 37 Q 2 31 -17 37 Z','#55473f',sw=2)
  for x in [-28,-18,-7,6,18,29]:line(c,[(x,48),(x+3,62)],'#928775',1.6)
 else:
  if kind in ['lead','hood']:
   shape(c,'M -27 28 Q -22 53 -4 58 Q 17 56 29 31',None,'#4d3d33',4)
   shape(c,'M -15 26 Q 0 20 17 26',None,'#493a33',3)
 c.save();c.translate(0,39 if ez else 35);mouth(c,v,amp);c.restore();c.restore()

def ik(shoulder,target,length=112,sign=1):
 a=np.array(shoulder,float);b=np.array(target,float);d=b-a;dist=np.linalg.norm(d);u=d/max(dist,1e-5);dist=min(dist,2*length-.1);mid=a+u*dist/2;perp=np.array([-u[1],u[0]]);return mid+perp*sign*math.sqrt(max(0,length**2-(dist/2)**2))
def person(c,kind,x,y,scale,t,phase,vis,amp,speaking=True,walk=0,focus=False):
 skin,shade,cloth,dark,pants=PALETTES[kind];ez=kind=='ezhi';listener=not speaking
 activity=max(0,min(1,256.28-t)) if kind=='lead' else (max(0,min(1,(t-255.9)/.65)) if ez else 0)
 bounce=(6-3*activity)*math.cos(phase+(.2 if kind=='hood' else -.2));sway=(2 if speaking else 3)*math.sin(phase*.5+(0 if kind=='hood' else 1))
 oval(c,x,y+5,83*scale,16*scale,'#343c3d',None,alpha=80)
 c.save();c.translate(x,y+bounce*scale);c.scale(scale*(1.17 if ez else 1),scale);c.rotate(sway*.35)
 # Trousers and articulate stride, with ankle/sole accents.
 stride=40*walk*math.sin(t*7)
 for side in [-1,1]:
  px=side*42;kx=side*43+side*stride;fx=side*49+side*stride*1.5;lift=max(0,side*math.sin(t*7))*walk*27
  shape(c,f'M {px-30} -263 L {px+29} -263 Q {kx+30} -160 {fx+22} {-32-lift} L {fx-25} {-27-lift} Q {kx-27} -139 {px-30} -263 Z',pants,sw=4)
  shape(c,f'M {px+15} -228 Q {kx+10} -129 {fx+11} {-40-lift}',None,'#667074',3)
  shape(c,f'M {fx-26} {-38-lift} L {fx+22} {-38-lift} Q {fx+30} {-19-lift} {fx+42} {-12-lift} Q {fx+47} {0-lift} {fx+28} {3-lift} L {fx-35} {3-lift} Q {fx-42} {-10-lift} {fx-26} {-38-lift} Z','#687778',sw=4)
  line(c,[(fx-32,-5-lift),(fx+33,-5-lift)],'#c0c3ad',3)
 # Torso, cuffs and cloth shadow planes.
 torso='M -65 -453 Q -88 -433 -89 -384 L -76 -261 Q 0 -238 77 -260 L 88 -384 Q 90 -431 64 -453 L 29 -467 L -29 -467 Z'
 shape(c,torso,cloth,sw=4)
 shape(c,'M 45 -436 Q 75 -405 69 -318 L 57 -260 L 79 -262 L 87 -380 Q 88 -420 64 -447 Z',dark,None)
 shape(c,'M -62 -295 Q -19 -312 9 -295 Q 39 -286 65 -298',None,dark,2.4)
 if kind=='lead' or kind=='hood':
  shape(c,'M -35 -465 Q -75 -480 -63 -434 Q -36 -413 0 -420 Q 38 -413 63 -434 Q 74 -480 35 -465 L 27 -446 Q 0 -432 -27 -446 Z',dark,sw=3)
  shape(c,'M -33 -456 Q 0 -437 34 -456',None,cloth,8)
  line(c,[(-22,-432),(-25,-382)],'#ead2a0' if kind=='lead' else '#d4d3bf',3);line(c,[(23,-432),(28,-385)],'#ead2a0' if kind=='lead' else '#d4d3bf',3)
  shape(c,'M -40 -313 L -50 -282 Q 0 -272 49 -282 L 40 -313',None,dark,2.8);line(c,[(-70,-265),(70,-265)],dark,5)
 elif ez:
  shape(c,'M -29 -460 L 29 -460 L 40 -260 L -34 -260 Z','#e8e1c8',sw=2)
  shape(c,'M -36 -461 L -68 -430 L -39 -394 L -52 -375 L -11 -305 L -15 -432 Z',dark,sw=2.5)
  shape(c,'M 35 -461 L 67 -430 L 38 -394 L 49 -375 L 10 -305 L 15 -431 Z',dark,sw=2.5)
  for yy in [-409,-375,-341,-307,-276]:oval(c,4,yy,3,4,'#bfaa6c',None)
  c.save();c.clipPath(svg(torso))
  for xx in range(-90,100,18):line(c,[(xx,-450),(xx,-250)],'#969a98',.7,90)
  for yy in range(-445,-245,18):line(c,[(-90,yy),(90,yy)],'#979d9a',.7,90)
  c.restore()
 else:
  line(c,[(0,-438),(0,-263)],dark,3);shape(c,'M -32 -458 L -4 -418 L 0 -450 L 10 -415 L 34 -458',None,dark,3)
  for yy in [-391,-355,-320,-285]:oval(c,6,yy,2.3,2.3,'#b2b7a6',None)
  rect(c,-58,-397,40,45,None,dark,2,r=3)
 # Independent hand phrases. Anatomical two-bone IK keeps elbows below shoulders.
 for side in [-1,1]:
  shoulder=(side*68,-433)
  g=.5+.5*math.sin(t*.94+(0 if side<0 else 2.3));g=g*g*(3-2*g)
  restx=side*(82+3*math.sin(phase*.5+side));resty=-220+3*math.cos(phase+side)
  tx=restx*(1-activity)+side*(100+55*g)*activity;ty=resty*(1-activity)+(-240-135*g+6*math.sin(phase*.5+side))*activity;openhand=g*activity>.35
  if walk:tx=tx*(1-walk)+side*97*walk;ty=ty*(1-walk)+(-235+side*22*math.sin(t*7))*walk;openhand=False
  # Continuous drawn elbow construction; no IK branch changes or rotation flips.
  a=np.array(shoulder);d=np.array([tx,ty]);b=a+(d-a)*.46+np.array([side*(16+12*activity),10+80*g*activity])
  p=skia.Path();p.moveTo(*a);p.lineTo(*b);p.lineTo(*d)
  c.drawPath(p,paint(INK,45));c.drawPath(p,paint(cloth,37));line(c,[tuple(b),tuple(d)],dark,7)
  oval(c,tx,ty,19,8,dark,sw=2)
  ang=side*(-12 if openhand else 0);hand(c,tx,ty+13,ang,skin,shade,openhand)
 angle=activity*3*math.sin(t*.7)+(1-activity)*7*math.cos(phase+(.2 if kind=='hood' else -.15))
 face(c,kind,t,vis if speaking else 0,amp if speaking else 0,angle)
 c.restore()

BG=None;VI=None;BEATS=None;PAPER=None;SECTIONS=None

def init():
 global BG,VI,BEATS,PAPER,SECTIONS
 if BG is None:
  SECTIONS=json.loads((W/'sections.json').read_text());BG=background();VI=np.load(W/'visemes.npy');BEATS=np.array(json.loads((W/'beats.json').read_text())['beat_seconds'])
  rng=np.random.default_rng(77);grain=np.zeros((HEIGHT,WIDTH,4),np.uint8);grain[:,:,:3]=np.where(rng.random((HEIGHT,WIDTH,1))>.5,255,0);grain[:,:,3]=rng.integers(0,12,(HEIGHT,WIDTH),dtype=np.uint8);grain[:,:,:3]=((grain[:,:,:3].astype(np.uint16)*grain[:,:,3,None])//255).astype(np.uint8);PAPER=skia.Image.fromarray(grain,colorType=skia.ColorType.kRGBA_8888_ColorType,alphaType=skia.AlphaType.kPremul_AlphaType)
  textured=skia.Surface(WIDTH,HEIGHT);tc=textured.getCanvas();tc.drawImage(BG,0,0);tc.drawImage(PAPER,0,0);BG=textured.makeImageSnapshot()
def frame(t):
 init();s=skia.Surface(WIDTH,HEIGHT);c=s.getCanvas();c.clear(color('#d7c9ab'));phase=2*math.pi*np.interp(t,BEATS,np.arange(len(BEATS)));values=VI[min(len(VI)-1,int(t*60))];v=int(np.argmax(values));amp=float(values.max())
 # Camera moves on the drawn stage: opening retreat, varied coverage, outro reveal.
 if t<7:z=1.08-.08*(t/7);cx=1280;cy=720
 elif t<249:
  section=next((q['name'] for q in SECTIONS if q['start']<=t<q['end']),'Verse 1');shot=int((t-7)//14)%5
  if section in ['Hook','Chorus','Bridge']:shot=4
  z=[1.05,1.28,1.12,1.35,1.0][shot];cx=[1280,1300,1160,1320,1280][shot]+12*math.sin(t*.17);cy=[760,840,780,850,720][shot]
 else:
  u=max(0,min(1,(t-256.28)/2.4));u=u*u*(3-2*u);ending=max(0,min(1,(t-271)/2.18));u*=1-ending*ending*(3-2*ending);z=1+.13*u;cx=1280+280*u;cy=720+90*u
 cx=max(1280/z,min(2560-1280/z,cx));cy=max(720/z,min(1440-720/z,cy))
 c.save();c.translate(1280,720);c.scale(z,z);c.translate(-cx,-cy);c.drawImage(BG,0,0)
 person(c,'hood',775,1180,.88,t,phase+.08,0,0,False)
 person(c,'blue',1760,1180,.89,t,phase-.12,0,0,False)
 advance=min(1,t/7);person(c,'lead',1280,1215+65*advance,1.0+.08*advance,t,phase,v,amp,t<256.28,walk=max(0,1-t/7))
 if t>=251.8:
  u=min(1,max(0,(t-251.8)/4.1));ease=u*u*(3-2*u);x=2800-770*ease;person(c,'ezhi',x,1280,1.08,t,phase,v,amp,t>=256.28,walk=(1-ease) if u<1 else 0)
 c.restore()
 # Static paper grain is stable across frames; no random flicker.
 return s.makeImageSnapshot()
if __name__=='__main__':
 import sys
 for t in [2,22,90,254,258,269]:
  im=frame(t);im.save(str(W/f'concept-{t}.png'),skia.kPNG)
 print('Concept frames ready')
