"""Mix local converted vocals into the existing MiniMax arrangement."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import correlate,correlation_lags,resample_poly
ROOT=Path(__file__).resolve().parents[1]; work=ROOT/'work/editable/minimax-01'; out=ROOT/'results/productions/editable-minimax-01'
out.mkdir(parents=True,exist_ok=False)
timeline=json.loads((ROOT/'music/editable/minimax.timeline.json').read_text(encoding='utf-8'))
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
mix=song
sf.write(work/'mix-float.wav',mix,SR,subtype='FLOAT')
subprocess.run(['ffmpeg','-v','error','-i',str(work/'mix-float.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'-c:a','pcm_s24le',str(out/'full.wav')],check=True)
for name,opts in [('full.mp3',[]),('preview.mp3',['-t','35'])]: subprocess.run(['ffmpeg','-v','error','-i',str(out/'full.wav'),*opts,'-b:a','256k',str(out/name)],check=True)
x,s=sf.read(out/'full.wav'); assert np.isfinite(x).all() and np.abs(x).max()<1
m={'local_inference':True,'dry':True,'added_echo':False,'added_reverb':False,'greeting_engine':'MiniMax, part of source lyrics','greeting_voice':'ADV','timeline':timeline,'duration':len(x)/s,'peak':float(np.abs(x).max()),'lyrics_sha256':sha(ROOT/'Lyrics/lyrics.txt'),'audio':[{'file':name,'sha256':sha(out/name)} for name in ['full.wav','full.mp3','preview.mp3']],'conversion':json.loads((work/'chunked-conversion.json').read_text(encoding='utf-8'))}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8'); print('Dry MiniMax ready',m['duration'])
