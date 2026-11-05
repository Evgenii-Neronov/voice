from pathlib import Path
import art,skia,numpy as np,math,json,time
W=Path(__file__).resolve().parent;beats=np.array(json.loads((W/'beats.json').read_text())['beat_seconds']);vi=np.load(W/'visemes.npy');start=time.time()
for kind in ['ezhi']:
 d=W/'sprites'/kind;d.mkdir(parents=True,exist_ok=True)
 for f in [0,*range(2988,3279)]:
  t=f/12;phase=2*math.pi*np.interp(t,beats,np.arange(len(beats)));v=vi[min(len(vi)-1,int(t*60))];speaking=(kind=='lead' and t<256.28) or (kind=='ezhi' and t>=256.28)
  surface=skia.Surface(640,800);c=surface.getCanvas();c.clear(0)
  walk=max(0,1-t/5) if kind=='lead' else (max(0,1-(t-251.8)/4.1) if kind=='ezhi' else 0)
  if f>=3012:art.person(c,kind,320,745,1,t,phase,int(np.argmax(v)),float(v.max()),speaking,walk)
  surface.makeImageSnapshot().save(str(d/f'{f+1:05d}.png'),skia.kPNG)
  if f%240==0:(W/'sprite-status.json').write_text(json.dumps({'kind':kind,'frame':f,'seconds':time.time()-start}))
print('SPRITES COMPLETE',time.time()-start,flush=True)
