import bpy,numpy as np,json
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;r=bpy.data.objects['Bip01.001'];raw=np.load(W/'dance.npy');a=raw[:,:,[0,2,1]]*.01;a[:,:,1]*=-1
pairs=[('L UpperArm','L Forearm',5,7),('L Forearm','L Hand',7,9),('R UpperArm','R Forearm',6,8),('R Forearm','R Hand',8,10),('L Thigh','L Calf',11,13),('L Calf','L Foot',13,15),('R Thigh','R Calf',12,14),('R Calf','R Foot',14,16)];angles=[]
for f in [1,30,60,100,140,180,220,250]:
 S.frame_set(f);bpy.context.view_layer.update();v=(f-1)/249*(len(a)-1);i=min(len(a)-2,int(v));p=a[i]*(1-(v-i))+a[i+1]*(v-i)
 for bn,ch,i,j in pairs:
  d=np.array(r.matrix_world.to_3x3()@(r.pose.bones['Bip01 '+ch].head-r.pose.bones['Bip01 '+bn].head));target=p[j]-p[i];cos=np.dot(d,target)/np.linalg.norm(d)/np.linalg.norm(target);angles.append(float(np.degrees(np.arccos(np.clip(cos,-1,1)))))
out={'max_joint_direction_error_degrees':max(angles),'median_degrees':float(np.median(angles))};(W/'dance-validation.json').write_text(json.dumps(out,indent=2));print(out)
