import bpy,json,numpy as np
from pathlib import Path
W=Path(__file__).resolve().parent; OLD=W.parent/'nyc-boombap'
bpy.ops.wm.read_factory_settings(use_empty=True)
clips={'rap':OLD/'assets/m_gestic_talk_excited_01.max.fbx','calm':OLD/'assets/m_gestic_talk_cool.max.fbx','listen':W/'assets/m_gestic_listen_relaxed_01.max.fbx','idle':W/'assets/m_idle_neutral_02.max.fbx','walk':W/'assets/m_walk_cool_01.max.fbx','stroll':W/'assets/m_walk_neutral_01.max.fbx'}
result={};meta={}
for key,path in clips.items():
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(path));added=set(bpy.data.objects)-old;r=next(o for o in added if o.type=='ARMATURE');a=r.animation_data.action
 names=[b.name for b in r.pose.bones];start,end=map(int,a.frame_range);rot=[];pel=[]
 for f in range(start,end+1):
  bpy.context.scene.frame_set(f);qs=[]
  for n in names:
   b=r.pose.bones[n];q=b.matrix.to_quaternion()
   if b.parent:q=b.parent.matrix.to_quaternion().inverted()@q
   qs.append(tuple(q))
  rot.append(qs);pel.append(tuple(r.pose.bones['Bip01 Pelvis'].head))
 result[key]=np.array(rot,dtype=np.float32);result[key+'_pelvis']=np.array(pel,dtype=np.float32)
 meta[key]={'bones':names,'frames':len(rot),'fps':30,'source':str(path)}
 for o in added:bpy.data.objects.remove(o,do_unlink=True)
 print(key,len(rot),flush=True)
np.savez_compressed(W/'motion-local.npz',**result);(W/'motion-meta.json').write_text(json.dumps(meta,indent=2))
