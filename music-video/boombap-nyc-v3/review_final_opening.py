from pathlib import Path
import subprocess
from PIL import Image
W=Path('work/nyc-boombap-v3');O=Path('outputs/nyc-boombap-v3-1440p');Q=W/'final-preview-frames';Q.mkdir(exist_ok=True)
for i,t in enumerate([.2,1,2,3,4,5,6,6.6,6.8,7,7.2,7.4,8,10,12,14]):
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(O/'opening-preview-1440p.mp4'),'-frames:v','1',str(Q/f'{i:02d}.jpg')],check=True)
im=Image.new('RGB',(1920,1080))
for i in range(16):im.paste(Image.open(Q/f'{i:02d}.jpg').resize((480,270)),((i%4)*480,(i//4)*270))
im.save(W/'final-opening-contact.jpg',quality=94)
