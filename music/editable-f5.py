"""Independent Russian voice-reference phrases for a bar-addressable dry rap session."""
import os,json,time,hashlib,sys,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1]; sys.stdout.reconfigure(encoding='utf-8')
cli=argparse.ArgumentParser(); cli.add_argument('--retake'); cli.add_argument('--natural',action='store_true'); cli.add_argument('--text'); cli.add_argument('--seed',type=int,default=2026110500); cli.add_argument('--output-project',default='music/editable/project-retake.json'); args=cli.parse_args()
for k,v in {'HF_HOME':R/'.cache/huggingface','TORCH_HOME':R/'.cache/torch','HF_HUB_OFFLINE':'1','WANDB_MODE':'disabled'}.items(): os.environ[k]=str(v)
import numpy as np,soundfile as sf,torch,torchaudio
# Avoid TorchCodec/FFmpeg DLL coupling on Windows; decode our local WAV with libsndfile.
def load_wav(path,*args,**kwargs):
 x,sr=sf.read(path,dtype='float32',always_2d=True); return torch.from_numpy(x.T.copy()),sr
torchaudio.load=load_wav
from f5_tts.api import F5TTS
from f5_tts.infer.utils_infer import preprocess_ref_audio_text
w=R/'work/editable'; (w/'refs').mkdir(exist_ok=True); out=w/'phrases'; out.mkdir(exist_ok=bool(args.retake))
x,sr=sf.read(R/'work/adv-ezhi/refs/adv-intro-reference.wav'); sf.write(w/'refs/adv.wav',x,sr)
x,sr=sf.read(R/'work/adv-ezhi/refs/ezhi.wav'); sf.write(w/'refs/ezhi.wav',x[:round(3.95*sr)],sr)
reftexts=json.loads((w/'refs/transcripts.json').read_text(encoding='utf-8'))
refs={role:(role+'.wav',reftexts[role]) for role in ['adv','ezhi']}
phrases=[('greeting','adv',0,7.5,'Йо, это рэп трек! С вами Эй Ди Ви, ака Адвентус Девотус!'),('intro-1','adv',7.5,2.5,'В деревне отменили деньги.'),('intro-2','adv',10,2.5,'Но курс свистулек растёт.'),('intro-3','adv',12.5,2.5,'На десять глиняных флейт'),('intro-4','adv',15,2.5,'Положен квантовый счёт.'),('chorus-1','adv',17.5,5,'Десять свистулек — квантовый компьютер!'),('chorus-2','adv',22.5,5,'Денег не будет — но есть контрагент!'),('chorus-3','adv',27.5,5,'Под русским куполом вечное утро,'),('changed-line','adv',32.5,5,'Денежного обмена нет — а эквивалент есть!'),('ezhi-one','ezhi',37.5,2.5,'Десять свистулек!')]
raw=(R/'Lyrics/lyrics.txt').read_text(encoding='utf-8-sig'); assert all(t in raw for _,_,_,_,t in phrases[1:])
jobs=phrases+[('changed-line-alt','adv',32.5,5,phrases[8][4])]
if args.retake:
 previous=json.loads((R/'music/editable/project.json').read_text(encoding='utf-8')); selected=next(x for x in previous['phrases'] if x['id']==args.retake)
 jobs=[(args.retake+'-take-'+str(args.seed),selected['role'],selected['start'],selected['slot'],args.text or selected['text'])]
model=F5TTS(ckpt_file=str(R/'models/f5-ru/model_last.safetensors'),vocab_file=str(R/'models/f5-ru/vocab.txt'),vocoder_local_path=str(R/'models/vocos-24k'),device='cuda')
records=[]
for i,(name,role,start,slot,text) in enumerate(jobs):
 ref,reftext=refs[role]; processed,_=preprocess_ref_audio_text(str(w/'refs'/ref),reftext,show_info=lambda _:None); refsec=sf.info(processed).duration
 seed=args.seed if args.retake else 2026110430+i; begin=time.perf_counter(); y,rate,_=model.infer(str(w/'refs'/ref),reftext,text,nfe_step=32,fix_duration=None if args.natural else refsec+slot-.18,seed=seed,show_info=lambda _:None)
 assert np.isfinite(y).all() and len(y)>rate*.2 and len(y)/rate<=slot+.1
 file=out/(name+'.wav'); assert not file.exists(), 'Choose a new take seed instead of overwriting'; sf.write(file,y,rate,subtype='FLOAT'); records.append({'id':name,'role':role,'start':start,'slot':slot,'text':text,'file':str(file.relative_to(R)),'sample_rate':rate,'duration':len(y)/rate,'seconds':time.perf_counter()-begin,'seed':seed,'steps':32,'duration_mode':'natural' if args.natural else 'slot_conditioned','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 (w/('f5-retake-'+str(args.seed)+'.json' if args.retake else 'f5-phrases.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8'); print(name,records[-1]['duration'],flush=True)
project={'bpm':96,'duration':45,'sample_rate':48000,'lyrics_sha256':hashlib.sha256((R/'Lyrics/lyrics.txt').read_bytes()).hexdigest(),'dry':True,'model_lock':'music/editable/f5.lock.json','phrases':records,'note':'Phrase onsets are placed on bars; this is not automatic syllable-level rap performance alignment.'}
if args.retake:
 old_alt=previous.get('retake',{}).get('replacement','changed-line-alt'); project=previous; project['phrases']=[x for x in project['phrases'] if x['id']!=old_alt]+records; project['retake']={'target':args.retake,'replacement':records[0]['id']}
(R/(args.output_project if args.retake else 'music/editable/project.json')).write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
