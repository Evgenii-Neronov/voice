"""Install the pinned Windows x64 CUDA runtime without system-wide changes."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/'benchmark/native-runtime.lock.json').read_text())
destination=ROOT/'vendor/audio-runtime'
destination.mkdir(parents=True,exist_ok=True)
for item in lock['archives']:
 archive=ROOT/'.cache/downloads'/item['local_name']
 archive.parent.mkdir(parents=True,exist_ok=True)
 if not archive.exists():
  temporary=archive.with_suffix('.partial')
  urllib.request.urlretrieve(item['url'],temporary)
  temporary.replace(archive)
 with archive.open('rb') as f:
  assert hashlib.file_digest(f,'sha256').hexdigest()==item['sha256'],archive
 with zipfile.ZipFile(archive) as bundle:
  for entry in bundle.infolist():
   if entry.is_dir(): continue
   # Runtime release archives are flattened into the explicitly owned directory.
   target=destination/Path(entry.filename).name
   payload=bundle.read(entry)
   if target.exists() and target.read_bytes()!=payload:
    raise RuntimeError(f'Refusing to replace a different existing runtime file: {target}')
   if not target.exists(): target.write_bytes(payload)
print(destination)
