from pathlib import Path
import json,hashlib,subprocess,re,numpy as np
from PIL import Image
from scipy.signal import correlate
W=Path(__file__).resolve().parent;O=W/'renders' if (W/'PROJECT.txt').exists() else W.parents[1]/'outputs/nyc-boombap-v5-1440p';V=O/'ADV-boombap-NYC-v5-montage-1440p.mp4';SOURCE=Path('I:/MyMusic/13 - New Rap/ADV-boombap-NYC-v3-1440p.mp4');audio=W/'audio/original.m4a'
if audio.exists():SOURCE=audio
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(V)]));vs=next(x for x in d['streams'] if x['codec_type']=='video');assert (vs['width'],vs['height'])==(2560,1440);assert vs['r_frame_rate']=='24/1';assert int(vs['nb_frames'])==6079
ass=(W/'subtitles.ass').read_text(encoding='utf8');old=(W/'subtitle-baseline.ass').read_text(encoding='utf8');assert not any(x in ass for x in '—–−');assert ass==old.translate(str.maketrans({'—':'-','–':'-','−':'-'}));assert '220,220,144,1' in ass
plan=json.loads((W/'edit-plan.json').read_text());assert sum(s['frames'] for s in plan)==6079;budget=json.loads((W/'budget.json').read_text());assert 49<=budget['street_percent']<=51
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

r={'video':V.name,'sha256':sha(V),'bytes':V.stat().st_size,'duration':float(d['format']['duration']),'resolution':[2560,1440],'fps':24,'frames':6079,'budget':budget,'street_frame_comparisons':street_checks,'audio_packets_identical':True,'audio_packet_sha256':ah,'audio_alignment':lags,'subtitle_only_dash_replacement':True,'dash_replacements':sum(old.count(x) for x in '—–−'),'subtitle_bottom_margin_px':144,'full_decode':'passed','review':'Street and dance moving previews reviewed through temporal contact sheets, bird still, graffiti growth and 21 final samples; not full audiovisual playback','rendering':'Street rerendered with planted lower body and damped head/neck; new scenes Blender 4.5.9 EEVEE Vulkan with ray tracing,16 samples; 2D graffiti Skia CPU; final NVENC','limits':['Original stock human appearance and approximate lip articulation unchanged','Dance is a directional retarget from AIST++ keypoints, not a new human performance','Street lower-body stance is fixed to prevent skating']}
r['foot_contact_validation']=json.loads((W/'foot-drift.json').read_text());assert all(x['foot_joint_drift_metres']==0 for x in r['foot_contact_validation'])
r['dance_direction_validation']=json.loads((W/'dance-validation.json').read_text());assert r['dance_direction_validation']['max_joint_direction_error_degrees']<.01
r['downloaded_assets']=json.loads((W/'asset-manifest.json').read_text())
(O/'validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
