from pathlib import Path
import shutil,json,subprocess,zipfile,hashlib
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-v5-1440p';P=O/'project';P.mkdir(parents=True,exist_ok=True)
for name in ['assemble.py','run_render.py','finish_dance.py','verify.py','render_street.py','render_shot.py','graffiti.py','fix_street.py','replace_birds.py','build_dance.py','check_feet.py','edit-plan.json','budget.json','subtitles.ass','subtitles.srt','subtitle-baseline.ass','requirements.txt','versions.json','BRIEF.md','README.md','CHANGES-RU.md','CREDITS.md','grounding.json','foot-drift.json','asset-manifest.json','scene-manifest.json','dance-source.json','dance-validation.json','dance.npy','bird_whistle.stl']:
 shutil.copy2(W/name,P/name)
for folder in ['shots','sets']:shutil.copytree(W/folder,P/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*preview*','*.blend1'))
assert (P/'street-v5.blend').exists(), 'Pack street textures first'
(P/'assets').mkdir(exist_ok=True);shutil.copy2(W.parent/'nyc-boombap-v2/assets/RubikWetPaint-Regular.ttf',P/'assets/RubikWetPaint-Regular.ttf')
s=(P/'graffiti.py').read_text().replace("W.parent/'nyc-boombap-v2/assets/RubikWetPaint-Regular.ttf'","W/'assets/RubikWetPaint-Regular.ttf'");(P/'graffiti.py').write_text(s,encoding='utf-8')
(P/'PROJECT.txt').write_text('Local NYC v5 project. Blender 4.5.9; FFmpeg; Python deps numpy scipy Pillow skia-python. Pre-rendered clean shots included; assemble.py recreates final with original audio.\n')
(P/'audio').mkdir(exist_ok=True);subprocess.run(['ffmpeg','-v','error','-y','-i','I:/MyMusic/13 - New Rap/ADV-boombap-NYC-v3-1440p.mp4','-map','0:a:0','-c:a','copy',str(P/'audio/original.m4a')],check=True)
for n in ['ROCKETBOX-LICENSE.md','RubikWetPaint-OFL.txt']:shutil.copy2(W.parents[1]/'outputs/nyc-boombap-v3-1440p'/n,P/n)
for n in ['README.md','CHANGES-RU.md','CREDITS.md','subtitles.srt','edit-plan.json','foot-drift.json']:shutil.copy2(W/n,O/n)
with zipfile.ZipFile(O/'ADV-boombap-NYC-v5-project.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for f in P.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(O))
print('PACKAGE COMPLETE',flush=True)
