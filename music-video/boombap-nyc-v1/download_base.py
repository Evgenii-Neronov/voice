from pathlib import Path
import urllib.request,json,concurrent.futures,zipfile
w=Path(__file__).resolve().parent;a=w/'assets';a.mkdir(exist_ok=True)
def get(url,p):
 if p.exists():return
 urllib.request.urlretrieve(url,p)
 print('downloaded',p.name,flush=True)
jobs=[]
for i in range(1,22):
 name=f'Male_Adult_{i:02d}'
 jobs.append((f'https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/Assets/Avatars/Adults/{name}/{name}.png',a/f'{name}.png'))
jobs.append(('https://download.blender.org/release/Blender4.5/blender-4.5.9-windows-x64.zip',w/'blender.zip'))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for _ in ex.map(lambda args:get(*args),jobs):pass
with zipfile.ZipFile(w/'blender.zip') as z:z.extractall(w/'tools')
print('BLENDER READY',flush=True)
