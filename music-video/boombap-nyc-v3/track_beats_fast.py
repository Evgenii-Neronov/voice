from pathlib import Path
import subprocess,numpy as np,json
from scipy.signal import stft,find_peaks,correlate
W=Path(__file__).resolve().parent;root=W.parents[1];sr=16000;hop=160
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(root/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3'),'-ac','1','-ar',str(sr),'-f','f32le','-'])
y=np.frombuffer(raw,dtype=np.float32);f,t,z=stft(y,fs=sr,nperseg=1024,noverlap=1024-hop)
a=np.log1p(abs(z)*100);flux=np.maximum(0,np.diff(a,axis=1));env=flux[(f>40)&(f<8000)].sum(axis=0);env=np.r_[0,env];env/=max(env.max(),1e-6)
ac=correlate(env-env.mean(),env-env.mean(),mode='full',method='fft')[len(env)-1:];lo,hi=int(60/115/.01),int(60/75/.01);lag=lo+np.argmax(ac[lo:hi]);period=lag*.01
# Dynamic programming follows local onset timing instead of accumulating fixed-grid drift.
from scipy.ndimage import gaussian_filter1d
strength=gaussian_filter1d(env,1.3);strength=strength/(np.std(strength)+1e-8)
n=len(strength);dp=np.zeros(n);back=np.full(n,-1,dtype=int);lags=np.arange(int(lag*.65),int(lag*1.45)+1);penalty=100*np.log(lags/lag)**2
for i in range(n):
 valid=lags[lags<=i]
 if len(valid):
  candidates=dp[i-valid]-penalty[:len(valid)];j=int(np.argmax(candidates))
  if candidates[j]>0:dp[i]=candidates[j];back[i]=i-valid[j]
 dp[i]+=strength[i]
end=max(range(n-lag,n),key=lambda i:dp[i]);chain=[]
while end>=0:chain.append(end);end=int(back[end])
beats=[float(t[i]) for i in chain[::-1]];period=float(np.median(np.diff(beats)))
r={'method':'Original mix spectral-flux autocorrelation (75-115 BPM), dynamic-programming local onset beat tracking; estimated beat grid','tempo_bpm':60/period,'beat_seconds':beats};(W/'beats.json').write_text(json.dumps(r,indent=2));print('BPM',r['tempo_bpm'],'first beats',beats[:15],flush=True)
