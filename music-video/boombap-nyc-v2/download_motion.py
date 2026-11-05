from pathlib import Path
import json,urllib.request,concurrent.futures
w=Path('work/nyc-boombap-v2');(w/'assets').mkdir(exist_ok=True)
t=json.loads(Path('work/nyc-boombap/rocketbox-tree.json').read_text(encoding='utf-8-sig'))['tree']
names=['m_gestic_listen_relaxed_01.max.fbx','m_idle_neutral_02.max.fbx','m_walk_cool_01.max.fbx','m_walk_neutral_01.max.fbx']
def get(o):
 p=o['path'];d=w/'assets'/Path(p).name
 if not d.exists():urllib.request.urlretrieve('https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/'+p,d)
 print(d,flush=True)
with concurrent.futures.ThreadPoolExecutor(4) as ex:list(ex.map(get,[o for o in t if Path(o['path']).name in names]))
