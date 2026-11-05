import bpy
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene
for name in ['ADV','Graffiti plaster']:
 ob=bpy.data.objects.get(name)
 if ob:bpy.data.objects.remove(ob,do_unlink=True)
assert not any(o.type=='FONT' and 'ADV' in o.data.body for o in S.objects)
for k in ['lead','hood','blue']:
 ob=bpy.data.objects[k]
 for ma in ob.data.materials:
  for n in ma.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and n.image.source=='SEQUENCE':n.image.filepath=str(W/'sprites'/k/'00001.png')
ob=bpy.data.objects['lead'];ob.animation_data_clear();ob.location=(0,-1,.03)
S.render.engine='CYCLES';S.cycles.samples=12;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(W/'street-no-graffiti.blend'))
