import bpy,sys
from mathutils import Vector
from pathlib import Path
p=Path(bpy.data.filepath);kind=p.stem
poses={'studio':((4,-5,3.7),(0,0,1.3),43),'roof':((-4,-6,2.4),(0,1.6,2),38),'metro':((-7,-3,1.8),(-3,3.5,1.7),35),'lab':((4,-5,2.8),(.6,.8,1.2),43)}
a,b,lens=poses[kind];cam=bpy.context.scene.camera;cam.location=a;cam.rotation_euler=(Vector(b)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;bpy.ops.wm.save_as_mainfile(filepath=str(p))
