from pathlib import Path
import json,re,numpy as np
from difflib import SequenceMatcher
W=Path(__file__).resolve().parent;R=Path('I:/VOICE/voice');brief=json.loads((R/'music/rap4-dialogue/brief.json').read_text(encoding='utf8'));base=json.loads((R/'work/rap4-dialogue/01/transcript.json').read_text(encoding='utf8'));tail=json.loads((R/'work/rap4-dialogue-outro/01/transcript.json').read_text(encoding='utf8'))
words=[w for seg in base for w in seg['words'] if w['start']<256.28]
words += [{**w,'start':w['start']+256.28,'end':w['end']+256.28} for seg in tail for w in seg['words']]
lines=[l.strip().replace('—','-').replace('–','-').replace('−','-') for l in brief['lyrics'].splitlines() if l.strip() and not l.startswith('[')]
def norm(s):return re.sub('[^a-zа-я0-9]','',s.lower().replace('ё','е'))
tokens=[{'word':w,'line':i} for i,line in enumerate(lines) for w in line.split() if norm(w)];an=[norm(x['word']) for x in tokens];bn=[norm(w['word']) for w in words];n,m=len(an),len(bn);dp=np.zeros((n+1,m+1));bt=np.zeros((n+1,m+1),np.uint8);dp[:,0]=np.arange(n+1)*.85;dp[0,:]=np.arange(m+1)*.85
for i in range(1,n+1):
 for j in range(1,m+1):
  sim=SequenceMatcher(None,an[i-1],bn[j-1]).ratio();cost=[dp[i-1,j-1]+1.3*(1-sim),dp[i-1,j]+.85,dp[i,j-1]+.85];k=int(np.argmin(cost));dp[i,j]=cost[k];bt[i,j]=k
anchors={};i=n;j=m
while i and j:
 k=bt[i,j]
 if k==0:
  if SequenceMatcher(None,an[i-1],bn[j-1]).ratio()>=.46:anchors[i-1]=words[j-1]['start']
  i-=1;j-=1
 elif k==1:i-=1
 else:j-=1
anchors[0]=0;outroi=next(i for i,l in enumerate(lines) if l.startswith('Семинар окончен'));anchors[next(i for i,x in enumerate(tokens) if x['line']==outroi)]=256.28
xs=sorted(anchors);ts=np.maximum.accumulate(np.interp(np.arange(n),xs,[anchors[k] for k in xs]));events=[]
for i,line in enumerate(lines):
 ids=[j for j,x in enumerate(tokens) if x['line']==i];a=float(ts[ids[0]]);end=float(ts[ids[-1]+1]) if ids[-1]+1<n else 272.3
 events.append({'start':a,'end':max(a+.15,end),'text':line,'speaker':'EZHI' if i>=outroi else 'ADV'})
events[0]['text']='Йо-йо, это рэп-трек, с вами ADV aka Adventus Devotus.'
(W/'alignment.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf8');(W/'timing-review.txt').write_text('\n'.join(f"{x['start']:7.2f} {x['end']:7.2f} {x['speaker']} {x['text']}" for x in events),encoding='utf8')
def tc(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02d}:{c//100%60:02d}.{c%100:02d}'
header=(W.parent/'nyc-boombap-v3/subtitles.ass').read_text(encoding='utf8').split('Dialogue:')[0];from PIL import ImageFont
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',56);out=[]
for e in events:
 rows=['']
 for word in e['text'].split():
  s=(rows[-1]+' '+word).strip()
  if f.getlength(s)>2050:rows.append(word)
  else:rows[-1]=s
 assert len(rows)<=2
 out.append(f"Dialogue: 0,{tc(e['start'])},{tc(e['end'])},Cinema,,0,0,0,,"+r'\N'.join(rows))
ass=header+'\n'.join(out);assert all(c not in ass for c in ['—','–','−']);(W/'subtitles.ass').write_text(ass,encoding='utf8')
(W/'audio-manifest.json').write_text(json.dumps({'track':'I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3','duration':273.188571,'outro_start':256.28,'ezhi_entrance_start':251.8,'ezhi_entrance_end':255.9,'source_alignment':'Existing local Whisper word timestamps, base plus outro at256.28s, text sequence alignment; approximate','subtitle_lines':len(events),'dash':'ASCII hyphen U+002D','outro_assignment':'All final block from Semинар окончен shown as Ezhi, per current user direction; audio unchanged'},ensure_ascii=False,indent=2),encoding='utf8');print('Aligned',len(events),'lines, outro index',outroi)
