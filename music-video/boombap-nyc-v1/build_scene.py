import bpy,math,random,json,os,time,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent; A=W/'assets'; OUT=W.parents[1]/'outputs/nyc-boombap-1440p'
random.seed(19); bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene;S.render.engine='BLENDER_EEVEE_NEXT';S.render.resolution_x=2560;S.render.resolution_y=1440;S.render.resolution_percentage=100;S.render.fps=24
S.eevee.taa_render_samples=16
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.compression=15
S.world=bpy.data.worlds.new('Blue dusk');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.17,.24,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.35
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.6
S.render.film_transparent=False
# Materials: no signage, text objects, logos, or road markings.
def material(name,c,rough=.6,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m
def pbr(name,asset,scale,tint=None):
 m=material(name,(.3,.3,.3));n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');geo=n.new('ShaderNodeNewGeometry');v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs[3].default_value=scale;l.new(geo.outputs['Position'],v.inputs[0])
 for kind in ['diff','nor_gl','rough']:
  path=A/f'{asset}_{kind}_2k.jpg'
  if not path.exists():continue
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True);tex.projection='BOX';tex.projection_blend=.2;l.new(v.outputs[0],tex.inputs['Vector'])
  if kind=='diff':
   if tint:
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.7;mix.inputs[2].default_value=(*tint,1);l.new(tex.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
   else:l.new(tex.outputs['Color'],p.inputs['Base Color'])
  elif kind=='rough':tex.image.colorspace_settings.name='Non-Color';l.new(tex.outputs[0],p.inputs['Roughness'])
  else:
   tex.image.colorspace_settings.name='Non-Color';normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55;l.new(tex.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
 return m
brick=pbr('Weathered red brick','red_bricks_04',.4);brickdark=pbr('Dark brown brick','red_bricks_04',.4,(.5,.4,.32));concrete=pbr('Stoop stone','concrete_wall_006',.65);asphalt=pbr('Asphalt','asphalt_02',.35)
black=material('Painted iron',(.025,.031,.033),.4,.6);trim=material('Limestone',(.31,.29,.25));glass=material('Unlit glass',(.018,.035,.05),.2,.45);warm=material('Warm occupied windows',(.65,.36,.15),.3,0,.65);coolglass=material('Cool window reflection',(.055,.1,.13),.25,.35);door=material('Plain dark wood',(.075,.045,.025));lampmat=material('Lamp glass',(.95,.68,.36),.2,0,4);yellow=material('Mustard yellow jacket',(.84,.49,.035),.7);rubber=material('Sneaker rubber',(.08,.085,.08),.8)
static=[]
meshcache={}
def cube(name,loc,size,mat,bevel=0):
 key=('cube',mat.name)
 if key not in meshcache:
  verts=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)]
  faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
  me=bpy.data.meshes.new('Box '+mat.name);me.from_pydata(verts,[],faces);me.materials.append(mat);meshcache[key]=me
 o=bpy.data.objects.new(name,meshcache[key]);S.collection.objects.link(o);o.location=loc;o.scale=size;static.append(o);return o
def rod(name,a,b,r,mat,vertices=8):
 key=('rod',mat.name,vertices)
 if key not in meshcache:
  vs=[(math.cos(k*2*math.pi/vertices),math.sin(k*2*math.pi/vertices),z) for z in [-.5,.5] for k in range(vertices)]
  fs=[tuple(range(vertices-1,-1,-1)),tuple(range(vertices,vertices*2))]+[(k,(k+1)%vertices,(k+1)%vertices+vertices,k+vertices) for k in range(vertices)]
  me=bpy.data.meshes.new('Rod '+mat.name);me.from_pydata(vs,[],fs);me.materials.append(mat);meshcache[key]=me
 a=Vector(a);b=Vector(b);delta=b-a;o=bpy.data.objects.new(name,meshcache[key]);S.collection.objects.link(o);o.location=(a+b)/2;o.scale=(r,r,delta.length);o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();static.append(o);return o
def area(name,loc,target,power,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
cube('Unmarked road',(0,-6,-.16),(110,15,.25),asphalt)
cube('Pavement',(0,1,-.02),(110,4.7,.28),concrete)
cube('Curb',(0,-1.3,.08),(110,.24,.35),concrete,.035)
for x in range(-48,51,2):cube('Pavement joint',(x,.5,.123),(.012,3.5,.005),black)
# Brownstone block: raised stoops, sash windows, cornices, fire escapes.
for bi,x in enumerate(range(-28,29,6)):
 h=13.7+(bi%3)*.7;front=3.3
 cube('Residential brick',(x,front+3,h/2),(5.92,6,h),brick if bi%3 else brickdark)
 cube('Foundation',(x,front-.06,.75),(5.95,.18,1.5),trim)
 for z in [3.2,h-.35,h+.02]:cube('Cornice',(x,front-.2,z),(6.12,.48,.18),trim)
 for floor in range(4):
  z=2.1+floor*3.03
  for col in [-1.82,0,1.82]:
   xx=x+col
   if floor==0 and col==0:continue
   cube('Window stone recess',(xx,front-.16,z),(1.25,.25,1.9),trim)
   wm=warm if random.random()<.26 else (coolglass if random.random()<.4 else glass)
   cube('Window pane',(xx,front-.31,z),(1.01,.03,1.63),wm)
   for dx in [-.51,.51]:cube('Sash',(xx+dx,front-.35,z),(.065,.06,1.7),black)
   for dz in [-.83,0,.83]:cube('Sash',(xx,front-.36,z+dz),(1.08,.065,.065),black)
   cube('Projecting sill',(xx,front-.43,z-.95),(1.42,.6,.13),trim)
   if (bi+floor+int(col))%4==0:cube('Window air conditioner',(xx,front-.66,z-.55),(.73,.6,.38),black)
 cube('Entrance',(x,front-.16,1.97),(1.12,.2,2.18),door)
 cube('Door glazing',(x,front-.28,2.2),(.71,.035,.98),glass)
 rod('Door handle',(x+.36,front-.32,1.62),(x+.36,front-.32,1.9),.023,trim)
 for j in range(5):cube('Stoop step',(x,front-1.55+j*.26,.1+j*.15),(1.65,.38,.21+j*.30),concrete)
 for side in [-1,1]:
  xx=x+side*.86
  rod('Stoop rail',(xx,front-1.7,.9),(xx,front-.3,1.7),.035,black)
  for j in range(5):rod('Rail upright',(xx,front-1.7+j*.3,.15+j*.14),(xx,front-1.7+j*.3,.9+j*.17),.018,black)
 # exterior steel fire escape on alternate facades
 if bi%2:
  xx=x+1.45
  for level in range(1,4):
   z=1.05+level*3.03;yy=front-.98
   cube('Fire escape platform',(xx,yy,z),(2.3,1.35,.09),black)
   for u in range(12):rod('Balustrade',(xx-1.1+u*.2,yy-.65,z),(xx-1.1+u*.2,yy-.65,z+.9),.016,black)
   rod('Rail top',(xx-1.14,yy-.65,z+.91),(xx+1.14,yy-.65,z+.91),.027,black)
   if level<3:
    for side in [-.32,.32]:rod('Ladder stringer',(xx-.8,yy+side,z+.06),(xx+.8,yy+side,z+3.03),.025,black)
    for j in range(12):
     rod('Ladder tread',(xx-.8+j*1.6/12,yy-.32,z+j*3.03/12),(xx-.8+j*1.6/12,yy+.32,z+j*3.03/12),.022,black)
 # rooftop parapet and simple tank silhouettes
 cube('Parapet',(x,front+.3,h+.3),(5.9,.3,.65),brick)
 if bi%3==1:
  bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.9,depth=1.7,location=(x,front+3,h+1.9));bpy.context.object.data.materials.append(door);static.append(bpy.context.object)
  bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=1.05,radius2=0,depth=.55,location=(x,front+3,h+3));bpy.context.object.data.materials.append(black);static.append(bpy.context.object)
  for dx in [-.7,.7]:rod('Tank leg',(x+dx,front+3,h),(x+dx,front+3,h+1.1),.07,black)
# Iron basement fences and stoop-side bins, all unbranded.
for x in [-8,-3.7,4.7,9]:
 for j in range(9):rod('Fence picket',(x+j*.19,2.35,.15),(x+j*.19,2.35,1.02),.018,black)
 rod('Fence rail',(x,2.35,.85),(x+1.6,2.35,.85),.028,black)
for x in [-4.8,5.1,11.2]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.29,depth=.83,location=(x,2.65,.52));bpy.context.object.data.materials.append(black);static.append(bpy.context.object)
 cube('Bin lid',(x,2.65,.95),(.64,.64,.06),black,.025)
for x in [-11,5.8,18]:
 rod('Streetlight pole',(x,-.9,.1),(x,-.9,5.8),.07,black,12)
 rod('Streetlight arm',(x,-.9,5.8),(x,-2.1,5.8),.045,black)
 cube('Streetlight housing',(x,-2.1,5.77),(.65,.4,.13),black,.04)
 cube('Streetlight lens',(x,-2.1,5.69),(.5,.32,.03),lampmat)
 area('Streetlight',(x,-2.1,5.6),(x,-.2,0),600,(1,.68,.35),2)
# Sparse distant opposite-side buildings make reverse angles read as a street.
for x in [-22,-12,12,22]:
 cube('Opposite block',(x,-18,7),(8,7,14),brickdark)
 for z in [2,5,8,11]:
  for dx in [-2,0,2]:cube('Far window',(x+dx,-14.48,z),(1.0,.02,1.6),warm if random.random()<.25 else glass)
area('Cool sky key',(-3,-6,8),(0,0,1),1700,(.48,.63,1),8)
area('Warm soft key',(-3,-4,3),(0,0,1.4),680,(1,.78,.53),4)
area('Edge light',(4,2.4,4),(0,0,1),1100,(.48,.66,1),3)
print('SET GEOMETRY READY',len(static),flush=True)
# Import existing full-body captured gesture clips.
actions=[]
for fn in ['m_gestic_talk_cool.max.fbx','m_gestic_talk_excited_01.max.fbx','m_gestic_talk_relaxed_01.max.fbx']:
 old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(A/fn));added=set(bpy.data.objects)-old
 rig=next(o for o in added if o.type=='ARMATURE');ac=rig.animation_data.action;ac.use_fake_user=True;actions.append(ac)
 for o in added:bpy.data.objects.remove(o,do_unlink=True)
characters=[]
for idx,(num,pos,angle) in enumerate([(17,(0,-.15,0),0),(18,(-1.8,.65,0),-.12),(12,(1.65,.85,0),.1),(4,(3.2,1.45,0),.24)]):
 folder=A/f'rocketbox/Assets/Avatars/Adults/Male_Adult_{num:02d}';old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(folder/f'Export/Male_Adult_{num:02d}_facial.fbx'));added=set(bpy.data.objects)-old;rig=next(o for o in added if o.type=='ARMATURE');mesh=next(o for o in added if o.type=='MESH')
 root=bpy.data.objects.new(f'Performer_{idx}',None);S.collection.objects.link(root);root.location=pos;root.rotation_euler.z=angle;rig.parent=root
 rig.animation_data_clear();rig.animation_data_create();track=rig.animation_data.nla_tracks.new();strip=track.strips.new('Captured gestures',1,actions[idx%3]);strip.scale=.8;strip.repeat=12
 # Replace all body lettering by plain fabric materials, retaining sculpted cloth normal maps.
 mats=list(mesh.data.materials)
 for mi,orig in enumerate(mats):
  m=material(f'Person{idx}_{orig.name}',(.3,.3,.3));mesh.data.materials[mi]=m;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
  category='head' if 'head' in orig.name else 'body';color=next((folder/'Textures').glob(f'*_{category}_color.tga'));tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(color),check_existing=True);l.new(tex.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.7
  normalfile=next((folder/'Textures').glob(f'*_{category}_normal.tga'));nt=n.new('ShaderNodeTexImage');nt.image=bpy.data.images.load(str(normalfile),check_existing=True);nt.image.colorspace_settings.name='Non-Color';nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.4;l.new(nt.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],p.inputs['Normal'])
  if category=='body':
   # Plain cloth shader variants share the imported UV-space wrinkle normal map.
   cloth=m.copy();cloth.name=f'Plain jacket {idx}';cp=cloth.node_tree.nodes.get('Principled BSDF')
   for link in list(cp.inputs['Base Color'].links):cloth.node_tree.links.remove(link)
   cp.inputs['Base Color'].default_value=[(.83,.48,.022,1),(.07,.075,.08,1),(.055,.11,.18,1),(.12,.08,.06,1)][idx]
   pants=cloth.copy();pants.name=f'Plain trousers {idx}';pants.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.027,.035,.045,1)
   shoes=cloth.copy();shoes.name=f'Plain shoes {idx}';shoes.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.13,.14,.14,1)
   ci=len(mesh.data.materials);mesh.data.materials.append(cloth);pi=len(mesh.data.materials);mesh.data.materials.append(pants);si=len(mesh.data.materials);mesh.data.materials.append(shoes)
   vg={g.index:g.name for g in mesh.vertex_groups}
   for poly in mesh.data.polygons:
    if poly.material_index!=mi:continue
    ww={}
    for vi in poly.vertices:
     for g in mesh.data.vertices[vi].groups:ww[vg[g.group]]=ww.get(vg[g.group],0)+g.weight
    dominant=max(ww,key=ww.get) if ww else ''
    if any(x in dominant for x in ['Hand','Finger']):continue
    if any(x in dominant for x in ['Foot','Toe']):poly.material_index=si
    elif any(x in dominant for x in ['Thigh','Calf','Pelvis']):poly.material_index=pi
    else:poly.material_index=ci
 for poly in mesh.data.polygons:poly.use_smooth=True
 characters.append((root,rig,mesh))
# Camera, restrained focal lengths, true dolly/orbit movement.
bpy.ops.object.camera_add(location=(0,-7,1.65));cam=bpy.context.object;cam.name='Cinema camera';S.camera=cam;cam.data.lens=42
cam.data.dof.use_dof=True;cam.data.dof.aperture_fstop=7.1
focus=bpy.data.objects.new('Focus lead',None);S.collection.objects.link(focus);focus.location=(0,0,1.4);cam.data.dof.focus_object=focus
S.frame_start=1;S.frame_end=6080
# Save GPU-ready base. Frame updates handled explicitly by render script.
S.frame_set(110)
cam.rotation_euler=(Vector((0,.35,1.2))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(W/'nyc-scene.blend'))
S.render.filepath=str(W/'first-frame.png');t=time.time();bpy.ops.render.render(write_still=True);print('RENDER_SECONDS',time.time()-t,flush=True)
(W/'scene-manifest.json').write_text(json.dumps({'objects':len(S.objects),'characters':[{'root':r.name,'rig':a.name,'mesh':m.name} for r,a,m in characters],'actions':[(a.name,list(a.frame_range)) for a in actions],'no_text_objects':all(o.type!='FONT' for o in S.objects)},indent=2))
