import bpy,sys,json,time
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;args=sys.argv[sys.argv.index('--')+1:];idx=int(args[0]);sh=json.loads((W/'edit-plan.json').read_text())[idx]
S.frame_start=sh['start_frame']+1;S.frame_end=sh['end_frame'];preview='preview' in args
if preview:S.frame_end=S.frame_start+199
S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=16;S.eevee.use_raytracing=True
S.render.resolution_percentage=50 if preview else 100;S.render.threads_mode='FIXED';S.render.threads=4
S.render.image_settings.file_format='FFMPEG';S.render.ffmpeg.format='MPEG4';S.render.ffmpeg.codec='H264';S.render.ffmpeg.constant_rate_factor='HIGH';S.render.ffmpeg.ffmpeg_preset='REALTIME';S.render.ffmpeg.audio_codec='NONE';S.render.use_sequencer=False
S.render.filepath=str(W/'shots'/f'{idx:02d}{"-preview" if preview else ""}.mp4');bpy.app.handlers.frame_change_post.clear();t=time.time();bpy.ops.render.render(animation=True);print('SECONDS',time.time()-t)
