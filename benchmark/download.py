"""Resolve immutable HF revisions once, then download those exact snapshots."""
import argparse
import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.environ["HF_HOME"] = str(ROOT / ".cache/huggingface")
MODELS = {"qwen17":"Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "qwen06":"Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", "chatterbox":"ResembleAI/chatterbox"}

def main():
    from huggingface_hub import HfApi, snapshot_download
    p = argparse.ArgumentParser()
    p.add_argument("models", nargs="+", choices=list(MODELS))
    a = p.parse_args()
    lock_path = ROOT / "benchmark/models.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    for name in a.models:
        if name not in lock:
            info = HfApi().model_info(MODELS[name])
            lock[name] = {"repo_id":MODELS[name], "revision":info.sha, "license":getattr(info.card_data, "license", None)}
            lock_path.write_text(json.dumps(lock, indent=2), encoding="utf-8")
        entry = lock[name]
        patterns = ["ve.pt","s3gen.pt","t3_mtl23ls_v3.safetensors","grapheme_mtl_merged_expanded_v1.json","conds.pt","*.md","LICENSE*"] if name == "chatterbox" else None
        snapshot_download(entry["repo_id"], revision=entry["revision"], local_dir=ROOT/"models"/name, allow_patterns=patterns, max_workers=4)
        print(name, entry, flush=True)
if __name__ == "__main__":
    main()
