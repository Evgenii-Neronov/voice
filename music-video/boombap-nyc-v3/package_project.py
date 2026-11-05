import bpy,json
from pathlib import Path
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-v3-1440p/project';O.mkdir(parents=True,exist_ok=True);S=bpy.context.scene
seq=S.sequence_editor_create();collection=seq.strips if hasattr(seq,'strips') else seq.sequences
sound=collection.new_sound('Original boombap track',str(W.parents[1]/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3'),channel=1,frame_start=1)
if hasattr(sound.sound,'pack'):sound.sound.pack()
S.render.use_sequencer=False;S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=24;S.eevee.use_raytracing=True;S.render.resolution_percentage=100;S.frame_set(1300)
S.render.filepath='//renders/NYC-v3-'
for name in ['Streetlight','Streetlight.002']:
 if name in bpy.data.objects:bpy.data.objects[name].data.use_shadow=False
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'NYC-boombap-v3.blend'),compress=True)
report={'file':str(O/'NYC-boombap-v3.blend'),'resolution':[S.render.resolution_x,S.render.resolution_y],'fps':S.render.fps,'frames':[S.frame_start,S.frame_end],'renderer':S.render.engine,'samples':S.eevee.taa_render_samples,'passerby_present':any(o.name=='Passerby 183cm' for o in S.objects),'text_objects':[{'name':o.name,'body':o.data.body} for o in S.objects if o.type=='FONT'],'packed_images':sum(bool(im.packed_file) for im in bpy.data.images),'sound_packed':bool(sound.sound.packed_file),'missing_files':[]}
for im in bpy.data.images:
 if im.source=='FILE' and im.users and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists():report['missing_files'].append(im.filepath)
(O.parent/'project-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
