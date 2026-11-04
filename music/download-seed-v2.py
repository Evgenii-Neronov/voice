"""Download pinned Seed-VC V2 dependencies inside gitignored models/."""
from pathlib import Path
import json,hashlib
from huggingface_hub import HfApi,hf_hub_download
R=Path(__file__).resolve().parents[1]; root=R/'models/seed-v2';root.mkdir(exist_ok=True);api=HfApi();rows=[]
spec={'Plachta/Seed-VC':['v2/cfm_small.pth','v2/ar_base.pth'],'Plachta/ASTRAL-quantization':['bsq32/bsq32_light.pth','bsq2048/bsq2048_light.pth'],'funasr/campplus':['campplus_cn_common.bin'],'nvidia/bigvgan_v2_22khz_80band_256x':['config.json','bigvgan_generator.pt'],'facebook/hubert-large-ll60k':['config.json','preprocessor_config.json','pytorch_model.bin'],'openai/whisper-small':['config.json','tokenizer.json','tokenizer_config.json','vocab.json','merges.txt','normalizer.json','added_tokens.json','special_tokens_map.json']}
lock=R/'music/seed-v2.lock.json';old=json.loads(lock.read_text()) if lock.exists() else None
for repo,names in spec.items():
 info=api.model_info(repo);rev=next((x['revision'] for x in old['models'] if x['repo']==repo),info.sha) if old else info.sha
 files=[];dest=root/repo.replace('/','--')
 for name in names:
  path=Path(hf_hub_download(repo,name,revision=rev,local_dir=dest));
  with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  files.append({'file':name,'bytes':path.stat().st_size,'sha256':digest});print(repo,name,path.stat().st_size,flush=True)
 rows.append({'repo':repo,'revision':rev,'license_metadata':getattr(info.card_data,'license',None),'local_dir':str(dest.relative_to(R)),'files':files})
 lock.write_text(json.dumps({'vendor_commit':'51383efd921027683c89e5348211d93ff12ac2a8','models':rows},indent=2),encoding='utf-8')
