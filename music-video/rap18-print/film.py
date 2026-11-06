from pathlib import Path
import json, math, subprocess, sys
import numpy as np
import skia as sk
from PIL import Image
from scipy.signal import find_peaks
W=Path(__file__).resolve().parent
ROOT=W.parents[1]
AUDIO=ROOT/'outputs/rap-18/rap-18.mp3'
sin,cos,pi=math.sin,math.cos,math.pi
INK='#20232b'; PAPER='#e7d8b9'; RED='#bf462e'; DARK='#752f29'; LIGHT='#f4e8cd'; GREY='#9a927e'
def paint(h,width=0):
    p=sk.Paint(Color=int('ff'+h[1:],16),AntiAlias=True)
    if width:
        p.setStyle(sk.Paint.kStroke_Style);p.setStrokeWidth(width);p.setStrokeCap(sk.Paint.kRound_Cap)
    return p
def poly(points,h,stroke=0,close=True):
    path=sk.Path();path.moveTo(*points[0])
    for pt in points[1:]:path.lineTo(*pt)
    if close:path.close()
    c.drawPath(path,paint(h,stroke))
def rect(x,y,w,h,col):c.drawRect(sk.Rect.MakeXYWH(x,y,w,h),paint(col))
def oval(x,y,rx,ry,col,width=0):c.drawOval(sk.Rect.MakeXYWH(x-rx,y-ry,2*rx,2*ry),paint(col,width))
def line(x,y,X,Y,col,w):c.drawLine(x,y,X,Y,paint(col,w))
from functools import lru_cache
@lru_cache(None)
def ridge_plate(ink):
    global c
    prior=c
    recorder=sk.PictureRecorder()
    c=recorder.beginRecording(sk.Rect.MakeLTRB(-100,-140,100,140))
    draw_ridges(ink)
    pic=recorder.finishRecordingAsPicture()
    c=prior
    return pic
def stamp(x,y,size,angle,ink=INK):
    c.save();c.translate(x,y);c.rotate(angle);c.scale(size,size);c.drawPicture(ridge_plate(ink));c.restore()
def draw_ridges(ink):
    for k in range(2,25):
        a0=.45+sin(k*.48)*.24+k*.07
        a=np.linspace(a0,a0+2*pi-.09-.17*(1+sin(k*.62)),80)
        pts=list(zip((k*3.3*np.cos(a)+5*np.sin(a*2)+2*np.sin(3*a+k*.13)).tolist(),(k*4.7*np.sin(a)+k*.31*np.cos(2*a)).tolist()))
        poly(pts,ink,1.9,False)
def hand(x,y,scale,angle):
    c.save();c.translate(x,y);c.rotate(angle);c.scale(scale,scale)
    # Profile of a printer's hand, thumb and fingers curled over the platen.
    outline=[(-370,64),(-170,26),(-86,-20),(-38,-49),(1,-52),(51,-40),(113,-31),(134,-22),(135,-11),(118,-5),(66,-11),(38,-12),(92,2),(111,13),(110,22),(95,25),(39,13),(80,33),(83,43),(71,48),(20,32),(42,54),(38,62),(22,62),(-25,41),(-67,48),(-111,68),(-180,105),(-370,149)]
    poly(outline,INK)
    for j in range(11):line(-300+j*12,65-j*2,-158+j*6,42-j*2,PAPER,1.5)
    for j in range(6):line(-75+j*6,9-j*3,-31+j*4,-17-j*3,PAPER,1.5)
    poly([(-361,60),(-190,21),(-163,104),(-365,160)],RED)
    for j in range(7):line(-188-j*5,29+j,-166-j*5,96+j,INK,2)
    c.restore()
def gear(x,y,r,t):
    pts=[]
    for i in range(72):
        a=i*pi/36+t;rr=r*(1 if i%4 in (1,2) else .88);pts.append((x+rr*cos(a),y+rr*sin(a)))
    poly(pts,INK);oval(x,y,r*.66,r*.66,PAPER)
    for j in range(5):
        a=t+j*2*pi/5;line(x,y,x+r*.68*cos(a),y+r*.68*sin(a),INK,r*.12)
    oval(x,y,r*.20,r*.20,RED)
def person(x,y,s,t):
    c.save();c.translate(x,y);c.scale(s,s)
    lean=sin(t)*3
    oval(lean,-47,8,10,INK);poly([(-6,-37),(6,-38),(10,-19),(6,-13),(-8,-13),(-10,-23)],INK)
    for side in [-1,1]:
        dx=sin(t)*6*side;line(side*4,-14,side*5+dx,0,INK,4);line(side*6,-34,side*13-dx,-20,INK,3)
    c.restore()
def sheet(x,y,w,h,angle,marked=True):
    c.save();c.translate(x,y);c.rotate(angle)
    poly([(7,6),(w+8,8),(w+5,h+9),(4,h+5)],DARK)
    poly([(0,0),(w,2),(w-3,h),(1,h-2)],LIGHT)
    if marked:stamp(w*.5,h*.48,min(w/205,h/280),-9,RED)
    c.restore()
def press(x,y,s,t,drop):
    c.save();c.translate(x,y);c.scale(s,s)
    for xx in (-123,114):rect(xx,-235,15,245,INK)
    rect(-146,-244,297,23,INK);rect(-146,-7,297,17,INK)
    gear(65,-276,48,t*.7);gear(-23,-276,46,-t*.7)
    rect(-8,-225,18,70+drop,INK);rect(-83,-161+drop,171,20,RED)
    for i in range(8):line(-74+i*19,-143+drop,-61+i*19,-143+drop,INK,2)
    c.restore()
def grain():
    rng=np.random.default_rng(18);a=rng.normal(0,1,(720,1280))
    rgba=np.zeros((720,1280,4),np.uint8);rgba[:,:,:3]=np.where(a[:,:,None]>0,245,33);rgba[:,:,3]=np.minimum(40,abs(a)*15)
    return sk.Image.fromarray(rgba,colorType=sk.ColorType.kRGBA_8888_ColorType)
texture=grain()
wav=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(AUDIO),'-ac','1','-ar','12000','-f','f32le','-']),np.float32)
dur=len(wav)/12000
blocks=wav[:len(wav)//240*240].reshape(-1,240)
low=np.abs(np.fft.rfft(blocks*np.hanning(240)))[:,1:4].sum(1)
beats=find_peaks(low,distance=12,prominence=np.percentile(low,65)*.6)[0]/50
def snap(t):return float(beats[np.argmin(abs(beats-t))])
cuts=[0]+[snap(t) for t in (9,18,28,38,49,59,70,81,92,103,115,127,138,149,159,169,179)]+[dur]
modes=['touch','print','face','sorting','rollers','tiles','sorting','face','rollers','tiles','scatter','crowd','scatter','build','press','hands','edition','last']
def frame(t):
    global c
    surf=sk.Surface(2560,1440);c=surf.getCanvas();c.scale(2,2)
    ix=min(len(modes)-1,np.searchsorted(cuts[1:],t,side='right'));mode=modes[ix];u=(t-cuts[ix])/(cuts[ix+1]-cuts[ix]);pulse=min(1,low[min(len(low)-1,int(t*50))]/(np.percentile(low[::20],95)+.001))
    c.clear(int('ff'+PAPER[1:],16))
    if mode in ('touch','print','hands','last'):
        rect(0,0,1280,720,INK)
        for k in range(11):line(-100,80*k+15,1350,80*k-190,DARK,2)
        c.save();c.translate(640,350);c.rotate(-9+u*2);sheet(-295,-275,590,550,0,False)
        if mode=='last':
            for j in range(3):stamp(-112+j*108,5+18*cos(j),.66,-12+j*10,RED)
        else:stamp(0,0,(.82 if mode=='hands' else 1.38),-12,RED)
        c.restore()
        if mode!='last':hand(370+90*sin(u*pi),330+50*cos(u*pi),1.65,-9)
        if mode=='hands':hand(990-90*u,350,1.3,172)
    elif mode=='face':
        c.save();c.translate(450+260*u,360);c.scale(3.7,3.7);stamp(0,0,1,-19,INK);c.restore()
        rect(914-u*75,0,22,720,RED)
        for j in range(8):rect(1000+j*35-u*75,0,3+(j%3)*4,720,INK)
    elif mode in ('sorting','tiles','scatter'):
        for row in range(5):
            for col in range(-1,10):
                drift=(t*45)%150 if mode=='sorting' else 0
                x=col*150+drift;y=row*150-28
                spread=(u if ix==10 else 1-u) if mode=='scatter' else 0
                x+=spread*100*sin(row+col);y+=spread*100*cos(row-col)
                c.save();c.translate(x+72,y+70);c.rotate(spread*33*sin(row*2+col))
                rect(-60,-60,120,122,LIGHT if (row+col)%4 else RED)
                if (row+col)%4==0 or mode=='sorting':stamp(0,0,.44,8,INK)
                else:person(0,35,1.22,t*.9+row+col)
                c.restore()
        if mode=='sorting':
            for x in (92,1050):rect(x-u*70,0,26,720,INK)
    elif mode=='rollers':
        rect(0,0,1280,720,RED)
        poly([(-40,500),(1340,225),(1340,330),(-40,610)],LIGHT)
        for j in range(6):gear(j*295-130+u*90,420-j*55+(145 if j%2 else -145),137,t*.23*(-1)**j)
        hand(-65+230*u,638,1.6,-20)
    elif mode in ('crowd','build','press','edition'):
        horizon=332;rect(0,0,1280,horizon,INK)
        oval(981-65*u,118,62,62,RED)
        for j in range(16):
            x=j*100-50-u*23;h=36+(j*67)%114;rect(x,horizon-h,77,h,DARK)
        for j in range(13):line(610,horizon, -1300+j*320,760,GREY,1)
        for j in range(6):line(0,354+j*j*13,1280,354+j*j*13,GREY,1)
        if mode in ('build','press','edition'):press(655,482,1.15*(.55+.45*u if mode=='build' else 1),t,75*(.5+.5*cos(t*2)))
        for j in range(17):
            x=34+j*77+(52*u if j%2 else -45*u); y=413+(j*73)%230
            person(x,y,(y-300)/95,t*2+j)
        if mode=='build':
            for j in range(3):sheet(238+j*300+u*40,482+j*19,104,77,-14+j*6,False)
        if mode=='edition':
            for j in range(4):sheet(99+j*319+u*35,513+sin(t+j)*8,114,149,-9+j*4)
    c.save();c.scale(2,2);c.drawImage(texture,0,0);c.restore()
    return surf.makeImageSnapshot()
if __name__=='__main__':
    preview='--preview' in sys.argv
    out=W/('preview.mp4' if preview else 'picture.mp4')
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgra','-s','2560x1440','-r','12','-i','-','-vf','fps=24','-c:v','h264_nvenc','-preset','p4','-cq','19','-b:v','0','-pix_fmt','yuv420p',str(out)],stdin=subprocess.PIPE)
    times=np.arange(24 if preview else math.ceil(dur*12))/12+(8 if preview else 0)
    if preview:
        samples=[Image.fromarray(frame(t).toarray()[:,:,[2,1,0]]).resize((320,180)) for t in [8.1,8.6,9.1,9.6,32,52,86,117,144,163,174,181]]
        sheetimg=Image.new('RGB',(1280,540))
        for i,img in enumerate(samples):sheetimg.paste(img,(i%4*320,i//4*180))
        sheetimg.save(W/'storyboard.jpg')
    for t in times:p.stdin.write(frame(t).tobytes())
    p.stdin.close();sys.exit(p.wait())

