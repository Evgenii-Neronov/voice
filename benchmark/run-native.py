"""Run pinned audio.cpp models; preserve requests, logs, timings and WAV hashes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {'fish-s2':'fish_audio', 'higgs3':'higgs_audio_tts', 'drama3':'fish_drama3'}
HIGGS_TAGS = {
 'neutral':'', 'neutral_control':'',
 'joy':'<|emotion:elation|><|prosody:expressive_high|>',
 'anger':'<|emotion:anger|><|prosody:expressive_high|>',
 'sadness':'<|emotion:sadness|><|prosody:speed_slow|>',
 'drawl':'<|prosody:speed_very_slow|><|prosody:expressive_high|>',
 'syllables':'',
 'singing_probe':'<|style:singing|>',
 'emotion_control':'<|emotion:relief|><|prosody:expressive_high|>',
}
FISH_TAGS = {
 'neutral':'', 'neutral_control':'', 'joy':'[excited]', 'anger':'[angry]',
 'sadness':'[sad]', 'drawl':'[Speak theatrically and slowly, stretching vowels, with irony]',
 'syllables':'[Sustain each vowel smoothly for two seconds]',
 'singing_probe':'[singing] [Slow lyrical melody, sustained vowels, expressive vibrato]',
 'emotion_control':'[joyful relief]',
}

def save(path, data):
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('model',choices=FAMILIES)
 p.add_argument('--run-id',required=True)
 p.add_argument('--model-file',type=Path)
 p.add_argument('--cases',nargs='+')
 p.add_argument('--backend',choices=['cpu','cuda'],default='cuda')
 p.add_argument('--session-option',action='append',default=[])
 p.add_argument('--timeout',type=int,default=5400)
 p.add_argument('--max-tokens',type=int,default=1024)
 p.add_argument('--no-tags',action='store_true',help='Explicit ablation: original spoken text without control prefix')
 p.add_argument('--request-option',action='append',default=[])
 a=p.parse_args()
 assert re.fullmatch(r'[A-Za-z0-9_-]+',a.run_id),'Unsafe run id'
 out=ROOT/'results'/a.run_id
 out.mkdir(exist_ok=False)
 lock=json.loads((ROOT/'benchmark/native-models.lock.json').read_text())
 model=(ROOT/(a.model_file or lock[a.model]['local_file'])).resolve()
 cases=json.loads((ROOT/'benchmark/cases.json').read_text(encoding='utf-8'))
 if a.cases:
  assert set(a.cases)<=set(c['id'] for c in cases),'Unknown case id'
  by_id={c['id']:c for c in cases}
  cases=[by_id[case_id] for case_id in a.cases]
 tags=HIGGS_TAGS if a.model=='higgs3' else FISH_TAGS
 if a.no_tags: tags={case['id']:'' for case in cases}
 requests=[]
 for case in cases:
  requests.append({'id':case['id'],'text':(tags[case['id']]+' '+case['text']).strip(),
   'language':'ru','seed':20261104,'max_tokens':a.max_tokens,'temperature':0.8,
   'top_k':4097 if a.model=='drama3' else 30,
   'top_p':0.9 if a.model=='drama3' else 0.8,'text_chunk_size':1024,
   'options':dict(option.split('=',1) for option in a.request_option)})
 save(out/'requests.json',requests)
 exe=ROOT/'vendor/audio-runtime/audiocpp_cli.exe'
 opts=[]
 if a.model=='drama3':
  opts=['fish_drama3.disk_experts=true','fish_drama3.expert_cache_size=8',
   'fish_drama3.cpu_expert_layers=0','fish_drama3.disk_expert_read_threads=1',
   'fish_drama3.context_length=2048']
 # Explicit overrides replace defaults, never pass duplicate keys.
 options=dict(option.split('=',1) for option in opts+a.session_option)
 command=[str(exe),'--task','tts','--family',FAMILIES[a.model],'--model',str(model),
  '--backend',a.backend,'--threads','8','--request-sequence',str(out/'requests.json'),
  '--out-dir',str(out),'--out-format','pcm16','--batch-manifest-out',str(out/'native-manifest.json'),
  '--metrics','--load-progress','0']
 for key,value in options.items(): command+=['--session-option',key+'='+value]
 data={'model':a.model,'model_file':str(model.relative_to(ROOT)),
  'source':lock[a.model],'runtime_version':subprocess.run([str(exe),'--version'],capture_output=True,text=True).stdout.strip(),
  'runtime_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
  'command':command,'backend':a.backend,'session_options':options,
  'voice_reference':None,'tags_disabled_ablation':a.no_tags,'protocol':'Native no-reference TTS, seed fixed; identity is not guaranteed across prompts.',
  'timing_scope':'Per-request native wall time; model initialization excluded. Whole run wall time includes initialization.',
  'status':'running','cases':[]}
 data['effective_precision']=lock[a.model]['precision'] if a.model_file is None else 'custom; inspect model hash'
 derived_path=ROOT/'benchmark/fish-mixed-q4.lock.json'
 if a.model=='fish-s2' and derived_path.exists():
  derived=json.loads(derived_path.read_text(encoding='utf-8'))
  if model==(ROOT/derived['local_file']).resolve():
   data['effective_precision']='Mixed Q4_K backbone; fast decoder, codec, embeddings and norms preserved from Q8 source'
   data['derived_weights']=derived
 with model.open('rb') as f: data['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
 expected=data.get('derived_weights',{}).get('sha256') or (lock[a.model]['sha256'] if a.model_file is None else None)
 if expected: assert data['model_sha256']==expected,'Model SHA256 mismatch'
 save(out/'manifest.json',data)
 env=os.environ.copy()
 temporary=ROOT/'.cache/audio.cpp-temp'
 temporary.mkdir(parents=True,exist_ok=True)
 env['TEMP']=env['TMP']=str(temporary)
 env['HF_HOME']=str(ROOT/'.cache/huggingface')
 started=time.perf_counter()
 samples=[]
 with (out/'runtime.log').open('w',encoding='utf-8') as log:
  process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
  while process.poll() is None:
   if time.perf_counter()-started>a.timeout:
    process.kill(); process.wait(); data['error']='Configured timeout exceeded; only this child process was killed.'; break
   gpu=subprocess.run(['nvidia-smi','--query-gpu=timestamp,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True)
   samples.append(gpu.stdout.strip())
   time.sleep(3)
 data['process_exit_code']=process.returncode
 data['whole_run_seconds']=time.perf_counter()-started
 (out/'gpu-whole-device.csv').write_text('timestamp, used_MiB, free_MiB, utilization_percent\n'+'\n'.join(samples)+'\n',encoding='utf-8')
 logtext=(out/'runtime.log').read_text(encoding='utf-8',errors='replace')
 native_path=out/'native-manifest.json'
 native_rows=json.loads(native_path.read_text(encoding='utf-8')).get('requests',[]) if native_path.exists() else []
 for case in cases:
  row={'id':case['id'],'text':case['text'],'instruction':case['instruction'],'effective_prompt':next(r['text'] for r in requests if r['id']==case['id'])}
  wav=out/(case['id']+'.wav')
  if wav.exists():
   with wave.open(str(wav),'rb') as w:
    row.update(duration_seconds=w.getnframes()/w.getframerate(),sample_rate=w.getframerate(),channels=w.getnchannels())
   match=re.search(r'metrics\['+re.escape(case['id'])+r'\]\.wall_ms=([\d.]+)',logtext)
   row.update(status='generated_unrated',wav=wav.name,sha256=hashlib.sha256(wav.read_bytes()).hexdigest(),generation_seconds=float(match[1])/1000 if match else None)
   if row['generation_seconds'] is not None:
    row['rtf']=row['generation_seconds']/row['duration_seconds']
   native=next((r for r in native_rows if r.get('id')==case['id']),{})
   details=native.get('custom_schema_output',{}).get('data')
   if details:
    row['native_generation']=details
    if details.get('reached_limit'):
     row['status']='generated_at_limit'
     row['completion_warning']='Token limit reached; this WAV may be truncated.'
  else:
   row.update(status='failed',error='No WAV produced; see runtime.log and process_exit_code.')
  data['cases'].append(row)
 data['status']='generated_unrated' if process.returncode==0 and all(r['status']=='generated_unrated' for r in data['cases']) else 'failed_or_partial'
 if process.returncode: data.setdefault('error',logtext[-4000:])
 save(out/'manifest.json',data)
 print(json.dumps({'run_id':a.run_id,'status':data['status'],'wall_seconds':data['whole_run_seconds'],'generated':sum(r['status'].startswith('generated_') for r in data['cases'])}),flush=True)
 return 0 if data['status']=='generated_unrated' else 2

if __name__=='__main__': raise SystemExit(main())
