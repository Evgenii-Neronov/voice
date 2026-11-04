"""Validate and locally transcribe a dry MiniMax performance with one Ezhi hook."""
import argparse,json,hashlib,os,sys
from pathlib import Path
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1]; sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser(); p.add_argument('--run-id',required=True); p.add_argument('--work-dir',required=True); a=p.parse_args(); out=R/'results/productions'/a.run_id; w=R/a.work_dir
m=json.loads((out/'manifest.json').read_text(encoding='utf-8')); generation=json.loads((R/'results/music'/a.run_id/'manifest.json').read_text(encoding='utf-8')); timeline=m['timeline']
def sha(path):
 with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
assert m['lyrics_sha256']==generation['source_lyrics_sha256']==sha(R/'Lyrics/lyrics.txt')
x,sr=sf.read(out/'full.wav',always_2d=True); assert sr==44100 and x.shape[1]==2 and np.isfinite(x).all() and np.max(np.abs(x))<1
assert abs(len(x)/sr-generation['audio'][0]['duration'])<.01
assert len(timeline['ezhi_regions'])==1
region=timeline['ezhi_regions'][0]; assert 10<region['start']<region['end']<len(x)/sr
assert region['lyrics']==['Десять свистулек!','Один кубит!','Кто здесь субъект?','Кто кого купит?']
for f in m['audio']: assert sha(out/f['file'])==f['sha256']
checks=[('greeting_ADV',0,6),('verse_ADV',20,30),('hook_Ezhi',max(0,region['start']-.12),region['end']+.12)]
dll=R/'.venvs/qwen/Lib/site-packages/torch/lib'; os.environ['PATH']=str(dll)+os.pathsep+os.environ['PATH']; h=os.add_dll_directory(str(dll))
from faster_whisper import WhisperModel
model=WhisperModel(str(R/'models/asr-whisper-small'),device='cuda',compute_type='float16',local_files_only=True,cpu_threads=4); rows=[]
for name,start,end in checks:
 file=w/(name+'-check.wav'); sf.write(file,x[int(start*sr):int(end*sr)].mean(axis=1),sr)
 segs,_=model.transcribe(str(file),language='ru',beam_size=3,condition_on_previous_text=False,vad_filter=False); text=' '.join(s.text for s in segs); rows.append({'part':name,'start':start,'end':end,'automatic_transcript':text}); print(name,text,flush=True)
result={'numerical_validation_passed':True,'sha256_validation_passed':True,'lyrics_sha256':m['lyrics_sha256'],'duration':len(x)/sr,'ezhi_region_seconds':[region['start'],region['end']],'all_other_vocal':'ADV reference conversion','greeting_voice':'ADV','dry':True,'local_inference':True,'generation_seconds':generation['whole_run_seconds'],'separation_seconds':json.loads((w/'separation.json').read_text())['seconds'],'conversion_seconds':m['conversion']['whole_run_seconds'],'asr_not_ground_truth':True,'human_listening_review':False,'checks':rows,'references':[{'role':role,'sha256':sha(w/'refs'/name)} for role,name in [('ADV','adv.wav'),('Ezhi','ezhi-conversion.wav')]]}
(out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
