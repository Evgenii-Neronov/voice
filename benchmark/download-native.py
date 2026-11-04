"""Download only the pinned GGUFs selected for the 16GB comparison."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
import hashlib
import time
import requests
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
from huggingface_hub import HfApi, hf_hub_download
SELECTION={
 'fish-s2':('audio-cpp/audio.cpp-gguf','Fish-Audio-S2-Pro-GGUF/fish-audio-s2-pro-q8_0.gguf','Q8_0'),
 'higgs3':('audio-cpp/audio.cpp-gguf','Higgs-Audio-v3-TTS-4B-GGUF/higgs-audio-v3-tts-4b-q8_0.gguf','Q8_0'),
 'drama3':('Jmica/Drama-3-GGUF','drama-3-backbone-8bit-experts-Q2_K.gguf','Q2_K experts, Q8_0 backbone, FP16 audio tower and codec')}
p=argparse.ArgumentParser()
p.add_argument('models',nargs='+',choices=SELECTION)
p.add_argument('--ranged',action='store_true',help='Resumable 32MiB HTTP ranges')
p.add_argument('--workers',type=int,default=8)
a=p.parse_args()
lock_path=ROOT/'benchmark/native-models.lock.json'
lock=json.loads(lock_path.read_text(encoding='utf-8')) if lock_path.exists() else {}
for name in a.models:
 if name not in lock:
  repo,file,precision=SELECTION[name]
  info=HfApi().model_info(repo,files_metadata=True)
  meta=next(x for x in info.siblings if x.rfilename==file)
  lock[name]={'repo_id':repo,'revision':info.sha,'file':file,'bytes':meta.size,'sha256':getattr(meta.lfs,'sha256',None),'precision':precision,'local_file':'models/native/'+file}
lock_path.write_text(json.dumps(lock,indent=2),encoding='utf-8')
def download(name):
 item=lock[name]
 print('Downloading',name,item,flush=True)
 target=ROOT/item['local_file']
 if a.ranged and not target.exists():
  parts=ROOT/'.cache/native-parts'/name
  parts.mkdir(parents=True,exist_ok=True)
  size=32*1024*1024
  def part(start):
   end=min(start+size,item['bytes'])-1
   path=parts/str(start)
   if path.exists() and path.stat().st_size==end-start+1: return path
   url=f"https://huggingface.co/{item['repo_id']}/resolve/{item['revision']}/{item['file']}?download=true&range_start={start}"
   for attempt in range(5):
    try:
     r=requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=(20,90))
     r.raise_for_status()
     assert r.status_code==206 and r.headers.get('content-range')==f"bytes {start}-{end}/{item['bytes']}"
     assert len(r.content)==end-start+1
     path.write_bytes(r.content)
     return path
    except Exception:
     if attempt==4: raise
     time.sleep(2**attempt)
  with ThreadPoolExecutor(max_workers=a.workers) as chunks:
   paths=list(chunks.map(part,range(0,item['bytes'],size)))
  target.parent.mkdir(parents=True,exist_ok=True)
  temporary=target.with_suffix('.partial')
  digest=hashlib.sha256()
  with temporary.open('wb') as output:
   for path in paths:
    payload=path.read_bytes(); digest.update(payload); output.write(payload)
  assert digest.hexdigest()==item['sha256'],'SHA256 mismatch'
  temporary.replace(target)
  for path in paths: path.unlink()
 elif not target.exists():
  hf_hub_download(item['repo_id'],filename=item['file'],revision=item['revision'],local_dir=ROOT/'models/native')
 with target.open('rb') as source:
  assert hashlib.file_digest(source,'sha256').hexdigest()==item['sha256'],'SHA256 mismatch'
 print('Finished',name,flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:
 list(pool.map(download,a.models))
