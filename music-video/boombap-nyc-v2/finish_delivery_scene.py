import bpy,json
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;man=json.loads((W/'scene-manifest.json').read_text())
if not S.get('passerby_height_calibrated'):
 measure=json.loads((W/'passerby-height.json').read_text());r=bpy.data.objects[man['characters'][3]['root']];r.scale*=measure['scale_multiplier'];S['passerby_height_calibrated']=True;S['passerby_rest_body_height_m']=1.83
font=bpy.data.fonts.load(str(W/'assets/RubikWetPaint-Regular.ttf'))
for o in S.objects:
 if o.name.startswith(('ADV painted','ADV ochre')):o.data.font=font;o.data.shear=.1
passobjects=[bpy.data.objects[man['characters'][3]['mesh']],bpy.data.objects['Open knee length trenchcoat']]+[bpy.data.objects[a['object']] for a in man['accessories'] if a['actor']==3]
for o in passobjects:
 for f,v in [(1,True),(792,True),(793,False),(1968,False),(1969,True),(6079,True)]:o.hide_render=v;o.keyframe_insert('hide_render',frame=f)
for c in man['characters'][1:]:
 m=bpy.data.objects[c['mesh']]
 for k in list(m.data.shape_keys.key_blocks):
  if k.name not in ['Basis','AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight']:m.shape_key_remove(k)
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'film-v2.blend'),compress=True)
