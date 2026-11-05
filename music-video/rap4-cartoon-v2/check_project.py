import bpy,json,math
from pathlib import Path
W=Path(__file__).resolve().parent;P=W.parents[1]/'outputs/rap4-cartoon-v2-1440p/project';S=bpy.context.scene
assert S.camera.data.type=='ORTHO';assert abs(S.camera.rotation_euler.x-math.radians(54.73561))<1e-4
assert S.render.engine=='CYCLES';assert S.cycles.samples==12
assert bpy.data.objects['ezhi']['height_metres']==1.65
missing=[];count=0
for kind in ['lead','hood','blue','ezhi']:
 for f in range(1,3280):
  count+=1
  if not (P/'sprites'/kind/f'{f:05d}.png').exists():missing.append((kind,f))
assert not missing,missing[:10]
for im in bpy.data.images:
 if im.source=='SEQUENCE':assert Path(bpy.path.abspath(im.filepath)).exists(),im.filepath
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.frame_set(3109);S.render.resolution_percentage=25;S.render.filepath=str(W/'portable-check.png');bpy.ops.render.render(write_still=True)
report={'image_sequence_files_checked':count,'missing':0,'relative_paths':True,'projection':'orthographic isometric','elevation_degrees':35.26439,'ezhi_height_metres':1.65,'renderer':'Cycles OptiX','portable_frame_3109':'rendered at25percent for path check'}
(W/'project-validation.json').write_text(json.dumps(report,indent=2))
