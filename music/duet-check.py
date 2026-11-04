"""Check short independent excerpts; keep private diagnostics under ignored work."""
import json,os,sys
from pathlib import Path
import soundfile as sf
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
dll=ROOT/'.venvs/qwen/Lib/site-packages/torch/lib'; os.environ['PATH']=str(dll)+os.pathsep+os.environ['PATH']; handle=os.add_dll_directory(str(dll))
from faster_whisper import WhisperModel
model=WhisperModel(str(ROOT/'models/asr-whisper-small'),device='cuda',compute_type='float16',cpu_threads=4,local_files_only=True)
rows=[]
variants=['ace-boombap','ace-industrial','minimax-room'] if '--greeting' not in sys.argv else ['ace-industrial-greeting-02']
for variant in variants:
 work=ROOT/'work/duets'/variant
 source=work/'stems/vocals.wav' if '--source' in sys.argv or '--greeting' in sys.argv else ROOT/'results/productions'/('duet-'+variant)/'full.wav'
 x,sr=sf.read(source,always_2d=True)
 intervals=[('greeting',0,11 if '--source' in sys.argv or '--greeting' in sys.argv else (9.5 if variant=='ace-boombap' else 5.7))]
 if '--source' in sys.argv: intervals.append(('intro-end',11,30))
 if '--source' not in sys.argv and '--greeting' not in sys.argv:
  timeline=json.loads((ROOT/'music/duet'/f'{variant}.timeline.json').read_text())
  intervals += [('adv',*timeline['fx_comparison_region']),('ezhi',timeline['ezhi_regions'][2]['start'],timeline['ezhi_regions'][2]['end'])]
 for label,s,e in intervals:
  path=work/f'check-{label}.wav'; sf.write(path,x[int(s*sr):int(e*sr)].mean(axis=1),sr,subtype='FLOAT')
  segments,info=model.transcribe(str(path),language='ru',beam_size=3,condition_on_previous_text=False,vad_filter=False)
  text=' '.join(t.text for t in segments)
  row={'variant':variant,'part':label,'start':s,'end':e,'text':text}; rows.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
(ROOT/'work/duets'/('greeting-check.json' if '--greeting' in sys.argv else 'source-check.json' if '--source' in sys.argv else 'final-check.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

if '--source' not in sys.argv and '--greeting' not in sys.argv:
 result={'method':'Local faster-whisper-small CUDA, independent short excerpts; not human listening or word-accuracy certification','status':'experimental_pronunciation_errors_and_asr_uncertainty','clips':rows}
 (ROOT/'results/productions/duet-asr-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
