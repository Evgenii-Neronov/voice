import bpy
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;S.eevee.shadow_pool_size='1024';S.eevee.taa_render_samples=16
if hasattr(S.render,'compositor_device'):S.render.compositor_device='GPU'
S.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(W/'evening-isometric.blend'))
for f in [481,3181]:
 S.frame_set(f);S.render.filepath=str(W/f'final-concept-{f}.png');bpy.ops.render.render(write_still=True)
