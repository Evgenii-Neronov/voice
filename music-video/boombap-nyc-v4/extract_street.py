from pathlib import Path
import json,subprocess
W=Path(__file__).resolve().parent;PLAN=json.loads((W/'edit-plan.json').read_text());(W/'shots').mkdir(exist_ok=True)
for s in PLAN:
 if s['scene']!='street':continue
 cmd=['ffmpeg','-v','error','-y','-ss',str(s['start']),'-i',str(W/'original-clean.mp4'),'-frames:v',str(s['frames']),'-an','-c:v','h264_nvenc','-preset','p5','-cq','18','-pix_fmt','yuv420p',str(W/'shots'/f"{s['index']:02d}.mp4")]
 subprocess.run(cmd,check=True,creationflags=subprocess.CREATE_NO_WINDOW);print('Street',s['index'],'complete',flush=True)
