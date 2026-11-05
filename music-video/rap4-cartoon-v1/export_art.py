from pathlib import Path
import skia
import art
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/rap4-cartoon-1440p';D=O/'editable-art';D.mkdir(exist_ok=True)
def svg_export(name,w,h,fn):
 stream=skia.FILEWStream(str(D/name));c=skia.SVGCanvas.Make(skia.Rect.MakeWH(w,h),stream,skia.SVGCanvas.kConvertTextToPaths_Flag);fn(c);del c;stream.flush()
svg_export('brownstone-background.svg',2560,1440,lambda c:art.background(c))
for kind in ['lead','hood','blue','ezhi']:
 def draw(c,k=kind):art.person(c,k,320,750,1,258 if k=='ezhi' else 12,2,10,.3,k in ['lead','ezhi'])
 svg_export(kind+'.svg',640,800,draw)
 s=skia.Surface(640,800);draw(s.getCanvas());s.makeImageSnapshot().save(str(D/(kind+'.png')),skia.kPNG)
print('Editable SVG and PNG assets exported')
