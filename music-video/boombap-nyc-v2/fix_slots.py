import bpy
from pathlib import Path
W=Path(__file__).resolve().parent
for owner in list(bpy.data.objects)+list(bpy.data.cameras)+list(bpy.data.shape_keys):
 a=owner.animation_data
 if a and a.action and a.action.slots:
  a.action_slot=a.action.slots[0];print('BOUND',owner.name,flush=True)
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'film-v2.blend'),compress=True)
