import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.environ['HF_HOME'] = str(ROOT / '.cache/huggingface')
from huggingface_hub import snapshot_download
lock = {'repo_id':'ACE-Step/Ace-Step1.5','revision':'19671f406d603126926c1b7e2adc169acbcade22','license':'mit','source_revision':'ca1e85fe9430179831e6bc6be790c332190a3866','patterns':['acestep-v15-turbo/*','vae/*','Qwen3-Embedding-0.6B/*','README.md']}
(ROOT/'benchmark/ace.lock.json').write_text(json.dumps(lock, indent=2),encoding='utf-8')
snapshot_download(lock['repo_id'],revision=lock['revision'],local_dir=ROOT/'models/ace',allow_patterns=lock['patterns'],max_workers=3)
