import bpy,json,math
from pathlib import Path
from mathutils import Quaternion,Vector
W=Path(__file__).resolve().parent;S=bpy.context.scene;r=bpy.data.objects['Bip01'];root=bpy.data.objects['Performer_0'];cam=S.camera
names=[b.name for b in r.pose.bones if any(x in b.name for x in ['Pelvis','Thigh','Calf','Foot','Toe']) or b.name in ['Bip01','Bip01 Spine']]
samples=[]
for f in range(1,176):
 S.frame_set(f);samples.append({'bones':{n:(tuple(r.pose.bones[n].rotation_quaternion),tuple(r.pose.bones[n].location)) for n in names},'root':tuple(root.location),'camloc':tuple(cam.location),'camrot':tuple(cam.rotation_euler)})
bpy.ops.wm.open_mainfile(filepath=str(W.parent/'nyc-boombap-v5/street-v5.blend'));S=bpy.context.scene;r=bpy.data.objects['Bip01'];root=bpy.data.objects['Performer_0'];cam=S.camera;mesh=bpy.data.objects['m022_hipoly_81_bones'];finalroot=root.location.copy();report=[]
for f,data in enumerate(samples,1):
 S.frame_set(f);t=(f-1)/24;u=max(0,min(1,(t-5.7)/1.5));u=u*u*(3-2*u)
 for name in names:
  b=r.pose.bones[name];b.rotation_quaternion=Quaternion(data['bones'][name][0]).slerp(Quaternion((1,0,0,0)),u);b.location=Vector(data['bones'][name][1])*(1-u);b.keyframe_insert('rotation_quaternion',frame=f);b.keyframe_insert('location',frame=f)
 root.location=(-.1,-2-2.2*min(1,t/6.8),0);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bottom=min((ev.matrix_world@v.co).z for v in me.vertices);ev.to_mesh_clear();root.location.z=-.034-bottom;root.keyframe_insert('location',frame=f)
 if t<6.8:
  cam.location=data['camloc'];cam.rotation_euler=data['camrot'];cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
 if f in [1,49,97,145,175]:report.append({'frame':f,'lead':list(root.location),'camera':list(cam.location),'sole_z':-.034})
# Hold the fixed stance and avoid extrapolated movement after the entrance.
root.location=finalroot;root.keyframe_insert('location',frame=176);root.keyframe_insert('location',frame=6079)
for name in names:
 b=r.pose.bones[name];b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0)
 for f in [176,6079]:b.keyframe_insert('rotation_quaternion',frame=f);b.keyframe_insert('location',frame=f)
for ob in [r,root,cam]:
 for fc in ob.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
S.frame_set(1);S['revision']='v6: restored lead walk and dolly opening, v5 planted stance thereafter';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/'street-v6.blend'),compress=True)
(W/'opening-motion.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
