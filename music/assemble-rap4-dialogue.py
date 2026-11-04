"""Rebuild only the omitted outro, keeping the original rap performance intact."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1];sr=44100;cut=round(256.40*sr);fade=round(.12*sr);offset=(cut-fade)/sr
base=R/'results/music/minimax-rap4-dialogue-01';tail=R/'results/music/minimax-rap4-dialogue-outro-01';out=R/'results/music/minimax-rap4-dialogue-final-01';out.mkdir(exist_ok=False)
w1=R/'work/rap4-dialogue/01';w2=R/'work/rap4-dialogue-outro/01';w=R/'work/rap4-dialogue-final/01';(w/'stems').mkdir(parents=True,exist_ok=False);shutil.copytree(w1/'refs',w/'refs')
def merge(p,q,d):
 a,s=sf.read(p,always_2d=True);b,t=sf.read(q,always_2d=True);assert s==t==sr and a.shape[1]==b.shape[1]
 ramp=np.linspace(0,1,fade)[:,None];y=np.concatenate([a[:cut-fade],a[cut-fade:cut]*(1-ramp)+b[:fade]*ramp,b[fade:]])
 assert np.isfinite(y).all();sf.write(d,y,sr,subtype='FLOAT');return len(y)/sr
secs=merge(base/'full.wav',tail/'full.wav',out/'full.wav')
for name in ['vocals.wav','instrumental.wav']:assert merge(w1/'stems'/name,w2/'stems'/name,w/'stems'/name)==secs
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g1=json.loads((base/'manifest.json').read_text(encoding='utf-8'));g2=json.loads((tail/'manifest.json').read_text(encoding='utf-8'));b=json.loads((R/'music/rap4-dialogue/brief.json').read_text(encoding='utf-8'))
assembly={'base_run':base.name,'outro_run':tail.name,'cut_seconds':cut/sr,'crossfade_seconds':fade/sr,'outro_offset_seconds':offset,'source_audio_sha256':[sha(base/'full.wav'),sha(tail/'full.wav')],'reason':'Original generation omitted last four outro lines; replace entire outro with a new local MiniMax performance.'}
g={**g1,'status':'assembled_local','audio':[{'file':'full.wav','duration':secs,'sample_rate':sr,'channels':2,'sha256':sha(out/'full.wav')}],'delivery':[],'whole_run_seconds':g1['whole_run_seconds']+g2['whole_run_seconds'],'generation_timing_scope':'Sum of two MiniMax generations; assembly excluded','assembly':assembly};g.pop('command',None);(out/'manifest.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
sep={'seconds':sum(json.loads((z/'separation.json').read_text())['seconds'] for z in [w1,w2]),'assembly':assembly};(w/'separation.json').write_text(json.dumps(sep,indent=2),encoding='utf-8')
intervals=[(57.62,61.25),(76.34,79.70),(107.14,112.18),(178.76,183.42),(204.50,209.60),(offset+9.66,offset+15.80)]
t={'base':out.name,'source_lyrics_path':b['source_lyrics_path'],'source_snapshot_path':b['source_lyrics_path'],'source_lyrics_sha256':b['original_lyrics_sha256'],'main_voice':'ADV','intro_voice':'ADV','intro_seconds':0,'greeting_in_music_generation':True,'dry':True,'expected_ezhi_occurrences':6,'ezhi_regions':[{'start':a,'end':z,'lyrics':lines} for (a,z),lines in zip(intervals,b['ezhi_lines'])],'crossfade_seconds':.06,'assembly':assembly,'boundary_evidence':'Local Whisper word timestamps from full base and separate outro. Endpoints with no gap use shared word boundary; fades are inside guest region. ASR is approximate.'}
(R/'music/rap4-dialogue/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8');print('Assembled seconds',secs,'Ezhi seconds',sum(z-a for a,z in intervals))
