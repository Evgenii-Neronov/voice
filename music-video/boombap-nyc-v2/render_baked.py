import bpy,sys,time
from pathlib import Path
S=bpy.context.scene;W=Path(__file__).resolve().parent
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.denoiser='OPTIX';S.cycles.denoising_use_gpu=True;S.render.use_persistent_data=True
args=sys.argv[sys.argv.index('--')+1:];S.frame_start=int(args[0]);S.frame_end=int(args[1]);S.render.filepath=str(Path(args[2]).resolve());S.render.resolution_percentage=int(args[3]) if len(args)>3 else 100
if len(args)>4 and args[4]=='eevee':
 S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=24;S.eevee.use_raytracing=True
 # Distant practical lamps do not need shadow maps for the performance area.
 # Keeping them exhausted EEVEE's atlas on wide shots (2270/2048 pages).
 for name in ['Streetlight','Streetlight.002']:
  if name in bpy.data.objects:bpy.data.objects[name].data.use_shadow=False
S.render.image_settings.file_format='FFMPEG';S.render.ffmpeg.format='MPEG4';S.render.ffmpeg.codec='H264';S.render.ffmpeg.constant_rate_factor='PERC_LOSSLESS';S.render.ffmpeg.ffmpeg_preset='REALTIME';S.render.ffmpeg.audio_codec='NONE';S.render.use_sequencer=False;S.render.threads_mode='FIXED';S.render.threads=4
bpy.app.handlers.frame_change_post.clear();t=time.time();bpy.ops.render.render(animation=True);print('RENDER_SECONDS',time.time()-t,flush=True)
