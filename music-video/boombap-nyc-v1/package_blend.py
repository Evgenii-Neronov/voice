import bpy,sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-1440p/project';O.mkdir(parents=True,exist_ok=True)
src=(W/'render.py').read_text(encoding='utf-8-sig');exec(compile(src.split('args=sys.argv')[0],str(W/'render.py'),'exec'))
S.frame_end=6079
# Native editable camera track: include both sides of every cut.
frames=set(range(1,6080,12))|{6079}
for cut in CUTS[1:-1]:
 f=math.ceil(cut*24)+1;frames.update([f-1,f])
for fr in sorted(frames):
 S.frame_set(fr);update(fr);cam.keyframe_insert('location',frame=fr);cam.keyframe_insert('rotation_euler',frame=fr);cam.data.keyframe_insert('lens',frame=fr)
# Audio-driven mouth shapes are editable independently of the body motion.
for fr in range(1,6080,3):
 S.frame_set(fr);update(fr)
 for _,_,mesh in chars:
  for k in mesh.data.shape_keys.key_blocks:
   if k.name!='Basis':k.keyframe_insert('value',frame=fr)
for dat in [cam,cam.data]+[m.data.shape_keys for _,_,m in chars]:
 if dat.animation_data and dat.animation_data.action:
  for fc in dat.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
seq=S.sequence_editor_create();collection=seq.strips if hasattr(seq,'strips') else seq.sequences
sound=collection.new_sound('Original boombap track',str(W.parents[1]/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3'),channel=1,frame_start=1)
if hasattr(sound.sound,'pack'):sound.sound.pack()
S.render.use_sequencer=False;S.frame_set(230);update(230)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'NYC-boombap.blend'),compress=True)
print('PACKED EDITABLE PROJECT',flush=True)
