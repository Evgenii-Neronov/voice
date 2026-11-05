from pathlib import Path
import json,hashlib,subprocess,re,numpy as np
from PIL import Image
from scipy.signal import correlate
W=Path(__file__).resolve().parent;O=W/'renders' if (W/'PROJECT.txt').exists() else W.parents[1]/'outputs/nyc-boombap-v6-1440p';V=O/'ADV-boombap-NYC-v6-montage-1440p.mp4';SOURCE=Path('I:/MyMusic/13 - New Rap/ADV-boombap-NYC-v3-1440p.mp4');audio=W/'audio/original.m4a'
if audio.exists():SOURCE=audio
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(V)]));vs=next(x for x in d['streams'] if x['codec_type']=='video');assert (vs['width'],vs['height'])==(2560,1440);assert vs['r_frame_rate']=='24/1';assert int(vs['nb_frames'])==6079
ass=(W/'subtitles.ass').read_text(encoding='utf8');old=(W/'subtitle-baseline.ass').read_text(encoding='utf8');assert not any(x in ass for x in '—–−');assert ass==old.translate(str.maketrans({'—':'-','–':'-','−':'-'}));assert '220,220,144,1' in ass
plan=json.loads((W/'edit-plan.json').read_text());assert sum(s['frames'] for s in plan)==6079;budget=json.loads((W/'budget.json').read_text());assert 73<=budget['street_percent']<=75;assert not any(x['scene'] in ['lab','dance','graffiti'] for x in plan)
Q=W/'qa';Q.mkdir(exist_ok=True);times=[3,22,36,48,57,64,86,100,113,125,139,151,163,173,185,204,214,225,233,239,249]
for i,t in enumerate(times):subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1',str(Q/f'{i:02d}.jpg')],check=True)
for page in range(3):
 im=Image.new('RGB',(1600,900))
 for j in range(8):
  n=page*8+j
  if n<len(times):im.paste(Image.open(Q/f'{n:02d}.jpg').resize((400,225)),((j%4)*400,(j//4)*225))
 im=im.crop((0,0,1600,450));im.save(O/f'contact-{page+1}.jpg',quality=94)
Image.open(Q/'01.jpg').save(O/'poster.jpg',quality=95)
subprocess.run(['ffmpeg','-v','error','-i',str(V),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
def wav(p,t):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-t','6','-ar','16000','-ac','1','-f','f32le','-']),dtype=np.float32)
lags=[]
for t in [0,120,240]:
 a=wav(SOURCE,t);b=wav(V,t);n=min(len(a),len(b));lag=int(np.argmax(correlate(b[:n],a[:n],method='fft'))-(n-1));assert abs(lag)<=16;lags.append({'at':t,'lag_ms':lag/16})
def packet_hash(p):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','-'])).hexdigest()
ah,bh=packet_hash(SOURCE),packet_hash(V);assert ah==bh,'Audio packets changed'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(4194304),b''):h.update(x)
 return h.hexdigest()

def crop(p,t):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=320:180,crop=320:145:0:0','-pix_fmt','rgb24','-f','rawvideo','-']),dtype=np.uint8).astype(np.float32)
street_checks=[]

r={'video':V.name,'sha256':sha(V),'bytes':V.stat().st_size,'duration':float(d['format']['duration']),'resolution':[2560,1440],'fps':24,'frames':6079,'budget':budget,'audio_packets_identical':True,'audio_packet_sha256':ah,'audio_alignment':lags,'subtitle_only_dash_replacement':True,'subtitle_bottom_margin_px':144,'full_decode':'passed','review':'Opening moving preview inspected through temporal frames, red-wire still and 21 final sampled frames; not full audiovisual playback','limits':['Original stock human appearance and approximate lip articulation retained','Forward walking restored only in the opening; planted stance thereafter']}
r['opening']=json.loads((W/'opening-motion.json').read_text());assert abs(r['opening'][0]['lead'][1]-r['opening'][-1]['lead'][1])>2
assert abs(r['opening'][0]['camera'][1]-r['opening'][3]['camera'][1])>1.8
r['red_wires']={k:json.loads((W/(k+'-red-wires.json')).read_text()) for k in ['studio','metro']}
(O/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
