import bpy,json,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;S=bpy.context.scene;man=json.loads((W/'scene-manifest.json').read_text());rows=[]
for t in [0,2,6.8,11.7,34,39.5,45.5,48,54,64,66,70,82,100,150,200,250]:
 S.frame_set(round(t*24)+1);row={'time':t,'camera':list(S.camera.location),'actors':[]}
 for c in man['characters']:
  r=bpy.data.objects[c['root']];rig=bpy.data.objects[c['rig']];mesh=bpy.data.objects[c['mesh']]
  row['actors'].append({'root':list(r.location),'yaw':r.rotation_euler.z,'head_quaternion':list(rig.pose.bones['Bip01 Head'].rotation_quaternion),'left_hand':list(rig.matrix_world@rig.pose.bones['Bip01 L Hand'].head),'right_hand':list(rig.matrix_world@rig.pose.bones['Bip01 R Hand'].head),'hidden':mesh.hide_render})
 rows.append(row)
lead_travel=rows[2]['actors'][0]['root'][1]-rows[0]['actors'][0]['root'][1]
assert abs(lead_travel+2.2)<.01
for c in man['characters']:
 for name in [c['root'],c['rig']]:
  a=bpy.data.objects[name].animation_data;assert a and a.action and a.action_slot,name
assert rows[7]['actors'][3]['root'][0]==rows[9]['actors'][3]['root'][0]
assert rows[0]['actors'][3]['hidden'] and not rows[7]['actors'][3]['hidden'] and rows[12]['actors'][3]['hidden']
assert set(o.data.body for o in S.objects if o.type=='FONT')=={'NY','ADV'}
report={'lead_opening_travel_m':lead_travel,'nominal_passerby_height_m':S.get('passerby_rest_body_height_m'),'all_actor_action_slots_bound':True,'passerby_stops_then_leaves':True,'only_authorized_scene_lettering':True,'samples':rows}
(W/'scene-validation.json').write_text(json.dumps(report,indent=2));print('SCENE VALIDATION PASSED',flush=True)
