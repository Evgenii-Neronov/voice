"""Pin upstream model cards/license revisions; keep verbatim files with ignored models."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
from huggingface_hub import HfApi,hf_hub_download
repos=['fishaudio/s2-pro','fishaudio/drama-3','bosonai/higgs-tts-3-4b','audio-cpp/audio.cpp-gguf','Jmica/Drama-3-GGUF']
out=ROOT/'benchmark/native-sources.lock.json'
previous=json.loads(out.read_text()) if out.exists() else {}
def fetch(repo):
 info=HfApi().model_info(repo,revision=previous.get(repo,{}).get('revision'))
 record={'revision':info.sha,'card_license':getattr(info.card_data,'license',None),'documents':[]}
 for entry in info.siblings:
  name=entry.rfilename
  if '/' not in name and (name.lower().startswith(('license','notice')) or name.lower()=='readme.md'):
   file=Path(hf_hub_download(repo,name,revision=info.sha,local_dir=ROOT/'models/native-metadata'/repo.replace('/','--')))
   record['documents'].append({'file':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'url':f'https://huggingface.co/{repo}/blob/{info.sha}/{name}'})
 return repo,record
with ThreadPoolExecutor(max_workers=3) as pool:
 records=dict(pool.map(fetch,repos))
out.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False,indent=2))
