from pathlib import Path
import json,time,subprocess
W=Path(__file__).resolve().parent;ROOT=W.parents[1];O=ROOT/'outputs/nyc-boombap-v2-1440p'
while True:
 try:state=json.loads((W/'status.json').read_text())
 except (OSError,json.JSONDecodeError):state={}
 if state.get('state')=='complete' or state.get('parts',{}).get('0',{}).get('state')=='complete':break
 time.sleep(10)
cmd=['ffmpeg','-hide_banner','-y','-i','part-00.mp4','-i',str(ROOT/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3'),'-t','15','-vf','ass=subtitles.ass','-c:v','h264_nvenc','-preset','p5','-cq','19','-b:v','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-movflags','+faststart',str(O/'opening-preview-1440p.mp4')]
with (W/'opening-preview.log').open('w') as log:subprocess.run(cmd,cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
print('OPENING PREVIEW COMPLETE',flush=True)
