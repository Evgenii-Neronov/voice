from pathlib import Path
import subprocess,json
W=Path(__file__).resolve().parent
root=W.parents[1]
audio=root/'outputs/rap-18/rap-18.mp3'
out=root/'outputs/rap18-nightshift-1440p'
out.mkdir(exist_ok=True)
video=out/'ADV-rap18-Nochnaya-smena-1440p.mp4'
def run(args):
    return subprocess.check_output([str(a) for a in args],cwd=W)
run(['ffmpeg','-v','error','-n','-i','picture.mp4','-i',audio,'-map','0:v','-map','1:a','-vf','ass=subtitles.ass','-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0','-c:a','copy','-movflags','+faststart',video])
run(['ffmpeg','-v','error','-xerror','-i',video,'-f','null','-'])
def ah(file):
    return run(['ffmpeg','-v','error','-i',file,'-map','0:a','-c','copy','-f','hash','-']).decode().strip()
assert ah(video)==ah(audio)
assert (W/'subtitles.ass').read_bytes()==(W.parent/'rap18-print/subtitles.ass').read_bytes()
v=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',video]))['streams']
assert (v[0]['width'],v[0]['height'],v[0]['nb_frames'])==(2560,1440,'4418')
print(v[0]['duration'],ah(video),flush=True)
