import bpy,math,json,sys,time
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
W=Path(__file__).resolve().parent;S=bpy.context.scene;DUR=253.283265
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.use_persistent_data=True
S.cycles.denoiser='OPTIX';S.cycles.denoising_use_gpu=True
man=json.loads((W/'scene-manifest.json').read_text());meta=json.loads((W/'motion-meta.json').read_text());data=np.load(W/'motion-local.npz');vis=np.load(W/'visemes.npy')
chars=[tuple(bpy.data.objects[c[k]] for k in ['root','rig','mesh']) for c in man['characters']]
corrections=[];indices=[]
for root,rig,mesh in chars:
 c={};ix={}
 for b in rig.data.bones:
  q=b.matrix_local.to_quaternion()
  if b.parent:q=b.parent.matrix_local.to_quaternion().inverted()@q
  c[b.name]=q.inverted()
 for clip in meta:ix[clip]={n:j for j,n in enumerate(meta[clip]['bones'])}
 corrections.append(c);indices.append(ix)
def sample(clip,t):
 a=data[clip];f=(t*30)%(len(a)-1);i=int(f);u=f-i
 x=a[i];y=a[i+1].copy();y[np.sum(x*y,axis=1)<0]*=-1;q=x*(1-u)+y*u;q/=np.linalg.norm(q,axis=1)[:,None]
 p=data[clip+'_pelvis'][i]*(1-u)+data[clip+'_pelvis'][i+1]*u
 return q,p
def mix(a,b,u):
 qa,pa=a;qb,pb=b;qb=qb.copy();qb[np.sum(qa*qb,axis=1)<0]*=-1;q=qa*(1-u)+qb*u;q/=np.linalg.norm(q,axis=1)[:,None];return q,pa*(1-u)+pb*u
foot_offsets=[0,0,0,0]
BAKING=False
cuts=[0,6.8,17.34,26,35.28,43.54,49,58,67,79.96,91.7,101.3,112.7,123.28,131.76,141.93,146.48,156.8,166.66,175.02,182.72,190.16,202.48,207.88,217.72,230.08,241.74,DUR]
types=[0,1,2,3,5,5,6,6,5,4,2,1,3,2,4,0,1,2,3,4,1,2,3,1,4,2,7]
def update(frame):
 t=(frame-1)/24;beat=2*math.pi*92/60*t
 for ci,(root,rig,mesh) in enumerate(chars):
  if ci==0:
   clip='rap';pose=sample(clip,t*.83+2.4)
   if t<7.2:
    walk=sample('walk',t*.6+.15);blend=max(0,min(1,(t-6.1)/1.1));pose=mix(walk,pose,blend)
   root.location=(-.1,-2.0-2.2*min(1,t/6.8),foot_offsets[ci]);root.rotation_euler.z=.025*math.sin(t*.31)
  elif ci in [1,2]:
   clip='listen' if ci==1 else 'idle';pose=sample(clip,t*(.78 if ci==1 else .69)+(5.4 if ci==1 else 2.1))
   root.location=((-1.65 if ci==1 else 1.55),(-2.25 if ci==1 else -2.1),foot_offsets[ci]);root.rotation_euler.z=(.42 if ci==1 else -.42)
  else:
   walktime=max(0,t-34);clip='stroll';walk=sample('stroll',walktime*.75);listen=sample('listen',max(0,t-48)*.75+3.8)
   arrival=max(0,min(1,(t-45.5)/2.5));arrival=arrival*arrival*(3-2*arrival);departure=max(0,min(1,(t-64)/2));departure=departure*departure*(3-2*departure)
   weight=arrival*(1-departure);pose=mix(walk,listen,weight)
   if t<=45:x=-8+(t-34)*.65
   elif t<48:u=t-45;x=-.85+.65*(u-u*u/6)
   elif t<=64:x=.125
   elif t<67:u=t-64;x=.125+.65*u*u/6
   else:x=1.1+(t-67)*.65
   root.location=(x,.55,foot_offsets[ci]);root.rotation_euler.z=(math.pi/2)*(1-weight)-.18*weight
  qs,pel=pose;idx=indices[ci][clip]
  # The source and target rest poses differ. Retarget local anatomical rotations,
  # not raw animation channels; this is the correction for the previous A-pose arms.
  for b in rig.pose.bones:
   if b.name in idx:
    b.rotation_mode='QUATERNION';b.rotation_quaternion=corrections[ci][b.name]@Quaternion(qs[idx[b.name]])
    b.location=(0,0,0)
  pb=rig.pose.bones['Bip01 Pelvis'];offset=Vector(pel)-rig.data.bones['Bip01 Pelvis'].head_local;offset.x=max(-7,min(7,offset.x));offset.y=max(-7,min(7,offset.y));pb.location=rig.data.bones['Bip01 Pelvis'].matrix_local.to_quaternion().inverted()@offset
  # Quiet independent beat listening, absolute additive poses (never accumulating).
  if ci in [1,2]:
   head=rig.pose.bones['Bip01 Head'];head.rotation_quaternion=head.rotation_quaternion@Quaternion((0,0,1),.045*math.sin(beat*(.5 if ci==1 else 1)+ci*1.8))
  # Small bent-knee accents during rap, with opposing shin rotation and pelvis drop.
  if ci==0 and t>7.2:
   dip=.5-.5*math.cos(beat*.25);dip=dip**5*.13
   for side in ['L','R']:
    for name,angle in [('Thigh',dip),('Calf',-2*dip),('Foot',dip)]:
     b=rig.pose.bones['Bip01 '+side+' '+name];b.rotation_quaternion=b.rotation_quaternion@Quaternion((0,0,1),angle)
   root.location.z-=dip*.12
  if mesh.data.shape_keys:
   for sk in mesh.data.shape_keys.key_blocks:
    if sk.name!='Basis':sk.value=0
   for name in ['AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight']:
    if name in mesh.data.shape_keys.key_blocks:mesh.data.shape_keys.key_blocks[name].value=max(0,1-abs((t+ci*.83)%4.27-.12)/.09)
   if ci==0:
    values=vis[min(len(vis)-1,max(0,int(t*60)))];names=['Sil','PP','FF','TH','DD','KK','CH','SS','nn','RR','aa','E','I','O','U']
    for k,n in enumerate(names):
     name=f'AA_VI_{k:02d}_{n}'
     if name in mesh.data.shape_keys.key_blocks:mesh.data.shape_keys.key_blocks[name].value=float(values[k])*.85
 if not BAKING:
  bpy.context.view_layer.update()
  for a in man['accessories']:
   r=chars[a['actor']][1];bpy.data.objects[a['object']].matrix_world=r.matrix_world@r.pose.bones[a['bone']].matrix@Matrix(a['offset'])
 # A real backwards tracking opening, then varied performance coverage.
 i=min(len(types)-1,max(0,np.searchsorted(cuts,t,side='right')-1));u=max(0,min(1,(t-cuts[i])/(cuts[i+1]-cuts[i])));u=u*u*(3-2*u);kind=types[i];y=chars[0][0].location.y
 shots={0:((-2.7,-11.4,2.1),(-1.6,-10.6,1.85),(0,-2.9,1.05),38),1:((-.4,-7.55,1.58),(.3,-7.3,1.62),(0,-4.15,1.28),48),2:((-2.6,-7.5,1.6),(-1.9,-7.4,1.7),(-.1,-4,1.3),48),3:((2.5,-7.5,1.4),(1.8,-7.3,1.6),(0,-4,1.32),48),4:((.1,-6.8,1.65),(-.25,-6.65,1.66),(-.1,-4.2,1.50),60),5:((-3.6,-11.6,2.3),(-2.8,-10.8,2.1),(-.2,-1.6,1.15),35),6:((2.8,-9.5,2),(-1.5,-10.2,2.15),(.1,-1.2,1.15),37),7:((-.5,-9.7,1.8),(1.7,-14.8,3.2),(0,-2,1.25),38)}
 p0,p1,target,lens=shots[kind];pos=Vector(p0).lerp(Vector(p1),u)
 if t<6.8:pos=Vector((-.55+.35*u,y-4.4,1.68));target=Vector((-.1,y,1.25));lens=42
 pos+=Vector((.003*math.sin(t*2.1),.002*math.sin(t*1.8),.003*math.sin(t*2.7)))
 cam=S.camera;cam.location=pos;cam.rotation_euler=(Vector(target)-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.focus_object=None;cam.data.dof.focus_distance=(Vector((-.1,y,1.5))-pos).length;cam.data.dof.aperture_fstop=5.6 if kind==4 else 8
def calibrate():
 update(1);deps=bpy.context.evaluated_depsgraph_get()
 for i,(root,rig,mesh) in enumerate(chars):
  ev=mesh.evaluated_get(deps);low=min((ev.matrix_world@Vector(v)).z for v in ev.bound_box);foot_offsets[i]=(-.025 if i<3 else .135)-low
 print('GROUND OFFSETS',foot_offsets,flush=True)
calibrate()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['stills']
mode=args[0]
if mode in ['bake','bakepass']:
 BAKING=True
 # Parenting uses the same explicit bone-space bind offset as preview; this removes
 # the slow frame handler and stores an editable, self-contained animation.
 for a in man['accessories'] if mode=='bake' else []:
  r=chars[a['actor']][1];o=bpy.data.objects[a['object']];o.parent=r;o.parent_type='BONE';o.parent_bone=a['bone'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Translation((0,-r.data.bones[a['bone']].length,0))@Matrix(a['offset'])
 channels={}
 def put(owner,path,val):
  key=(owner,path)
  if key not in channels:channels[key]=[]
  channels[key].append(tuple(val) if hasattr(val,'__len__') else (val,))
 frames=sorted(set(range(1,6080,2))|{6079}|{max(1,min(6079,int(t*24)+k)) for t in cuts for k in [0,1,2]}) if mode=='bake' else list(range(817,2162,2))
 for f in frames:
  update(f)
  for root,rig,mesh in chars if mode=='bake' else chars[3:]:
   put(root,'location',root.location);put(root,'rotation_euler',root.rotation_euler)
   for b in rig.pose.bones:
    put(rig,b.path_from_id('rotation_quaternion'),b.rotation_quaternion)
    if b.name=='Bip01 Pelvis':put(rig,b.path_from_id('location'),b.location)
   for k in mesh.data.shape_keys.key_blocks:
    if k.name!='Basis':put(mesh.data.shape_keys,k.path_from_id('value'),k.value)
  if mode=='bake':
   put(S.camera,'location',S.camera.location);put(S.camera,'rotation_euler',S.camera.rotation_euler);put(S.camera.data,'lens',S.camera.data.lens);put(S.camera.data,'dof.focus_distance',S.camera.data.dof.focus_distance);put(S.camera.data,'dof.aperture_fstop',S.camera.data.dof.aperture_fstop)
  if f%601==0:print('BAKING',f,flush=True)
 actions={};ft=np.array(frames,np.float32)
 for (owner,path),values in channels.items():
  if owner not in actions:
   owner.animation_data_clear();owner.animation_data_create();ac=bpy.data.actions.new(owner.name+' performance');owner.animation_data.action=ac;actions[owner]=ac
  arr=np.array(values,np.float32)
  for j in range(arr.shape[1]):
   fc=actions[owner].fcurves.new(path,index=j);fc.keyframe_points.add(len(frames));fc.keyframe_points.foreach_set('co',np.column_stack((ft,arr[:,j])).ravel())
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'
   fc.update()
 for owner,ac in actions.items():owner.animation_data.action_slot=ac.slots[0]
 S.frame_start=1;S.frame_end=6079;S.frame_set(1);S.render.resolution_percentage=100
 bpy.ops.wm.save_as_mainfile(filepath=str(W/'film-v2.blend'),compress=True);print('BAKED',len(frames),len(channels),flush=True)
elif mode in ['stills','compare']:
 S.render.resolution_percentage=50
 if mode=='compare':
  S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=48;S.eevee.use_raytracing=True
 for frame in [65,260,1105,1300,1650] if mode=='stills' else [260,1300]:
  S.frame_set(frame);update(frame);S.render.filepath=str(W/f'preview-{frame:04d}.jpg');bpy.ops.render.render(write_still=True)
elif mode=='render':
 start,end=int(args[1]),int(args[2]);dest=args[3];S.frame_start=start;S.frame_end=end;S.render.resolution_percentage=int(args[4]) if len(args)>4 else 100
 S.render.image_settings.file_format='FFMPEG';S.render.ffmpeg.format='MPEG4';S.render.ffmpeg.codec='H264';S.render.ffmpeg.constant_rate_factor='PERC_LOSSLESS';S.render.ffmpeg.ffmpeg_preset='REALTIME';S.render.ffmpeg.audio_codec='NONE';S.render.use_sequencer=False;S.render.filepath=dest
 def handler(scene,*rest):update(scene.frame_current)
 bpy.app.handlers.frame_change_post.clear();bpy.app.handlers.frame_change_post.append(handler);bpy.ops.render.render(animation=True)
