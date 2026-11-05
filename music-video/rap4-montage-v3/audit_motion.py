from pathlib import Path
import art,skia,numpy as np,json
from scipy.ndimage import label
W=Path(__file__).resolve().parent;checks=[];motion=np.load(W/'performance-motion.npz');metrics={}
for kind in ['lead','hood','blue']:
 a=motion[kind];metrics[kind]={}
 for name,cols in [('left_wrist',(5,6)),('right_wrist',(9,10))]:
  v=np.linalg.norm(np.diff(a[:,cols],axis=0),axis=1);metrics[kind][name]={'max_px_per_frame':float(v.max()),'p95_px_per_frame':float(np.percentile(v,95))};assert v.max()<6.01
 for t in np.linspace(0,273,100):
  s=skia.Surface(640,800);s.getCanvas().clear(0);art.person(s.getCanvas(),kind,320,745,1,float(t),0,0,0,False,0)
  alpha=np.asarray(s.makeImageSnapshot())[:,:,3];lab,_=label(alpha>128);head,body=lab[230,320],lab[390,320];checks.append(bool(head and head==body))
 assert all(checks),'Disconnected neck'
 edits=json.loads((W/f'motion-edit-{kind}.json').read_text());ids=[x['source_index'] for x in edits];assert len(ids)==len(set(ids))
 metrics[kind]['source_excerpts']=len(ids);metrics[kind]['repeated_source_excerpt']=False
r={'metrics':metrics,'neck_samples':len(checks),'disconnected_neck_samples':checks.count(False),'method':'Full-track numeric speed/source-repeat checks and 300 sampled alpha-connectivity checks from face to torso. Not an aesthetic guarantee.'}
(W/'motion-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
