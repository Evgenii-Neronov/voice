import bpy,json,numpy as np,math
from pathlib import Path
from mathutils import Matrix
W=Path(__file__).resolve().parent;V2=W.parent/'nyc-boombap-v2';S=bpy.context.scene
man=json.loads((V2/'scene-manifest.json').read_text());lighting=json.loads((W/'lighting-v1.json').read_text());beatdata=json.loads((W/'beats.json').read_text());beats=np.array(beatdata['beat_seconds']);frames=np.arange(1,6080,dtype=float);times=(frames-1)/24
# Fractional beat index gives continuous body phase while retaining measured accents.
phase=2*np.pi*np.interp(times,beats,np.arange(len(beats)),left=0,right=len(beats)-1)
report={'actors':[],'removed':[],'lighting_source':'nyc-boombap/nyc-final-scene.blend','subtitle_bottom_px':144,'beat_bpm_estimate':beatdata['tempo_bpm']}
def norm(q):return q/np.maximum(np.linalg.norm(q,axis=1,keepdims=True),1e-12)
def hemi(q):
 q=q.copy();n=0
 for i in range(1,len(q)):
  if q[i-1]@q[i]<0:q[i]*=-1;n+=1
 return q,n
def angles(q):return np.degrees(2*np.arccos(np.clip(np.abs(np.sum(q[:-1]*q[1:],axis=1)),0,1)))
def mul_axis(q,axis,a):
 b=np.zeros_like(q);b[:,0]=np.cos(a/2);b[:,axis+1]=np.sin(a/2)
 w=q[:,0]*b[:,0]-np.sum(q[:,1:]*b[:,1:],axis=1);xyz=q[:,0,None]*b[:,1:]+b[:,0,None]*q[:,1:]+np.cross(q[:,1:],b[:,1:]);return np.column_stack([w,xyz])
def write(fc,y):
 fc.keyframe_points.clear();fc.keyframe_points.add(len(frames));fc.keyframe_points.foreach_set('co',np.column_stack([frames,y]).ravel())
 for k in fc.keyframe_points:k.interpolation='LINEAR'
 fc.update()
for ci,c in enumerate(man['characters'][:3]):
 rig=bpy.data.objects[c['rig']];ac=rig.animation_data.action;paths={fc.data_path for fc in ac.fcurves if fc.data_path.endswith('rotation_quaternion')};stats={'actor':ci,'sign_flips_corrected':0,'old_max_frame_degrees':0,'new_max_frame_degrees':0,'old_frames_over_30deg':0,'new_frames_over_30deg':0,'worst_old':[]}
 for path in sorted(paths):
  fcs=[ac.fcurves.find(path,index=j) for j in range(4)];x=np.array([k.co.x for k in fcs[0].keyframe_points]);raw=np.column_stack([[k.co.y for k in fc.keyframe_points] for fc in fcs]);old=norm(np.column_stack([np.interp(frames,x,raw[:,j]) for j in range(4)]));oa=angles(old)
  fixed,n=hemi(norm(raw));stats['sign_flips_corrected']+=n
  q=norm(np.column_stack([np.interp(frames,x,fixed[:,j]) for j in range(4)]));q,_=hemi(q)
  # Small symmetric filter removes sampling chatter without flattening gesture shapes.
  p=np.pad(q,((1,1),(0,0)),mode='edge');q=norm((p[:-2]+2*p[1:-1]+p[2:])/4)
  if ci in (1,2):
   ph=phase+(.10 if ci==1 else -.14);sway=np.sin(ph*.5+(0 if ci==1 else .65));pulse=(1+np.cos(ph))/2;envelope=np.minimum(1,times/1.3)
   if 'Bip01 Head"' in path:q=mul_axis(q,2,envelope*(.12 if ci==1 else .105)*np.cos(ph));q=mul_axis(q,0,envelope*.025*sway)
   if 'Bip01 Spine1"' in path:q=mul_axis(q,2,envelope*.04*np.cos(ph-.25));q=mul_axis(q,0,envelope*(.045 if ci==1 else .055)*sway)
   for bone,factor in [('Thigh',1),('Calf',-2),('Foot',1)]:
    if (' '+bone+'"') in path:q=mul_axis(q,2,envelope*.035*pulse*factor)
  q,_=hemi(norm(q));na=angles(q);stats['old_max_frame_degrees']=max(stats['old_max_frame_degrees'],float(oa.max()));stats['new_max_frame_degrees']=max(stats['new_max_frame_degrees'],float(na.max()));stats['old_frames_over_30deg']+=int((oa>30).sum());stats['new_frames_over_30deg']+=int((na>30).sum())
  if oa.max()>30:stats['worst_old'].append({'bone':path,'frame':int(np.argmax(oa)+1),'degrees':float(oa.max())})
  for j,fc in enumerate(fcs):write(fc,q[:,j])
 if ci in (1,2):
  root=bpy.data.objects[c['root']];ra=root.animation_data.action
  for axis in [0,2]:
   fc=ra.fcurves.find('location',index=axis);base=np.array([fc.evaluate(f) for f in frames]);ph=phase+(.10 if ci==1 else -.14);env=np.minimum(1,times/1.3)
   y=base+env*(.022*np.sin(ph*.5+(0 if ci==1 else .65)) if axis==0 else -.005*(1+np.cos(ph))/2);write(fc,y)
 report['actors'].append(stats)
# Remove the entire passerby hierarchy and its separately attached wardrobe.
remove=set();root=bpy.data.objects.get(man['characters'][3]['root'])
if root:remove.update([root,*root.children_recursive])
for a in man['accessories']:
 if a['actor']==3 and a['object'] in bpy.data.objects:remove.add(bpy.data.objects[a['object']])
for name in ['Open knee length trenchcoat','Cap NY embroidery']:
 if name in bpy.data.objects:remove.add(bpy.data.objects[name])
for o in sorted(remove,key=lambda x:x.name):report['removed'].append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Restore exact V1 light transforms, powers, colour, sizes, world and colour management.
for d in lighting['lights']:
 o=bpy.data.objects[d['name']];o.matrix_world=Matrix(d['matrix']);o.data.energy=d['energy'];o.data.color=d['color'];o.data.size=d['size'];o.data.use_shadow=d['use_shadow']
 if o.name in ['Streetlight','Streetlight.002']:o.data.use_shadow=False
S.world.use_nodes=True;nodes=S.world.node_tree.nodes;nodes.clear();bg=nodes.new('ShaderNodeBackground');out=nodes.new('ShaderNodeOutputWorld');bg.inputs[0].default_value=lighting['world']['color'];bg.inputs[1].default_value=lighting['world']['strength'];S.world.node_tree.links.new(bg.outputs[0],out.inputs[0])
for key in ['view_transform','look','exposure']:setattr(S.view_settings,key,lighting[key])
S.frame_set(1);S.render.resolution_percentage=100;S.render.filepath='//renders/NYC-v3-';S['revision']='V3: continuous quaternion curves, beat listening, V1 lighting, no passerby or NY'
assert not any(o.type=='FONT' and 'NY' in o.data.body for o in S.objects)
assert all(s['new_frames_over_30deg']==0 for s in report['actors']),report['actors']
report['text_objects']=[o.data.body for o in S.objects if o.type=='FONT'];(W/'motion-validation.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(W/'film-v3.blend'),compress=True);print(json.dumps(report),flush=True)
