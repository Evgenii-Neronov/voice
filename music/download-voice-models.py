"""Pinned, verified local voice conversion GGUF packages; no hosted generation."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,time
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
from huggingface_hub import HfApi,hf_hub_download
repo='audio-cpp/audio.cpp-gguf'
revision='fd2fe4c3195bc410f8b817bf7c7519fd822686fb'
files=['BS-RoFormer-ep368-GGUF/bs-roformer-ep368-q8_0.gguf','SeedVC-MLX-GGUF/seed-vc-mlx-q8_0.gguf']
info=HfApi().model_info(repo,revision=revision,files_metadata=True)
root=ROOT/'models/voice-production'; root.mkdir(parents=True,exist_ok=True)
records=[]
for name in files:
 meta=next(x for x in info.siblings if x.rfilename==name)
 records.append({'file':name,'bytes':meta.size,'sha256':getattr(meta.lfs,'sha256',None)})
lock={'repo_id':repo,'revision':info.sha,'runtime_lock':'benchmark/native-runtime.lock.json','files':records}
lockfile=ROOT/'music/voice-models.lock.json'
lockfile.write_text(json.dumps(lock,indent=2)+'\n',encoding='utf-8')
def fetch(item):
 target=root/item['file']; target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():
  if item['bytes']<16*1024**2:
   hf_hub_download(repo,item['file'],revision=revision,local_dir=root)
  else:
   parts=ROOT/'.cache/music-parts'/item['file'].replace('/','_'); parts.mkdir(parents=True,exist_ok=True)
   size=32*1024**2
   def chunk(start):
    end=min(start+size,item['bytes'])-1; path=parts/str(start)
    if path.exists() and path.stat().st_size==end-start+1: return path
    url=f"https://huggingface.co/{repo}/resolve/{revision}/{item['file']}?download=true&range_start={start}"
    for attempt in range(5):
     try:
      r=requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=(20,90)); r.raise_for_status()
      assert r.status_code==206 and r.headers.get('content-range')==f"bytes {start}-{end}/{item['bytes']}"
      assert len(r.content)==end-start+1
      path.write_bytes(r.content); return path
     except Exception:
      if attempt==4: raise
      time.sleep(2**attempt)
   with ThreadPoolExecutor(max_workers=8) as pool: paths=list(pool.map(chunk,range(0,item['bytes'],size)))
   temporary=target.with_suffix('.partial'); digest=hashlib.sha256()
   with temporary.open('wb') as out:
    for part in paths:
     payload=part.read_bytes(); digest.update(payload); out.write(payload)
   assert digest.hexdigest()==item['sha256']
   temporary.replace(target)
   for part in paths: part.unlink()
 with target.open('rb') as stream: actual=hashlib.file_digest(stream,'sha256').hexdigest()
 if item['sha256']: assert actual==item['sha256'],target
 item['sha256']=actual
 print('Verified',item['file'],item['bytes'],flush=True)
with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(fetch,records))
lockfile.write_text(json.dumps(lock,indent=2)+'\n',encoding='utf-8')
print('Complete',root,flush=True)
