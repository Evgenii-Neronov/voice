import bpy,json,numpy as np
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;S.frame_set(180)
man=json.loads((W/'scene-manifest.json').read_text())
report=[]
for ci,c in enumerate(man['characters'][:3]):
 r=bpy.data.objects[c['rig']];root=bpy.data.objects[c['root']];ac=r.animation_data.action
 root.animation_data_clear();root.rotation_euler=(0,0,[0,.42,-.42][ci]);root.location=[(-.1,-4.2,0),(-1.65,-2.25,0),(1.55,-2.1,0)][ci]
 for b in r.pose.bones:
  low=any(s in b.name for s in ['Pelvis','Thigh','Calf','Foot','Toe']) or b.name in ['Bip01','Bip01 Spine']
  if low:
   for fc in list(ac.fcurves):
    if fc.data_path.startswith(b.path_from_id()+'.'):ac.fcurves.remove(fc)
   b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0)
  elif any(s in b.name for s in ['Head','Neck']):
   path=b.path_from_id('rotation_quaternion');fs=[ac.fcurves.find(path,index=j) for j in range(4)]
   if not all(fs):continue
   q=np.array([[k.co.y for k in fc.keyframe_points] for fc in fs]).T
   q/=np.linalg.norm(q,axis=1)[:,None]
   mean=q.mean(axis=0);mean/=np.linalg.norm(mean)
   q=mean+(q-mean)*(.18 if 'Head' in b.name else .30);q/=np.linalg.norm(q,axis=1)[:,None]
   for j,fc in enumerate(fs):
    for k,v in zip(fc.keyframe_points,q[:,j]):k.co.y=float(v)
    fc.update()
 S.frame_set(180);bpy.context.view_layer.update();ob=bpy.data.objects[c['mesh']];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();zs=[(ev.matrix_world@v.co).z for v in mesh.vertices];bottom=min(zs);ev.to_mesh_clear();root.location.z-=bottom+.034
 report.append({'actor':ci,'sole_before':bottom,'root_z':root.location.z})
# Preserve framing of the introductory dolly with the now planted performer.
cam=S.camera
if cam.animation_data:
 fc=cam.animation_data.action.fcurves.find('location',index=1)
 if fc:
  for k in fc.keyframe_points:
   t=(k.co.x-1)/24
   if t<6.8:k.co.y-=2.2*(1-t/6.8)
  fc.update()
S.frame_set(180);S.render.resolution_percentage=50;S.eevee.taa_render_samples=16
bpy.ops.wm.save_as_mainfile(filepath=str(W/'street-v5.blend'),compress=True)

(W/'grounding.json').write_text(json.dumps(report,indent=2));print(report)
