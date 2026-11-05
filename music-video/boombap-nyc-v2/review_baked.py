import bpy,sys,time
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.denoiser='OPTIX';S.cycles.denoising_use_gpu=True;S.render.use_persistent_data=True;S.render.resolution_percentage=50;S.render.image_settings.file_format='JPEG'
for frame in [65,260,950,1130,1300,1650]:
 S.frame_set(frame);S.render.filepath=str(W/f'checked-{frame:04d}.jpg');t=time.time();bpy.ops.render.render(write_still=True);print('FRAME_SECONDS',frame,time.time()-t,flush=True)
