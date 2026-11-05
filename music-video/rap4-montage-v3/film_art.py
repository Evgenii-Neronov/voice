"""Original illustrated hip-hop locations and montage, rendered locally with Skia."""
from pathlib import Path
import math,json,functools,numpy as np,skia
import art
from art import rect,poly,line,oval,shape,paint,color
W=Path(__file__).resolve().parent;WW,HH=2560,1440
PLAN=json.loads((W/'edit-plan.json').read_text());VI=np.load(W/'visemes.npy');INK='#20232c'
def lerp(a,b,u):return a+(b-a)*u
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def iso(x,y,z=0):return (1280+(x-y)*130,760+(x+y)*75-z*150)
def cube(c,x,y,z,sx,sy,sz,top,front,side,sw=3):
 p=lambda a,b,d:iso(a,b,d)
 poly(c,[p(x,y,z+sz),p(x+sx,y,z+sz),p(x+sx,y+sy,z+sz),p(x,y+sy,z+sz)],top,INK,sw)
 poly(c,[p(x,y+sy,z),p(x+sx,y+sy,z),p(x+sx,y+sy,z+sz),p(x,y+sy,z+sz)],front,INK,sw)
 poly(c,[p(x+sx,y,z),p(x+sx,y+sy,z),p(x+sx,y+sy,z+sz),p(x+sx,y,z+sz)],side,INK,sw)
def glow(c,x,y,rx,ry,h,alpha=80):
 shader=skia.GradientShader.MakeRadial((x,y),1,[color(h,alpha),color(h,0)],None,skia.TileMode.kClamp)
 c.save();c.translate(x,y);c.scale(rx,ry)
 shader=skia.GradientShader.MakeRadial((0,0),1,[color(h,alpha),color(h,0)],None,skia.TileMode.kClamp)
 c.drawCircle(0,0,1,skia.Paint(Shader=shader,AntiAlias=True));c.restore()
def lamp(c,x,y):
 line(c,[(x,y),(x,y+160)],'#333943',8);oval(c,x,y+170,38,14,'#e9be63',INK,4);glow(c,x,y+180,150,110,'#ffcb67',90)
def speaker(c,x,y,w=220,h=380):
 rect(c,x,y,w,h,'#242b34',sw=5,r=6);rect(c,x+12,y+12,w-24,h-24,'#46515a',sw=2,r=3)
 for cy,r in [(y+h*.28,w*.23),(y+h*.7,w*.34)]:
  oval(c,x+w/2,cy,r,r,'#181e29','#899188',4);oval(c,x+w/2,cy,r*.77,r*.77,'#313b49','#111923',2);oval(c,x+w/2,cy,r*.29,r*.29,'#6e7b84',INK,3)
 for xx in [x+8,x+w-8]:
  for yy in [y+8,y+h-8]:oval(c,xx,yy,2,2,'#c9c3b4',None)
def skyline(c,shift=0):
 rng=np.random.default_rng(132)
 for x in range(-150,2800,130):
  h=int(rng.integers(170,450));xx=x+shift
  rect(c,xx,620-h,115,h,'#293346','#172131',2)
  for wx in range(15,100,25):
   for wy in range(15,h-10,38):
    if rng.random()<.43:rect(c,xx+wx,620-h+wy,9,16,'#b8945d',None)
def roof(c):
 c.clear(color('#16263d'));glow(c,1750,260,900,580,'#4e5d77',90);oval(c,1980,150,65,65,'#d9d1ad',None);skyline(c)
 poly(c,[(-200,880),(1350,460),(2800,900),(1350,1750)],'#5c666c',INK,5)
 for j in range(-6,11):line(c,[iso(-10,j),iso(10,j)],'#748080',2)
 for j in range(-10,11):line(c,[iso(j,-6),iso(j,9)],'#454f59',2)
 # Water tower and its diagonal supports.
 for x in [1780,2080]:
  line(c,[(x,390),(x-35,730)],'#313a42',15)
 line(c,[(1745,730),(2080,390),(1780,390),(2045,730)],'#25323d',7)
 rect(c,1730,230,405,310,'#7d6b58',sw=5);oval(c,1932,230,202,60,'#a18a6a',sw=4);oval(c,1932,540,202,60,'#5d5348',sw=4)
 for x in range(1745,2130,29):line(c,[(x,250),(x,535)],'#3d4143',3)
 for y in [300,440]:line(c,[(1740,y),(2125,y)],'#222d38',10)
 for x in range(-100,2700,140):line(c,[(x,730),(x,875)],'#23313f',8)
 line(c,[(-100,745),(2700,745)],'#a0a69c',8);line(c,[(-100,855),(2700,855)],'#223344',8)
 cube(c,-5,1,0,1.4,1.2,.65,'#777f7d','#485660','#33424c')
 glow(c,1290,1160,780,350,'#f1c16d',37)
def studio(c):
 c.clear(color('#382d39'));poly(c,[(0,0),(1380,0),(1380,620),(0,1040)],'#65545b',INK,5);poly(c,[(1380,0),(2560,0),(2560,1040),(1380,620)],'#433f50',INK,5)
 poly(c,[(0,1040),(1380,620),(2560,1040),(2560,1440),(0,1440)],'#9a775b',INK,5)
 for y in range(680,1500,100):line(c,[(0,y+280),(2560,y-300)],'#5e4b47',3)
 for x in range(50,1300,190):
  for y in range(60,650,130):
   rect(c,x,y,160,110,'#3a3642',sw=3,r=7)
   for dx in range(15,155,25):line(c,[(x+dx,y+8),(x+dx,y+102)],'#292e3b',5)
 rect(c,1580,95,740,430,'#242b37',sw=10);rect(c,1602,117,696,386,'#596b78',sw=3)
 poly(c,[(1610,125),(1800,125),(2130,490),(1980,490)],'#7b8487',None)
 # Record shelves; no typography on sleeves.
 for y in [590,770,950]:
  rect(c,1690,y,650,150,'#3d3340',sw=4)
  for i in range(24):
   x=1704+i*26;col=['#bb895f','#a9a58b','#697b86','#a77361','#433c49'][i%5];rect(c,x,y+10,19,125,col,sw=1)
  rect(c,1675,y+140,680,17,'#bb9270',sw=3)
 speaker(c,120,770,230,400);lamp(c,1030,-80);lamp(c,2150,-80)
 glow(c,1160,1040,680,500,'#eac594',45)
def metro(c):
 c.clear(color('#344d55'));rect(c,0,0,2560,720,'#668181',None)
 for y in range(20,730,65):
  for x in range(-40,2600,140):rect(c,x+(70 if y%2 else 0),y,132,58,'#8faaa1', '#4e7072',2)
 rect(c,0,80,2560,65,'#bd9562',None);line(c,[(0,155),(2560,155)],'#203c48',5)
 # A parked carriage beyond the platform.
 rect(c,-80,230,2770,450,'#a5b4aa',sw=6,r=28);rect(c,-80,580,2770,70,'#b98757',None)
 for x in range(-50,2700,420):
  rect(c,x,280,310,220,'#253f4d',sw=7,r=18);poly(c,[(x+20,300),(x+130,300),(x+270,480),(x+170,480)],'#5b7b85',None)
  line(c,[(x+355,245),(x+355,650)],'#526c72',7)
 poly(c,[(0,720),(2560,650),(2560,1440),(0,1440)],'#6e7b7b',INK,5)
 for y in range(760,1550,150):line(c,[(0,y),(2560,y-70)],'#a7afa1',3)
 for x in range(-300,2900,250):line(c,[(x,700),(x+400,1440)],'#475d65',3)
 poly(c,[(0,710),(2560,640),(2560,680),(0,750)],'#d6b26a',None)
 for x in range(40,2560,55):oval(c,x,724-x*.027,3,3,'#705b45',None)
 for x in [530,1700]:
  rect(c,x,110,380,23,'#e0d5a3',None,r=10);glow(c,x+190,160,380,140,'#d5ddbd',50)
def court(c):
 c.clear(color('#25374b'));skyline(c);poly(c,[(0,750),(1530,500),(2850,1070),(1900,1600),(-300,1300)],'#5d706b',INK,5)
 for x in range(-800,3400,110):line(c,[(x,190),(x+850,850)],'#64777b',2)
 for x in range(-800,3400,110):line(c,[(x,850),(x+850,190)],'#64777b',2)
 for x in range(40,2600,450):line(c,[(x,150),(x,900)],'#1c2c3a',10)
 line(c,[(0,170),(2560,170)],'#a2a99b',7)
 # Painted court ellipse, three-point arc, free throw stripe.
 oval(c,1450,1130,690,180,None,'#c9b883',7);line(c,[(160,1350),(2150,770)],'#c9b883',7)
 line(c,[(590,890),(590,470)],'#283742',24);rect(c,360,300,460,250,'#cabfa2',sw=8)
 rect(c,490,380,180,125,None,'#515961',6);oval(c,580,540,110,25,None,'#b66544',12)
 for x in range(490,690,35):line(c,[(x,540),(550+(x-490)*.4,660),(x+12,545)],'#d7d1b7',3)
 for x in [100,2330]:
  line(c,[(x,160),(x,850)],'#263746',12);rect(c,x-90,140,180,60,'#cfc9a0',sw=4,r=8);glow(c,x,350,600,440,'#d0c497',45)
 glow(c,1350,1170,900,240,'#d5b275',30)
def warehouse(c):
 c.clear(color('#202334'));poly(c,[(0,0),(2560,0),(2560,990),(0,990)],'#343143',None)
 for x in range(50,2700,390):
  line(c,[(x,0),(x,990)],'#1b2430',18);line(c,[(x,0),(x+390,580),(x,580),(x+390,0)],'#4f4b5a',9)
 poly(c,[(0,980),(2560,850),(2560,1440),(0,1440)],'#595063',INK,5)
 for x in [70,2020]:
  speaker(c,x,520,330,620);speaker(c,x+35,220,260,280)
 line(c,[(0,90),(2560,90)],'#79808b',13)
 for x in [600,1280,1900]:
  rect(c,x-45,90,90,100,'#222d39',sw=4,r=10)
  poly(c,[(x-18,190),(x+18,190),(x+490,1200),(x-490,1200)],'#4b4659',None)
  glow(c,x,1140,520,170,'#dfba70' if x==1280 else '#5d94a1',60)
def record(c,x,y,r,angle=0):
 c.save();c.translate(x,y);c.scale(1,.63);c.rotate(angle)
 oval(c,0,0,r,r,'#20212a','#0c1720',8)
 for rr in np.linspace(r*.28,r*.97,44):oval(c,0,0,rr,rr,None,'#55515b',1.2)
 poly(c,[(0,0),(r*.87,-r*.45),(r*.25,-r*.96)],'#333744',None)
 oval(c,0,0,r*.24,r*.24,'#caa459','#20262d',5);oval(c,0,0,9,9,'#1c2530',None);c.restore()
def vinyl(c,t):
 c.clear(color('#483443'));poly(c,[(0,250),(1850,-70),(2700,330),(2250,1430),(-100,1260)],'#b19471',INK,6)
 for y in range(80,1600,70):line(c,[(0,y),(2560,y-360)],'#89715f',2)
 poly(c,[(220,420),(1600,170),(2360,500),(1980,1280),(190,1120)],'#555c66',INK,8)
 poly(c,[(190,1120),(1980,1280),(1980,1360),(190,1200)],'#333844',INK,6)
 record(c,1120,760,655,t*28)
 oval(c,2060,550,85,45,'#343943',sw=5);line(c,[(2060,550),(1950,720),(1710,740),(1640,820)],'#19242e',26);line(c,[(2060,550),(1950,720),(1710,740),(1640,820)],'#b4b3a8',13)
 rect(c,260,1020,100,60,'#cbaa62',sw=4,r=8)
 for i in range(7):rect(c,2110+i*22,820-i*10,10,120,'#293541',None)
def speakers(c,t):
 c.clear(color('#314356'));speaker(c,80,70,700,1200);speaker(c,900,210,720,1100);speaker(c,1780,-80,700,1200)
 for x,y in [(430,900),(1260,980),(2130,700)]:
  oval(c,x,y,220,220,None,'#d1a454',7);oval(c,x,y,240+3*math.sin(t*2),240+3*math.sin(t*2),None,'#667e8b',2)
@functools.lru_cache(10)
def background(scene):
 s=skia.Surface(WW,HH);c=s.getCanvas();{'roof':roof,'skyline':roof,'studio':studio,'metro':metro,'train':metro,'court':court,'warehouse':warehouse}[scene](c)
 rng=np.random.default_rng(18)
 for i in range(1800):
  x,y=rng.uniform(0,WW),rng.uniform(0,HH);line(c,[(x,y),(x+rng.uniform(1,6),y)],'#d5c9a8',1,35)
 return s.makeImageSnapshot()
def performer(c,kind,x,y,scale,t,speaking=True,echo=False):
 v=VI[min(len(VI)-1,int(t*60))]
 if echo:
  c.saveLayer(None,skia.Paint(Alphaf=.12));art.person(c,kind,x-24,y+5,scale,t-.12,0,int(v.argmax()),float(v.max()),speaking,0);c.restore()
 art.person(c,kind,x,y,scale,t,0,int(v.argmax()),float(v.max()),speaking,0)
def foreground(c,scene,pan):
 if scene in ['metro','train']:
  for x in [-70-pan*1.9,2450-pan*1.9]:
   poly(c,[(x,0),(x+100,0),(x+160,1440),(x+30,1440)],'#2c4854',INK,6);line(c,[(x+80,0),(x+130,1440)],'#87a09c',7)
 elif scene in ['roof','skyline']:
  line(c,[(-60-pan*1.5,1390),(2690-pan*1.5,1260)],'#172736',20)
 elif scene=='warehouse':
  for x in [50-pan*1.3,2350-pan*1.3]:poly(c,[(x,1160),(x+150,1130),(x+240,1440),(x-20,1440)],'#171e2b',None)
def collage(c,t,u):
 c.clear(color('#d6cbb0'));rng=np.random.default_rng(66);base=math.floor(u*3)
 for i in range(7):
  x=-150+i*450+70*math.sin(u*2+i);y=130+(i%2)*180
  pts=[(x,y),(x+300,y-45),(x+390,y+60),(x+340,y+800),(x-40,y+920)]
  poly(c,pts,['#293849','#b18b59','#817e75'][i%3],None)
 for x,y,r in [(440,790,350),(2080,460,410)]:record(c,x,y,r,t*5)
 c.save();c.translate(1280,640);c.rotate(-6+u*5);rect(c,-370,-470,740,940,'#bdad8e',sw=7);c.save();c.clipRect(skia.Rect.MakeXYWH(-360,-460,720,920));performer(c,'lead',0,1050,2.4,t,True);c.restore();c.restore()
 for i in range(6):
  x=260+i*450;line(c,[(x,220),(x+75,340),(x+20,530)],'#d1ab5d',8)
def frame(t):
 shot=next(s for s in PLAN if s['start']<=t<s['end']);scene=shot['scene'];u=(t-shot['start'])/(shot['end']-shot['start']);s=skia.Surface(WW,HH);c=s.getCanvas();c.clear(color('#202936'))
 pan=(u-.5)*(190 if shot['shot'] in ['travel','wide'] else 65);zoom=1.12+(.06*u if shot['shot']!='close' else .02*u)
 if scene=='vinyl':
  c.save();c.translate(1280,720);c.scale(zoom,zoom);c.translate(-1280-pan,-720);vinyl(c,t)
  # A held record-hand gesture, not a metronomic repeated scratch.
  h=smooth(u/.25)*(1-smooth((u-.75)/.25));c.save();c.translate(380+100*h,650);c.rotate(68);c.scale(3.2,3.2);art.hand(c,0,0,0,'#b8794c','#895438',True);c.restore();c.restore()
 elif scene=='speakers':speakers(c,t)
 elif scene=='collage':collage(c,t,u)
 else:
  bg=background(scene);c.save();c.translate(1280,720);c.scale(zoom,zoom);c.translate(-1280-pan,-720);c.drawImage(bg,0,0)
  if scene=='train':
   # A carriage moves independently behind the foreground platform columns.
   off=lerp(-2100,2200,smooth(u));rect(c,off,240,2200,570,'#879f9c',sw=8,r=30)
   for xx in range(50,2100,370):
    rect(c,off+xx,305,280,300,'#263f50',sw=8,r=24);poly(c,[(off+xx+20,330),(off+xx+100,330),(off+xx+250,580),(off+xx+160,580)],'#67878b',None)
   line(c,[(off,730),(off+2200,730)],'#d0a663',30)
  elif scene=='skyline':
   for x in [-50,2200]:line(c,[(x,200),(x+140,1210)],'#1d3041',36)
  elif scene=='court' and shot['shot']=='detail':
   x=lerp(400,1800,smooth(u));oval(c,x,1170,80,75,'#b57643',INK,6);line(c,[(x-60,1120),(x+65,1220)],INK,5);oval(c,x,1170,32,74,None,INK,4)
  else:
   close=shot['shot']=='close';scale=1.45 if close else (.83 if shot['shot']=='wide' else 1.04);xx=1280;yy=1210
   if not close and shot['shot']=='wide':
    performer(c,'hood',650,1125,.67,t,False);performer(c,'blue',1970,1170,.72,t,False)
   echo=bool(shot['effects']) and .3<u<.36;performer(c,'lead',xx,yy,scale,t,True,echo)
   if scene=='studio':
    line(c,[(1700,1280),(1700,700),(1500,620)],'#212c37',10);oval(c,1500,620,55,70,'#464954',INK,5);oval(c,1440,650,70,90,None,'#1c2733',7)
  c.restore();foreground(c,scene,pan)
 # Short paper-edge transitions; no added words, numbers or logos.
 elapsed=t-shot['start']
 if shot['index'] in [1,5,8,12,14,15,19,22,25,26,29] and elapsed<.20:
  p=elapsed/.2;edge=WW*(1-p);poly(c,[(edge-80,0),(WW,0),(WW,HH),(edge+100,HH),(edge-20,1000),(edge+60,630)],'#c8bba0',None)
 return s.makeImageSnapshot()
if __name__=='__main__':
 for t in [12,20,28,37,47,56,72,79,90,110,122,128,136,148,157,168,180,188,201,207,216,228,238,242,246]:frame(t).save(str(W/f'concept-{t}.png'),skia.kPNG)
 print('New location concepts rendered')
