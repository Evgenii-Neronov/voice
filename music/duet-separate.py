"""Separate the new music takes, preserving raw voice references locally."""
import argparse,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('variants',nargs='+'); p.add_argument('--work-root',default='work/duets'); p.add_argument('--source-prefix',default='duet-'); a=p.parse_args()
for variant in a.variants:
 work=ROOT/a.work_root/variant
 if (work/'separation.json').exists():
  print('Already separated',variant,flush=True); continue
 work.mkdir(parents=True,exist_ok=True)
 (work/'refs').mkdir(exist_ok=True)
 for name in ['adv.wav','ezhi-conversion.wav']: shutil.copy2(ROOT/'work/adv-ezhi/refs'/name,work/'refs'/name)
 source=ROOT/'results/music'/(a.source_prefix+variant)/'full.wav'
 converted=work/'separation-input.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-ar','44100','-c:a','pcm_f32le',str(converted)],check=True)
 source=converted
 command=[str(ROOT/'vendor/audio-runtime/audiocpp_cli.exe'),'--task','sep','--family','bs_roformer','--model',str(ROOT/'models/voice-production/BS-RoFormer-ep368-GGUF/bs-roformer-ep368-q8_0.gguf'),'--backend','cuda','--threads','8','--audio',str(source),'--out-dir',str(work/'stems'),'--out-format','float32','--metrics','--load-progress','0']
 start=time.perf_counter()
 with (work/'separation.log').open('w') as log: subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
 (work/'separation.json').write_text(json.dumps({'command':command,'seconds':time.perf_counter()-start},indent=2),encoding='utf-8')
 print('Separated',variant,flush=True)
