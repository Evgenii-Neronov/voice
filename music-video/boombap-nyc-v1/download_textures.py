from pathlib import Path
import urllib.request,concurrent.futures
p=Path(__file__).resolve().parent/'assets'
def get(args):
 a,k=args;url=f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/{a}/{a}_{k}_2k.jpg';dst=p/f'{a}_{k}_2k.jpg'
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  dst.write_bytes(urllib.request.urlopen(req).read());print(dst.name,flush=True)
 except Exception as e:print(url,e,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:list(ex.map(get,[(a,k) for a in ['red_bricks_04','asphalt_02','concrete_wall_006'] for k in ['diff','nor_gl','rough']]))
