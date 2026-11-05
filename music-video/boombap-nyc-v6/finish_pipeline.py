from pathlib import Path
import json,subprocess,time,sys
W=Path(__file__).resolve().parent;plan=json.loads((W/'edit-plan.json').read_text())
while not all((W/f"status-{s['index']:02d}.json").exists() for s in plan):time.sleep(10)
for script in ['assemble.py','verify.py','package_project.py']:
 print(script,flush=True)
 with (W/(script+'.log')).open('w') as f:subprocess.run([sys.executable,'-X','utf8',str(W/script)],stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
print('COMPLETE',flush=True)
