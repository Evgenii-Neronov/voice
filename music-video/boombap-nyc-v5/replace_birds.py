import bpy,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;S=bpy.context.scene
for o in list(S.objects):
 if o.name.startswith(('Clay whistle','Whistle mouthpiece','Whistle opening')):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.stl_import(filepath=str(W/'bird_whistle.stl'));o=bpy.context.object;o.name='Ceramic bird - NEMO_MK2 CC BY-SA'
# Original printable model is Z-up in millimeters.
mi=Vector([min(v.co[i] for v in o.data.vertices) for i in range(3)]);ma=Vector([max(v.co[i] for v in o.data.vertices) for i in range(3)])
for v in o.data.vertices:v.co-=Vector(((mi.x+ma.x)/2,(mi.y+ma.y)/2,mi.z))
o.scale=(.004,.004,.004)
clay=bpy.data.materials.get('Terracotta clay');o.data.materials.clear();o.data.materials.append(clay)
for p in o.data.polygons:p.use_smooth=True
mod=o.modifiers.new('Reduce hidden print triangulation','DECIMATE');mod.ratio=.23
bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
for i in range(10):
 b=o if i==0 else o.copy()
 if i:b.data=o.data;S.collection.objects.link(b)
 b.location=(-1.55+(i%5)*.72,-.38+(i//5)*.76,1.031);b.rotation_euler.z=math.radians(-25+(i%3)*24)
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(W/'sets/lab.blend'),compress=True)
print('Bird source bounds',list(mi),list(ma),'triangles',len(o.data.polygons))
