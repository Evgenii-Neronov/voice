import bpy,numpy as np,json
from pathlib import Path
W=Path(__file__).resolve().parent;r=bpy.data.objects['Bip01'];ac=r.animation_data.action;fixed=0
for path in {fc.data_path for fc in ac.fcurves if fc.data_path.endswith('rotation_quaternion')}:
 fs=[ac.fcurves.find(path,index=j) for j in range(4)]
 q=np.array([[k.co.y for k in fc.keyframe_points] for fc in fs]).T
 for i in range(1,len(q)):
  if q[i]@q[i-1]<0:q[i]*=-1;fixed+=1
 for j,fc in enumerate(fs):
  for k,v in zip(fc.keyframe_points,q[:,j]):k.co.y=float(v)
  fc.update()
bpy.ops.wm.save_as_mainfile(filepath=str(W/'street-v6.blend'),compress=True);print('SIGN FIXES',fixed)
