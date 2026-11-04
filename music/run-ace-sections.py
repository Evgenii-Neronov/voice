"""Generate four local ACE sections to reduce long-form lyric reordering."""
from pathlib import Path
import os,sys,json,time,hashlib,dataclasses
R=Path(__file__).resolve().parents[1];sys.stdout.reconfigure(encoding='utf-8')
for k,v in {'HF_HOME':R/'.cache/huggingface','TORCH_HOME':R/'.cache/torch','ACESTEP_CHECKPOINTS_DIR':R/'models/ace','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}.items():os.environ[k]=str(v)
sys.path.insert(0,str(R/'vendor/ace-step'))
import numpy as np,soundfile as sf,torch
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams,GenerationConfig,generate_music
from tokenizers import Tokenizer
class LocalHandler(AceStepHandler):
 def _ensure_models_present(self,*,checkpoint_path,config_path,prefer_source,vae_variant=None):
  required=[f'{config_path}/model.safetensors','vae/diffusion_pytorch_model.safetensors','Qwen3-Embedding-0.6B/model.safetensors'];missing=[x for x in required if not (Path(checkpoint_path)/x).is_file()];return ('Missing '+str(missing),False) if missing else None
b=json.loads((R/'music/ace-esoteric/brief.json').read_text(encoding='utf-8'));lyrics=b['lyrics'];cuts=[0]+[lyrics.index(tag) for tag in ['[Verse 2]','[Verse 3]','[Verse 4]']]+[len(lyrics)];parts=[lyrics[cuts[i]:cuts[i+1]].strip() for i in range(4)];assert ''.join(''.join(s.split()) for s in parts)==''.join(lyrics.split())
handler=LocalHandler();msg,ok=handler.initialize_service(project_root=str(R/'vendor/ace-step'),config_path='acestep-v15-turbo',device='cuda',offload_to_cpu=True,offload_dit_to_cpu=True,compile_model=False,use_flash_attention=False);assert ok,msg
tok=Tokenizer.from_file(str(R/'models/ace/Qwen3-Embedding-0.6B/tokenizer.json'));rows=[];audio=[]
for i,part in enumerate(parts,1):
 out=R/'results/music'/f'ace-esoteric-section-{i:02}';out.mkdir(exist_ok=True)
 if (out/'manifest.json').exists():
  row=json.loads((out/'manifest.json').read_text(encoding='utf-8'));assert row['lyrics']==part and row['params']['caption']==b['caption']+' Perform only the supplied lines once in order. No repeated verse or extra chorus.' and row['config']['seeds']==[2026111110+i], 'Existing section parameters differ'
  assert row['sha256']==hashlib.sha256((out/'full.wav').read_bytes()).hexdigest(), 'Cached section changed'
 else:
  tokens=len(tok.encode(part).ids);assert tokens<2000;duration=round((len(part.split())/1.65+2)/ (240/84))*(240/84)
  params=GenerationParams(caption=b['caption']+' Perform only the supplied lines once in order. No repeated verse or extra chorus.',lyrics=part,bpm=84,keyscale='D minor',timesignature='4',vocal_language='ru',duration=duration,inference_steps=8,thinking=False,use_cot_metas=False,use_cot_caption=False,use_cot_language=False)
  config=GenerationConfig(batch_size=1,audio_format='wav',use_random_seed=False,seeds=[2026111110+i]);t=time.perf_counter();res=generate_music(handler,LLMHandler(),params,config,save_dir=str(out));assert res.success,res.error;Path(res.audios[0]['path']).replace(out/'full.wav');row={'lyrics':part,'params':dataclasses.asdict(params),'config':dataclasses.asdict(config),'seconds':time.perf_counter()-t,'sha256':hashlib.sha256((out/'full.wav').read_bytes()).hexdigest()};(out/'manifest.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
 x,sr=sf.read(out/'full.wav',always_2d=True);assert sr==48000 and np.isfinite(x).all();audio.append(x);rows.append(row);print('SECTION READY',i,len(x)/sr,flush=True)
out=R/'results/music/ace-esoteric-sections-01';out.mkdir(exist_ok=False);fade=round(.18*sr);y=audio[0];boundaries=[]
for x in audio[1:]:
 boundaries.append((len(y)-fade)/sr);ramp=np.linspace(0,1,fade)[:,None];y=np.concatenate([y[:-fade],y[-fade:]*(1-ramp)+x[:fade]*ramp,x[fade:]])
sf.write(out/'full.wav',y,sr,subtype='FLOAT');m={'status':'generated_sections_unrated','model':'ACE-Step 1.5 turbo','local_inference':True,'brief':b,'source_lyrics_sha256':b['original_lyrics_sha256'],'generation_seconds':sum(x['seconds'] for x in rows),'audio':[{'file':'full.wav','duration':len(y)/sr,'sample_rate':sr,'channels':2,'sha256':hashlib.sha256((out/'full.wav').read_bytes()).hexdigest()}],'assembly':{'crossfade_seconds':.18,'section_offsets':[0]+boundaries},'sections':[f'ace-esoteric-section-{i:02}' for i in range(1,5)],'lock':json.loads((R/'benchmark/ace.lock.json').read_text())};(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print('ASSEMBLED',len(y)/sr,flush=True)
