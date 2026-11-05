import bpy,math,json,sys,random
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=32;S.eevee.use_raytracing=True
S.render.resolution_x=2560;S.render.resolution_y=1440;S.render.resolution_percentage=100;S.render.fps=12;S.frame_end=3279
S.world.color=(.04,.04,.04);S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.11,.24,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.12
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=.65
def mat(name,c,rough=.75,em=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em;return m
ink=mat('Ink - midnight blue',(.022,.032,.052));stone=mat('Warm limestone',(.37,.32,.28));road=mat('Rain-dark asphalt',(.045,.064,.09),.27);pavement=mat('Sidewalk blue slate',(.22,.25,.29),.5);door=mat('Painted doors',(.055,.09,.13));warm=mat('Warm window light',(.9,.43,.12),em=.85);glass=mat('Blue windows',(.05,.11,.19),.25);metal=mat('Iron',(.045,.065,.08),.35);yellow=mat('ADV ochre',(.83,.49,.08));red=mat('Bicycle enamel',(.38,.065,.04),.3)
brick=mat('Illustrated brick',(.34,.12,.07));nt=brick.node_tree;tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Color1'].default_value=(.39,.15,.10,1);tex.inputs['Color2'].default_value=(.22,.075,.055,1);tex.inputs['Mortar'].default_value=(.16,.14,.15,1);tex.inputs['Scale'].default_value=7;tex.inputs['Mortar Size'].default_value=.025;tex.inputs['Brick Width'].default_value=.6;tex.inputs['Row Height'].default_value=.12;nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
def box(name,loc,scale,ma,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel:mod=o.modifiers.new('Soft ink edge','BEVEL');mod.width=bevel;mod.segments=1;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def rod(name,a,b,r,ma):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(ma);return o
def torus(name,loc,r,t,ma):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=40,minor_segments=8,location=loc,rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=name;o.data.materials.append(ma);return o
box('Street', (0,0,-.14),(38,30,.25),road)
box('Sidewalk',(0,3,.04),(28,3.2,.24),pavement)
for x in range(-14,15):box('Pavement seam',(x,3,.166),(.012,3.1,.005),ink,0)
for y in [1.9,3,4]:box('Pavement seam',(0,y,.166),(28,.012,.005),ink,0)
box('Brownstone block',(0,6,3.7),(25,4,7.1),brick)
for z in [.65,3.25,6.1,7.25]:box('Stone course',(0,3.94,z),(25,.17,.13),stone)
for x in [-10,-5,0,5,10]:
 box('Facade pilaster',(x,3.92,3.75),(.12,.16,7),stone)
 for wx in [x+1.15,x+3.4]:
  for z in [2.1,4.6,6.65]:
   box('Window ink frame',(wx,3.85,z),(1.25,.18,1.3),ink)
   box('Window',(wx,3.735,z),(1.05,.04,1.1),warm if int(wx*3+z)%3==0 else glass,0)
   box('Window mullion',(wx,3.69,z),(.035,.035,1.1),stone,0);box('Window crossbar',(wx,3.69,z),(1.1,.035,.035),stone,0)
   box('Window sill',(wx,3.70,z-.7),(1.4,.36,.12),stone)
 for dx in [x+.1]:
  box('Door surround',(dx,3.75,1.35),(1.1,.22,2.3),stone);box('Door',(dx,3.59,1.35),(.85,.05,2.1),door)
  box('Door glass',(dx,3.55,1.85),(.6,.03,.7),glass);rod('Door handle',(dx+.28,3.50,.9),(dx+.28,3.50,1.15),.02,yellow)
  for i in range(3):box('Stoop',(dx,3.5-i*.24,.2+(3-i)*.11),(1.5,.5,.22*(3-i)),stone)
  for side in [-1,1]:
   for i in range(4):rod('Stoop rail',(dx+side*.8,3.7-i*.3,.25),(dx+side*.8,3.7-i*.3,1.2-i*.15),.025,metal)
   rod('Stoop handrail',(dx+side*.8,3.7,1.2),(dx+side*.8,2.8,.75),.035,metal)
def light(name,typ,loc,col,power,size=1,target=None):
 d=bpy.data.lights.new(name,typ);d.energy=power;d.color=col
 if typ=='AREA':d.shape='DISK';d.size=size
 if typ=='POINT':d.shadow_soft_size=size
 o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc
 if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 return o
lampglass=mat('Lantern golden glass',(1,.56,.18),em=4)
for x,y in [(-4,1.3),(4.5,1.3),(7,-3.3),(-9,1.3)]:
 rod('Lamp post',(x,y,.15),(x,y,3.55),.055,metal);box('Lamp plinth',(x,y,.22),(.23,.23,.45),metal)
 box('Lantern cap',(x,y,3.9),(.5,.5,.10),metal);box('Lantern glow',(x,y,3.64),(.30,.30,.42),lampglass)
 for dx in [-.2,.2]:
  for dy in [-.2,.2]:rod('Lantern cage',(x+dx,y+dy,3.4),(x+dx,y+dy,3.9),.018,metal)
 light('Practical warm lamp','POINT',(x,y,3.30),(1,.48,.18),420,.23)
light('Moon softbox','AREA',(1,-4,9),(.30,.49,1),300,8,(0,1,0))
light('Warm bounced streetlight','AREA',(-3,-4,4),(1,.61,.32),450,5,(0,0,1))
# Boombox on sidewalk.
box('Boombox', (2.7,2.05,.48),(1.15,.32,.6),ink)
for x in [2.33,3.07]:
 torus('Speaker rim',(x,1.875,.48),.19,.025,stone);box('Speaker face',(x,1.875,.48),(.31,.015,.31),metal)
box('Tape deck',(2.7,1.87,.48),(.22,.025,.18),stone);rod('Aerial',(3.1,2,.8),(3.45,2,1.55),.009,stone)
for a,b in [((2.35,2,.8),(2.35,2,.95)),((2.35,2,.95),(3.05,2,.95)),((3.05,2,.95),(3.05,2,.8))]:rod('Boombox handle',a,b,.025,metal)
# Bicycle against house.
for x in [-3.6,-2.2]:
 torus('Bike tyre',(x,3.48,.6),.43,.035,ink);torus('Bike rim',(x,3.48,.6),.39,.012,stone)
 for i in range(16):
  a=i*math.tau/16;rod('Spoke',(x,3.48,.6),(x+.38*math.cos(a),3.48,.6+.38*math.sin(a)),.004,stone)
for a,b in [((-3.6,.6),(-3.2,1.2)),((-3.2,1.2),(-2.85,.6)),((-2.85,.6),(-3.6,.6)),((-3.2,1.2),(-2.5,1.2)),((-2.5,1.2),(-2.85,.6)),((-2.5,1.2),(-2.2,.6)),((-2.5,1.2),(-2.45,1.45))]:rod('Bike frame',(a[0],3.48,a[1]),(b[0],3.48,b[1]),.025,red)
box('Bike seat',(-3.2,3.48,1.27),(.3,.15,.07),ink);rod('Handlebars',(-2.45,3.48,1.45),(-2.25,3.48,1.45),.025,metal)
# Drawn cast in a dimensional set. Metres calibrated from crown to soles.
for kind,height,x,y in [('lead',1.80,0,-1),('hood',1.76,-1.8,-.65),('blue',1.83,1.55,.45),('ezhi',1.65,2.6,.8)]:
 scale=height/640;wid=640*scale;hei=800*scale
 mesh=bpy.data.meshes.new(kind);mesh.from_pydata([(-wid/2,0,-55*scale),(wid/2,0,-55*scale),(wid/2,0,745*scale),(-wid/2,0,745*scale)],[],[(0,1,2,3)]);mesh.uv_layers.new()
 for i,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):mesh.uv_layers.active.data[i].uv=uv
 ob=bpy.data.objects.new(kind,mesh);S.collection.objects.link(ob);ob.location=(x,y,.03);ob.rotation_euler[2]=math.pi/4
 ma=mat(kind+' illustrated',(.8,.8,.8));nt=ma.node_tree;p=nt.nodes['Principled BSDF'];im=nt.nodes.new('ShaderNodeTexImage');first=1;im.image=bpy.data.images.load(str(W/'sprites'/kind/f'{first:05d}.png'));im.image.source='SEQUENCE';im.image_user.frame_duration=3280-first+1;im.image_user.frame_start=first;im.image_user.use_auto_refresh=True
 nt.links.new(im.outputs['Color'],p.inputs['Base Color']);nt.links.new(im.outputs['Alpha'],p.inputs['Alpha']);nt.links.new(im.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.12;p.inputs['Roughness'].default_value=1;ma.surface_render_method='DITHERED';ob.data.materials.append(ma)
 ob['height_metres']=height
 if kind=='ezhi':
  for f,xx,zz in [(1,8,-8),(3018,8,-8),(3020,7.8,.03),(3070,2.6,.03),(3279,2.6,.03)]:ob.location=(xx,y,zz);ob.keyframe_insert('location',frame=f)
 if ob.animation_data:
  for fc in ob.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Isometric director camera';S.camera=cam;cam.data.type='ORTHO';cam.data.lens=50;cam.data.clip_end=200
# Translating true isometric camera; constant 45-degree azimuth /35.264-degree elevation.
shots=[]
boundaries=[0,8,22,38,54,67.48,81.88,98,115,132,146,161,178,196.74,210.86,228,244,251,256.28,265,271,273.25]
patterns=[(-.6,.7,1.2,11.6),(.25,-.1,1.0,7.0),(-.65,.15,1.2,8.5),(0,-1,1.15,4.8),(0,.4,1.2,10),(.3,.2,1.3,9)]
for i,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
 x,y,z,span=patterns[i%len(patterns)]
 if a>=251:x,y,z,span=(1.3,.1,1.25,10.5)
 if a>=256.28:x,y,z,span=(2.4,.8,1.0,5.6)
 if a>=265:x,y,z,span=(2.6,.8,1.1,4.8)
 if a>=271:x,y,z,span=(.9,.6,1.3,12)
 shots.append({'start':a,'end':b,'target':[x,y,z],'span':span,'purpose':('Guest final response' if a>=251 else ['Reveal the street past foreground lantern','Lead delivery and hand accents','Listeners respond in a wider group','Tight argument','Release to architecture','Hook ensemble'][i%6])})
 for f,u in [(round(a*12)+1,0),(round(b*12),1)]:
  target=Vector((x+(u-.5)*1.15,y+(u-.5)*.45,z)) if i else Vector((3.2*(1-u),-.7+1.4*u,1.6));cam.location=target+Vector((10,-10,10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span-(.3*u if a<271 else -.5*u);cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('ortho_scale',frame=f)
for owner in [cam,cam.data]:
 for fc in owner.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
(W/'street-camera-plan.json').write_text(json.dumps(shots,indent=2))
S.render.image_settings.file_format='PNG';S.render.film_transparent=False;S.render.use_file_extension=True
S.use_nodes=True;tree=S.node_tree;tree.nodes.clear();rl=tree.nodes.new('CompositorNodeRLayers');gl=tree.nodes.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.threshold=1.8;gl.quality='MEDIUM';gl.size=7;co=tree.nodes.new('CompositorNodeComposite');tree.links.new(rl.outputs['Image'],gl.inputs['Image']);tree.links.new(gl.outputs['Image'],co.inputs['Image'])
S.eevee.shadow_pool_size='1024';S.render.engine='CYCLES';S.cycles.samples=12;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(W/'street-no-graffiti.blend'))
