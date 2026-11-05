from pathlib import Path
import numpy as np,json,zipfile,math
from scipy.ndimage import gaussian_filter1d
from motion_data import Z,read
W=Path(__file__).resolve().parent;rng=np.random.default_rng(1903);candidates=[]
with zipfile.ZipFile(Z) as z:
 for name in sorted(z.namelist()):
  if not Path(name).name.startswith(('gMH','gLH')) or not name.endswith('.pkl'):continue
  raw=read(z,name)['keypoints3d_optim']
  if not np.isfinite(raw).all() or len(raw)<420:continue
  q=gaussian_filter1d(raw,3,axis=0);centre=(q[:,5]+q[:,6])/2;width=np.linalg.norm(q[:,5]-q[:,6],axis=1);basis=q[:,5]-q[:,6];basis[:,1]=0;basis/=np.maximum(np.linalg.norm(basis,axis=1,keepdims=True),1e-5)
  rel=q-centre[:,None];x=np.sum(rel*basis[:,None],axis=-1)/width[:,None];y=-(q[:,:,1]-centre[:,1,None])/width[:,None];xy=np.stack([x,y],axis=-1)
  speed=np.linalg.norm(np.diff(xy[:,[7,8,9,10]],axis=0),axis=-1)*60
  best=None
  for a in range(60,len(q)-360,120):
   b=a+360;w=xy[a:b];score=float(np.percentile(speed[a:b-1],85)+2*np.maximum(0,-w[:,[9,10],1]).mean()+np.std(q[a:b,11:13,1])/np.median(width[a:b]))
   if np.percentile(w[:,[9,10],1],5)<-.6:continue
   if best is None or score<best[0]:best=(score,a,b)
  if best is not None:candidates.append((best[0],name,best[1],best[2],xy[best[1]:best[2]].copy()))
candidates.sort(key=lambda c:c[0]);unique=[];seen=set()
for c in candidates:
 p=Path(c[1]).stem.split('_');key=(p[0],p[3],p[-1])
 if key not in seen:unique.append(c);seen.add(key)
assert len(unique)>=20,len(unique)
np.savez_compressed(W/'source-motion-excerpts.npz',**{f'c{i}':c[4] for i,c in enumerate(unique[:64])})
manifest=[{'index':i,'source':c[1],'start_seconds':c[2]/60,'end_seconds':c[3]/60,'activity_score':c[0]} for i,c in enumerate(unique[:64])]
(W/'motion-sources.json').write_text(json.dumps(manifest,indent=2))
duration=273.25;fps=24;n=math.ceil(duration*fps);time=np.arange(n)/fps;lyrics=json.loads((W/'alignment.json').read_text(encoding='utf8'));out={};edits=[]
for ki,kind in enumerate(['lead','hood','blue']):
 choices=rng.permutation(len(manifest));cur=0.;segments=[];skeleton=np.zeros((n,17,2));prev=None;used=[]
 while cur<duration:
  ci=int(choices[len(used)%len(choices)]);src=unique[ci][4];rate=float(rng.uniform(.54,.76));length=len(src)/60/rate;end=min(duration,cur+length);ids=np.flatnonzero((time>=cur)&(time<end));u=np.minimum(len(src)-1,(time[ids]-cur)*rate*60);res=np.stack([np.interp(u,np.arange(len(src)),src[:,j,k]) for j in range(17) for k in range(2)],axis=-1).reshape(-1,17,2)
  if prev is not None:
   blend=np.clip((time[ids]-cur)/.75,0,1);blend=blend*blend*(3-2*blend);res=prev[None]*(1-blend[:,None,None])+res*blend[:,None,None]
  skeleton[ids]=res;prev=res[-1];used.append(ci);segments.append({'start':cur,'end':end,'source_index':ci,'playback_rate':rate});cur=end
 skeleton=gaussian_filter1d(skeleton,2,axis=0)
 channels=np.zeros((n,15));channels[:,0]=np.clip((skeleton[:,11,0]+skeleton[:,12,0])*2,-2,2);channels[:,1]=np.clip((skeleton[:,0,0])*12,-5,5);channels[:,2]=0
 # Sparse phrase gestures with preparation, stroke, hold and recovery. No beat oscillator.
 envelope=np.zeros((n,2))+.08
 for li,line in enumerate(lyrics):
  if line['start']>256.28:continue
  if kind!='lead' or rng.random()<.28:continue
  arm=int(rng.integers(2));start=line['start']+float(rng.uniform(.2,.65));length=min(line['end']-start,float(rng.uniform(1.8,3.8)));u=(time-start)/max(length,.5);e=np.zeros(n);up=(u>=0)&(u<.3);hold=(u>=.3)&(u<.65);down=(u>=.65)&(u<1);e[up]=np.sin(u[up]/.3*math.pi/2)**2;e[hold]=1;e[down]=np.cos((u[down]-.65)/.35*math.pi/2)**2;envelope[:,arm]=np.maximum(envelope[:,arm],e*.68);edits.append({'actor':kind,'line':li,'start':start,'duration':length,'arm':arm})
 for arm,side in enumerate([-1,1]):
  sh,el,wr=(6,8,10) if side<0 else (5,7,9);a=skeleton[:,el]-skeleton[:,sh];b=skeleton[:,wr]-skeleton[:,el]
  a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),.2);b/=np.maximum(np.linalg.norm(b,axis=-1,keepdims=True),.2)
  anchor=np.array([side*68,-433]);elbow=anchor+a*108;wrist=elbow+b*108;restel=np.array([side*85,-330]);restwr=np.array([side*88,-220]);e=envelope[:,arm,None]
  elbow=restel*(1-e)+elbow*e;wrist=restwr*(1-e)+wrist*e
  elbow[:,0]=np.clip(elbow[:,0],-170,170);wrist[:,0]=np.clip(wrist[:,0],-190,190);wrist[:,1]=np.clip(wrist[:,1],-421,-205)
  channels[:,3+arm*4:7+arm*4]=np.concatenate([elbow,wrist],axis=-1);channels[:,11+arm]=(envelope[:,arm]>.36)
 if kind!='lead':channels[:,0]*=.65;channels[:,1]*=.7
 channels[:,:11]=gaussian_filter1d(channels[:,:11],1.5,axis=0)
 # Limit each elbow/wrist's drawing-space speed to avoid short phrase snaps.
 for pair in [(3,5),(5,7),(7,9),(9,11)]:
  a,b=pair
  for frame in range(1,n):
   delta=channels[frame,a:b]-channels[frame-1,a:b];speed=np.linalg.norm(delta)
   if speed>6:channels[frame,a:b]=channels[frame-1,a:b]+delta*6/speed
 channels[:,:11]=gaussian_filter1d(channels[:,:11],3,axis=0);out[kind]=channels.astype(np.float32)
 (W/f'motion-edit-{kind}.json').write_text(json.dumps(segments,indent=2))
np.savez_compressed(W/'performance-motion.npz',**out);(W/'gesture-events.json').write_text(json.dumps(edits,indent=2))
report={'source_clips':len(manifest),'hiphop_sequences_screened':len(candidates),'fps':fps,'duration':duration,'looping':False,'source':'AIST++ optimized3D keypoints, Middle/LA hiphop','adaptation':'Low-activity six-second excerpts;54-76% playback,0.75s transitions, amplitude restraint, sparse phrase envelopes and rests. Body/head/arm directions retargeted to drawing, not a full dance reproduction.','gesture_events':len(edits)}
(W/'motion-report.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
