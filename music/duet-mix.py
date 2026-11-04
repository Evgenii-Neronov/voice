"""Render a two-voice musical performance with room reflections and tempo delays."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt,fftconvolve
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('variant'); a=p.parse_args()
v=json.loads((ROOT/'music/duet'/(a.variant+'.json')).read_text(encoding='utf-8'))
timeline=json.loads((ROOT/'music/duet'/(a.variant+'.timeline.json')).read_text(encoding='utf-8'))
work=ROOT/'work/duets'/a.variant; out=ROOT/'results/productions'/('duet-'+a.variant);
assert not (out/'manifest.json').exists(), 'Refusing to overwrite a completed production'
out.mkdir(parents=True,exist_ok=True)
SR=44100
def read(name,mono=False):
 x,sr=sf.read(work/name,always_2d=True); assert sr==SR and np.isfinite(x).all()
 return x.mean(axis=1) if mono else x
def sha(path):
 with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
source=read('stems/vocals.wav',True); inst=read('stems/instrumental.wav'); length=len(source)
def envelope(x):
 hop=441; y=np.pad(x,(0,(-len(x))%hop)); return np.sqrt(np.mean(y.reshape(-1,hop)**2,axis=1)+1e-12)
source_env=envelope(source)
def level(x):
 assert abs(len(x)-length)<SR*.1
 x=np.pad(x,(0,max(0,length-len(x))))[:length]
 positions=[]; gains=[]
 for s in range(0,length,SR*2):
  orig=source[s:s+SR*2]; part=x[s:s+SR*2]
  positions.append(s+len(orig)/2); gains.append(float(np.clip(np.sqrt(np.mean(orig**2)+1e-10)/np.sqrt(np.mean(part**2)+1e-10),.4,8)))
 x*=np.interp(np.arange(length),positions,gains)
 gate=np.clip((20*np.log10(source_env+1e-8)+48)/14,0,1)
 x*=np.interp(np.arange(length),np.arange(len(gate))*441,gate)
 return .75*np.tanh(x/.75)
adv=level(read('adv-vocal-chunked.wav',True)); ezhi=level(read('ezhi-vocal-chunked.wav',True))
mask=np.zeros(length)
for region in timeline['ezhi_regions']:
 left=max(0,int(region['start']*SR)); right=min(length,int(region['end']*SR)); mask[left:right]=1
 fade=min(int(.06*SR),(right-left)//2)
 if left>0: mask[left:left+fade]=np.linspace(0,1,fade)
 if right<length: mask[right-fade:right]=np.linspace(1,0,fade)
assert np.all(mask[:min(int(5*SR),length)]==1),'Greeting must belong to Ezhi'
vocal=adv*(1-mask)+ezhi*mask
# Mild cleanup before spatial effects; no pitch/formant trick masquerading as accent correction.
vocal=sosfilt(butter(2,75,btype='highpass',fs=SR,output='sos'),vocal)
tail=2*SR; dry=np.pad(vocal,(0,tail)); total=len(dry)
rng=np.random.default_rng(v['seed']); room=np.zeros((total,2)); irs=[]
for channel in range(2):
 count=int((v['room']*1.6+.05)*SR); t=np.arange(count)/SR
 ir=rng.normal(size=count)*np.exp(-6.9078*t/v['room']); ir[:int(.028*SR)]=0
 ir=sosfilt(butter(3,4300,btype='lowpass',fs=SR,output='sos'),ir)
 ir*=.7/(np.linalg.norm(ir)+1e-12)
 for delay,gain in [(0.014,.42),(.027,.29),(.043,.22),(.071,.14)]: ir[int((delay+channel*.003)*SR)]+=gain
 ir/=max(np.linalg.norm(ir),1e-12); irs.append(ir)
 room[:,channel]=fftconvolve(dry,ir)[:total]
 # Store the deterministic room impulse response in ignored work for reproduction.
 sf.write(work/f'room-ir-{channel}.wav',ir,SR,subtype='FLOAT')
energy=np.interp(np.arange(total),np.arange(len(source_env))*441,source_env,left=0,right=0)
duck=1/(1+5*energy)
room*=duck[:,None]
echo=np.zeros((total,2)); filtered=sosfilt(butter(2,[220,3400],btype='bandpass',fs=SR,output='sos'),dry)
delay=round((60/v['bpm'])*v['delay_beats']*SR)
for repeat in range(1,5):
 offset=delay*repeat
 if offset>=total: break
 echo[offset:,(repeat-1)%2]+=filtered[:-offset]*(.48**(repeat-1))
echo*=duck[:,None]
bed=np.pad(inst,((0,tail),(0,0)))
dry_mix=bed+dry[:,None]
wet_mix=dry_mix+v['wet']*room+v['delay_send']*echo
wet_mix[-int(.3*SR):]*=np.linspace(1,0,int(.3*SR))[:,None]
sf.write(work/'dry-mix.wav',dry_mix,SR,subtype='FLOAT'); sf.write(work/'wet-mix.wav',wet_mix,SR,subtype='FLOAT')
measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(work/'wet-mix.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=12:print_format=json','-f','null','NUL'],capture_output=True,text=True,check=True)
stats=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])[0]
normalizer=f"loudnorm=I=-14:TP=-1.5:LRA=12:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true:print_format=json"
with (out/'mastering.log').open('w') as log:
 subprocess.run(['ffmpeg','-hide_banner','-i',str(work/'wet-mix.wav'),'-af',normalizer,'-ar',str(SR),'-c:a','pcm_s24le',str(out/'full.wav')],stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(out/'full.wav'),'-codec:a','libmp3lame','-b:a','256k',str(out/'full.mp3')],check=True)
full,sr=sf.read(out/'full.wav',always_2d=True)
assert len(full)==total and np.isfinite(full).all() and np.abs(full).max()<1
preview_regions=timeline['preview_regions']; clips=[]
for left,right in preview_regions:
 clip=full[int(left*SR):int(right*SR)].copy(); fade=min(int(.08*SR),len(clip)//2)
 clip[:fade]*=np.linspace(0,1,fade)[:,None]; clip[-fade:]*=np.linspace(1,0,fade)[:,None]; clips.append(clip)
sf.write(work/'preview.wav',np.concatenate(clips),SR)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(work/'preview.wav'),'-codec:a','libmp3lame','-b:a','256k',str(out/'preview.mp3')],check=True)
left,right=timeline['fx_comparison_region']; ab=[]
for mix in [dry_mix,wet_mix]:
 clip=mix[int(left*SR):int(right*SR)].copy(); clip*=.12/(np.sqrt(np.mean(clip**2))+1e-9)
 clip=.9*np.tanh(clip/.9); ab.append(clip)
sf.write(work/'fx-ab.wav',np.concatenate([ab[0],np.zeros((SR//2,2)),ab[1]]),SR)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(work/'fx-ab.wav'),'-codec:a','libmp3lame','-b:a','256k',str(out/'fx-dry-then-wet.mp3')],check=True)
m={'status':'rendered_not_human_rated','variant':a.variant,'local_inference':True,'duration':len(full)/SR,'sample_rate':SR,'channels':2,'peak':float(np.abs(full).max()),'brief':v,'timeline':timeline,'greeting_engine':timeline.get('greeting_engine',v['engine']),'greeting_voice':'Ezhi via Seed-VC reference','separate_tts_used':False,'effects':{'room_rt60':v['room'],'reverb_send':v['wet'],'echo_delay_seconds':delay/SR,'echo_send':v['delay_send'],'ducked_returns':True,'mastering_input':stats},'voice_conversion':json.loads((work/'chunked-conversion.json').read_text()),'audio':[]}
for name in ['full.wav','full.mp3','preview.mp3','fx-dry-then-wet.mp3']:
 file=out/name; m['audio'].append({'file':name,'bytes':file.stat().st_size,'sha256':sha(file)})
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'variant':a.variant,'duration':m['duration'],'peak':m['peak']}),flush=True)
