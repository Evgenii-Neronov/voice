"""Backfill native completion details from saved engine manifests, without changing audio."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for native in sorted((ROOT/'results').glob('*/native-manifest.json')):
 path=native.parent/'manifest.json'
 if not path.exists(): continue
 data=json.loads(path.read_text(encoding='utf-8'))
 if data.get('status')=='running': continue
 records=json.loads(native.read_text(encoding='utf-8')).get('requests',[])
 changed=False
 for row in data.get('cases',[]):
  engine=next((r for r in records if r.get('id')==row['id']),{})
  details=engine.get('custom_schema_output',{}).get('data')
  if details and row.get('native_generation')!=details:
   row['native_generation']=details; changed=True
   if details.get('reached_limit'):
    row['status']='generated_at_limit'
    row['completion_warning']='Token limit reached; this WAV may be truncated.'
    data['status']='failed_or_partial'
 if changed:
  path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(path.parent.name)
