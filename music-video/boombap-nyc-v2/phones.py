from pathlib import Path
import json,time,numpy as np,soundfile as sf,torch
from scipy.signal import resample_poly
from scipy.ndimage import gaussian_filter1d
from transformers import Wav2Vec2ForCTC
W=Path(__file__).resolve().parent;M=Path('I:/VOICE/voice/models/lipsync/wav2vec2-espeak')
vocab={v:k for k,v in json.loads((M/'vocab.json').read_text(encoding='utf8')).items()}
model=Wav2Vec2ForCTC.from_pretrained(str(M),local_files_only=True).to('cuda').eval()
x,sr=sf.read('I:/VOICE/voice/work/minimax-trio/boombap-01/stems/vocals.wav');x=x.mean(axis=1) if x.ndim>1 else x
x=resample_poly(x,16000,sr).astype('float32');duration=len(x)/16000;events=[]
for a in range(0,len(x),16000*16):
 start=max(0,a-16000);end=min(len(x),a+16000*17);xx=x[start:end];xx=(xx-xx.mean())/np.sqrt(xx.var()+1e-7)
 with torch.inference_mode():p=model(torch.tensor(xx[None],device='cuda')).logits[0].float().softmax(-1).cpu().numpy()
 ids=p.argmax(-1);dt=(end-start)/16000/len(ids)
 for k,id in enumerate(ids):
  t=start/16000+k*dt
  if a/16000<=t<min(duration,a/16000+16) and id>3:events.append({'time':round(t,4),'phone':vocab[int(id)],'confidence':round(float(p[k,id]),3)})
 print('phones',round(end/16000,1),flush=True)
# CTC emits sparse peaks. Interpolate nearest peaks within a bounded coarticulation window.
def vis(p):
 if p.startswith(('p','b','m')):return 1
 if p.startswith(('f','v','ɸ','β')):return 2
 if p.startswith(('θ','ð')):return 3
 if p.startswith(('tʃ','dʒ','ʃ','ʒ','ʂ','ʐ','ɕ','tɕ','dʑ','ʑ')):return 6
 if p.startswith(('t','d')):return 4
 if p.startswith(('k','ɡ','g','x','h','q','χ')):return 5
 if p.startswith(('s','z')):return 7
 if p.startswith(('n','l','ŋ','ɲ','ɫ')):return 8
 if p.startswith(('r','ɹ','ɾ','ʁ')):return 9
 if p.startswith(('u','ʊ','w','y','ju','ɯ','ʉ')):return 14
 if p.startswith(('o','ɔ','ɒ','ɵ','ø','œ')):return 13
 if p.startswith(('i','ɪ','ɨ','j')):return 12
 if p.startswith(('e','ɛ')):return 11
 return 10
fps=60;weights=np.zeros((int(duration*fps)+1,15),np.float32);ts=np.array([e['time'] for e in events])
for i in range(len(weights)):
 t=i/fps;k=np.searchsorted(ts,t);k=min(len(ts)-1,k)
 if k and abs(ts[k-1]-t)<abs(ts[k]-t):k-=1
 distance=abs(ts[k]-t)
 if distance<.105:
  amp=np.sqrt(np.mean(x[max(0,int(t*16000)-320):min(len(x),int(t*16000)+320)]**2)+1e-8)
  weights[i,vis(events[k]['phone'])]=min(1,amp/.055)*max(0,1-distance/.14)
weights=gaussian_filter1d(weights,.9,axis=0)
np.save(W/'visemes.npy',weights);(W/'phonemes.json').write_text(json.dumps({'model':str(M),'method':'audio CTC phone peaks, nearest bounded interpolation, 60Hz coarticulation','events':events},ensure_ascii=False),encoding='utf8')
print('DONE',len(events),weights.shape)
