"""Pinned Russian F5 and Vocos downloads, range-resumable and SHA256 checked."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,time
from pathlib import Path
import requests
from huggingface_hub import HfApi,hf_hub_download
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
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

locks=[]
for repo,revision,folder,files in [('TVI/f5-tts-ru-accent','e2996d89da1d17a09ca4be7fb06075968c228af7','f5-ru',['model_last.safetensors','vocab.txt','README.md']),('charactr/vocos-mel-24khz','0feb3fdd929bcd6649e0e7c5a688cf7dd012ef21','vocos-24k',['config.yaml','pytorch_model.bin','README.md'])]:
 root=ROOT/'models'/folder; root.mkdir(parents=True,exist_ok=True)
 info=HfApi().model_info(repo,revision=revision,files_metadata=True); records=[]
 for name in files:
  meta=next(x for x in info.siblings if x.rfilename==name); records.append({'file':name,'bytes':meta.size,'sha256':getattr(meta.lfs,'sha256',None)})
 with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(fetch,records))
 locks.append({'repo':repo,'revision':revision,'folder':str(root),'files':records})
 (ROOT/'music/editable/f5.lock.json').write_text(json.dumps(locks,indent=2),encoding='utf-8')
