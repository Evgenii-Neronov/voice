"""Validate the finished mix, export a three-role preview, and record loudness."""
import hashlib,json,re,subprocess
from pathlib import Path
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[1]; work=ROOT/'work/adv-ezhi'; out=ROOT/'results/productions/adv-ezhi-03'
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
x,sr=sf.read(out/'full.wav',always_2d=True)
assert sr==44100 and x.shape[1]==2 and np.isfinite(x).all() and np.max(np.abs(x))<1
assert abs(len(x)/sr-(sf.info(ROOT/manifest['base_track']).duration+10))<1/sr
clips=[]
regions=[(0,6),(40,48),(148.1,154.7)]
for start,end in regions:
 clip=x[int(start*sr):int(end*sr)].copy(); fade=int(.1*sr)
 clip[:fade]*=np.linspace(0,1,fade)[:,None]; clip[-fade:]*=np.linspace(1,0,fade)[:,None]; clips.append(clip)
sf.write(work/'roles-preview.wav',np.concatenate(clips),sr)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(work/'roles-preview.wav'),'-codec:a','libmp3lame','-b:a','256k',str(out/'roles-preview.mp3')],check=True)
log=subprocess.run(['ffmpeg','-hide_banner','-i',str(out/'full.wav'),'-af','ebur128=peak=true','-f','null','NUL'],capture_output=True,text=True,check=True).stderr
summary=log.rsplit('Summary:',1)[-1].split('[out#',1)[0].strip()+'\n'; (out/'loudness.txt').write_text(summary,encoding='utf-8')
manifest['verification']={'finite_samples':True,'sample_clipping':False,'exact_base_duration_plus_intro':True,'human_listening_review':False,'roles_preview_regions_seconds':regions}
manifest['verification']['loudness_summary']=summary.split('[out#')[0].strip()
manifest['audio']=[record for record in manifest['audio'] if record['file']!='roles-preview.mp3']
for record in manifest['audio']:
 with (out/record['file']).open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==record['sha256']
file=out/'roles-preview.mp3'
manifest['audio'].append({'file':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
for name in ['greeting','roles-preview','check-adv-chunked','check-adv-mix','check-ezhi-mix']:
 path=work/(name+'.asr.json')
 if path.exists(): manifest['verification'][name+'_asr']=[{'start':r['start'],'end':r['end'],'text':r['text']} for r in json.loads(path.read_text(encoding='utf-8'))]
manifest['inference_metrics']={}
for name in ['separation','greeting']:
 lines=(work/(name+'.log')).read_text(encoding='utf-8').splitlines()
 manifest['inference_metrics'][name]=[line for line in lines if line.startswith('metrics.')]
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(summary)
