from pathlib import Path
import shutil,subprocess,json,re
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/nyc-boombap-v4-1440p';P=O/'project';P.mkdir(parents=True,exist_ok=True)
files=['plan.py','build_sets.py','render_shot.py','run_new_3d.py','graffiti.py','extract_street.py','assemble.py','verify.py','BRIEF.md','README.md','CREDITS.md','requirements.txt','edit-plan.json','budget.json','subtitles.ass','subtitle-baseline.ass','subtitle-validation.json','source-validation.json']
for n in files:shutil.copy2(W/n,P/n)
shutil.copytree(W/'sets',P/'sets',dirs_exist_ok=True);shutil.copy2(W/'original-clean.mp4',P/'original-clean.mp4')
shutil.copy2(W.parents[1]/'outputs/nyc-boombap-v3-1440p/project/NYC-boombap-v3.blend',P/'original-street-v3.blend')
for n in ['ROCKETBOX-LICENSE.md','RubikWetPaint-OFL.txt']:shutil.copy2(W.parents[1]/'outputs/nyc-boombap-v3-1440p'/n,P/n)
(P/'audio').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','I:/MyMusic/13 - New Rap/ADV-boombap-NYC-v3-1440p.mp4','-map','0:a:0','-c:a','copy',str(P/'audio/original.m4a')],check=True)
(P/'assets').mkdir(exist_ok=True)
for base in ['concrete_wall_006','red_bricks_04','asphalt_02']:
 for typ in ['diff','rough']:shutil.copy2(W.parent/'nyc-boombap/assets'/f'{base}_{typ}_2k.jpg',P/'assets'/f'{base}_{typ}_2k.jpg')
s=(P/'build_sets.py').read_text().replace("str(W.parent/'nyc-boombap/assets')","str(W/'assets')");(P/'build_sets.py').write_text(s)
s=(P/'plan.py').read_text().replace("W.parent/'nyc-boombap-v3/subtitles.ass'","W/'subtitle-baseline.ass'");(P/'plan.py').write_text(s)
(P/'PROJECT.txt').write_text('Portable local NYC v4 project. Set BLENDER_EXE; FFmpeg must be in PATH. See README.md. No weights required.\n')
def stamp(t):
 h,m,s=t.split(':');return f'{int(h):02d}:{int(m):02d}:{float(s):06.3f}'.replace('.',',')
rows=[]
for l in (W/'subtitles.ass').read_text(encoding='utf8').splitlines():
 if l.startswith('Dialogue:'):
  p=l.split(',',9);rows.append(f"{len(rows)+1}\n{stamp(p[1])} --> {stamp(p[2])}\n{p[9].replace(chr(92)+'N',chr(10))}\n")
(W/'subtitles.srt').write_text('\n'.join(rows),encoding='utf8')
for n in ['README.md','BRIEF.md','CREDITS.md','subtitles.ass','subtitles.srt','budget.json','subtitle-validation.json','source-validation.json']:shutil.copy2(W/n,O/n)
shutil.copy2(W/'subtitles.srt',P/'subtitles.srt');shutil.copy2(W/'transition-preview.mp4',O/'transition-preview-720p.mp4')
print('PROJECT COPIED',flush=True)
