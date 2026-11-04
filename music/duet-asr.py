"""GPU-local word timestamps for a musical duet; no uploaded audio."""
import argparse,json,os,sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface'); os.environ['HF_HUB_OFFLINE']='1'
dll=ROOT/'.venvs/qwen/Lib/site-packages/torch/lib'
os.environ['PATH']=str(dll)+os.pathsep+os.environ['PATH']
handle=os.add_dll_directory(str(dll))
from faster_whisper import WhisperModel
p=argparse.ArgumentParser(); p.add_argument('variants',nargs='+'); a=p.parse_args()
model=WhisperModel(str(ROOT/'models/asr-whisper-small'),device='cuda',compute_type='float16',cpu_threads=4,num_workers=1,local_files_only=True)
for variant in a.variants:
 work=ROOT/'work/duets'/variant
 segments,info=model.transcribe(str(work/'stems/vocals.wav'),language='ru',beam_size=5,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
 rows=[]
 for s in segments:
  rows.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words]})
  (work/'transcript.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
  print(variant,round(s.start,2),round(s.end,2),s.text,flush=True)
 (work/'asr-complete.json').write_text(json.dumps({'device':'cuda','model':'faster-whisper-small','segments':len(rows)}),encoding='utf-8')
