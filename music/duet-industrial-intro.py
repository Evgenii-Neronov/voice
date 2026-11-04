"""Use the clearer MiniMax musical greeting before the industrial ACE performance."""
import json
from pathlib import Path
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1]; w=R/'work/duets/ace-industrial'; backup=w/'stems-original'; (w/'stems').rename(backup); (w/'stems').mkdir()
for name in ['vocals.wav','instrumental.wav']:
 a,s=sf.read(R/'work/duets/minimax-room/stems'/name,always_2d=True); b,t=sf.read(backup/name,always_2d=True); assert s==t==44100
 head=a[:round(5.7*s)].copy(); rest=b[11*s:].copy(); f=round(.06*s); head[-f:]*=np.linspace(1,0,f)[:,None]; rest[:f]*=np.linspace(0,1,f)[:,None]
 sf.write(w/'stems'/name,np.concatenate([head,rest]),s,subtype='FLOAT')
p=R/'music/duet/ace-industrial.timeline.json'; m=json.loads(p.read_text(encoding='utf-8')); shift=-5.3
if 'edit' not in m:
 for region in m['ezhi_regions']:
  if region['start']>0: region['start']+=shift
  region['end']+=shift
m['preview_regions']=[[0,5.7],[29,41],[131.6,143.6]]; m['fx_comparison_region']=[29,41]; m['greeting_engine']='minimax'; m['edit']={'musical_greeting_source':'duet-minimax-room','source_interval':[0,5.7],'ace_resume_seconds':11,'timeline_shift_seconds':shift,'reason':'ACE greeting poorly recognized in two trials; clearer MiniMax musical phrase selected, not TTS'}
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(w/'greeting-edit.json').write_text(json.dumps(m['edit'],indent=2),encoding='utf-8')
