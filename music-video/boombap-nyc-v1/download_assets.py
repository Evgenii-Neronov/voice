from pathlib import Path
import json,urllib.request,concurrent.futures
w=Path(__file__).resolve().parent;a=w/'assets';tree=json.loads((w/'rocketbox-tree.json').read_text(encoding='utf-8-sig'))['tree'];jobs=[]
for o in tree:
 p=o['path']
 if any(f'/Male_Adult_{i:02d}/' in p for i in [17,18,12,4]) and (p.endswith('_facial.fbx') or p.endswith('_color.tga') or p.endswith('_normal.tga')):
  dst=a/'rocketbox'/p;dst.parent.mkdir(parents=True,exist_ok=True);jobs.append(('https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/'+p,dst))
 if p.endswith('.fbx') and any(n in p for n in ['m_gestic_talk_cool.max','m_gestic_talk_excited_01.max','m_gestic_talk_relaxed_01.max']):
  jobs.append(('https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/'+p,a/Path(p).name))
jobs.append(('https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/LICENSE.md',a/'ROCKETBOX-LICENSE.md'))
for asset in ['red_bricks_04','asphalt_02','concrete_wall_006']:
 try:
  d=json.load(urllib.request.urlopen('https://api.polyhaven.com/files/'+asset));(a/(asset+'-files.json')).write_text(json.dumps(d))
  for kind in ['diff','nor_gl','rough']:
   f=d[kind]['2k']['jpg'];jobs.append((f['url'],a/Path(f['url']).name))
 except Exception as e:print(asset,e,flush=True)
def get(job):
 url,p=job
 if not p.exists():urllib.request.urlretrieve(url,p)
 print(p.name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:list(ex.map(get,jobs))
(w/'download-manifest.json').write_text(json.dumps([{'url':u,'path':str(p)} for u,p in jobs],indent=2))
