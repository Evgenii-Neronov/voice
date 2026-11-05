from pathlib import Path
import shutil,subprocess,zipfile
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-v6-1440p';P=O/'project';P.mkdir(parents=True,exist_ok=True)
files=['assemble.py','verify.py','run_render.py','render_street.py','render_shot.py','restore_opening.py','continuous_quaternions.py','red_wires.py','BRIEF.md','README.md','CREDITS.md','requirements.txt','versions.json','edit-plan.json','budget.json','subtitles.ass','subtitles.srt','subtitle-baseline.ass','opening-motion.json','studio-red-wires.json','metro-red-wires.json']
for n in files:shutil.copy2(W/n,P/n)
for folder in ['shots','sets']:shutil.copytree(W/folder,P/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*preview*','*.blend1'))
shutil.copy2(W/'street-v6.blend',P/'street-v6.blend')
(P/'audio').mkdir(exist_ok=True);subprocess.run(['ffmpeg','-v','error','-y','-i','I:/MyMusic/13 - New Rap/ADV-boombap-NYC-v3-1440p.mp4','-map','0:a:0','-c:a','copy',str(P/'audio/original.m4a')],check=True)
(P/'PROJECT.txt').write_text('NYC v6 portable render and editing project. See README.md.\n')
for n in ['ROCKETBOX-LICENSE.md','RubikWetPaint-OFL.txt']:shutil.copy2(W.parents[1]/'outputs/nyc-boombap-v3-1440p'/n,P/n)
for n in ['README.md','CREDITS.md','subtitles.srt','edit-plan.json','opening-motion.json']:shutil.copy2(W/n,O/n)
shutil.copy2(W/'shots/00-preview.mp4',O/'opening-preview-720p.mp4')
with zipfile.ZipFile(O/'ADV-boombap-NYC-v6-project.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for f in P.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(O))
print('PACKAGE COMPLETE',flush=True)
