import bpy
from pathlib import Path
W=Path(__file__).resolve().parent;changed=[]
for mat in bpy.data.objects['ezhi'].data.materials:
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image and n.image.source=='SEQUENCE':n.image.filepath=str(W/'sprites/ezhi/00001.png');changed.append(n.image.name)
assert changed, 'missing Ezhi sequence'
