from pathlib import Path
import sys,json,shutil,importlib.metadata as md,subprocess,zipfile,hashlib
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/rap4-cartoon-1440p';P=O/'project';P.mkdir(exist_ok=True)
for name in ['art.py','render.py','visemes.npy','beats.json','sections.json','alignment.json','audio-manifest.json','subtitles.ass','requirements.txt','BRIEF.md']:
 shutil.copy2(W/name,P/name)
shutil.copytree(W/'assets',P/'assets',dirs_exist_ok=True);shutil.copytree(O/'editable-art',P/'editable-art',dirs_exist_ok=True)
(P/'audio').mkdir(exist_ok=True);shutil.copy2('I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3',P/'audio/track.mp3')
(P/'PROJECT.txt').write_text('Portable illustrated Rap4 project. Original audio included locally; never staged to Git.\n')
(P/'README.md').write_text('''# Editable 2D music video project

Windows + Python3.12 + FFmpeg with NVENC (NVIDIA). Install exact drawing dependencies into a separate environment:

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe render.py
```

Output goes to `renders/`. Test a passage with `--start 250 --duration 23.188571 --name test-outro`.

Edit art.py for drawings, poses, character positions and camera choices. `editable-art/` contains editable SVG and PNG drawings; those are exports, while render.py draws the path definitions in art.py. Edit subtitles.ass for caption text/timing. Original track is audio/track.mp3. Precomputed visemes.npy supplies mouth shapes; no model download is needed to reproduce this version. Windows Arial is required for matching subtitle typography.

See BRIEF.md for staging. The guest is a stylized approximation based on the reference. This is procedural2D puppet animation,12 drawings/s in24fps video.
''',encoding='utf8')
L=P/'licenses';L.mkdir(exist_ok=True);dep={}
for name in ['skia-python','numpy','scipy','pillow']:
 d=md.distribution(name);meta=md.metadata(name);dep[name]={'version':d.version,'license_expression':meta.get('License-Expression'),'license_classifiers':[c for c in meta.get_all('Classifier',[]) if c.startswith('License')]}
 for f in d.files:
  if '/licenses/' in str(f) and str(f).lower().endswith(('license','license.txt','license.md','copying')):
   target=L/(name+'-'+Path(str(f)).name);shutil.copy2(d.locate_file(f),target)
dep['python']=sys.version;dep['python_executable']=sys.executable;dep['ffmpeg']=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]
(W/'dependencies.json').write_text(json.dumps(dep,indent=2));shutil.copy2(W/'dependencies.json',P/'dependencies.json')
# SRT accompanies ASS for editing in external video software.
a=json.loads((W/'alignment.json').read_text(encoding='utf8'))
def tc(t):
 m=round(t*1000);return f'{m//3600000:02d}:{m//60000%60:02d}:{m//1000%60:02d},{m%1000:03d}'
srt='\n\n'.join(f"{i+1}\n{tc(e['start'])} --> {tc(e['end'])}\n{e['text']}" for i,e in enumerate(a))+'\n'
for path in [O/'subtitles.srt',P/'subtitles.srt'] :path.write_text(srt,encoding='utf8')
shutil.copy2(W/'subtitles.ass',O/'subtitles.ass');print('Portable project staged')
