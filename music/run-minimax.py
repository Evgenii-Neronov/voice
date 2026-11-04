"""Local MiniMax Music 3 GGUF: pinned runtime, auditable requests and audio."""
import argparse,hashlib,json,re,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--run-id',required=True)
p.add_argument('--duration',type=int,default=30)
p.add_argument('--full-lyrics',action='store_true')
p.add_argument('--brief',type=Path)
a=p.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9_-]+',a.run_id)
out=ROOT/'results/music'/a.run_id; out.mkdir(exist_ok=False)
base=json.loads((ROOT/'results/music/ace-turbo-full-01/manifest.json').read_text(encoding='utf-8'))
lyrics=base['params']['lyrics']
if not a.full_lyrics: lyrics=lyrics.split('[Verse 1]')[0].strip()
options={'lyrics':lyrics,'duration_sec':str(a.duration),'num_inference_steps':'30','guidance_scale':'1.7','ar_guidance_scale':'1.5','top_k':'50','seed':'20261104'}
request=[{'id':'full','text':base['params']['caption'],'seed':20261104,'options':options}]
brief=json.loads((ROOT/a.brief).read_text(encoding='utf-8')) if a.brief else {}
if brief:
 a.duration=brief['duration']; a.full_lyrics=True
 options.update(lyrics=brief['lyrics'],duration_sec=str(a.duration),seed=str(brief['seed']))
 request[0].update(text=brief['caption'],seed=brief['seed'])
def write(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(out/'requests.json',request)
exe=ROOT/'vendor/audio-runtime/audiocpp_cli.exe'
command=[str(exe),'--task','gen','--family','minimax_music3','--model',str(ROOT/'models/music/MiniMax-Music3-GGUF'),'--backend','cuda','--threads','8','--request-sequence',str(out/'requests.json'),'--out-dir',str(out),'--out-format','pcm16','--batch-manifest-out',str(out/'native-manifest.json'),'--metrics','--load-progress','0','--session-option','minimax_music3.mem_saver=true','--session-option','minimax_music3.perf_mode=cuda_perf']
m={'status':'running','local_inference':True,'model':'MiniMax-Music3 GGUF Q4/Q8/Q4','scope':'full lyrics' if a.full_lyrics else 'original intro only (8 lines)','source_lyrics_sha256':base['source_lyrics_sha256'],'runtime_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'model_lock':json.loads((ROOT/'music/minimax.lock.json').read_text()),'command':command,'requested_budget_seconds':a.duration,'audio':[]}
m['brief']=brief
if brief: m['source_lyrics_sha256']=brief.get('original_lyrics_sha256',m['source_lyrics_sha256'])
write(out/'manifest.json',m)
start=time.perf_counter(); peak=0
try:
 with (out/'runtime.log').open('w',encoding='utf-8') as log:
  process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
  while process.poll() is None:
   try:
    memory=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True,timeout=8)
    peak=max(peak,int(memory.strip().splitlines()[0]))
   except (ValueError,subprocess.SubprocessError): pass
   time.sleep(2)
  m['returncode']=process.returncode
  if process.returncode: raise RuntimeError(f'Native exit {process.returncode}; see runtime.log')
 import soundfile as sf,numpy as np
 target=out/'full.wav'; data,sr=sf.read(target,always_2d=True)
 assert data.size and np.isfinite(data).all() and np.abs(data).max()>0
 m['audio']=[{'file':'full.wav','sample_rate':sr,'channels':data.shape[1],'duration':len(data)/sr,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'peak':float(np.abs(data).max()),'rms':float(np.sqrt(np.mean(data**2)))}]
 for name,extra in [('full.mp3',['-codec:a','libmp3lame','-b:a','256k']),('preview.wav',['-t','20','-c:a','pcm_s16le'])]:
  dest=out/name
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(target),*extra,str(dest)],check=True)
  m.setdefault('delivery',[]).append({'file':name,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 m['status']='generated_unrated'
except Exception:
 m['status']='failed'; m['error']=traceback.format_exc(); traceback.print_exc()
m['whole_run_seconds']=time.perf_counter()-start
m['whole_gpu_peak_used_mib']=peak
m['memory_scope']='Whole card, includes other applications, sampled every ~2 seconds'
write(out/'manifest.json',m)
print(json.dumps({'status':m['status'],'seconds':m['whole_run_seconds'],'audio':m['audio']}),flush=True)
raise SystemExit(0 if m['status']=='generated_unrated' else 1)
