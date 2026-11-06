"""Night Shift. A miniature railway constructed in perspective, with a tiled station interlude."""
import math, functools, random, subprocess, sys
from pathlib import Path
import skia as sk
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent
R=W.parents[1]
audio=R/'outputs/rap-18/rap-18.mp3'
sin,cos,pi=math.sin,math.cos,math.pi
@functools.lru_cache(512)
def pen(h,w=0):
    p=sk.Paint(Color=int('ff'+h,16),AntiAlias=True)
    if w:p.setStyle(sk.Paint.kStroke_Style);p.setStrokeWidth(w);p.setStrokeJoin(sk.Paint.kRound_Join);p.setStrokeCap(sk.Paint.kRound_Cap)
    return p
def path(pts,h,w=0,close=True):
    a=sk.Path();a.moveTo(*pts[0])
    for pt in pts[1:]:a.lineTo(*pt)
    if close:a.close()
    c.drawPath(a,pen(h,w))
def line(a,b,h,w):c.drawLine(*a,*b,pen(h,w))
def box(x,y,w,h,col):c.drawRect(sk.Rect.MakeXYWH(x,y,w,h),pen(col))
def ell(x,y,w,h,col):c.drawOval(sk.Rect.MakeXYWH(x-w,y-h,2*w,2*h),pen(col))
def grad(y,h,top,bot):
    sh=sk.GradientShader.MakeLinear([(0,y),(0,y+h)],[pen(top).getColor(),pen(bot).getColor()])
    c.drawRect(sk.Rect.MakeXYWH(-400,y,2200,h),sk.Paint(Shader=sh))
def lamp(x,y,r,col):
    sh=sk.GradientShader.MakeRadial((x,y),r,[pen(col).getColor(),int('44'+col,16),int('00'+col,16)],[0,.15,1])
    c.drawCircle(x,y,r,sk.Paint(Shader=sh,AntiAlias=True))
def tag():
    # Interlocking marker lettering, with separate shadow, keyline and paint passes.
    letters=[[(0,88),(47,3),(69,0),(77,88)],[(24,55),(77,43)],[(88,84),(103,2),(136,8),(155,29),(146,55),(94,87)],[(154,8),(165,82),(219,-6)]]
    for off,col,weight in [(7,'172133',19),(0,'102237',20),(0,'76cdc3',14),(0,'ffd08a',5)]:
        for pts in letters:path([(x+off,y+off) for x,y in pts],col,weight,False)
    for x,y,h in [(27,59,24),(76,69,33),(147,42,21),(166,77,28)]:
        line((x,y),(x-2,y+h),'76cdc3',2);ell(x-2,y+h,2,3,'76cdc3')
    path([(-4,112),(82,101),(153,101),(207,83)],'ffd08a',3,False)
@functools.lru_cache(None)
def station_plate():
    global c
    prior=c;rec=sk.PictureRecorder();c=rec.beginRecording(sk.Rect.MakeXYWH(-900,-100,3500,1110))
    grad(0,550,'293b47','53615d')
    for i in range(-15,44):
        for j in range(12):
            x=i*61+30*(j%2);y=18+j*39
            if (i*19+j*5)%9==0:box(x+1,y+1,59,37,'425452')
            line((x,y),(x+61,y),'304441',1);line((x,y),(x,y+39),'334743',1)
    for x in [-360,380,1120,1860]:
        box(x,44,208,9,'e5b685');lamp(x+104,49,100,'dfa16e')
        box(x+16,347,187,9,'b48065');box(x+16,325,187,13,'a67762')
        for xx in (x+31,x+179):box(xx,355,7,47,'203441')
    c.save();c.translate(640,179);c.rotate(-6);c.scale(1.37,1.37);tag();c.restore()
    box(-900,408,3500,75,'34444b');box(-900,422,3500,5,'d5ab70');box(-900,452,3500,9,'1c2e38')
    grad(482,330,'192a38','111d29')
    for x in range(-900,2500,62):path([(x,482),(x+11,482),(x-116,770),(x-141,770)],'354449')
    for y in (538,656):box(-900,y,3500,6,'82968b')
    p=rec.finishRecordingAsPicture();c=prior;return p
def passenger(x,y,s,t,coat):
    c.save();c.translate(x,y);c.scale(s,s)
    ell(1,-49,6,8,'172531');path([(-4,-42),(4,-42),(10,-16),(7,-12),(-9,-13)],coat)
    for k in [-1,1]:
        line((k*3,-14),(k*(4+sin(t)*2),0),'15222e',3)
    c.restore()
def station(t,u,exitshot=False):
    c.save();z=1.15+.13*sin(pi*u);c.translate(640,324);c.scale(z,z);c.translate(-640-((u-.5)*280),-324);c.drawPicture(station_plate())
    for x,s,col in [(219,1.27,'253541'),(1054,1.56,'6d524c'),(1094,1.43,'293844')]:passenger(x,408,s,t*.6+x,col)
    c.restore()
    for x in (-130,1470):
        xx=x-u*450;path([(xx,0),(xx+44,0),(xx+60,720),(xx-5,720)],'12202a')
    if exitshot:train(1650-u*3600,460,1.25,t)
def train(x,y,s,t):
    c.save();c.translate(x,y);c.scale(s,s)
    for i in range(4):
        xx=i*399;path([(xx,0),(xx+11,-109),(xx+27,-123),(xx+373,-123),(xx+389,-110),(xx+391,0)],'3f5761')
        box(xx+4,-32,382,9,'c17961');box(xx+5,-7,379,9,'1e2d35')
        for j in range(8):
            wx=xx+17+j*46;box(wx,-96,35,44,'e1b98f' if (i+j)%3 else '96adb0')
            if (i+j)%2:ell(wx+15,-68,5,7,'485259');box(wx+9,-63,13,10,'485259')
        for ax in [40,342]:ell(xx+ax,4,15,15,'16202a')
    c.restore()
def distant(t,dawn):
    grad(0,425,'344058' if dawn else '101929','daa17d' if dawn else '526477')
    ell(1003-t*.12,145,43,43,'edc196' if dawn else 'c4c8b6')
    for layer in (0,1):
        for j in range(-1,26):
            x=j*65-(t*(1.5+layer*2))%65
            h=22+((j*47+13*layer)%115);box(x,372-h,62,h,'5a5861' if dawn else ('3a4c61','2a3d50')[layer])
def ride(t,u,kind,angle):
    night=kind!='dawn'; distant(t,not night)
    hy=288+13*sin(t*.19);vx=630+132*sin(t*.12)+angle*165
    grad(hy,740-hy,'344249' if night else '6e635c','13212e' if night else '334550')
    def pr(x,y,z):
        return vx+728*x/z,hy+728*(2.7-y)/z
    speed={'exchange':5.4,'campus':4.8,'mill':7.8,'bridge':8.3,'dawn':4.5,'tunnel':6.8}[kind]
    pos=t*speed
    for x,col in [(-5,'657177'),(-3.6,'a9b9b4'),(-1,'7d989b'),(1,'bdbaa3'),(3.6,'8ca4a1'),(5,'47616d')]:
        path([pr(x,0,240),pr(x+.065,0,240),pr(x+.065,0,1.2),pr(x,0,1.2)],col)
    for i in range(68,0,-1):
        z=i*1.5-pos%1.5
        if z<2:continue
        a,b=pr(-2,-.05,z),pr(2,-.05,z)
        line(a,b,'48535a',max(1,12/z))
    for i in range(22,0,-1):
        z=i*8-pos%8
        if z<2:continue
        ident=i+int(pos//8)
        for side in (-1,1):
            x=side*(6 if kind in ('tunnel','bridge') else 8)
            def face(coords,h):path([pr(*v) for v in coords],h)
            H=5+(ident*7+side*9)%13
            if kind in ('exchange','campus','mill','dawn'):
                depth=6.7;outside=x+side*4
                if kind=='campus':H=5+(ident%3==0)*2
                face([(x,0,z),(x,0,z+depth),(x,H,z+depth),(x,H,z)],'344657' if side<0 else '34434b')
                face([(x,0,z),(outside,0,z),(outside,H,z),(x,H,z)],'233542' if night else '5d5658')
                for row in range(1,int(H),2):
                    for k in (1,3,5):
                        if (ident+k+row)%5==0:continue
                        face([(x,row,z+k),(x,row+.55,z+k),(x,row+.55,z+k+1),(x,row,z+k+1)],'c29f79' if (ident+row)%3 else '659d9e')
                if kind=='campus':
                    for k in (1,3,5):
                        line(pr(x-side*.6,0,z+k),pr(x-side*.6,4,z+k),'9e9785',max(1,110/z))
                    face([(x-side*.8,4,z),(x-side*.8,4,z+6),(x-side*.8,5,z+3)],'c1a386')
                if kind=='mill':
                    xx=outside+side*2
                    line(pr(xx,0,z),pr(xx,H+4,z),'705251',max(1,490/z))
                    if ident%3==0:
                        for j in range(5):
                            a,b=pr(xx+j*.43,H+4+j*.6,z);ell(a,b,(j+2)*35/z,(j+2)*19/z,'647278')
            else:
                col='506174' if kind=='bridge' else '304759'
                line(pr(x,0,z),pr(x,8,z),col,max(1,182/z))
                line(pr(x,8,z),pr(-x,8,z),'536470',max(1,127/z))
                if kind=='bridge':line(pr(x,0,z),pr(x,8,z+8),'79828a',max(1,85/z))
                else:face([(x,0,z),(x,0,z+8),(x,8,z+8),(x,8,z)],'263746' if ident%2 else '223140')
            lx,ly=pr(side*4.7,4,z);base=pr(side*4.7,0,z)
            line(base,(lx,ly),'233746',max(1,36/z));lamp(lx,ly,max(2,145/z),'f8b779')
    if kind=='bridge' and angle>0:train(1480-u*3300,493,.65,t)
    if angle==0:
        path([(0,0),(30,0),(105,645),(182,720),(0,720)],'101d28')
        path([(1280,0),(1251,0),(1186,610),(1110,720),(1280,720)],'121e29')
        path([(0,685),(295,621),(880,640),(1280,708),(1280,720),(0,720)],'1a2b36')
        for j in range(4):ell(900+j*18,670+j,3,2,'e8ae74')
def control(t,u):
    grad(0,720,'182e36','15202f')
    # Luminous route board, three tracks split and reconnect around a dark island.
    paths=[[(30,410),(190,410),(315,260),(690,260),(855,384),(1250,384)],[(30,434),(200,434),(336,285),(514,285),(680,466),(1010,466),(1090,401),(1250,401)],[(30,457),(236,457),(363,325),(550,325),(714,185),(1052,185),(1250,333)]]
    for n,pts in enumerate(paths):
        col=['e9a779','79b9b2','889ab7'][n]
        path(pts,col,4,False)
        for x,y in pts[1:-1]:ell(x,y,9,9,'1a2b37');c.drawCircle(x,y,8,pen(col,2))
        v=(u*.92+n*.25)%1*(len(pts)-1);k=int(v);f=v-k
        x,y=[pts[k][i]*(1-f)+pts[k+1][i]*f for i in [0,1]];lamp(x,y,30,col)
    for j in range(14):box(j*110,0,2,720,'253941')
def carriage(t,u):
    # The carriage windows double as exchange charts. Bars reflected in the glass grow into buildings.
    grad(0,720,'1b2c42','49616a')
    for j in range(24):
        x=j*73-(t*93)%73
        v=28+104*(.5+.5*sin(j*11.6+t*.56))
        box(x,345-v,56,v+42,'314957')
        for k in range(3):box(x+7+14*k,350-v,5,7,'dba675')
    for j in range(29):
        x=j*47-(t*20)%47
        cen=228+54*sin(j*.57+t*.16);r=9+18*(.5+.5*cos(j*1.7))
        col='c99480' if j%3==0 else '83aaa5'
        line((x,cen-r-13),(x,cen+r+12),col,1.4);box(x-4,cen-r,8,2*r,col)
    box(0,0,1280,72,'24303c');box(0,380,1280,12,'c59878');grad(392,328,'425056','1c2935')
    for x in [156,552,948]:
        xx=x-48*u;box(xx,0,16,380,'273b44');box(xx+16,70,3,310,'97a5a0')
        line((xx+68,52),(xx+68,110),'918f84',3);path([(xx+68,108),(xx+53,134),(xx+84,134)],'d9b591',4)
    for j in range(5):
        x=75+j*244-u*49;y=496+10*sin(j+t*.3)
        path([(x-68,720),(x-55,y+72),(x-26,y+41),(x+28,y+44),(x+62,y+74),(x+76,720)],'172731')
        ell(x,y,32,48,'1c2d34');path([(x-25,y-27),(x-15,y-49),(x+12,y-49),(x+28,y-20)],'141e29')
        line((x-22,y+57),(x-40,y+110),'40505a',2)
def auditorium(t,u):
    grad(0,720,'1b2335','52444b')
    for j in range(9):
        x=j*168-38*u;box(x,32,146,310,'364756')
        for k in range(3):line((x,96+k*64),(x+146,96+k*64),'273944',3)
    # The lit lectern sits on a conveyor. Rows of desks are progressively replaced by identical parcels.
    path([(350,0),(856,0),(1015,382),(234,382)],'48555a')
    path([(530,332),(727,332),(709,468),(553,468)],'685955')
    box(520,320,217,12,'d6a377');passenger(620,318,1.9,t*.5,'6f6460')
    for row in range(3):
        y=426+row*115;delta=178+row*43
        for j in range(9):
            x=-110+j*delta-(u*90+row*57)
            if (j+row)%7 < u*7:
                path([(x-15,y),(x-15,y-52),(x+36,y-63),(x+81,y-49),(x+81,y)],'856c5b')
                path([(x-15,y-52),(x+31,y-40),(x+81,y-49),(x+36,y-63)],'c69f7b')
                line((x+31,y-40),(x+31,y),'503f40',2)
            else:passenger(x+30,y,1.45+row*.35,t*.44+j,'30414a')
            box(x-37,y,151+row*28,9,'aa8771')
            line((x-21,y+9),(x-26,y+63),'28353c',5)
        box(0,y+60,1280,8,'303b43')
def frame(t):
    global c
    surf=sk.Surface(2560,1440);c=surf.getCanvas();c.scale(2,2)
    seq=[(0,'tunnel',0),(10,'campus',-1),(20,'control',0),(25,'campus',0),(39,'carriage',1),(52,'bridge',0),(61,'station',0),(71,'departure',0),(80,'control',0),(87,'mill',0),(100,'auditorium',-1),(111,'bridge',1),(122,'auditorium',0),(135,'station',0),(144,'tunnel',0),(154,'control',0),(161,'dawn',1),(172,'carriage',-1),(178,'dawn',0),(184.15,'end',0)]
    i=next(i for i in range(len(seq)-1) if seq[i+1][0]>t);a,m,angle=seq[i];u=(t-a)/(seq[i+1][0]-a)
    if m in ('station','departure'):station(t,u,m=='departure')
    elif m=='control':control(t,u)
    elif m=='carriage':carriage(t,u)
    elif m=='auditorium':auditorium(t,u)
    else:ride(t,u,m,angle)
    return surf.makeImageSnapshot()
if __name__=='__main__':
    preview='--preview' in sys.argv
    if preview:
        board=Image.new('RGB',(1200,675))
        for j,t in enumerate((5,28,46,58,65,75,83,94,116,126,151,166)):
            im=Image.fromarray(frame(t).toarray()[:,:,[2,1,0]]).resize((300,169));board.paste(im,(j%4*300,j//4*169))
        board.crop((0,0,1200,507)).save(W/'board.jpg')
    out=W/('preview.mp4' if preview else 'picture.mp4')
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s','2560x1440','-r','24','-i','-','-an','-c:v','h264_nvenc','-preset','p4','-cq','18','-b:v','0','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
    for n in range(48 if preview else 4418):p.stdin.write(frame(n/24+(60 if preview else 0)).tobytes())
    p.stdin.close();sys.exit(p.wait())

