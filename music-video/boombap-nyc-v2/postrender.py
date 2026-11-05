from pathlib import Path
import time,json,subprocess,sys
W=Path(__file__).resolve().parent
while True:
 try:state=json.loads((W/'status.json').read_text())
 except (OSError,json.JSONDecodeError):state={}
 if state.get('state')=='complete':break
 time.sleep(10)
(W/'verification-status.json').write_text(json.dumps({'state':'checking'}))
with (W/'verification.log').open('w',encoding='utf8') as log:
 p=subprocess.run([sys.executable,str(W/'verify_final.py')],stdout=log,stderr=subprocess.STDOUT)
(W/'verification-status.json').write_text(json.dumps({'state':'passed' if p.returncode==0 else 'failed','exit_code':p.returncode}))
print('POSTRENDER',p.returncode,flush=True)
