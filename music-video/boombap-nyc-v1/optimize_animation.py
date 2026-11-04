import bpy,numpy as np
from pathlib import Path
W=Path(__file__).resolve().parent
kept={'Basis','AA_VI_10_aa','AA_VI_11_E','AA_VI_13_O','AK_25_JawOpen','AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight'}
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.data.shape_keys:
  for k in list(o.data.shape_keys.key_blocks):
   if k.name not in kept:o.shape_key_remove(k)
before=after=0
for a in bpy.data.actions:
 for f in a.fcurves:
  n=len(f.keyframe_points);before+=n
  if n<3:after+=n;continue
  arr=np.empty(n*2,np.float32);f.keyframe_points.foreach_get('co',arr);arr=arr.reshape(-1,2)
  ix=[0,n-1] if np.ptp(arr[:,1])<1e-6 else sorted(set(range(0,n,3))|{n-1});co=arr[ix].flatten()
  f.keyframe_points.clear();f.keyframe_points.add(len(ix));f.keyframe_points.foreach_set('co',co)
  for k in f.keyframe_points:k.interpolation='LINEAR'
  f.update();after+=len(ix)
print('KEYS',before,after,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'nyc-render.blend'),compress=True)
