"""Offline Seed-VC V2 paired timbre/style experiments on identical rap excerpts."""
from pathlib import Path
import os,sys,json,time,hashlib
R=Path(__file__).resolve().parents[1];sys.stdout.reconfigure(encoding='utf-8')
for k,v in {'HF_HOME':R/'.cache/huggingface','TORCH_HOME':R/'.cache/torch','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}.items():os.environ[k]=str(v)
sys.path.insert(0,str(R/'vendor/seed-vc'))
import numpy as np,soundfile as sf,torch,yaml
from hydra.utils import instantiate
from omegaconf import OmegaConf
import hf_utils
root=R/'models/seed-v2'
def local_model(repo_id,model_filename='pytorch_model.bin',config_filename=None):
 path=root/repo_id.replace('/','--')/model_filename;assert path.is_file(),path
 return str(path) if config_filename is None else (str(path),str(path.parent/config_filename))
hf_utils.load_custom_model_from_hf=local_model
cfg=OmegaConf.create(yaml.safe_load((R/'vendor/seed-vc/configs/v2/vc_wrapper.yaml').read_text()))
for key in ['content_extractor_narrow','content_extractor_wide']:
 cfg[key].tokenizer_name=str(root/'openai--whisper-small');cfg[key].ssl_model_name=str(root/'facebook--hubert-large-ll60k')
cfg.vocoder.pretrained_model_name_or_path=str(root/'nvidia--bigvgan_v2_22khz_80band_256x')
w=R/'work/seedv2-test';w.mkdir(exist_ok=True);out=R/'results/experiments/seedv2-test-01';out.mkdir(parents=True,exist_ok=True)
base=R/'work/rap4-dialogue-final/01';x,sr=sf.read(base/'stems/vocals.wav',always_2d=True)
for role,start,end,ref in [('adv',30,42,'adv.wav'),('ezhi',107.14,112.18,'ezhi-conversion.wav')]:
 sf.write(w/(role+'-source.wav'),x[int(start*sr):int(end*sr)].mean(axis=1),sr,subtype='FLOAT');a,rate=sf.read(base/'refs'/ref,always_2d=True);sf.write(w/(role+'-ref.wav'),a[:8*rate].mean(axis=1),rate,subtype='FLOAT')
print('Loading pinned offline models',flush=True);start=time.perf_counter();model=instantiate(cfg);model.load_checkpoints();model.to('cuda').eval();model.setup_ar_caches(max_batch_size=1,max_seq_len=4096,dtype=torch.float16,device=torch.device('cuda'));print('Models ready',time.perf_counter()-start,flush=True)
rows=json.loads((out/'manifest.json').read_text(encoding='utf-8')) if (out/'manifest.json').exists() else []
for role,style in [('adv',False),('adv',True),('ezhi',True)]:
 name=role+('-style' if style else '-timbre');target=out/(name+'.wav')
 if target.exists():
  assert any(r['name']==name and r['sha256']==hashlib.sha256(target.read_bytes()).hexdigest() for r in rows), 'Existing output has no matching manifest'
  continue
 torch.manual_seed(2026111201);torch.cuda.reset_peak_memory_stats();begin=time.perf_counter();full=None
 with torch.inference_mode():
  for _,audio in model.convert_voice_with_streaming(source_audio_path=str(w/(role+'-source.wav')),target_audio_path=str(w/(role+'-ref.wav')),diffusion_steps=30,length_adjust=1.0,intelligebility_cfg_rate=.7,similarity_cfg_rate=.7,top_p=.9,temperature=.8,repetition_penalty=1.1,convert_style=style,anonymization_only=False,device=torch.device('cuda'),dtype=torch.float16,stream_output=True):
   if audio is not None:full=audio
 assert full is not None;rate,y=full;assert np.isfinite(y).all() and len(y)>rate*.2;sf.write(target,y,rate,subtype='PCM_24')
 row={'name':name,'convert_style':style,'seconds':time.perf_counter()-begin,'duration':len(y)/rate,'sample_rate':rate,'peak_gpu_bytes':torch.cuda.max_memory_allocated(),'seed':2026111201,'steps':30,'top_p':.9,'temperature':.8,'repetition_penalty':1.1,'intelligibility_cfg':.7,'similarity_cfg':.7,'source_sha256':hashlib.sha256((w/(role+'-source.wav')).read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256((w/(role+'-ref.wav')).read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()};rows.append(row);(out/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(row,flush=True)
