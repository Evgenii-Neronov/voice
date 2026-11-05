from pathlib import Path
import subprocess
from PIL import Image
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-v3-1440p';Q=W/'preview-frames';Q.mkdir(exist_ok=True)
for i,t in enumerate([5.6+i*.2 for i in range(16)]):
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(W/'preview-silent.mp4'),'-frames:v','1',str(Q/f'{i:02d}.jpg')],check=True)
im=Image.new('RGB',(1920,1080))
for i in range(16):im.paste(Image.open(Q/f'{i:02d}.jpg').resize((480,270)),((i%4)*480,(i//4)*270))
im.save(W/'transition-contact.jpg',quality=94)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(W/'preview-silent.mp4'),'-i',str(W.parents[1]/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3'),'-vf','ass=subtitles.ass','-t','12','-c:v','h264_nvenc','-cq','18','-c:a','aac','-b:a','256k',str(O/'motion-preview-720p.mp4')],cwd=W,check=True)
