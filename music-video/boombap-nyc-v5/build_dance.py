import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;S=bpy.context.scene
with bpy.data.libraries.load(str(W/'street-v5.blend'),link=False) as (src,dst):dst.objects=['Performer_1','Bip01.001','m023_hipoly_81_bones']
for o in dst.objects:
 if o and not o.name in S.objects:S.collection.objects.link(o)
root=next(o for o in dst.objects if o.name.startswith('Performer'));rig=next(o for o in dst.objects if o.type=='ARMATURE');mesh=next(o for o in dst.objects if o.type=='MESH')
root.animation_data_clear();rig.animation_data_clear();root.location=(0,0,.01);root.rotation_euler=(0,0,0)
if mesh.data.shape_keys:
 mesh.data.shape_keys.animation_data_clear()
 for k in mesh.data.shape_keys.key_blocks:k.value=0
# The roof becomes a dance floor; remove the suspended decorative cube.
for o in list(S.objects):
 if o.name.startswith(('Floating wire cube','Cube edge')):bpy.data.objects.remove(o,do_unlink=True)
raw=np.load(W/'dance.npy');N=250
# AIST Y-up centimetres to Blender Z-up metres; preserve captured changes.
a=raw[:,:,[0,2,1]]*.01;a[:,:,1]*=-1
height=np.median(a[:,0,2]-np.minimum(a[:,15,2],a[:,16,2]));a*=1.48/height
center=(a[0,11]+a[0,12])/2;a[:,:,:2]-=center[:2]
anklefloor=np.percentile(a[:,[15,16],2],5);a[:,:,2]-=anklefloor
pairs=[('L UpperArm',5,7),('L Forearm',7,9),('R UpperArm',6,8),('R Forearm',8,10),('L Thigh',11,13),('L Calf',13,15),('R Thigh',12,14),('R Calf',14,16)]
def aim(name,d):
 b=rig.pose.bones['Bip01 '+name];target=rig.matrix_world.inverted().to_3x3()@Vector(d)
 child={'Spine':'Spine1','Spine1':'Spine2','L UpperArm':'L Forearm','R UpperArm':'R Forearm','L Forearm':'L Hand','R Forearm':'R Hand','L Thigh':'L Calf','R Thigh':'R Calf','L Calf':'L Foot','R Calf':'R Foot','L Foot':'L Toe0','R Foot':'R Toe0'}[name]
 current=b.matrix.to_quaternion();direction=rig.pose.bones['Bip01 '+child].head-b.head;turn=direction.rotation_difference(target);desired=turn@current
 rest=b.bone.matrix_local.to_quaternion()
 if b.parent:
  desired=b.parent.matrix.to_quaternion().inverted()@desired
  rest=b.parent.bone.matrix_local.to_quaternion().inverted()@rest
 b.rotation_quaternion=rest.inverted()@desired
 b.location=(0,0,0);bpy.context.view_layer.update()
for f in range(1,N+1):
 pos=(f-1)/(N-1)*(len(a)-1);i=min(len(a)-2,int(pos));p=a[i]*(1-(pos-i))+a[i+1]*(pos-i)
 for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0)
 root.location=(float((p[11,0]+p[12,0])*.5),float((p[11,1]+p[12,1])*.5),0);bpy.context.view_layer.update()
 torso=(p[5]+p[6]-p[11]-p[12])*.5
 for name in ['Spine','Spine1']:aim(name,torso)
 for name,i,j in pairs:aim(name,p[j]-p[i])
 # Feet follow the captured dancer's facing direction while lying on the floor.
 side=Vector(p[5]-p[6]);front=Vector((side.y,-side.x,0));front.normalize()
 for sideName in ['L','R']:aim(sideName+' Foot',front)
 bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();low=min((ev.matrix_world@v.co).z for v in me.vertices);ev.to_mesh_clear();root.location.z=.005-low;bpy.context.view_layer.update()
 for b in rig.pose.bones:b.keyframe_insert('rotation_quaternion',frame=f)
 root.keyframe_insert('location',frame=f)
 if f%50==0:print('DANCE',f,flush=True)
for ob in [root,rig]:
 for fc in ob.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
S.frame_start=1;S.frame_end=N;S.frame_set(100);S.camera.data.dof.use_dof=False
S['motion_source']='AIST++ gMH_sBM_cAll_d24_mMH2_ch10, CC BY 4.0, 3D keypoint directional retarget'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/'sets/dance.blend'),compress=True)
