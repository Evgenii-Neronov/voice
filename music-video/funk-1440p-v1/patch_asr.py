import os,json
dll_path=r'I:\VOICE\voice\.venvs\qwen\Lib\site-packages\torch\lib'
dll_handle=os.add_dll_directory(dll_path)
os.environ['PATH']=dll_path+os.pathsep+os.environ['PATH']
import soundfile as sf
from faster_whisper import WhisperModel
p=r'I:\VOICE\voice\work\minimax-trio\funk-01\stems\vocals.wav'
a,sr=sf.read(p); a=a[int(53*sr):int(87*sr)]
sf.write('work/funk-video/gap.wav',a,sr)
m=WhisperModel(r'I:\VOICE\voice\models\asr-whisper-small',device='cuda',compute_type='float16')
segs,info=m.transcribe('work/funk-video/gap.wav',language='ru',word_timestamps=True,vad_filter=False,beam_size=5,initial_prompt='Многополярная вечность. Десять свистулек — квантовый компьютер. Денежного обмена нет — а эквивалент есть. Dasein, Hyperstition, ретрокаузальность.')
r=[]
for s in segs:
 r.append({'start':s.start+53,'end':s.end+53,'text':s.text,'words':[{'start':w.start+53,'end':w.end+53,'word':w.word} for w in s.words]})
json.dump(r,open('work/funk-video/gap-transcript.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('patched segments',len(r))
