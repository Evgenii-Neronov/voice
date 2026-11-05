from pathlib import Path
import json,subprocess,hashlib,numpy as np
from PIL import Image
from scipy.signal import correlate
W=Path(__file__).resolve().parent;ROOT=W.parents[1];O=ROOT/'outputs/nyc-boombap-v3-1440p';V=O/'ADV-boombap-NYC-v3-1440p.mp4'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
d=probe(V);vs=next(s for s in d['streams'] if s['codec_type']=='video');au=next(s for s in d['streams'] if s['codec_type']=='audio');assert (vs['width'],vs['height'])==(2560,1440);assert vs['r_frame_rate']=='24/1';assert abs(float(d['format']['duration'])-253.283265)<.06
parts=[probe(p) for p in sorted(W.glob('part-??.mp4'))];counts=[int(x['streams'][0]['nb_frames']) for x in parts];assert sum(counts)==6079,counts
qa=W/'qa';qa.mkdir(exist_ok=True);times=[.2,2,6,11.7,26,39.5,45.5,48,54,64,69,78,95,118,145,186,220,250]
for i,t in enumerate(times):subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1',str(qa/f'{i:02d}.jpg')],check=True)
for j in range(2):
 im=Image.new('RGB',(1920,1080))
 for k in range(9):im.paste(Image.open(qa/f'{j*9+k:02d}.jpg').resize((640,360)),((k%3)*640,(k//3)*360))
 im.save(O/f'contact-sheet-{j+1}.jpg',quality=93)
Image.open(qa/'08.jpg').save(O/'poster.jpg',quality=95)
subprocess.run(['ffmpeg','-v','error','-i',str(V),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
def audio(p,start):
 data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(p),'-t','8','-ac','1','-ar','16000','-f','f32le','-']);return np.frombuffer(data,dtype=np.float32)
lags=[]
for start in [0,120,240]:
 a=audio(ROOT/'outputs/original-voices/main/07-minimax-trio-boombap-01.mp3',start);b=audio(V,start);n=min(len(a),len(b));c=correlate(b[:n],a[:n],mode='full',method='fft');lag=int(np.argmax(c)-(n-1));assert abs(lag)<=32,(start,lag);lags.append({'at_seconds':start,'lag_ms':lag/16})
h=hashlib.sha256()
with V.open('rb') as f:
 for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
report={'video':V.name,'sha256':h.hexdigest(),'size_bytes':V.stat().st_size,'resolution':[2560,1440],'fps':24,'duration':float(d['format']['duration']),'frames_per_part':counts,'renderer':'Blender 4.5.9 EEVEE / Vulkan, 24 samples, ray tracing enabled','encoder':'FFmpeg h264_nvenc p6 CQ18','audio_sample_rate':au['sample_rate'],'audio_alignment':lags,'full_decode':'passed','visual_review':'18 sampled final frames, 7-second opening temporal contact sheet, V3 moving opening/transition preview and all-frame skeletal continuity audit; not a claim of full audiovisual playback','known_limits':['Stylized stock human topology retained to preserve lead appearance; not photoreal scanned humans','Retargeted captured conversation/walking motion plus small beat accents; not dedicated recorded rap mocap','Audio-derived automatic phoneme-to-viseme mapping; timing and articulation remain approximate','Subtitle boundaries remain approximate at unclear generated pronunciation']}
(O/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False),flush=True)
