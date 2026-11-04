import bpy,json
from pathlib import Path
W=Path(__file__).resolve().parent
S=bpy.context.scene
static=[o for o in S.objects if o.type=='MESH' and not any(m.type=='ARMATURE' for m in o.modifiers)]
verts=[];faces=[];ids=[];mats=[]
for o in static:
 off=len(verts);verts.extend(tuple(o.matrix_world @ v.co) for v in o.data.vertices)
 local=[]
 for mat in o.data.materials:
  if mat not in mats:mats.append(mat)
  local.append(mats.index(mat))
 for p in o.data.polygons:faces.append(tuple(off+i for i in p.vertices));ids.append(local[p.material_index] if local else 0)
me=bpy.data.meshes.new('Residential block geometry');me.from_pydata(verts,[],faces)
for m in mats:me.materials.append(m)
for p,i in zip(me.polygons,ids):p.material_index=i
obj=bpy.data.objects.new('Unmarked residential block',me);S.collection.objects.link(obj)
for o in static:bpy.data.objects.remove(o,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
# Remove unresolved unused importer images; all visible materials use explicit downloaded textures.
for im in list(bpy.data.images):
 if im.source=='FILE' and not Path(bpy.path.abspath(im.filepath)).exists() and not im.packed_file:
  if not im.users:bpy.data.images.remove(im)
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=96;S.eevee.taa_render_samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(W/'nyc-optimized.blend'),compress=True)
print('OPTIMIZED',len(static),'static objects to one;',len(verts),'vertices',flush=True)
