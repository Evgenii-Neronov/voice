import bpy,sys,json
from pathlib import Path
W=Path(__file__).resolve().parent;kind=sys.argv[sys.argv.index('--')+1];changed=[]
for o in bpy.context.scene.objects:
 if o.get('grow'):
  for slot in o.material_slots:
   if slot.material and slot.material.name.startswith('Ochre paint'):
    m=slot.material.copy();m.name='Red growing wire';m.diffuse_color=(.65,.018,.012,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.65,.018,.012,1);slot.material=m;changed.append(o.name)
assert len(changed)==3,changed
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(W/'sets'/f'{kind}.blend'),compress=True)
(W/f'{kind}-red-wires.json').write_text(json.dumps({'objects':changed,'red_linear_rgb':[.65,.018,.012]},indent=2))
