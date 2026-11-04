"""Create the requested introduction locally, using only the user's voice reference."""
import hashlib,json,subprocess,time
from pathlib import Path
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[1]; work=ROOT/'work/adv-ezhi'
samples,sr=sf.read(work/'refs/adv.wav')
segments=json.loads((work/'refs/adv.asr.json').read_text(encoding='utf-8'))
# Two clearly transcribed phrases; exclude uncertain words at the start of the reference.
ranges=[(3.94,7.32),(14.0,16.60)]
reference=np.concatenate([part for i,(s,e) in enumerate(ranges) for part in ([np.zeros(int(.18*sr))] if i else [])+[samples[int(s*sr):int(e*sr)]]])
ref=work/'refs/adv-intro-reference.wav'; sf.write(ref,reference,sr)
words=[w['word'] for segment in segments for w in segment['words'] if any(w['start']>=s and w['end']<=e for s,e in ranges)]
reference_text=''.join(words).strip()
text='[confident] Йо, это рэп-трек, с вами Эй Ди Ви, ака Адвентус Девотус!'
command=[str(ROOT/'vendor/audio-runtime/audiocpp_cli.exe'),'--task','clon','--family','fish_audio','--model',str(ROOT/'models/native/Fish-Audio-S2-Pro-GGUF/fish-audio-s2-pro-q8_0.gguf'),'--backend','cuda','--threads','8','--text',text,'--voice-ref',str(ref),'--reference-text',reference_text,'--seed','20261104','--max-tokens','512','--out',str(work/'greeting.wav'),'--metrics','--load-progress','0']
(work/'greeting-command.private.json').write_text(json.dumps(command,ensure_ascii=False,indent=2),encoding='utf-8')
start=time.perf_counter()
with (work/'greeting.log').open('w',encoding='utf-8') as log: subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
m={'requested_text':'Йо, это рэп трек, с вами ADV aka Adventus Devotus','spoken_text':text,'model':'Fish S2 Pro Q8','reference_ranges_seconds':ranges,'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'seconds':time.perf_counter()-start,'local_inference':True}
(work/'greeting.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(m,ensure_ascii=False))
