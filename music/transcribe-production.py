"""Local CPU ASR with word times; private transcripts stay in ignored work/."""
import argparse,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
os.environ['HF_HUB_OFFLINE']='1'
from faster_whisper import WhisperModel
p=argparse.ArgumentParser(); p.add_argument('files',nargs='+'); p.add_argument('--short-check',action='store_true'); a=p.parse_args()
model=WhisperModel(str(ROOT/'models/asr-whisper-small'),device='cpu',compute_type='int8',cpu_threads=4,num_workers=1,local_files_only=True)
for name in a.files:
 source=ROOT/name
 segments,info=model.transcribe(str(source),language='ru',beam_size=5,word_timestamps=True,vad_filter=not a.short_check,condition_on_previous_text=False,max_new_tokens=128 if a.short_check else None)
 records=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in s.words]} for s in segments]
 target=source.with_suffix('.asr.json'); target.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 print(source.name, json.dumps(records,ensure_ascii=False),flush=True)
