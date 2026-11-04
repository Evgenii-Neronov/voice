"""Mix local converted vocals into the existing MiniMax arrangement."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import correlate,correlation_lags,resample_poly
ROOT=Path(__file__).resolve().parents[1]; work=ROOT/'work/adv-ezhi'; out=ROOT/'results/productions/adv-ezhi-03'
out.mkdir(parents=True,exist_ok=True)
timeline=json.loads((ROOT/'music/adv-ezhi.timeline.json').read_text(encoding='utf-8'))
SR=44100
def read(name,mono=False):
 x,sr=sf.read(work/name,always_2d=True); assert np.isfinite(x).all()
 if sr!=SR:
  from math import gcd
  divisor=gcd(sr,SR); x=resample_poly(x,SR//divisor,sr//divisor,axis=0)
 return x.mean(axis=1) if mono else x
def sha(path):
 with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
source=read('stems/vocals.wav',True); inst=read('stems/instrumental.wav'); length=len(source)
def env(x,hop=441):
 pad=np.pad(x,(0,(-len(x))%hop)); return np.sqrt(np.mean(pad.reshape(-1,hop)**2,axis=1)+1e-12)
source_env=env(source)
def align(x):
 x=np.pad(x,(0,max(0,length-len(x))))[:length]
 e=env(x); c=correlate(e-e.mean(),source_env-source_env.mean(),mode='full',method='fft')
 lags=correlation_lags(len(e),len(source_env)); valid=np.abs(lags)<=20
 lag=int(lags[valid][np.argmax(c[valid])])*441
 if lag>0: x=np.pad(x[lag:],(0,lag))
 elif lag<0: x=np.pad(x[:lag],(-lag,0))
 # Slow loudness matching retains syllable dynamics and limits gain to 18 dB.
 block=SR*2; gains=[]; positions=[]
 for start in range(0,length,block):
  a=source[start:start+block]; b=x[start:start+block]
  gain=np.sqrt(np.mean(a*a)+1e-10)/np.sqrt(np.mean(b*b)+1e-10)
  gains.append(float(np.clip(gain,0.4,8.0))); positions.append(start+len(a)/2)
 x=x*np.interp(np.arange(length),positions,gains)
 # Suppress conversion noise in original vocal pauses; no original singer is mixed back.
 gate=np.clip((20*np.log10(source_env+1e-8)+48)/14,0,1)
 x*=np.interp(np.arange(length),np.arange(len(gate))*441,gate)
 return x,{'alignment_shift_samples':lag,'gain_min':min(gains),'gain_max':max(gains)}
adv,adv_stats=align(read('adv-vocal-chunked.wav',True)); ezhi,ezhi_stats=align(read('ezhi-vocal-chunked.wav',True))
mask=np.zeros(length)
for item in timeline['ezhi_regions']:
 a=max(0,int(item['start']*SR)); b=min(length,int(item['end']*SR)); mask[a:b]=1
 fade=min(int(.06*SR),(b-a)//2)
 mask[a:a+fade]=np.linspace(0,1,fade); mask[b-fade:b]=np.linspace(1,0,fade)
vocal=adv*(1-mask)+ezhi*mask
# Gentle soft knee catches converted consonant peaks before the mastering limiter.
vocal=.65*np.tanh(vocal/.65)
song=inst+np.repeat(vocal[:,None],2,axis=1)
greeting=read('greeting.wav',True); intro_seconds=timeline['intro_seconds']; intro_len=round(intro_seconds*SR)
intro=inst[:intro_len].copy()*.32
offset=round(.65*SR); assert offset+len(greeting)<intro_len
greeting*=min(8,.11/np.sqrt(np.mean(greeting*greeting)+1e-12))
intro[offset:offset+len(greeting)]+=greeting[:,None]
fade=int(.08*SR); intro[:fade]*=np.linspace(0,1,fade)[:,None]; intro[-fade:]*=np.linspace(1,0,fade)[:,None]
song[:fade]*=np.linspace(0,1,fade)[:,None]
mix=np.concatenate([intro,song]); sf.write(work/'mix-float.wav',mix,SR,subtype='FLOAT')
# One deterministic mastering pass; keep the unmastered float render locally.
target=out/'full.wav'
subprocess.run(['ffmpeg','-y','-hide_banner','-i',str(work/'mix-float.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'-c:a','pcm_s24le',str(target)],stdout=subprocess.DEVNULL,stderr=(work/'mastering.log').open('w'),check=True)
for name,opts in [('full.mp3',['-codec:a','libmp3lame','-b:a','256k']),('preview.mp3',['-t','30','-codec:a','libmp3lame','-b:a','256k'])]:
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(target),*opts,str(out/name)],check=True)
samples,sr=sf.read(target,always_2d=True)
assert np.isfinite(samples).all() and np.max(np.abs(samples))<1 and len(samples)==len(mix)
m={'local_inference':True,'status':'rendered_not_human_rated','base_track':'results/music/minimax-full-01/full.wav','base_sha256':sha(ROOT/'results/music/minimax-full-01/full.wav'),'timeline':timeline,'adv':adv_stats,'ezhi':ezhi_stats,'greeting':json.loads((work/'greeting.json').read_text(encoding='utf-8')),'sample_rate':sr,'channels':2,'duration':len(samples)/sr,'peak':float(np.abs(samples).max()),'rms':float(np.sqrt(np.mean(samples*samples))),'audio':[]}
for name in ['full.wav','full.mp3','preview.mp3']:
 p=out/name; m['audio'].append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p)})
m['references']=[{'label':label,'sha256':sha(Path(path))} for label,path in [('ADV','I:/MyMusic/13 - New Rap/Recording (14).wav'),('Ежи','G:/Videos/2026-11-04 18-30-56.mkv')]]
m['voice_conversion']={'model':'Seed-VC GGUF Q8','route':'v1_svc','steps':40,'seed':20261104,'native_sample_rate':44100,'render_sample_rate':SR,'processing':'12-second cores, 0.4-second context each side; overlap-add; avoids 30-second content truncation'}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'duration':m['duration'],'peak':m['peak'],'adv':adv_stats,'ezhi':ezhi_stats},ensure_ascii=False))
