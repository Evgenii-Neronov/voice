"""Local TTS benchmark. Pin models with download.py before inference."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
for name, sub in {"HF_HOME":".cache/huggingface", "TORCH_HOME":".cache/torch", "XDG_CACHE_HOME":".cache", "NUMBA_CACHE_DIR":".cache/numba", "PKUSEG_HOME":".cache/pkuseg"}.items():
    os.environ[name] = str(ROOT / sub)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=["qwen17", "qwen06", "chatterbox"], required=True)
    p.add_argument("--cases", nargs="*")
    p.add_argument("--seed", type=int, default=20261104)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--threads", type=int, default=0, help="CPU torch threads; 0 keeps the runtime default")
    p.add_argument("--out", required=True, help="New output directory; existing results are never overwritten")
    a = p.parse_args()
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=False)
    manifest = {"model":a.model, "seed":a.seed,"device":a.device,"cases":[],"status":"starting"}
    def save():
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        import numpy as np
        import soundfile as sf
        import torch
        from transformers import set_seed
        if a.threads > 0:
            torch.set_num_threads(a.threads)
        manifest["torch_num_threads"] = torch.get_num_threads()
        manifest["packages"] = {k:importlib.metadata.version(k) for k in ["torch","torchaudio","transformers","numpy","soundfile"]}
        manifest["model_lock"] = json.loads((ROOT / "benchmark/models.lock.json").read_text(encoding="utf-8"))[a.model]
        if a.device.startswith("cuda"):
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA unavailable; refusing silent CPU fallback")
            manifest["gpu"] = torch.cuda.get_device_name()
            manifest["cuda"] = torch.version.cuda
            torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        model_dir = ROOT / "models" / a.model
        if a.model.startswith("qwen"):
            from qwen_tts import Qwen3TTSModel
            model = Qwen3TTSModel.from_pretrained(str(model_dir), device_map=a.device, dtype=torch.bfloat16, attn_implementation="sdpa")
        else:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            model = ChatterboxMultilingualTTS.from_local(str(model_dir), device=a.device, t3_model="v3")
        manifest["load_seconds"] = time.perf_counter() - start
        cases = json.loads((ROOT / "benchmark/cases.json").read_text(encoding="utf-8"))
        if a.cases and set(a.cases) - {x["id"] for x in cases}:
            raise ValueError("Unknown case ID")
        for case in cases:
            if a.cases and case["id"] not in a.cases:
                continue
            set_seed(a.seed); random.seed(a.seed); np.random.seed(a.seed)
            row = dict(case, seed=a.seed)
            manifest["cases"].append(row)
            try:
                if a.device.startswith("cuda"):
                    torch.cuda.synchronize()
                start = time.perf_counter()
                with torch.inference_mode():
                    if a.model.startswith("qwen"):
                        instruction = case["instruction"] if a.model == "qwen17" else ""
                        wavs, sr = model.generate_custom_voice(text=case["text"], language="Russian", speaker="Ryan", instruct=instruction, max_new_tokens=700)
                        wave = np.asarray(wavs[0], dtype=np.float32)
                        row["effective_controls"] = {"speaker":"Ryan","instruction":instruction,"max_new_tokens":700,"attention":"sdpa","dtype":"bfloat16"}
                    else:
                        wave = model.generate(case["text"], language_id="ru", exaggeration=case["exaggeration"], cfg_weight=0.3).detach().cpu().numpy().squeeze()
                        sr = model.sr
                        row["effective_controls"] = {"exaggeration":case["exaggeration"],"cfg_weight":0.3,"instruction_supported":False,"t3_model":"v3"}
                if a.device.startswith("cuda"):
                    torch.cuda.synchronize()
                row["generation_seconds"] = time.perf_counter() - start
                if wave.size == 0 or not np.isfinite(wave).all():
                    raise ValueError("Empty or non-finite waveform")
                row.update(sample_rate=int(sr), duration_seconds=len(wave)/sr, peak=float(np.max(np.abs(wave))), rms=float(np.sqrt(np.mean(wave**2))), clipped_fraction=float(np.mean(np.abs(wave)>=1)))
                row["rtf"] = row["generation_seconds"] / row["duration_seconds"]
                file = out / (case["id"] + ".wav")
                sf.write(file, wave, sr, subtype="PCM_16")
                row.update(status="generated_unrated",wav=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest())
                if a.device.startswith("cuda"):
                    row["peak_allocated_gib"] = torch.cuda.max_memory_allocated()/2**30
                print(json.dumps(row, ensure_ascii=False), flush=True)
            except Exception:
                row.update(status="failed",error=traceback.format_exc())
            save()
        manifest["status"] = "completed" if all(x["status"]=="generated_unrated" for x in manifest["cases"]) else "partial_failure"
    except Exception:
        manifest.update(status="failed",error=traceback.format_exc())
        traceback.print_exc()
    save()
    return 0 if manifest["status"] == "completed" else 1

if __name__ == "__main__":
    raise SystemExit(main())
