import bpy,json
from pathlib import Path
W=Path(__file__).resolve().parent;S=bpy.context.scene;m=bpy.data.objects['Passerby portrait approximation'];bpy.context.view_layer.update();vs=[m.matrix_world@v.co for v in m.data.vertices];h=max(v.z for v in vs)-min(v.z for v in vs);print('REST_HEIGHT',h,'scale',list(m.parent.parent.scale));(W/'passerby-height.json').write_text(json.dumps({'rest_body_height_m':h,'target_m':1.83,'scale_multiplier':1.83/h}))
