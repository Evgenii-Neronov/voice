import bpy,json
from pathlib import Path
S=bpy.context.scene
r={'exposure':S.view_settings.exposure,'look':S.view_settings.look,'view_transform':S.view_settings.view_transform,'lights':[],'world':{}}
for o in S.objects:
 if o.type=='LIGHT':r['lights'].append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'size',0),'matrix':[list(x) for x in o.matrix_world],'use_shadow':o.data.use_shadow})
for n in S.world.node_tree.nodes:
 if n.type=='BACKGROUND':r['world']={'color':list(n.inputs[0].default_value),'strength':n.inputs[1].default_value}
Path(__file__).with_name('lighting-v1.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
