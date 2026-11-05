import bpy
from pathlib import Path
W=Path(__file__).resolve().parent;P=W.parents[1]/'outputs/rap4-cartoon-v2-1440p/project';S=bpy.context.scene
for im in bpy.data.images:
 if im.source=='SEQUENCE':
  original=Path(bpy.path.abspath(im.filepath));im.filepath='//sprites/'+original.parent.name+'/'+original.name
for font in bpy.data.fonts:
 if font.filepath and font.filepath!='<builtin>':font.pack()
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=12;S.cycles.use_denoising=True;S.cycles.denoiser='OPTIX';S.cycles.denoising_use_gpu=True;S.cycles.max_bounces=4;S.cycles.transparent_max_bounces=4;S.render.use_persistent_data=True;S.render.resolution_percentage=100;S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'evening-isometric.blend'))
