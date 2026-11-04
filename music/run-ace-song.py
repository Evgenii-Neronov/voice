"""Render the user's complete lyrics locally with the pinned ACE-Step installation."""
import argparse,dataclasses,hashlib,json,os,re,sys,time,traceback,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for key,value in {'HF_HOME':ROOT/'.cache/huggingface','TORCH_HOME':ROOT/'.cache/torch','ACESTEP_CHECKPOINTS_DIR':ROOT/'models/ace'}.items(): os.environ[key]=str(value)
os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
sys.path.insert(0,str(ROOT/'vendor/ace-step'))
p=argparse.ArgumentParser()
p.add_argument('--run-id',required=True); p.add_argument('--seed',type=int,default=20261104)
p.add_argument('--duration',type=float,default=250); p.add_argument('--instrumental',action='store_true')
p.add_argument('--config',choices=['acestep-v15-turbo'],default='acestep-v15-turbo')
a=p.parse_args()
assert re.fullmatch(r'[A-Za-z0-9_-]+',a.run_id)
out=ROOT/'results/music'/a.run_id; out.mkdir(parents=True,exist_ok=False)
source=ROOT/'Lyrics/lyrics.txt'; raw=source.read_text(encoding='utf-8-sig')
metadata={}; lines=[]; sections=[]
for line in raw.splitlines():
 match=re.fullmatch(r'\[(Title|Style|Vocal|Mood):\s*(.*?)\]',line)
 if match: metadata[match[1]]=match[2]; continue
 section=re.fullmatch(r'\[([^:\]]+):\s*(.*?)\]',line)
 if section:
  sections.append({'section':section[1],'direction':section[2]})
  line='['+section[1]+']'
 lines.append(line)
lyrics='\n'.join(lines).strip()
assert [x for x in raw.splitlines() if x.strip() and not x.startswith('[')]==[x for x in lyrics.splitlines() if x.strip() and not x.startswith('[')]
caption='Russian abstract hip-hop and UK underground boom bap, 96 BPM, dusty jazz breakbeats, distorted upright bass, dissonant Rhodes, modular synth glitches, turntable scratches, industrial percussion. High-pitched nasal male Russian rap, fast multisyllabic double-time flow, sharp diction, dry irony. Spoken rap, no sung melody, no deep baritone. Evolving arrangement, sparse verses, heavy chorus, breakdown, bells and tape-stop ending.'
if a.instrumental:
 caption='Instrumental UK abstract boom bap beat, 96 BPM, dusty jazz breakbeats, distorted upright bass, dissonant Rhodes, modular synth glitches, turntable scratches, industrial percussion. Tight swung drums, sparse groove, dark absurdist atmosphere, no vocals, no speech.'
 lyrics='[Instrumental]'
(out/'lyrics.normalized.txt').write_text(lyrics+'\n',encoding='utf-8')
manifest={'status':'starting','model':a.config,'local_inference':True,'seed':a.seed,'source_lyrics_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'metadata':metadata,'section_directions':sections,'instrumental':a.instrumental,'audio':[],'lock':json.loads((ROOT/'benchmark/ace.lock.json').read_text())}
def save(): (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
save()
try:
 from tokenizers import Tokenizer
 tok=Tokenizer.from_file(str(ROOT/'models/ace/Qwen3-Embedding-0.6B/tokenizer.json'))
 manifest['lyric_token_count']=len(tok.encode(lyrics).ids)
 assert manifest['lyric_token_count']<2000,'Refusing potential silent lyric truncation'
 from acestep.handler import AceStepHandler
 from acestep.llm_inference import LLMHandler
 from acestep.inference import GenerationParams,GenerationConfig,generate_music
 import torch,soundfile as sf,numpy as np
 class LocalHandler(AceStepHandler):
  def _ensure_models_present(self,*,checkpoint_path,config_path,prefer_source,vae_variant=None):
   required=[f'{config_path}/model.safetensors','vae/diffusion_pytorch_model.safetensors','Qwen3-Embedding-0.6B/model.safetensors']
   missing=[x for x in required if not (Path(checkpoint_path)/x).is_file()]
   return ('Missing local files: '+str(missing),False) if missing else None
 handler=LocalHandler()
 message,ok=handler.initialize_service(project_root=str(ROOT/'vendor/ace-step'),config_path=a.config,device='cuda',offload_to_cpu=True,offload_dit_to_cpu=True,compile_model=False,use_flash_attention=False)
 if not ok: raise RuntimeError(message)
 params=GenerationParams(caption=caption,lyrics=lyrics,bpm=96,keyscale='D minor',timesignature='4',vocal_language='unknown' if a.instrumental else 'ru',duration=a.duration,inference_steps=8,thinking=False,use_cot_metas=False,use_cot_caption=False,use_cot_language=False)
 config=GenerationConfig(batch_size=1,audio_format='wav',use_random_seed=False,seeds=[a.seed])
 manifest['params']=dataclasses.asdict(params); manifest['config']=dataclasses.asdict(config); save()
 torch.cuda.reset_peak_memory_stats()
 start=time.perf_counter(); result=generate_music(handler,LLMHandler(),params,config,save_dir=str(out))
 manifest['generation_seconds']=time.perf_counter()-start
 manifest['torch_peak_allocated_bytes']=torch.cuda.max_memory_allocated()
 if not result.success: raise RuntimeError(result.error)
 assert len(result.audios)==1
 generated=Path(result.audios[0]['path']); target=out/'full.wav'; generated.replace(target)
 samples,sr=sf.read(target,always_2d=True)
 assert samples.size and np.isfinite(samples).all() and np.max(np.abs(samples))>0
 info=sf.info(target)
 manifest['audio'].append({'file':'full.wav','sample_rate':sr,'channels':info.channels,'duration':info.duration,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'peak':float(np.abs(samples).max()),'rms':float(np.sqrt(np.mean(samples**2)))})
 assert abs(info.duration-a.duration)<2,'Unexpected output duration'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(target),'-codec:a','libmp3lame','-b:a','256k',str(out/'full.mp3')],check=True)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(target),'-t','20','-c:a','pcm_s16le',str(out/'preview.wav')],check=True)
 for name in ['full.mp3','preview.wav']:
  file=out/name; manifest.setdefault('delivery',[]).append({'file':name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 manifest['status']='generated_unrated'
except Exception:
 manifest['status']='failed'; manifest['error']=traceback.format_exc(); traceback.print_exc()
save()
print(json.dumps({'status':manifest['status'],'run':a.run_id,'generation_seconds':manifest.get('generation_seconds')}),flush=True)
raise SystemExit(0 if manifest['status']=='generated_unrated' else 1)
