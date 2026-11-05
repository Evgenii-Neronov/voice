from pathlib import Path
import json,urllib.request
w=Path('work/nyc-boombap-v2');m=Path('I:/VOICE/voice/models/lipsync/wav2vec2-espeak');m.mkdir(parents=True,exist_ok=True)
base='https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft/resolve/main/'
for f in ['config.json','preprocessor_config.json','vocab.json','pytorch_model.bin','README.md']:
 p=m/f
 if not p.exists():
  print('Downloading',f,flush=True);urllib.request.urlretrieve(base+f,p)
 print(f,p.stat().st_size,flush=True)
