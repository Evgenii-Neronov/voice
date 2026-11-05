from pathlib import Path
import json,subprocess,hashlib,numpy as np,math
from PIL import Image
from scipy.signal import correlate
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/rap4-montage-v3-1440p';V=O/'ADV-rap4-hiphop-montage-v3-1440p.mp4';TRACK='I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3'
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(V)]));vs=next(s for s in d['streams'] if s['codec_type']=='video');assert (vs['width'],vs['height'])==(2560,1440);assert vs['r_frame_rate']=='24/1';assert abs(float(d['format']['duration'])-273.188571)<.08
ass=(W/'subtitles.ass').read_text(encoding='utf8');assert all(x not in ass for x in ['—','–','−']);assert '220,220,144,1' in ass;events=json.loads((W/'alignment.json').read_text(encoding='utf8'));assert events[-5]['text'].startswith('Семинар окончен');assert events[-5]['start']==256.28
Q=W/'qa-final';Q.mkdir(exist_ok=True);times=[3,12,20,28,37,47,56,72,79,90,110,122,128,136,148,157,168,180,188,201,207,216,228,242,251,257,265]
for i,t in enumerate(times):subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1',str(Q/f'{i:02d}.jpg')],check=True)
for j in range(3):
 im=Image.new('RGB',(1920,1080))
 for k in range(9):im.paste(Image.open(Q/f'{j*9+k:02d}.jpg').resize((640,360)),((k%3)*640,(k//3)*360))
 im.save(O/f'contact-sheet-{j+1}.jpg',quality=94)
Image.open(Q/'25.jpg').save(O/'poster.jpg',quality=95)
subprocess.run(['ffmpeg','-v','error','-i',str(V),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
def audio(p,t):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-t','8','-ac','1','-ar','16000','-f','f32le','-']),dtype=np.float32)
lags=[]
for t in [0,130,260]:
 a=audio(TRACK,t);b=audio(V,t);n=min(len(a),len(b));lag=int(np.argmax(correlate(b[:n],a[:n],method='fft'))-(n-1));assert abs(lag)<=32;lags.append({'seconds':t,'lag_ms':lag/16})
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
r={'video':V.name,'sha256':sha(V),'bytes':V.stat().st_size,'source_audio_sha256':sha(TRACK),'duration':float(d['format']['duration']),'resolution':[2560,1440],'fps':24,'frames':int(vs.get('nb_frames',0)),'drawing_rate':{'street':12,'new_illustrations':24},'full_decode':'passed','audio_alignment':lags,'subtitle_lines':len(events),'long_dashes':False,'subtitle_margin_px':144,'ezhi_enters':[251.8,255.9],'ezhi_outro_start':256.28,'renderer':'New scenes: Skia CPU original illustration; street: Blender 4.5.9 Cycles OptiX GPU path tracing; FFmpeg NVENC encoding','visual_review':'12-second moving transit/roof preview checked as temporal contact sheet; native portrait frame; 300 alpha-connectivity neck samples; 27 final sampled frames. Not full audiovisual playback','limitations':['AIST++ dance motion adapted to limited drawn animation; not dedicated rap acting capture. New scenes are 2D with drawn lighting, street alone is ray traced','Reference-inspired Ezhi likeness is approximate','Automatic audio-derived visemes and ASR-assisted lyric timings are approximate']}
r['street_seconds']=32.188571;r['street_percent']=32.188571/273.188571*100;assert r['street_percent']<=15
r['subtitle_identical_to_v2']=sha(W/'subtitles.ass')==sha(W.parent/'rap4-cartoon-v2/subtitles.ass');assert r['subtitle_identical_to_v2']
r['actual_street_frames']=r['frames']-5784;r['actual_street_percent']=100*r['actual_street_frames']/r['frames'];assert r['actual_street_percent']<=15
r['motion_validation']=json.loads((W/'motion-validation.json').read_text())
(O/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
