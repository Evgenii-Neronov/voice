from pathlib import Path
import os,json,numpy as np,subprocess
W=Path(__file__).resolve().parent
dll=Path('I:/VOICE/voice/.venvs/qwen/Lib/site-packages/torch/lib');os.environ['PATH']=str(dll)+os.pathsep+os.environ['PATH'];h=os.add_dll_directory(str(dll))
from faster_whisper import WhisperModel
x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i','I:/VOICE/voice/work/rap4-dialogue-final/01/stems/vocals.wav','-f','f32le','-ac','1','-ar','16000','-']),np.float32)
m=WhisperModel('I:/VOICE/voice/models/asr-whisper-small',device='cuda',compute_type='float16',local_files_only=True)
rows=[]
for a in range(0,274,18):
 lo=max(0,a-3);hi=min(len(x)/16000,a+21)
 segs,_=m.transcribe(x[int(lo*16000):int(hi*16000)],language='ru',beam_size=5,word_timestamps=True,condition_on_previous_text=False,vad_filter=False)
 for s in segs:
  for w in s.words:
   if a<=lo+(w.start+w.end)/2<min(a+18,len(x)/16000):rows.append({'start':lo+w.start,'end':lo+w.end,'word':w.word,'probability':w.probability})
 (W/'fresh-words.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('ASR',a,flush=True)
