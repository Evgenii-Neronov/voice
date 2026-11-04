"""Work around audio.cpp 0.9.3 Seed-VC's 30-second Whisper content window."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import resample_poly,correlate,correlation_lags
ROOT=Path(__file__).resolve().parents[1]; work=ROOT/'work/adv-ezhi'
p=argparse.ArgumentParser(); p.add_argument('--route',choices=['v1_svc','v1_whisper_bigvgan_vc'],default='v1_whisper_bigvgan_vc'); a=p.parse_args()
folder=work/('chunks-'+a.route+'-02'); folder.mkdir(exist_ok=False)
source,sr=sf.read(work/'stems/vocals.wav',always_2d=True); source=source.mean(axis=1); n=len(source)
assert sr==44100
timeline=json.loads((ROOT/'music/adv-ezhi.timeline.json').read_text(encoding='utf-8'))
records=[]; requests=[]; context=round(.4*sr); core=12*sr
for speaker in ['adv','ezhi']:
 intervals=[(s,min(n,s+core)) for s in range(0,n,core)] if speaker=='adv' else [(int(t['start']*sr),int(t['end']*sr)) for t in timeline['ezhi_regions']]
 for i,(start,end) in enumerate(intervals):
  left=max(0,start-context); right=min(n,end+context); identity=f'{speaker}-{i:03}'
  path=folder/(identity+'-source.wav'); sf.write(path,source[left:right],sr)
  assert (right-left)/sr<30, 'Refusing native content truncation'
  reference=work/('refs/adv.wav' if speaker=='adv' else 'refs/ezhi-conversion.wav')
  requests.append({'id':identity,'audio':str(path),'voice_ref':str(reference),'route':a.route,'seed':20261104,'num_inference_steps':40,'options':{'duration_scale':1.0,'inference_guidance_scale':0.7,'f0_condition':a.route=='v1_svc','auto_f0_adjust':False,'semitone_shift':0}})
  records.append({'id':identity,'speaker':speaker,'left':left,'right':right,'core_start':start,'core_end':end})
(folder/'requests.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2),encoding='utf-8')
exe=ROOT/'vendor/audio-runtime/audiocpp_cli.exe'
command=[str(exe),'--task','svc' if a.route=='v1_svc' else 'vc','--family','seed_vc','--model',str(ROOT/'models/voice-production/SeedVC-MLX-GGUF/seed-vc-mlx-q8_0.gguf'),'--backend','cuda','--threads','8','--request-sequence',str(folder/'requests.json'),'--out-dir',str(folder),'--out-format','pcm16','--metrics','--load-progress','0']
start=time.perf_counter()
with (folder/'runtime.log').open('w',encoding='utf-8') as log: subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
timing=time.perf_counter()-start
def envelope(x):
 hop=441; x=np.pad(x,(0,(-len(x))%hop)); return np.sqrt(np.mean(x.reshape(-1,hop)**2,axis=1)+1e-12)
for speaker in ['adv','ezhi']:
 accum=np.zeros(n); weights=np.zeros(n)
 for r in [row for row in records if row['speaker']==speaker]:
  file=folder/(r['id']+'.wav'); y,rate=sf.read(file,always_2d=True); y=y.mean(axis=1)
  if rate!=sr:
   from math import gcd
   g=gcd(sr,rate); y=resample_poly(y,sr//g,rate//g)
  expected=r['right']-r['left']; assert abs(len(y)-expected)<sr*.1
  y=np.pad(y,(0,max(0,expected-len(y))))[:expected]
  orig=source[r['left']:r['right']]; e1=envelope(y); e2=envelope(orig)
  corr=correlate(e1-e1.mean(),e2-e2.mean(),method='fft'); lags=correlation_lags(len(e1),len(e2)); valid=np.abs(lags)<=10
  lag=int(lags[valid][np.argmax(corr[valid])])*441
  if lag>0: y=np.pad(y[lag:],(0,lag))
  elif lag<0: y=np.pad(y[:lag],(-lag,0))
  w=np.ones(expected); fade=min(2*context,expected//2)
  if r['left']>0: w[:fade]=np.linspace(0,1,fade)
  if r['right']<n: w[-fade:]=np.linspace(1,0,fade)
  accum[r['left']:r['right']]+=y*w; weights[r['left']:r['right']]+=w
  r['alignment_shift_samples']=lag; r['output_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
 if speaker=='adv': assert np.min(weights)>0,'Uncovered source samples'
 merged=np.divide(accum,weights,out=np.zeros(n),where=weights>1e-8)
 sf.write(work/(speaker+'-vocal-chunked.wav'),merged,sr,subtype='FLOAT')
result={'route':a.route,'chunk_core_seconds':12,'context_seconds':.4,'seed':20261104,'steps':40,'whole_run_seconds':timing,'records':records,'command':command,'runtime_sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
(work/'chunked-conversion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'converted','seconds':timing,'chunks':len(records)}))
