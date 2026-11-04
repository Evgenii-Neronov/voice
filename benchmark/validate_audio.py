"""Decode every saved WAV and check numerical validity; not a listening rating."""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for path in sorted((ROOT/'results').glob('*/*.wav')):
    samples,sr=sf.read(path,always_2d=True)
    assert len(samples)>0 and np.isfinite(samples).all(),path
    assert np.max(np.abs(samples))>0,path
    info=sf.info(path)
    rows.append({'file':str(path.relative_to(ROOT)).replace('\\','/'),'sample_rate':sr,'channels':samples.shape[1],'seconds':len(samples)/sr,'subtype':info.subtype,'peak':float(np.max(np.abs(samples))),'rms':float(np.sqrt(np.mean(samples**2)))})
assert rows,'No WAVs to validate'
report={'count':len(rows),'total_seconds':sum(x['seconds'] for x in rows),'files':rows}
(ROOT/'results/audio-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
