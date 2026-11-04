"""Dry sample-accurate modular session: replace one beat region or one voice phrase."""
import json,hashlib,subprocess,argparse
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
R=Path(__file__).resolve().parents[1]; w=R/'work/editable'
cli=argparse.ArgumentParser(); cli.add_argument('--project',default='music/editable/project.json'); cli.add_argument('--output',default='results/editable/modular'); args=cli.parse_args()
out=R/args.output; out.mkdir(parents=True,exist_ok=False)
p=json.loads((R/args.project).read_text(encoding='utf-8')); SR=p['sample_rate']; n=round(p['duration']*SR)

def read(path):
 x,s=sf.read(path,always_2d=True)
 if s!=SR:
  from math import gcd
  g=gcd(s,SR); x=resample_poly(x,SR//g,s//g,axis=0)
 return x
patch=p.get('beat_patch',{'file':'results/music/editable-beat-repaint-01/full.wav','start':10,'end':20}); beat=read(R/p.get('beat_source','work/editable/beat-source.wav'))[:n]; regenerated=read(R/patch['file'])[:n]; edited=beat.copy(); a,b=round(patch['start']*SR),round(patch['end']*SR); blend=np.ones(b-a); f=round(.08*SR); blend[:f]=np.linspace(0,1,f); blend[-f:]=np.linspace(1,0,f); edited[a:b]=beat[a:b]*(1-blend[:,None])+regenerated[a:b]*blend[:,None]
# Same constant gain for both beat versions, so the original outside the patch is identical.
bgain=.10/(np.sqrt(np.mean(beat**2))+1e-9); beat*=bgain; edited*=bgain
retake=p.get('retake',{'target':'changed-line','replacement':'changed-line-alt'})
voices=np.zeros(n); alternative=np.zeros(n); clips={}
for row in p['phrases']:
 x=read(R/row['file']).mean(axis=1); x*=.12/(np.sqrt(np.mean(x*x))+1e-9); x=.6*np.tanh(x/.6); f=min(240,len(x)//2); x[:f]*=np.linspace(0,1,f); x[-f:]*=np.linspace(1,0,f)
 assert len(x)<=round(row['slot']*SR); clips[row['id']]=x
 if row['id']!=retake['replacement']: start=round(row['start']*SR); voices[start:start+len(x)]+=x
alternative[:]=voices; target=next(row for row in p['phrases'] if row['id']==retake['target']); a2,b2=round(target['start']*SR),round((target['start']+target['slot'])*SR); alternative[a2:b2]=0; x=clips[retake['replacement']]; alternative[a2:a2+len(x)]=x
mixes={'01-original-beat':beat+voices[:,None],'02-beat-patch':edited+voices[:,None],'03-line-retake':beat+alternative[:,None]}
gain=min(1,.87/max(float(np.abs(x).max()) for x in mixes.values()))
assert np.array_equal(mixes['01-original-beat'][:a],mixes['02-beat-patch'][:a]) and np.array_equal(mixes['01-original-beat'][b:],mixes['02-beat-patch'][b:])
assert np.array_equal(mixes['01-original-beat'][:a2],mixes['03-line-retake'][:a2]) and np.array_equal(mixes['01-original-beat'][b2:],mixes['03-line-retake'][b2:])
assert np.max(np.abs(mixes['01-original-beat'][a:b]-mixes['02-beat-patch'][a:b]))>.01
assert np.max(np.abs(mixes['01-original-beat'][a2:b2]-mixes['03-line-retake'][a2:b2]))>.01
records=[]
for name,x in mixes.items():
 file=out/(name+'.wav'); sf.write(file,x*gain,SR,subtype='PCM_24'); subprocess.run(['ffmpeg','-v','error','-i',str(file),'-b:a','256k',str(out/(name+'.mp3'))],check=True)
 y,s=sf.read(file); assert np.isfinite(y).all() and np.abs(y).max()<1
 records.append({'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'duration':len(y)/s,'peak':float(np.abs(y).max())})
for name,x in [('beat-original',beat),('beat-edited',edited),('vocal',voices),('vocal-retake',alternative)]: sf.write(out/(name+'.wav'),x*gain,SR,subtype='PCM_24')
for name,x in clips.items(): sf.write(out/(name+'.wav'),x*gain,SR,subtype='PCM_24')
manifest={'local_inference':True,'dry':True,'added_reverb':False,'added_delay':False,'bpm':96,'project':p,'common_master_gain':gain,'validated':{'beat_edit_unchanged_outside_seconds':[a/SR,b/SR],'voice_edit_unchanged_outside_seconds':[a2/SR,b2/SR],'test':'Exact sample equality outside selected ranges before shared PCM24 conversion; lossy MP3 not covered'},'audio':records,'note':'Dry means no added spatial processing. Generated beat may contain its own ambience. Bar placement is not syllable-level flow control.'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print('Three dry modular versions validated',flush=True)
