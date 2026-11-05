from pathlib import Path
import subprocess,json,time
W=Path(__file__).resolve().parent
O=W/'renders' if (W/'PROJECT.txt').exists() else W.parents[1]/'outputs/rap4-montage-v3-1440p';O.mkdir(parents=True,exist_ok=True)
track=W/'audio/track.mp3'
if not track.exists():track=Path('I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3')
dest=O/'ADV-rap4-hiphop-montage-v3-1440p.mp4'
cmd=['ffmpeg','-hide_banner','-y','-i',str(W/'street-opening.mp4'),'-i',str(W/'illustrated-middle.mp4'),'-i',str(W/'street-outro.mp4'),'-i',str(track),'-filter_complex','[0:v]fps=24,trim=duration=8,setpts=PTS-STARTPTS[a];[1:v]fps=24,trim=duration=241,setpts=PTS-STARTPTS[b];[2:v]fps=24,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,ass=subtitles.ass[v]','-map','[v]','-map','3:a:0','-t','273.188571','-r','24','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-pix_fmt','yuv420p','-c:a','aac','-b:a','320k','-movflags','+faststart',str(dest)]
begin=time.time()
with (W/'assembly.log').open('w') as log:subprocess.run(cmd,cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'assembly-status.json').write_text(json.dumps({'state':'complete','seconds':time.time()-begin,'output':str(dest)},indent=2));print(dest,flush=True)
