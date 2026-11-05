from pathlib import Path
import art,skia,numpy as np,json,time
W=Path(__file__).resolve().parent;vi=np.load(W/'visemes.npy');frames=list(range(1,97))+list(range(2989,3280));start=time.time()
for k in ['lead','hood','blue']:
 d=W/'sprites'/k;d.mkdir(parents=True,exist_ok=True)
 for f in frames:
  t=(f-1)/12;v=vi[min(len(vi)-1,int(t*60))];s=skia.Surface(640,800);s.getCanvas().clear(0);art.person(s.getCanvas(),k,320,745,1,t,0,int(v.argmax()),float(v.max()),k=='lead' and t<256.28,0);s.makeImageSnapshot().save(str(d/f'{f:05d}.png'),skia.kPNG)
 print(k,'complete',time.time()-start,flush=True)
