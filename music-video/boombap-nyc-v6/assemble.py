from pathlib import Path
import json,subprocess,time
W=Path(__file__).resolve().parent;O=W/'renders' if (W/'PROJECT.txt').exists() else W.parents[1]/'outputs/nyc-boombap-v6-1440p';O.mkdir(parents=True,exist_ok=True);plan=json.loads((W/'edit-plan.json').read_text())
for s in plan:
 p=W/'shots'/f"{s['index']:02d}.mp4";d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]));v=next(x for x in d['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==s['frames'],(p,v['nb_frames'],s['frames']);assert (v['width'],v['height'])==(2560,1440)
(W/'parts.txt').write_text('\n'.join(f"file 'shots/{s['index']:02d}.mp4'" for s in plan))
audio=W/'audio/original.m4a';source=audio if audio.exists() else Path('I:/MyMusic/13 - New Rap/ADV-boombap-NYC-v3-1440p.mp4')
cmd=['ffmpeg','-hide_banner','-y','-f','concat','-safe','0','-i','parts.txt','-i',str(source),'-map','0:v:0','-map','1:a:0','-vf','ass=subtitles.ass','-r','24','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(O/'ADV-boombap-NYC-v6-montage-1440p.mp4')]
begin=time.time()
with (W/'assembly.log').open('w') as f:subprocess.run(cmd,cwd=W,stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'assembly-status.json').write_text(json.dumps({'seconds':time.time()-begin,'state':'complete'},indent=2));print('ASSEMBLY COMPLETE',flush=True)
