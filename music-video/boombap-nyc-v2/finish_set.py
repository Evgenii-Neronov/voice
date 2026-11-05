import bpy
from pathlib import Path
W=Path(__file__).resolve().parent
for o in bpy.context.scene.objects:
 if o.name.startswith(('Side white plaster patch','ADV painted','ADV ochre','Graffiti paint drip')):
  o.location.x+=1.75;o.location.z-=1.1
  if o.type=='FONT':o.data.size*=.78
ny=bpy.data.objects.get('Cap NY embroidery')
if ny:
 ny.data.font=bpy.data.fonts.load('C:/Windows/Fonts/timesbd.ttf');ny.data.space_character=.55;ny.data.shear=0
bpy.ops.wm.save_as_mainfile(filepath=str(W/'film-v2.blend'),compress=True)
