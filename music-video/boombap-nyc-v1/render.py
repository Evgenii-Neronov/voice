import bpy,math,json,sys,time
import numpy as np
from pathlib import Path
from mathutils import Vector,Euler,Quaternion
W=Path(__file__).resolve().parent;S=bpy.context.scene
manifest=json.loads((W/'scene-manifest.json').read_text());env=np.load(W/'voice-envelope.npy');cam=S.camera;fps=24;DUR=253.283265
chars=[(bpy.data.objects[x['root']],bpy.data.objects[x['rig']],bpy.data.objects[x['mesh']]) for x in manifest['characters']]
# The lead uses the more expressive captured clip; support actors keep quieter motions.
leadstrip=chars[0][1].animation_data.nla_tracks[0].strips[0]
expressive=chars[1][1].animation_data.nla_tracks[0].strips[0].action
leadstrip.action=expressive;leadstrip.action_frame_start=expressive.frame_range[0];leadstrip.action_frame_end=expressive.frame_range[1];leadstrip.scale=.8;leadstrip.repeat=12
# Only authentic 3D set geometry and performers are visible; subtitles added at final mux.
# Move between wide, waist-up, oblique, and intimate performance shots. No graphics.
CUTS=[0,7.5,17.34,26,35.28,43.54,54.2,59.68,69.64,79.96,91.7,101.3,112.7,123.28,131.76,136.22,141.93,146.48,156.8,166.66,175.02,182.72,190.16,202.48,207.88,217.72,230.08,241.74,253.283265]
TYPES=[0,1,2,3,1,4,2,1,3,4,2,1,3,2,4,0,1,2,3,4,1,2,3,1,4,2,0,5]
SHOTS={
0:((-1.0,-10,2.0),(.0,-7.2,1.7),(.5,.65,1.15),35),
1:((-.45,-4.1,1.42),(.35,-3.8,1.53),(0,.0,1.25),52),
2:((-2.8,-4.3,1.5),(-1.9,-4.1,1.65),(.05,.15,1.35),50),
3:((2.7,-4.3,1.25),(1.8,-3.8,1.48),(.15,.2,1.25),48),
4:((.0,-3.35,1.63),(-.45,-3.1,1.68),(0,-.08,1.52),55),
5:((.5,-6.5,1.8),(1.6,-11.8,2.9),(.55,.6,1.25),38)}
subtokens=[w for l in json.loads((W/'alignment.json').read_text(encoding='utf8')) for w in l['words']]
def update(frame):
 t=(frame-1)/fps;i=min(len(TYPES)-1,max(0,np.searchsorted(CUTS,t,side='right')-1));u=(t-CUTS[i])/(CUTS[i+1]-CUTS[i]);u=max(0,min(1,u));u=u*u*(3-2*u)
 p0,p1,tar,lens=SHOTS[TYPES[i]];pos=Vector(p0).lerp(Vector(p1),u)
 # Bounded millimetric handheld movement, independent of audio peaks.
 pos+=Vector((.009*math.sin(t*2.1),.004*math.sin(t*1.8),.007*math.sin(t*2.7)))
 if i==0:
  pos=Vector((-5.5,-15,7)).lerp(Vector((-2,-8,2.2)),u);tar=Vector((.3,2.7,3.8)).lerp(Vector((.3,.3,1.25)),u)
 cam.location=pos;cam.rotation_euler=(Vector(tar)-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.aperture_fstop=5.6 if TYPES[i]==4 else 8
 amp=float(env[min(len(env)-1,int(t*48))]);phase=t*2*math.pi*(92/60)
 for ci,(root,rig,mesh) in enumerate(chars):
  sk=mesh.data.shape_keys
  if sk:
   for name in ['AA_VI_10_aa','AA_VI_11_E','AA_VI_13_O','AK_25_JawOpen','AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight']:
    if name in sk.key_blocks:sk.key_blocks[name].value=0
   blink=max(0,1-abs((t+ci*.57)%4.1-.12)/.09)
   for name in ['AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight']:
    if name in sk.key_blocks:sk.key_blocks[name].value=blink
   if ci==0:
    for name,val in [('AA_VI_10_aa',amp*.48),('AA_VI_11_E',amp*.22*(.5+.5*math.sin(t*16))),('AA_VI_13_O',amp*.18*(.5+.5*math.sin(t*11))),('AK_25_JawOpen',amp*.08)]:
     if name in sk.key_blocks:sk.key_blocks[name].value=val
 S.render.filepath=str(W/'frames'/f'{frame:06d}.jpg')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'test'
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=96;S.render.resolution_percentage=100;S.eevee.taa_render_samples=12
(W/'frames').mkdir(exist_ok=True)
if mode=='test': frames=[1,180,450,700,1450,1850,3400,4950,5980]
elif mode=='motion':frames=range(180,276)
elif mode=='pose':frames=[229,252,700]
else:frames=range(int(args[1]),int(args[2])+1)
t0=time.time()
for n,fr in enumerate(frames):
 S.frame_set(fr);update(fr)
 if mode in ['test','motion','pose']:S.render.filepath=str(W/f'{mode}-{fr:06d}.jpg')
 elif Path(S.render.filepath).exists():continue
 bpy.ops.render.render(write_still=True)
 if n%12==0:print(f'PROGRESS {fr} {n+1} frames {time.time()-t0:.2f}s',flush=True)
print('COMPLETE',mode,time.time()-t0,flush=True)

