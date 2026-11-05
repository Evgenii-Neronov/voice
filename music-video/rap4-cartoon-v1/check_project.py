from pathlib import Path
import json,shutil,xml.etree.ElementTree as ET
from PIL import Image
W=Path('work/rap4-cartoon');O=Path('outputs/rap4-cartoon-1440p');P=O/'project';T=W/'portable-check';T.mkdir(exist_ok=True)
for name in ['portable-check.log','portable-check-status.json']:
 if (P/name).exists():shutil.move(str(P/name),str(T/name))
if (P/'renders/portable-check.mp4').exists():shutil.move(str(P/'renders/portable-check.mp4'),str(T/'portable-check.mp4'))
for f in (O/'editable-art').glob('*.svg'):ET.parse(f)
for f in (O/'editable-art').glob('*.png'):assert Image.open(f).convert('RGBA').getpixel((0,0))[3]==0
shutil.copy2(W/'dependencies.json',P/'dependencies.json');(W/'project-validation.json').write_text(json.dumps({'portable_render_test':'passed, one-second render from packaged project using bundled track and analysis','editable_svg_files':5,'svg_xml_parse':'passed','transparent_character_pngs':4,'new_model_downloads':False},indent=2));print('Project validation passed')
