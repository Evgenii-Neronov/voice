import bpy
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
bpy.ops.object.light_add(type='AREA',location=(1,-4,3));o=bpy.context.object;o.name='Dance soft front fill';o.data.energy=180;o.data.shape='DISK';o.data.size=4;o.data.color=(.75,.83,1);o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/'sets/dance.blend'),compress=True)
