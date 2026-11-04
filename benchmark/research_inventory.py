"""Capture metadata for shortlisted models without downloading their weights."""
import datetime
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
from huggingface_hub import HfApi
ids=['fishaudio/s2-pro','fishaudio/drama-3','bosonai/higgs-tts-3-4b','FunAudioLLM/Fun-CosyVoice3-0.5B-2512','k2-fsa/OmniVoice','Plachta/Seed-VC']
result={'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'models':[]}
api=HfApi()
for repo in ids:
    row={'repo_id':repo,'url':'https://huggingface.co/'+repo,'local_inference':'not_tested'}
    try:
        info=api.model_info(repo,files_metadata=True)
        row.update(revision=info.sha,license=getattr(info.card_data,'license',None),repository_bytes=sum(x.size or 0 for x in info.siblings),files=[{'name':x.rfilename,'bytes':x.size} for x in info.siblings])
    except Exception as exc:
        row['metadata_error']=str(exc)
    result['models'].append(row)
(ROOT/'results/research-models.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print([(x['repo_id'],x.get('revision'),x.get('repository_bytes')) for x in result['models']])
