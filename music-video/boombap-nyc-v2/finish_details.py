import bpy
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;S=bpy.context.scene;S.frame_set(1)
if not S.get('v2_detail_fix'):
 m=bpy.data.objects['m022_hipoly_81_bones'];attr=m.data.color_attributes['Fabric regions']
 for v in m.data.vertices:
  color=list(attr.data[v.index].color);color[0]=((m.matrix_world@v.co).z-.86)/.02;attr.data[v.index].color=color
 ny=bpy.data.objects['Cap NY embroidery'];rig=bpy.data.objects['Bip01'];delta=(rig.matrix_world@rig.data.bones['Bip01 Head'].matrix_local).inverted().to_3x3()@Vector((0,0,.031));ma=ny.matrix_basis.copy();ma.translation+=delta;ny.matrix_basis=ma
 for o in S.objects:
  if o.name.startswith(('Side white plaster patch','ADV painted','ADV ochre','Graffiti paint drip')):o.location.x+=9.4
  if o.name.startswith(('Bicycle','Alloy rim','Wheel axle','Wheel spoke','Seat post','Handlebar','Black hand grip','Chainring','Pedal crank','Kickstand')):o.location.x+=2.1
 for ma in bpy.data.materials:
  if ma.use_nodes and ('head' in ma.name.lower()):
   p=ma.node_tree.nodes.get('Principled BSDF')
   if p and 'Subsurface Scale' in p.inputs:p.inputs['Subsurface Scale'].default_value=.002
 S['v2_detail_fix']=True
bpy.ops.wm.save_as_mainfile(filepath=str(W/'film-v2.blend'),compress=True)
