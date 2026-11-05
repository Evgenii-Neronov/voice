"""Original dimensional hip-hop inserts. No flat backdrop images or added typography."""
import bpy,math,random,sys,os
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent
kind=sys.argv[sys.argv.index('--')+1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.render.engine='BLENDER_EEVEE_NEXT';S.eevee.taa_render_samples=16;S.eevee.use_raytracing=True;S.eevee.shadow_pool_size='1024'
S.render.resolution_x=2560;S.render.resolution_y=1440;S.render.resolution_percentage=100;S.render.fps=24
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.025,.038,.065,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.22
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=-.3

def mat(name,c,rough=.5,metal=0,em=0,grain=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes;p=n['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 if grain:
  no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=48;no.inputs['Detail'].default_value=3;bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.18;bu.inputs['Distance'].default_value=.025;m.node_tree.links.new(no.outputs['Fac'],bu.inputs['Height']);m.node_tree.links.new(bu.outputs['Normal'],p.inputs['Normal'])
 return m
def texture(name,base):
 m=mat(name,(.3,.3,.3),.7);n=m.node_tree.nodes;p=n['Principled BSDF'];tc=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeVectorMath');mp.operation='SCALE';mp.inputs[3].default_value=.45;m.node_tree.links.new(tc.outputs['Object'],mp.inputs[0])
 for suff,socket in [('diff','Base Color'),('rough','Roughness')]:
  fn=Path(os.environ.get('ASSET_DIR',str(W.parent/'nyc-boombap/assets')))/f'{base}_{suff}_2k.jpg'
  if fn.exists():
   im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(fn),check_existing=True);im.image.pack();im.projection='BOX';im.projection_blend=.15
   if suff!='diff':im.image.colorspace_settings.name='Non-Color'
   m.node_tree.links.new(mp.outputs[0],im.inputs['Vector']);m.node_tree.links.new(im.outputs['Color'],p.inputs[socket])
 return m
black=mat('Rubber and black enamel',(.018,.024,.03),.38,grain=True);steel=mat('Brushed aluminium',(.35,.42,.46),.29,.8,grain=True);brass=mat('Old brass',(.54,.29,.075),.3,.72);wood=mat('Walnut',(.16,.065,.025),.48,grain=True);gold=mat('Ochre paint',(.85,.48,.055),.6,grain=True);blue=mat('Petrol blue',(.025,.13,.19),.5);cream=mat('Warm paper',(.66,.59,.43),.8,grain=True);clay=mat('Terracotta clay',(.42,.17,.075),.85,grain=True);concrete=texture('Concrete','concrete_wall_006');brick=texture('Brick','red_bricks_04');floor=texture('Asphalt','asphalt_02');lightmat=mat('Warm practical',(.95,.56,.2),.4,em=4);cyan=mat('Cold rack indicators',(.1,.62,.8),.4,em=2)
def box(name,loc,size,ma,bevel=.025,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel:mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if parent:o.parent=parent
 return o
def cyl(name,loc,r,depth,ma,verts=48,rotation=None,parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(ma)
 if rotation:o.rotation_euler=rotation
 if parent:o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 return o
def sphere(name,loc,size,ma,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(ma)
 for p in o.data.polygons:p.use_smooth=True
 if parent:o.parent=parent
 return o
def curve(name,pts,r,ma,parent=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);S.collection.objects.link(o);cu.materials.append(ma)
 if parent:o.parent=parent
 return o
def rod(name,a,b,r,ma,parent=None):return curve(name,[a,b],r,ma,parent)
def ring(name,loc,r,thick,ma,axis='z',parent=None):
 pts=[]
 for i in range(65):
  a=i*math.tau/64;v=(r*math.cos(a),r*math.sin(a),0) if axis=='z' else (r*math.cos(a),0,r*math.sin(a));pts.append(tuple(loc[j]+v[j] for j in range(3)))
 return curve(name,pts,thick,ma,parent)
def empty(name):o=bpy.data.objects.new(name,None);S.collection.objects.link(o);return o
def area(name,loc,target,power,color,size=3):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def speaker(loc,scale=1):
 x,y,z=loc;box('Speaker cabinet',(x,y,z),(1*scale,.65*scale,1.7*scale),black,.045)
 for dz,r in [(-.35,.34),(.5,.16)]:
  cyl('Speaker cone',(x,y-.34*scale,z+dz*scale),r*scale,.035,black,rotation=(math.pi/2,0,0));ring('Speaker rim',(x,y-.37*scale,z+dz*scale),r*scale,.015*scale,steel,'y');sphere('Dust cap',(x,y-.40*scale,z+dz*scale),(r*.33*scale,.07*scale,r*.33*scale),black)
def graffiti_wall(y,x0=0,z0=2,width=3):
 rng=random.Random(55)
 for j in range(9):
  pts=[]
  for i in range(90):
   u=i/89;pts.append((x0+width*(u-.5)+.23*math.sin(u*math.tau*2+j),y,z0+.48*math.sin(u*math.tau*(1+j%2)+j*.5)+j*.09))
  o=curve('Growing painted contour',pts,.025 if j%2 else .045,[gold,blue,cream][j%3]);o['grow']=True
def deck(x,y,z):
 box('Turntable plinth',(x,y,z),(1.9,1.45,.22),black,.06);box('Metal deck plate',(x,y,z+.125),(1.82,1.38,.025),steel,.025)
 spin=empty('Vinyl spindle');spin.location=(x-.17,y,z+.17)
 cyl('Platter',(0,0,0),.63,.035,steel,parent=spin);cyl('Record',(0,0,.024),.6,.014,black,parent=spin)
 for r in [.22+i*.011 for i in range(34)]:ring('Record groove',(0,0,.033),r,.0011,steel,parent=spin)
 cyl('Blank ochre label',(0,0,.035),.16,.003,gold,parent=spin);cyl('Spindle',(0,0,.05),.012,.04,steel,parent=spin)
 rod('Record highlight',(.18,.0,.035),(.55,.1,.035),.005,black,spin)
 cyl('Tonearm base',(x+.64,y+.43,z+.19),.09,.1,black);curve('S tonearm',[(x+.64,y+.43,z+.26),(x+.65,y+.1,z+.29),(x+.49,y-.16,z+.29),(x+.25,y-.29,z+.24)],.018,steel);box('Pickup cartridge',(x+.25,y-.29,z+.21),(.13,.08,.045),black,.01)
 box('Start button',(x-.76,y-.52,z+.15),(.18,.12,.02),gold,.01)
 for i in range(7):box('Pitch slider marks',(x+.77,y-.41+i*.08,z+.15),(.04,.009,.003),cream,0)
 box('Pitch fader',(x+.70,y-.1,z+.18),(.09,.09,.04),black,.008)
 return spin

if kind=='studio':
 box('Studio floor',(0,0,-.15),(12,12,.3),wood);box('Rear brick wall',(0,3.6,2.3),(12,.3,4.6),brick);box('Side wall',(-4.7,0,2.3),(.25,8,4.6),concrete)
 box('Worktable top',(0,0,1.1),(4.4,2,.15),wood,.06)
 for x in [-1.9,1.9]:
  for y in [-.8,.8]:box('Table leg',(x,y,.5),(.09,.09,1),steel,.01)
 deck(-.9,0,1.25);deck(1.15,.1,1.25)
 box('Mixer',(.1,-.26,1.32),(.45,.85,.18),black,.025)
 for x in [-.04,.10,.24]:
  for y in [-.5,-.3,-.1,.1]:cyl('Mixer knob',(x,y,1.44),.035,.04,steel,16)
 for x in [-3,3]:speaker((x,2.3,1.15),1.15)
 for x in [-2.8,0,2.8]:
  for z in [.4,1.2,2.0]:
   box('Record shelf',(x,3.15,z),(2.2,.65,.09),wood)
   for j in range(15):
    o=box('Unlettered record sleeve',(x-.95+j*.13,3.18,z+.36),(.06,.48,.63),[black,cream,blue,wood][j%4],.003);o.rotation_euler[1]=.02*math.sin(j)
 for x in [-1.7,1.7]:
  cyl('Pendant shade',(x,.2,3.25),.33,.13,black);cyl('Pendant diffuser',(x,.2,3.17),.27,.015,lightmat);rod('Cable',(x,.2,3.3),(x,.2,4.5),.008,black)
 area('Warm overhead',(-1,-.5,3.1),(0,0,1),450,(1,.65,.35),2);area('Blue window',(4,-1,3),(0,0,1),300,(.35,.55,1),3);area('Soft front',(-1,-4,2),(0,1,1),180,(1,.8,.6),3)
 graffiti_wall(3.42,0,3.05,3.6)
elif kind=='metro':
 box('Platform',(0,-1,-.25),(32,5,.5),concrete);box('Track pit',(0,4,-.65),(34,6,.2),black);box('Opposite tiled wall',(0,7,2),(35,.3,5),concrete)
 for y in [3.4,4.7]:rod('Rail',(-20,y,-.3),(20,y,-.3),.045,steel)
 for x in range(-16,17):box('Rail sleeper',(x,4,-.43),(.15,2.2,.13),wood,.01)
 box('Platform warning strip',(0,1.2,.02),(32,.38,.035),gold,.008)
 for x in range(-14,15,3):
  box('Riveted steel column',(x,-.1,2),(.23,.35,4),blue);box('Column foot',(x,-.1,.15),(.5,.6,.3),steel)
  for z in [.6,1.5,2.4,3.3]:sphere('Rivet',(x,-.29,z),(.025,.015,.025),steel)
  box('Fluorescent strip',(x,-1.6,3.9),(1.8,.12,.045),lightmat,.008)
 for x in [-9,-3,3,9]:area('Platform lamp',(x,-1.1,3.7),(x,1,0),230,(.67,.8,1),2)
 train=empty('Train carriage')
 box('Carriage body',(0,4.3,1.6),(13,2.25,3.0),steel,.16,train);box('Train ochre stripe',(0,3.155,1.05),(12.8,.015,.13),gold,.01,train)
 for x in [-5.2,-3.1,-1.0,1.1,3.2,5.3]:
  box('Dark window frame',(x,3.14,2.1),(1.65,.045,1.1),black,.1,train);box('Blue glass',(x,3.108,2.1),(1.45,.018,.9),blue,.075,train)
  box('Window reflected light',(x-.35,3.09,2.24),(.1,.008,.6),steel,.01,train)
 for x in [-2.1,2.1]:
  for dx in [-.36,.36]:box('Carriage door',(x+dx,3.1,1.45),(.68,.04,2.35),steel,.02,train);box('Door window',(x+dx,3.06,2.05),(.42,.02,.73),black,.05,train)
 for x in [-4,4]:
  for y in [3.6,5]:cyl('Train wheel',(x,y,.1),.42,.15,black,rotation=(math.pi/2,0,0),parent=train)
 area('Train bounce',(0,1.8,3.2),(0,4,1),550,(1,.68,.38),7)
 graffiti_wall(6.82,0,2.2,6)
elif kind=='roof':
 box('Rooftop',(0,0,-.18),(16,14,.35),floor);box('Parapet',(0,5.7,.6),(16,.3,1.2),brick);box('Parapet cap',(0,5.7,1.25),(16,.43,.12),concrete)
 for x in [-6,6]:
  for y in [-5,-1,3]:rod('Rail post',(x,y,0),(x,y,1.1),.03,steel)
  rod('Rail',(x,-6,1.1),(x,5,1.1),.03,steel)
 box('Ventilation duct',(-3,3,.65),(2.6,1.5,1.3),steel,.08)
 for i in range(12):box('Vent slat',(-3.9+i*.16,2.22,.65),(.04,.03,.95),black,.005)
 for x in [3,4.4]:
  for y in [2.5,3.9]:rod('Water tower leg',(x,y,0),(x,y,3.5),.06,steel)
 cyl('Water tank',(3.7,3.2,3.6),1.25,2.7,wood,64)
 for z in [2.35,3.1,4.0,4.85]:ring('Tank steel band',(3.7,3.2,z),1.26,.025,steel)
 for i in range(28):
  a=i*math.tau/28;rod('Tank stave',(3.7+1.26*math.cos(a),3.2+1.26*math.sin(a),2.3),(3.7+1.26*math.cos(a),3.2+1.26*math.sin(a),4.9),.012,black)
 rng=random.Random(99)
 for i in range(28):
  x=rng.uniform(-35,35);y=rng.uniform(14,35);h=rng.uniform(3,14);box('Distant building',(x,y,h/2-1),(rng.uniform(2,4),3,h),blue,.02)
  for xx in [-.6,.6]:
   for z in range(1,int(h),2):
    if rng.random()<.6:box('Distant window',(x+xx,y-1.52,z-1),(.35,.01,.6),lightmat,0)
 cube=empty('Floating wire cube');cube.location=(0,1.5,2)
 for a in range(8):
  pa=[(-1 if a&(1<<j)==0 else 1)*.65 for j in range(3)]
  for j in range(3):
   b=a^(1<<j)
   if a<b:pb=[(-1 if b&(1<<k)==0 else 1)*.65 for k in range(3)];rod('Cube edge',pa,pb,.025,brass,cube)
 speaker((-3,-1,.65),.7)
 area('Warm roof practical',(-4,-2,4),(0,1,1),650,(1,.55,.25),3);area('Sky cool',(3,4,8),(0,0,0),900,(.25,.42,1),8)
 S.world.node_tree.nodes['Background'].inputs[0].default_value=(.065,.10,.21,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.45
elif kind=='lab':
 box('Industrial floor',(0,0,-.15),(14,14,.3),concrete);box('Warehouse wall',(0,4,2.4),(14,.3,4.8),brick)
 for x in [-5,-2.5,0,2.5,5]:box('Steel upright',(x,3.8,2.4),(.13,.2,4.8),steel);rod('Cross brace',(x,3.68,0),(x+2.5,3.68,4.7),.03,steel)
 box('Clay workbench',(0,0,.95),(4.4,1.8,.16),wood,.04)
 for x in [-1.9,1.9]:
  for y in [-.7,.7]:box('Bench leg',(x,y,.45),(.12,.12,.9),steel)
 for i in range(10):
  x=-1.5+(i%5)*.64;y=-.38+(i//5)*.68;sphere('Clay whistle body',(x,y,1.16),(.25,.16,.15),clay);rod('Whistle mouthpiece',(x+.12,y,1.15),(x+.37,y,1.20),.055,clay);sphere('Whistle opening',(x-.05,y-.10,1.29),(.035,.025,.01),black)
 for x in [3.0,4.25]:
  box('Computing rack',(x,2.5,1.25),(1.05,.85,2.5),black,.05)
  for z in [.25+i*.27 for i in range(8)]:
   box('Rack module',(x,2.055,z),(.9,.035,.19),steel,.01)
   for xx in [-.35,-.28,-.21]:box('Rack LED',(x+xx,2.028,z),(.025,.012,.025),cyan,.001)
   for j in range(9):box('Cooling slit',(x-.08+j*.045,2.028,z),(.01,.01,.12),black,0)
 speaker((-3.2,2.5,.9),1)
 for x in [-2,2]:rod('Overhead pipe',(x,-4,3.9),(x,4,3.9),.07,steel)
 graffiti_wall(3.81,-1,2.5,4.4)
 area('Amber work light',(-2,-1,3.3),(0,0,1),450,(1,.53,.22),2);area('Rack blue',(4,0,3),(3,2,1),400,(.20,.53,1),2);area('Front bounce',(0,-4,2),(0,1,1),120,(.55,.65,1),4)
else:raise ValueError(kind)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Directed camera';cam.data.lens=42;cam.data.clip_end=200;S.camera=cam
S.use_nodes=True;n=S.node_tree.nodes;n.clear();rl=n.new('CompositorNodeRLayers');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.threshold=2;gl.quality='LOW';co=n.new('CompositorNodeComposite');S.node_tree.links.new(rl.outputs['Image'],gl.inputs['Image']);S.node_tree.links.new(gl.outputs['Image'],co.inputs['Image'])
(W/'sets').mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(W/'sets'/f'{kind}.blend'))
