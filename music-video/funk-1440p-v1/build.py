from pathlib import Path
import json,re,math,subprocess,hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[2]; W=ROOT/'work/funk-video'; OUT=ROOT/'outputs/funk-video-1440p'; W.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
AUDIO=ROOT/'outputs/original-voices/main/09-minimax-trio-funk-01.mp3'
REPO=Path('I:/VOICE/voice')
brief=json.loads((REPO/'music/minimax-trio/funk.json').read_text(encoding='utf-8'))
raw=json.loads((REPO/'work/minimax-trio/funk-01/transcript.json').read_text(encoding='utf-8'))
gap=json.loads((W/'gap-transcript.json').read_text(encoding='utf-8'))
words=[w for s in raw for w in s['words'] if w['end']<=54.96 or w['start']>=85.68]
words += [w for s in gap for w in s['words'] if w['start']>=54.96 and w['end']<=85.68]
words.sort(key=lambda w:w['start'])
lines=[]; section='Intro'
for l in brief['lyrics'].splitlines():
 if l.startswith('['): section=l.strip('[]'); continue
 if l.strip(): lines.append({'text':l.strip(),'section':section})
# Correct displayed artist spelling while retaining original audio.
lines[0]['text']='Йо, это рэп трек, с вами ADV aka Adventus Devotus'
def norm(s): return re.sub(r'[^a-zа-яё0-9]','',s.lower()).replace('ё','е')
tokens=[]
for i,l in enumerate(lines):
 for token in l['text'].split():
  if norm(token): tokens.append({'word':token,'line':i})
  elif tokens and tokens[-1]['line']==i: tokens[-1]['word']+=' '+token
a=[norm(x['word']) for x in tokens]; b=[norm(x['word']) for x in words]
n,m=len(a),len(b); dp=np.zeros((n+1,m+1),np.float32); bt=np.zeros((n+1,m+1),np.uint8)
dp[:,0]=np.arange(n+1)*.85; dp[0,:]=np.arange(m+1)*.85
for i in range(1,n+1):
 for j in range(1,m+1):
  sim=SequenceMatcher(None,a[i-1],b[j-1]).ratio()
  opts=(dp[i-1,j-1]+1.3*(1-sim),dp[i-1,j]+.85,dp[i,j-1]+.85)
  k=int(np.argmin(opts)); dp[i,j]=opts[k]; bt[i,j]=k
pairs=[];i=n;j=m
while i and j:
 k=bt[i,j]
 if k==0:
  if SequenceMatcher(None,a[i-1],b[j-1]).ratio()>=.42: pairs.append((i-1,j-1))
  i-=1;j-=1
 elif k==1:i-=1
 else:j-=1
pairs.reverse(); anchors={i:words[j]['start'] for i,j in pairs}
# Explicit phrase anchor for artist intro, whose ASR is unreliable.
for k,t in enumerate([0,.14,.78,1.04,1.27,1.55,1.8,2.1,2.6,3.25]): anchors[k]=t
xs=sorted(anchors); ts=np.interp(np.arange(n),xs,[anchors[x] for x in xs]); ts=np.maximum.accumulate(ts)
# Explicit anchors for two ambiguous ASR boundaries.
for k,x in enumerate(tokens):
 if lines[x['line']]['text'].startswith('Ник Ленд') and norm(x['word'])=='ник': ts[k]=85.68
 if lines[x['line']]['text']=='Кто кого купит?' and ts[k]<160:
  ts[k]={'кто':154.60,'кого':154.74,'купит':155.10}.get(norm(x['word']),ts[k])
for k,x in enumerate(tokens): x['start']=round(float(ts[k]),3);x['end']=round(float(ts[k+1] if k+1<n else 254.8),3)
for i,l in enumerate(lines):
 ww=[w for w in tokens if w['line']==i];l['words']=ww;l['start']=ww[0]['start'];l['end']=ww[-1]['end']
(W/'alignment.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf8')
(W/'timing-review.txt').write_text('\n'.join(f"{l['start']:7.2f} - {l['end']:7.2f}  {l['text']}" for l in lines),encoding='utf8')
DUR=257.9273
# Phrases define chapters; designs evolve from clay to computation and back.
scenes=[(0,'ОБМЕН','whistle'),(18.74,'ПОЧВА / КОД','village'),(41.56,'СРАСТАНИЕ','hybrid'),(63.38,'10 : 1','exchange'),(85.68,'ПЕТЛЯ СВЯЗИ','loop'),(108.3,'ВЫХОД','grid'),(129.4,'ДВА ПРОЕКТА','hybrid'),(142.22,'БЕЗ ГОЛОВЫ','exchange'),(156.74,'ПРОТИВОРЕЧИЕ','loop'),(179.54,'КУРС СВИСТУЛЬКИ','machine'),(201.22,'ХОЛОД','machine'),(214,'10 : 1','exchange'),(221.42,'ПРЕДЕЛ','grid'),(233.44,'ПЕТЛЯ НЕ ЗАМКНУТА','loop'),(244.58,'ОДИННАДЦАТАЯ','whistle')]
cream=(237,231,213); ink=(34,39,35); red=(170,61,38); muted=(122,121,104)
font='C:/Windows/Fonts/arialbd.ttf'; mono='C:/Windows/Fonts/consola.ttf'
def ft(s,mo=False):return ImageFont.truetype(mono if mo else font,s)
def whistle(d,cx,cy,s=1,col=ink):
 def pts(p): return [(int(cx+x*s),int(cy+y*s)) for x,y in p]
 d.polygon(pts([(-190,40),(-170,-55),(-105,-108),(8,-108),(80,-60),(150,-42),(169,-70),(213,-69),(210,-8),(151,9),(96,85),(-29,110),(-143,92)]),fill=col)
 d.ellipse((cx-87*s,cy-49*s,cx-49*s,cy-11*s),fill=cream)
 d.line(pts([(-140,54),(-90,69),(-28,78),(45,58)]),fill=cream,width=max(2,int(s*4)))
 for x in [-110,-70,-30,10,50]:d.line(pts([(x,5),(x+15,31)]),fill=cream,width=max(2,int(s*3)))
def machine(d,cx,cy,s=1):
 x=cx-150*s;y=cy-240*s;d.rectangle((x,y,cx+150*s,cy+240*s),outline=ink,width=6)
 for i in range(6):
  yy=y+25*s+i*76*s;d.rectangle((x+22*s,yy,cx+128*s,yy+52*s),outline=ink,width=3)
  for j in range(3):d.ellipse((x+38*s+j*22*s,yy+17*s,x+47*s+j*22*s,yy+26*s),fill=red if j==0 else ink)
  d.line((cx+15*s,yy+25*s,cx+105*s,yy+25*s),fill=ink,width=3)
def dome(d,cx,cy,s=1):
 d.arc((cx-230*s,cy-220*s,cx+230*s,cy+220*s),180,360,fill=ink,width=7)
 d.line((cx-230*s,cy,cx+230*s,cy),fill=ink,width=6)
 for x in [-140,-50,70]:
  xx=cx+x*s; yy=cy-70*s
  d.rectangle((xx,yy,xx+74*s,cy),outline=ink,width=4)
  d.line((xx-7*s,yy,xx+37*s,yy-47*s,xx+82*s,yy),fill=ink,width=4)
  d.rectangle((xx+30*s,yy+28*s,xx+44*s,cy),fill=red)
def drawscene(idx,label,kind):
 # Native 2560 x 1440 artwork. Sparse deterministic ink flecks imitate print stock.
 im=Image.new('RGB',(2560,1440),cream);d=ImageDraw.Draw(im);rng=np.random.default_rng(91)
 for _ in range(4500):
  x=int(rng.integers(2560));y=int(rng.integers(1440));v=int(rng.integers(214,232));d.point((x,y),fill=(v,v-4,v-14))
 d.line((112,160,2448,160),fill=ink,width=2)
 d.text((112,83),'ADV / ДЕСЯТЬ СВИСТУЛЕК',font=ft(30,True),fill=ink)
 d.text((1810,83),'СИНГУЛЯРНОСТЬ / 01',font=ft(30,True),fill=ink)
 d.text((114,247),f'{idx+1:02d}   /   {label}',font=ft(28,True),fill=red)
 d.line((112,1270,2448,1270),fill=ink,width=2)
 d.text((112,1310),'ГЛИНА → КОД → ГЛИНА',font=ft(26,True),fill=muted)
 d.text((1995,1310),'FUNK / 2026',font=ft(26,True),fill=muted)
 cx=2070;cy=730
 if kind=='whistle':
  whistle(d,cx,cy,1.4)
  for j in range(3): d.arc((cx+230+j*35,cy-155-j*24,cx+290+j*35,cy-65+j*24),-65,60,fill=red,width=4)
  d.text((1830,1020),'11' if idx==14 else '10',font=ft(130),fill=red)
 elif kind=='village':
  dome(d,cx,cy,1.25);d.line((cx,cy+35,cx,cy+160),fill=red,width=4);machine(d,cx,cy+300,.37)
 elif kind=='machine':
  machine(d,cx,cy,1.12)
  d.arc((cx-280,cy-310,cx+280,cy+310),45,165,fill=red,width=5)
  for j in range(5): d.line((cx-255,cy-100+j*48,cx-180,cy-100+j*48),fill=red,width=3)
 elif kind=='exchange':
  for j in range(10): whistle(d,1870+(j%2)*210,480+(j//2)*92,.35)
  d.text((2160,600),'=',font=ft(110),fill=red);d.rectangle((2275,630,2385,740),outline=ink,width=6);d.line((2330,600,2330,770),fill=red,width=3)
  d.text((1830,1030),'10 / 1',font=ft(90),fill=ink)
 elif kind=='hybrid':
  dome(d,cx,cy-20,1.12)
  for j in range(6):
   xx=cx-210+j*85;d.line((xx,cy+10,xx,cy+140+(j%2)*70,cx,cy+140+(j%2)*70),fill=red,width=4)
  machine(d,cx,cy+285,.36)
 elif kind=='loop':
  d.arc((cx-270,cy-270,cx+270,cy+270),-62,265,fill=ink,width=14)
  d.polygon([(cx-50,cy-290),(cx+30,cy-270),(cx-30,cy-230)],fill=red)
  whistle(d,cx,cy,.8)
  d.line((cx+130,cy-280,cx+260,cy-160),fill=red,width=6)
 elif kind=='grid':
  for j in range(3):
   for k in range(3):
    xx=cx-260+j*180; yy=cy-260+k*180;d.rectangle((xx,yy,xx+135,yy+135),outline=ink,width=4)
    if j==k:whistle(d,xx+67,yy+68,.22,red)
  d.line((cx-285,cy+300,cx+260,cy+300),fill=red,width=6)
 d.text((1810,1170),['ОБЪЕКТ / ГЛИНА','ОБЪЕКТ / СИСТЕМА'][kind not in ('whistle','exchange')],font=ft(22,True),fill=muted)
 im.save(W/f'scene-{idx:02d}.png')
for idx,(_,label,kind) in enumerate(scenes):drawscene(idx,label,kind)
# ASS: word-by-word ink reveals, stable baselines, no bouncing text.
def at(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1440
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lyrics,Arial,88,&H00232722,&HFF232722,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Small,Consolas,26,&H0068797A,&HFF68797A,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
events=[]
def ev(st,en,style,text,layer=1):
 if en>st:events.append(f'Dialogue: {layer},{at(st)},{at(en)},{style},,0,0,0,,{text}')
for l in lines:
 txt=l['text'];hook=txt in ['Десять свистулек!','Один кубит!','Кто здесь субъект?','Кто кого купит?']
 size=138 if hook else 88
 f=ft(size);maxw=1510
 # maintain token timing while wrapping to actual font widths
 wrapped=[];current=[]
 for w in l['words']:
  candidate=' '.join(x['word'] for x in current+[w])
  if current and f.getlength(candidate)>maxw:wrapped.append(current);current=[]
  current.append(w)
 if current:wrapped.append(current)
 y=int(700-len(wrapped)*size*.58)
 st=l['start'];end=min(l['end'],254.9)
 for row,ww in enumerate(wrapped):
  text=f'{{\\pos(112,{y+int(row*size*1.17)})\\fs{size}\\fad(0,90)}}'
  if hook:text+='{\\c&H263DAA&}'
  delay=max(0,round((ww[0]['start']-st)*100))
  if delay:text+=f'{{\\k{delay}}}'+r'\h'
  for w in ww:
   dur=max(1,round((w['end']-w['start'])*100));text+=f'{{\\k{dur}}}'+w['word']+' '
  ev(st,end,'Lyrics',text)
 # progression indication tied to each phrase rather than arbitrary waveform
 ev(st,end,'Small',f'{{\\pos(114,1110)}}{lines.index(l)+1:02d} / {len(lines):02d}')
# restrained transient-driven mark: measured bass onsets; no fabricated BPM grid
subprocess.run(['ffmpeg','-v','error','-y','-i',str(AUDIO),'-ac','1','-ar','8000',str(W/'analysis.wav')],check=True)
import soundfile as sf
from scipy.signal import butter,sosfilt,find_peaks
sig,sr=sf.read(W/'analysis.wav');low=sosfilt(butter(3,150,fs=sr,output='sos'),sig)
hop=160;eng=np.array([np.sqrt(np.mean(low[i:i+hop]**2)) for i in range(0,len(low),hop)])
flux=np.maximum(0,np.diff(eng,prepend=eng[0]));peaks,_=find_peaks(flux,distance=12,prominence=np.quantile(flux,.80))
for p in peaks:
 st=p*hop/sr;ev(st,min(st+.12,DUR),'Lyrics',r'{\pos(2408,1312)\1c&H263DAA&\fad(0,90)\p1}m 0 0 l 16 0 16 16 0 16',2)
# Clear ending after the last spoken line.
ev(254.9,DUR,'Lyrics',r'{\pos(112,610)\fs104\fad(200,400)}МАШИНА ПРОСИТ СКИДКУ.')
(W/'lyrics.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf-8-sig')
# lossless static art sequence; FFmpeg supplies 30fps and animated ASS reveals
concat=[]
for i,(st,_,_) in enumerate(scenes):
 end=scenes[i+1][0] if i+1<len(scenes) else DUR
 concat += [f"file 'scene-{i:02d}.png'",f'duration {end-st:.5f}']
concat.append(f"file 'scene-{len(scenes)-1:02d}.png'")
(W/'scenes.txt').write_text('\n'.join(concat),encoding='utf8')
manifest={'input':str(AUDIO),'sha256':hashlib.sha256(AUDIO.read_bytes()).hexdigest(),'duration':DUR,'resolution':[2560,1440],'fps':30,'scenes':scenes,'lyrics_source':str(REPO/'music/minimax-trio/funk.json'),'timing':'Faster Whisper word timestamps + gap retranscription + fuzzy monotonic mapping to source lyrics; imperfect diction may differ from printed lyrics.','art':'Original procedural 2D ink illustrations; Pillow CPU, libass CPU, NVIDIA NVENC encoder','audio':'Unchanged arrangement, no voice conversion, no effects. AAC delivery encoding.'}
(OUT/'production.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Prepared',len(lines),'lyric lines;',len(peaks),'transients;',len(scenes),'scenes')
