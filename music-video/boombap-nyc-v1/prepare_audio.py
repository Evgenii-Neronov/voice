from pathlib import Path
import json,re,math
import numpy as np
from difflib import SequenceMatcher
import soundfile as sf
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-1440p';R=Path('I:/VOICE/voice')
brief=json.loads((R/'music/minimax-trio/boombap.json').read_text(encoding='utf8'));raw=json.loads((R/'work/minimax-trio/boombap-01/transcript.json').read_text(encoding='utf8'))
words=[w for s in raw for w in s['words']];lines=[]
for l in brief['lyrics'].splitlines():
 if l.strip() and not l.startswith('['):lines.append({'text':l.strip()})
lines[0]['text']='Йо, это рэп трек, с вами ADV aka Adventus Devotus'
def norm(s):return re.sub('[^a-zа-я0-9]','',s.lower().replace('ё','е'))
tokens=[]
for i,l in enumerate(lines):
 for t in l['text'].split():
  if norm(t):tokens.append({'word':t,'line':i})
  elif tokens:tokens[-1]['word']+=' '+t
an=[norm(x['word']) for x in tokens];bn=[norm(x['word']) for x in words];n=len(an);m=len(bn);dp=np.zeros((n+1,m+1));bt=np.zeros((n+1,m+1),np.uint8);dp[:,0]=np.arange(n+1)*.85;dp[0,:]=np.arange(m+1)*.85
for i in range(1,n+1):
 for j in range(1,m+1):
  sim=SequenceMatcher(None,an[i-1],bn[j-1]).ratio();cost=(dp[i-1,j-1]+1.3*(1-sim),dp[i-1,j]+.85,dp[i,j-1]+.85);k=int(np.argmin(cost));dp[i,j]=cost[k];bt[i,j]=k
anchors={};i=n;j=m
while i and j:
 k=bt[i,j]
 if k==0:
  if SequenceMatcher(None,an[i-1],bn[j-1]).ratio()>=.42:anchors[i-1]=words[j-1]['start']
  i-=1;j-=1
 elif k==1:i-=1
 else:j-=1
for k,t in enumerate([0,.15,.35,.65,1,1.3,1.55,1.9,2.4,2.95]):anchors[k]=t
xs=sorted(anchors);ts=np.maximum.accumulate(np.interp(np.arange(n),xs,[anchors[k] for k in xs]))
for i,x in enumerate(tokens):x['start']=float(ts[i]);x['end']=float(ts[i+1] if i+1<n else 243.82)
for i,l in enumerate(lines):
 ww=[t for t in tokens if t['line']==i];l['start']=ww[0]['start'];l['end']=ww[-1]['end'];l['words']=ww
(W/'alignment.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf8')
(W/'timing-review.txt').write_text('\n'.join(f"{l['start']:6.2f} {l['end']:6.2f} {l['text']}" for l in lines),encoding='utf8')
def tc(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02d}:{c//100%60:02d}.{c%100:02d}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 2560
PlayResY: 1440
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cinema,Arial,56,&H004CEBFF,&H004CEBFF,&H00141310,&H80000000,0,0,0,0,100,100,0,0,1,2.3,1.2,2,220,220,105,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
from PIL import ImageFont
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',56)
events=[]
for l in lines:
 txt=l['text'];words=txt.split();rows=['']
 for word in words:
  nxt=(rows[-1]+' '+word).strip()
  if f.getlength(nxt)>1750:rows.append(word)
  else:rows[-1]=nxt
 assert len(rows)<=2
 events.append(f"Dialogue: 0,{tc(l['start'])},{tc(l['end'])},Cinema,,0,0,0,,"+r'\N'.join(rows))
(W/'subtitles.ass').write_text(header+'\n'.join(events),encoding='utf-8-sig');(O/'subtitles.ass').write_text(header+'\n'.join(events),encoding='utf-8-sig')
a,sr=sf.read(R/'work/minimax-trio/boombap-01/stems/vocals.wav');a=a.mean(axis=1);hop=round(sr/48);env=np.array([np.sqrt(np.mean(a[k:k+hop]**2)) for k in range(0,len(a),hop)]);env=np.clip(env/max(.01,np.quantile(env,.93)),0,1);np.save(W/'voice-envelope.npy',env)
print('Subtitles and vocal envelope ready',len(lines))
