import bpy,sys,time
from pathlib import Path
S=bpy.context.scene;args=sys.argv[sys.argv.index('--')+1:];a,b=int(args[0]),int(args[1]);dest=Path(args[2]).resolve();S.frame_start=a;S.frame_end=b;S.render.resolution_percentage=int(args[3]) if len(args)>3 else 100
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=12;S.cycles.use_denoising=True;S.cycles.denoiser='OPTIX';S.cycles.denoising_use_gpu=True;S.cycles.max_bounces=4;S.cycles.transparent_max_bounces=4;S.render.use_persistent_data=True
if hasattr(S.render,'compositor_device'):S.render.compositor_device='GPU'
S.render.image_settings.file_format='FFMPEG';S.render.ffmpeg.format='MPEG4';S.render.ffmpeg.codec='H264';S.render.ffmpeg.constant_rate_factor='HIGH';S.render.ffmpeg.ffmpeg_preset='REALTIME';S.render.filepath=str(dest);S.render.use_sequencer=False;S.render.threads_mode='FIXED';S.render.threads=4
t=time.time();bpy.ops.render.render(animation=True);print('RENDER_SECONDS',time.time()-t,flush=True)
