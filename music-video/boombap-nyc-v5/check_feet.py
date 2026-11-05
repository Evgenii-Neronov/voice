import bpy,json,numpy as np
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;report=[]
for ri,name in enumerate(['Bip01','Bip01.001','Bip01.002']):
 rig=bpy.data.objects[name];samples=[]
 for f in [1,30,100,180,600,1200,2400,3600,4800,6079]:
  S.frame_set(f);bpy.context.view_layer.update();samples.append([list(rig.matrix_world@rig.pose.bones['Bip01 '+side+' Foot'].head) for side in ['L','R']])
 a=np.array(samples);report.append({'rig':name,'foot_joint_drift_metres':float(np.max(np.linalg.norm(a-a[0],axis=2)))})
(W/'foot-drift.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
