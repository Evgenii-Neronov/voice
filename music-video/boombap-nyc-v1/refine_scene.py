import bpy,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;S=bpy.context.scene;man=json.loads((W/'scene-manifest.json').read_text());S.view_settings.exposure=-1.25
# Three performers read clearly; discard the fourth avatar with unusable hair cards.
last=man['characters'].pop()
for k in ['mesh','rig','root']:bpy.data.objects.remove(bpy.data.objects[last[k]],do_unlink=True)
for ci,c in enumerate(man['characters']):
 root=bpy.data.objects[c['root']];mesh=bpy.data.objects[c['mesh']];deps=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(deps)
 low=min((ev.matrix_world@Vector(v)).z for v in ev.bound_box);root.location.z += .135-low
 print('FOOT HEIGHT',ci,low,'offset',root.location.z,flush=True)
 attr=mesh.data.color_attributes.new(name='Fabric regions',type='FLOAT_COLOR',domain='POINT');vg={g.index:g.name for g in mesh.vertex_groups}
 for v in mesh.data.vertices:
  jacket=skin=shoe=0
  for g in v.groups:
   n=vg[g.group]
   if any(q in n for q in ['Spine','Neck','Head','Clavicle','UpperArm','Forearm']):jacket+=g.weight
   if any(q in n for q in ['Hand','Finger']):skin+=g.weight
   if any(q in n for q in ['Foot','Toe']):shoe+=g.weight
  attr.data[v.index].color=(min(1,jacket),min(1,skin),min(1,shoe),1)
 mat=mesh.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF');tex=next(x for x in n if x.type=='TEX_IMAGE' and x.image and 'color' in x.image.name)
 at=n.new('ShaderNodeVertexColor');at.layer_name='Fabric regions';sep=n.new('ShaderNodeSeparateColor');l.new(at.outputs['Color'],sep.inputs[0]);jmix=n.new('ShaderNodeMixRGB');l.new(sep.outputs[0],jmix.inputs[0]);jmix.inputs[1].default_value=(.025,.03,.045,1);jmix.inputs[2].default_value=[(.95,.50,.008,1),(.055,.06,.07,1),(.045,.08,.12,1)][ci]
 smix=n.new('ShaderNodeMixRGB');l.new(sep.outputs[1],smix.inputs[0]);l.new(jmix.outputs[0],smix.inputs[1]);l.new(tex.outputs[0],smix.inputs[2]);fmix=n.new('ShaderNodeMixRGB');l.new(sep.outputs[2],fmix.inputs[0]);l.new(smix.outputs[0],fmix.inputs[1]);fmix.inputs[2].default_value=(.07,.075,.08,1);l.new(fmix.outputs[0],p.inputs['Base Color'])
 for poly in mesh.data.polygons:
  if poly.material_index!=1:poly.material_index=0
(W/'scene-manifest.json').write_text(json.dumps(man,indent=2))
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'nyc-final-scene.blend'),compress=True)
