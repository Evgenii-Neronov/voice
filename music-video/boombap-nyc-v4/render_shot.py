import bpy,sys,math,json,time
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:];idx=int(args[0]);mode=args[1] if len(args)>1 else 'full';shot=json.loads((W/'edit-plan.json').read_text())[idx];kind=shot['scene'];N=shot['frames'];S=bpy.context.scene;cam=S.camera
paths={1:((4,-5,3.7),(2.6,-4,2.7),(0,0,1.3),(0,0,1.3),43),3:((-4,-6,2.4),(1.6,-5,2.8),(0,1.6,2),(1,2.5,2.5),38),6:((-7,-3,1.8),(1,-3.2,2.1),(-3,3.5,1.7),(5,3.5,1.7),35),8:((4,-5,2.8),(.8,-4.2,2.2),(.6,.8,1.2),(.6,.8,1.2),43),9:((-.5,-2,2.6),(-1.4,-1.6,2.2),(-.9,0,1.45),(-.9,0,1.45),53),11:((3,-5,3.5),(-2,-4,2.1),(0,1.5,2),(0,1.5,2),43),14:((-1.8,-2.7,2.3),(4,-3.8,2.6),(-.5,0,1.1),(2.5,1.8,1.3),48),16:((2,-3,2.2),(-4,-3,1.8),(0,3.5,1.8),(-3,3.5,1.8),38),19:((1.5,-3,2.6),(4.7,-6.2,3.6),(0,0,1.4),(0,.7,1.6),43)}
a,b,c,d,lens=paths[idx];cam.data.lens=lens
for f in range(1,N+1):
 u=(f-1)/max(1,N-1);v=u*u*(3-2*u);cam.location=Vector(a).lerp(Vector(b),v);target=Vector(c).lerp(Vector(d),v);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
for ob in S.objects:
 if ob.name.startswith('Vinyl spindle'):
  ob.rotation_euler[2]=0;ob.keyframe_insert('rotation_euler',frame=1);ob.rotation_euler[2]=N/24*math.tau*33.3/60;ob.keyframe_insert('rotation_euler',frame=N)
 if ob.name=='Train carriage':
  for f,x in [(1,0),(round(N*.22),0),(N,-15 if idx==6 else 15)]:ob.location.x=x;ob.keyframe_insert('location',frame=f)
 if ob.name=='Floating wire cube':
  for f,z,rot in [(1,1.9,0),(N,2.25,.8)]:ob.location.z=z;ob.rotation_euler=(.2+rot*.2,.35+rot*.3,rot);ob.keyframe_insert('location',frame=f);ob.keyframe_insert('rotation_euler',frame=f)
 if ob.get('grow'):
  ob.data.bevel_factor_end=.015;ob.data.keyframe_insert('bevel_factor_end',frame=1);ob.data.bevel_factor_end=1;ob.data.keyframe_insert('bevel_factor_end',frame=round(N*.8))
 if ob.animation_data:
  for fc in ob.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
S.frame_start=1;S.frame_end=N;S.render.use_sequencer=False;S.render.threads_mode='FIXED';S.render.threads=4;S.render.resolution_percentage=100
S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=16;S.eevee.use_raytracing=True
(W/'shots').mkdir(exist_ok=True)
if mode=='still':
 S.frame_set(round(N*.45));S.render.image_settings.file_format='PNG';S.render.filepath=str(W/f'concept-{idx:02d}.png');bpy.ops.render.render(write_still=True)
else:
 if mode=='preview':S.frame_end=min(N,72);S.render.resolution_percentage=50
 S.render.image_settings.file_format='FFMPEG';S.render.ffmpeg.format='MPEG4';S.render.ffmpeg.codec='H264';S.render.ffmpeg.constant_rate_factor='HIGH';S.render.ffmpeg.ffmpeg_preset='REALTIME';S.render.ffmpeg.audio_codec='NONE';S.render.filepath=str(W/'shots'/f'{idx:02d}{"-preview" if mode=="preview" else ""}.mp4')
 begin=time.time();bpy.ops.render.render(animation=True);print('RENDER_SECONDS',time.time()-begin,flush=True)
