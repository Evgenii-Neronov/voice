from pathlib import Path
import json,time,subprocess,sys
W=Path(__file__).resolve().parent
while True:
 try:r=json.loads((W/'ADV-rap4-cartoon-1440p-status.json').read_text())
 except (OSError,json.JSONDecodeError):r={}
 if r.get('state')=='complete':break
 time.sleep(3)
with (W/'verification.log').open('w',encoding='utf8') as log:p=subprocess.run([sys.executable,str(W/'verify.py')],stdout=log,stderr=subprocess.STDOUT)
(W/'verification-status.json').write_text(json.dumps({'state':'passed' if p.returncode==0 else 'failed','exit_code':p.returncode}));print('VERIFICATION',p.returncode,flush=True)
