from pathlib import Path
import json,urllib.request,concurrent.futures
w=Path('work/nyc-boombap-v2');t=json.loads(Path('work/nyc-boombap/rocketbox-tree.json').read_text(encoding='utf-8-sig'))['tree']
def get(o):
 p=o['path'];d=w/'assets/rocketbox'/p;d.parent.mkdir(parents=True,exist_ok=True)
 if not d.exists():urllib.request.urlretrieve('https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/'+p,d)
 print(d.name,flush=True)
with concurrent.futures.ThreadPoolExecutor(5) as ex:list(ex.map(get,[o for o in t if '/Male_Adult_08/' in o['path'] and (o['path'].endswith('_facial.fbx') or o['path'].endswith('_color.tga') or o['path'].endswith('_normal.tga'))]))
