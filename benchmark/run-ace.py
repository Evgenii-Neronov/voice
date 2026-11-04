"""ACE-Step 1.5 original Russian song; no optional language model."""
import argparse
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback
ROOT = Path(__file__).resolve().parents[1]
os.environ['HF_HOME'] = str(ROOT/'.cache/huggingface')
os.environ['TORCH_HOME'] = str(ROOT/'.cache/torch')
os.environ['ACESTEP_CHECKPOINTS_DIR'] = str(ROOT/'models/ace')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
sys.path.insert(0,str(ROOT/'vendor/ace-step'))
p=argparse.ArgumentParser()
p.add_argument('--out',required=True)
p.add_argument('--seed',type=int,default=20261104)
a=p.parse_args()
out=ROOT/a.out
out.mkdir(parents=True,exist_ok=False)
manifest={'model':'ace-step-1.5-turbo','seed':a.seed,'status':'starting','thinking':False}
try:
    from acestep.handler import AceStepHandler
    from acestep.llm_inference import LLMHandler
    from acestep.inference import GenerationParams, GenerationConfig, generate_music
    import soundfile as sf
    import torch
    manifest['lock']=json.loads((ROOT/'benchmark/ace.lock.json').read_text())
    class BenchmarkAceHandler(AceStepHandler):
        def _ensure_models_present(self, *, checkpoint_path, config_path, prefer_source, vae_variant=None):
            # Upstream checks the unused LM too; this no-LM benchmark validates
            # the actual required weight files and forbids implicit downloads.
            required=[f'{config_path}/model.safetensors','vae/diffusion_pytorch_model.safetensors','Qwen3-Embedding-0.6B/model.safetensors']
            missing=[x for x in required if not (Path(checkpoint_path)/x).is_file()]
            if missing:
                return ('Run benchmark/download-ace.py; missing '+str(missing),False)
            return None
    handler=BenchmarkAceHandler()
    message,ok=handler.initialize_service(project_root=str(ROOT/'vendor/ace-step'),config_path='acestep-v15-turbo',device='cuda',offload_to_cpu=True,offload_dit_to_cpu=True,compile_model=False,use_flash_attention=False)
    if not ok:
        raise RuntimeError(message)
    params=GenerationParams(caption='An intimate Russian lyrical ballad, expressive solo male singer, sustained vowels, gentle vibrato, sparse piano accompaniment, clear vocals, slow emotional delivery.',lyrics='[Verse]\nТихий свет над рекой,\nВозвращайся домой.\nЯ по звёздам пройду,\nГолос твой я найду.',bpm=80,keyscale='A minor',timesignature='4',vocal_language='ru',duration=30,inference_steps=8,thinking=False,use_cot_metas=False,use_cot_caption=False,use_cot_language=False)
    config=GenerationConfig(batch_size=1,audio_format='wav',use_random_seed=False,seeds=[a.seed])
    manifest['params']=dataclasses.asdict(params)
    manifest['config']=dataclasses.asdict(config)
    start=time.perf_counter()
    result=generate_music(handler,LLMHandler(),params,config,save_dir=str(out))
    manifest['generation_seconds']=time.perf_counter()-start
    if not result.success:
        raise RuntimeError(result.error)
    manifest['audio']=[]
    for item in result.audios:
        file=Path(item['path'])
        info=sf.info(file)
        manifest['audio'].append({'file':file.name,'sample_rate':info.samplerate,'duration':info.duration,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    if not manifest['audio']:
        raise RuntimeError('No output audio')
    manifest['status']='generated_unrated'
except (Exception, KeyboardInterrupt):
    manifest.update(status='failed',error=traceback.format_exc())
    traceback.print_exc()
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
raise SystemExit(0 if manifest['status']=='generated_unrated' else 1)
