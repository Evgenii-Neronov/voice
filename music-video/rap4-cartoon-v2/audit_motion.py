from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import label
W=Path(__file__).resolve().parent;checks=[]
for kind in ['lead','hood','blue','ezhi']:
 frames=range(3014,3280,7) if kind=='ezhi' else range(1,3280,31)
 for f in frames:
  a=np.asarray(Image.open(W/'sprites'/kind/f'{f:05d}.png'))[:,:,3];lab,n=label(a>128)
  # Interior face and torso samples are linked through opaque neck artwork.
  head=lab[230,320];body=lab[390,320];checks.append({'kind':kind,'frame':f,'connected':bool(head and head==body)})
bad=[x for x in checks if not x['connected']]
(W/'neck-validation.json').write_text(json.dumps({'sampled_frames':len(checks),'disconnected_samples':bad,'method':'Connected-component alpha test from face interior to torso interior; samples across full animation. Not a whole-frame visual quality guarantee.'},indent=2));print(len(checks),'samples;',len(bad),'failures');assert not bad
