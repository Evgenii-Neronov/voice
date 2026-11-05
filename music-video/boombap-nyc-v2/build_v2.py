import bpy,math,json,random
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
W=Path(__file__).resolve().parent;OLD=W.parent/'nyc-boombap';S=bpy.context.scene
man=json.loads((OLD/'scene-manifest.json').read_text());chars=[tuple(bpy.data.objects[c[k]] for k in ['root','rig','mesh']) for c in man['characters']]
random.seed(51)
def mat(name,c,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
black=mat('Soft black rubber',(.012,.016,.018),.68);chrome=mat('Brushed aluminium',(.32,.35,.38),.29,.8);brown=mat('Brown wool felt',(.075,.043,.023),.92);coatmat=mat('Tobacco gabardine',(.16,.095,.045),.8);white=mat('Ivory cotton',(.65,.62,.53),.7);ink=mat('ADV charcoal paint',(.025,.032,.037),.85);gold=mat('ADV ochre paint',(.73,.34,.025),.85)
def cube(name,loc,size,ma,bev=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bev:b=o.modifiers.new('Rounded manufactured edges','BEVEL');b.width=bev;b.segments=3;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def rod(name,a,b,r,ma):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(ma)
 for p in o.data.polygons:p.use_smooth=True
 return o
def torus(name,loc,major,minor,ma,rotation=(math.pi/2,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=12,location=loc,major_radius=major,minor_radius=minor,rotation=rotation);o=bpy.context.object;o.name=name;o.data.materials.append(ma)
 for p in o.data.polygons:p.use_smooth=True
 return o
def surface(name,verts,faces,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(ma);o=bpy.data.objects.new(name,me);S.collection.objects.link(o);return o
# Refine existing faces and clothing, preserving the lead's geometry and identity.
keep=['Basis']+[f'AA_VI_{i:02d}_{n}' for i,n in enumerate(['Sil','PP','FF','TH','DD','KK','CH','SS','nn','RR','aa','E','I','O','U'])]+['AK_25_JawOpen','AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight']
for ci,(root,rig,mesh) in enumerate(chars):
 rig.animation_data_clear()
 for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
 if mesh.data.shape_keys:
  for k in list(mesh.data.shape_keys.key_blocks):
   if k.name not in keep:mesh.shape_key_remove(k)
  mesh.data.shape_keys.animation_data_clear()
 sub=mesh.modifiers.new('Smooth silhouette subdivision','SUBSURF');sub.levels=1;sub.render_levels=1
 for ma in mesh.data.materials[:2]:
  n=ma.node_tree.nodes;l=ma.node_tree.links;p=n.get('Principled BSDF')
  if 'head' in ma.name.lower():
   p.inputs['Roughness'].default_value=.47;p.inputs['Subsurface Weight'].default_value=.075;p.inputs['Subsurface Radius'].default_value=(1,.4,.2)
  else:
   # Sharpen the garment boundary, removing the old dark gradient across the hem.
   sep=next((x for x in n if x.type=='SEPARATE_COLOR'),None)
   if sep:
    oldlinks=list(sep.outputs[0].links);step=n.new('ShaderNodeMath');step.operation='GREATER_THAN';step.inputs[1].default_value=.45;l.new(sep.outputs[0],step.inputs[0])
    for link in oldlinks:l.new(step.outputs[0],link.to_socket)
   p.inputs['Sheen Weight'].default_value=.22;p.inputs['Sheen Roughness'].default_value=.65
   noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=190;noise.inputs['Detail'].default_value=2
   bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0007;l.new(noise.outputs['Fac'],bump.inputs['Height'])
   if p.inputs['Normal'].links:l.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
   l.new(bump.outputs['Normal'],p.inputs['Normal'])
# A separate light-skinned, short-haired avatar supplies the portrait approximation.
folder=W/'assets/rocketbox/Assets/Avatars/Adults/Male_Adult_08';old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(folder/'Export/Male_Adult_08_facial.fbx'));added=set(bpy.data.objects)-old
rr=next(o for o in added if o.type=='ARMATURE');mm=next(o for o in added if o.type=='MESH');pr=bpy.data.objects.new('Passerby 183cm',None);S.collection.objects.link(pr);rr.parent=pr;rr.name='Passerby skeleton';rr.animation_data_clear();mm.name='Passerby portrait approximation'
for b in rr.pose.bones:b.matrix_basis=Matrix.Identity(4)
for k in list(mm.data.shape_keys.key_blocks):
 if k.name not in keep:mm.shape_key_remove(k)
for mi,original in enumerate(list(mm.data.materials)):
 cat='head' if 'head' in original.name.lower() else 'body';ma=mat('Passerby '+cat,(.1,.07,.04),.55);mm.data.materials[mi]=ma;n=ma.node_tree.nodes;l=ma.node_tree.links;p=n.get('Principled BSDF')
 tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(next((folder/'Textures').glob('*_'+cat+'_color.tga'))));l.new(tex.outputs['Color'],p.inputs['Base Color'])
 if cat=='head':p.inputs['Subsurface Weight'].default_value=.065
 else:
  # Keep skin-colored hands while tinting the shirt and trousers for the overcoat.
  attr=mm.data.color_attributes.get('Hand skin') or mm.data.color_attributes.new(name='Hand skin',type='FLOAT_COLOR',domain='POINT');vg={g.index:g.name for g in mm.vertex_groups}
  for v in mm.data.vertices:
   hand=sum(g.weight for g in v.groups if 'Hand' in vg[g.group] or 'Finger' in vg[g.group]);attr.data[v.index].color=(hand,hand,hand,1)
  at=n.new('ShaderNodeVertexColor');at.layer_name='Hand skin';mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.13,.077,.035,1);l.new(at.outputs['Color'],mix.inputs[0]);l.new(tex.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
for p in mm.data.polygons:p.use_smooth=True
sub=mm.modifiers.new('Smooth portrait silhouette','SUBSURF');sub.levels=1
chars.append((pr,rr,mm));pr.scale=(1.011,)*3
# Tailored open coat: weighted rings follow torso/pelvis/thighs rather than a rigid cone.
verts=[];faces=[];rings=[(.49,.31,.18),(.75,.27,.17),(1.01,.245,.165),(1.26,.265,.17),(1.44,.265,.145)]
for z,rx,ry in rings:
 for j in range(25):
  a=math.radians(16)+j*math.radians(328)/24;verts.append((rx*math.sin(a),-ry*math.cos(a),z))
for k in range(len(rings)-1):
 for j in range(24):a=k*25+j;faces.append((a,a+1,a+26,a+25))
co=surface('Open knee length trenchcoat',verts,faces,coatmat)
# World canonical front is -Y; transform into the avatar's bind space.
bpy.context.view_layer.update();co.parent=pr
for n in ['Bip01 Pelvis','Bip01 Spine','Bip01 Spine1','Bip01 Spine2']:co.vertex_groups.new(name=n)
for v in co.data.vertices:
 n='Bip01 Pelvis' if v.co.z<1.0 else ('Bip01 Spine' if v.co.z<1.2 else 'Bip01 Spine2');co.vertex_groups[n].add([v.index],1,'REPLACE')
arm=co.modifiers.new('Coat follows skeleton','ARMATURE');arm.object=rr
solid=co.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.004
sub=co.modifiers.new('Soft coat drape','SUBSURF');sub.levels=2
for p in co.data.polygons:p.use_smooth=True
# Head and chest accessories are attached by explicit world transforms during baking.
access=[]
def accessory(obj,actor,bone):
 bpy.context.view_layer.update();access.append((obj,actor,bone,obj.matrix_world.copy()))
# Hat is modelled around a canonical 1.83m human, later bound from a matching rest pose.
brim=torus('Fedora curved brim',(0,0,1.765),.135,.014,brown,(0,0,0));brim.scale=(1,1.25,.55)
accessory(brim,3,'Bip01 Head')
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(0,.015,1.805));hat=bpy.context.object;hat.name='Pinched brown fedora crown';hat.scale=(.106,.13,.095);hat.data.materials.append(brown)
for p in hat.data.polygons:p.use_smooth=True
for v in hat.data.vertices:
 if v.co.z>.45:v.co.z-=.2*(1-abs(v.co.x))
accessory(hat,3,'Bip01 Head')
band=torus('Fedora dark ribbon',(0,.01,1.775),.108,.012,black,(0,0,0));band.scale=(1,1.2,1);accessory(band,3,'Bip01 Head')
shirt=surface('White shirt front',[(-.09,-.171,1.40),(.09,-.171,1.40),(.065,-.185,1.15),(-.065,-.185,1.15)],[(0,1,2,3)],white);accessory(shirt,3,'Bip01 Spine2')
tie=surface('Black tie',[(0,-.184,1.39),(.029,-.188,1.34),(.018,-.196,1.17),(0,-.20,1.14),(-.018,-.196,1.17),(-.029,-.188,1.34)],[(0,1,2,3,4,5)],black);accessory(tie,3,'Bip01 Spine2')
for sign in [-1,1]:
 lapel=surface('Coat folded lapel',[(sign*.12,-.18,1.44),(sign*.23,-.16,1.34),(sign*.1,-.21,1.18),(sign*.065,-.19,1.35)],[(0,1,2,3)],coatmat);accessory(lapel,3,'Bip01 Spine2')
# Parked steel bicycle, detailed with spokes, drivetrain, saddle and swept handlebars.
bx,by=-3.75,2.55
frame=mat('Bicycle faded burgundy enamel',(.17,.025,.018),.38,.5)
def bp(x,z,y=0):return (bx+x,by+y,z)
for x in [-.56,.56]:
 torus('Bicycle tyre',bp(x,.47),.335,.027,black);torus('Alloy rim',bp(x,.47),.306,.009,chrome)
 rod('Wheel axle',bp(x,.47,-.07),bp(x,.47,.07),.025,chrome)
 for j in range(28):
  a=j*2*math.pi/28;rod('Wheel spoke',bp(x,.47,(-1)**j*.025),bp(x+.303*math.cos(a),.47+.303*math.sin(a)),.0016,chrome)
for a,b in [((-.56,.47),(-.12,.49)),((-.12,.49),(-.28,1.0)),((-.28,1.0),(-.56,.47)),((-.28,1.0),(.36,1.02)),((.36,1.02),(-.12,.49)),((.36,1.02),(.56,.47))]:rod('Bicycle frame tube',bp(*a),bp(*b),.019,frame)
rod('Seat post',bp(-.28,1),bp(-.30,1.13),.015,chrome);cube('Bicycle saddle',bp(-.31,1.15),(.24,.15,.055),black,.025)
rod('Handlebar stem',bp(.36,1.02),bp(.33,1.18),.016,chrome);rod('Handlebar',bp(.33,1.18,-.24),bp(.33,1.18,.24),.014,chrome)
for y in [-.24,.24]:rod('Black hand grip',bp(.33,1.18,y),bp(.43,1.18,y),.023,black)
torus('Chainring',bp(-.12,.49,-.06),.09,.008,chrome);rod('Pedal crank',bp(-.12,.49,-.08),bp(-.23,.38,-.08),.011,chrome);cube('Bicycle pedal',bp(-.23,.38,-.14),(.1,.15,.025),black)
rod('Kickstand',bp(-.13,.48,.03),bp(-.25,.14,.22),.008,chrome)
# Boombox sits on the sidewalk at curb; no product lettering.
bb=(2.5,-.65,.38);cube('Boombox body',bb,(.72,.22,.43),black,.025);cube('Brushed front panel',(bb[0],bb[1]-.116,bb[2]),(.69,.015,.39),chrome,.012)
for dx in [-.23,.23]:
 for radius,ma in [(.145,black),(.12,chrome),(.108,black),(.045,chrome)]:torus('Boombox speaker',(bb[0]+dx,bb[1]-.139,bb[2]-.01),radius,.008,ma)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=12,location=(bb[0]+dx,bb[1]-.138,bb[2]-.01));o=bpy.context.object;o.name='Speaker cone';o.scale=(.106,.018,.106);o.data.materials.append(black)
cube('Cassette door',(bb[0],bb[1]-.133,bb[2]-.035),(.135,.02,.135),black,.008)
for dx in [-.035,.035]:torus('Cassette reel',(bb[0]+dx,bb[1]-.15,bb[2]-.02),.021,.004,chrome)
for dx in [-.25,.25]:rod('Boombox carry handle',(bb[0]+dx,bb[1],.59),(bb[0]+dx,bb[1],.70),.012,black)
rod('Boombox carry handle',(bb[0]-.25,bb[1],.70),(bb[0]+.25,bb[1],.70),.014,black);rod('Telescopic antenna',(bb[0]+.29,bb[1]+.07,.59),(bb[0]+.53,bb[1]+.07,1.12),.0035,chrome)
for dx in [-.08,-.04,0,.04,.08]:cube('Deck button',(bb[0]+dx,bb[1]-.02,.602),(.027,.065,.013),chrome,.003)
# User-authorized lettering only: small side-wall graffiti and embroidered NY emblem.
plaster=mat('Weathered off white plaster',(.53,.51,.44),.94);cube('Side white plaster patch',(-6.95,3.115,1.95),(2.3,.025,1.2),plaster,.008)
def lettering(name,body,loc,size,ma,extrude=0):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.align_x='CENTER';cu.size=size;cu.extrude=extrude;cu.shear=.19;cu.space_character=.85;o=bpy.data.objects.new(name,cu);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);cu.materials.append(ma);return o
lettering('ADV painted outline','ADV',(-6.94,3.093,1.57),.95,ink)
lettering('ADV ochre fill','ADV',(-6.98,3.088,1.61),.88,gold)
# Short paint drips make the hand-painted mark part of the wall, no extra symbols.
for x in [-7.7,-7.15,-6.55]:rod('Graffiti paint drip',(x,3.082,1.56),(x,3.082,1.38+random.random()*.12),.009,ink)
ny=lettering('Cap NY embroidery','NY',(.013,.002,1.739),.043,white,.0008);accessory(ny,0,'Bip01 Head')
# World and physically based illumination. Cycles preview determines final renderer settings.
block=bpy.data.objects.get('Unmarked residential block')
if block:
 bevel=block.modifiers.new('Small real edge highlights','BEVEL');bevel.width=.008;bevel.segments=2;block.modifiers.new('Architectural normals','WEIGHTED_NORMAL')
for ma in bpy.data.materials:
 if ma.name in ['Warm occupied windows','Unlit glass','Cool window reflection']:
  n=ma.node_tree.nodes;l=ma.node_tree.links;p=n.get('Principled BSDF');geo=n.new('ShaderNodeNewGeometry');wave=n.new('ShaderNodeTexWave');wave.bands_direction='Z';wave.inputs['Scale'].default_value=6;l.new(geo.outputs['Position'],wave.inputs['Vector']);mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.04,.035,.025,1);mix.inputs[2].default_value=(.32,.26,.16,1) if 'Warm' in ma.name else (.035,.055,.075,1);l.new(wave.outputs['Color'],mix.inputs[0]);l.new(mix.outputs[0],p.inputs['Base Color'])
  if 'Warm' in ma.name:l.new(mix.outputs[0],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.3
  p.inputs['Roughness'].default_value=.19;p.inputs['Coat Weight'].default_value=.5
S.world.use_nodes=True;n=S.world.node_tree.nodes;l=S.world.node_tree.links;n.clear();out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');env=n.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load('I:/UnrealProduction/Assets/industrial_sunset_puresky_4k.hdr');bg.inputs[1].default_value=.26;l.new(env.outputs[0],bg.inputs[0]);l.new(bg.outputs[0],out.inputs[0])
for o in S.objects:
 if o.type=='LIGHT':
  if o.data.type=='AREA':o.data.energy*=.55;o.data.size=max(o.data.size,4)
S.view_settings.exposure=-.15;S.view_settings.look='AgX - Medium High Contrast'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=24;S.cycles.use_denoising=True;S.cycles.adaptive_threshold=.08;S.cycles.max_bounces=5;S.cycles.diffuse_bounces=3;S.cycles.glossy_bounces=3
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.render.resolution_x=2560;S.render.resolution_y=1440;S.render.fps=24
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=96;S.render.threads_mode='FIXED';S.render.threads=6
S.camera.data.dof.use_dof=True;S.camera.data.dof.aperture_fstop=5.6
# Store accessory bind transforms in canonical rest coordinates; their animated world pose is baked later.
for root,rig,mesh in chars:root.location=(0,0,0);root.rotation_euler=(0,0,0)
bpy.context.view_layer.update()
bind=[]
for obj,ci,bone,matrix in access:
 rig=chars[ci][1];rest=rig.matrix_world@rig.data.bones[bone].matrix_local;bind.append({'object':obj.name,'actor':ci,'bone':bone,'offset':[list(row) for row in rest.inverted()@matrix]})
(W/'scene-manifest.json').write_text(json.dumps({'characters':[{'root':a.name,'rig':b.name,'mesh':c.name} for a,b,c in chars],'accessories':bind},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(W/'scene-v2.blend'),compress=True)
print('SCENE READY',len(S.objects),flush=True)
