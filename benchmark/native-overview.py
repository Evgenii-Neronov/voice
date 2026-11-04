"""Summarize selected complete native runs; timing and memory scopes remain explicit."""
import csv
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
SELECTED=['fish-s2-q8-run1','fish-s2-q4-run1','higgs3-q8-run4','drama3-q2-pinned-run1']
rows=[]
for name in SELECTED:
 folder=ROOT/'results'/name
 data=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
 cases=data['cases']
 assert len(cases)==9 and all(r['status'].startswith('generated_') for r in cases),name
 duration=sum(r['duration_seconds'] for r in cases)
 elapsed=sum(r['generation_seconds'] for r in cases)
 gpu=list(csv.DictReader((folder/'gpu-whole-device.csv').read_text().splitlines(),skipinitialspace=True))
 rss=[int(x) for x in re.findall(r'peak_rss_mb=(\d+)',(folder/'runtime.log').read_text(encoding='utf-8',errors='replace'))]
 reached=[r.get('native_generation',{}).get('reached_limit') for r in cases]
 rows.append({'run_id':name,'model':data['model'],'status':data['status'],
  'precision':data.get('effective_precision',data['source']['precision']),
  'wav_count':len(cases),'audio_seconds':duration,'generation_seconds':elapsed,
  'weighted_rtf':elapsed/duration,'min_rtf':min(r['rtf'] for r in cases),'max_rtf':max(r['rtf'] for r in cases),
  'whole_run_seconds':data['whole_run_seconds'],
  'whole_gpu_max_sampled_mib':max(int(r['used_MiB']) for r in gpu if r.get('used_MiB')),
  'process_peak_rss_mib':max(rss) if rss else None,
  'any_native_reached_limit':any(reached) if all(x is not None for x in reached) else None,
  'singing_probe':next({k:r[k] for k in ['duration_seconds','generation_seconds','rtf','sha256']} for r in cases if r['id']=='singing_probe')})
result={'runs':rows,'selected_wav_count':sum(r['wav_count'] for r in rows),
 'notes':['RTF excludes model initialization; lower is faster.',
 'GPU samples cover the whole card, including unrelated processes; RSS is CPU memory.',
 'Higgs syllables prefix removed after slow-tag failures; see requests and NATIVE_BENCHMARK.md.',
 'No listening scores, ASR/WER, MIDI accuracy or statistical seed sweep.']}
(ROOT/'results/native-overview.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
