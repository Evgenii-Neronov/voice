"""Create Fish S2 mixed Q4 from pinned Q8, preserving acoustic decoder and codec."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/'benchmark/native-models.lock.json').read_text())['fish-s2']
source=ROOT/lock['local_file']
target=source.with_name('fish-audio-s2-pro-mixed-q4_k.gguf')
record=ROOT/'benchmark/fish-mixed-q4.lock.json'
def digest(path):
 with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
assert digest(source)==lock['sha256'],'Source hash mismatch'
if target.exists():
 assert record.exists() and digest(target)==json.loads(record.read_text())['sha256'],'Existing derived model is not verified'
 print('Already verified:',target)
else:
 command=[str(ROOT/'vendor/audio-runtime/audiocpp_gguf.exe'),'--input',str(source),'--output',str(target),
  '--type','q4_k','--family','fish_audio']
 for prefix in ['model_weights/fast_*','model_weights/codebook_embeddings*','model_weights/embeddings*','model_weights/norm*','codec_weights*']:
  command+=['--keep-type',prefix+'=orig']
 env=os.environ.copy()
 temporary=ROOT/'.cache/audio.cpp-temp'; temporary.mkdir(parents=True,exist_ok=True)
 env['TEMP']=env['TMP']=str(temporary)
 logfile=ROOT/'results/fish-mixed-q4-conversion.log'
 with logfile.open('w',encoding='utf-8') as log:
  subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 data={'source':lock,'local_file':str(target.relative_to(ROOT)).replace('\\','/'),
  'sha256':digest(target),'bytes':target.stat().st_size,'command':command,
  'recipe':'https://github.com/0xShug0/audio.cpp/blob/1d30ef6ab29df98cf4b6ef38c7dca1d6c99738f6/docs/proposals/fish_audio_quantization_recipe.md',
  'note':'Derived from Q8, not original BF16. Acoustic fast decoder, embeddings, norms and codec retain input precision. Embedded sidecars automatically preserved by audio.cpp 0.9.3.'}
 record.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(data),flush=True)
