from pathlib import Path
W=Path(__file__).resolve().parent;V2=W.parent/'nyc-boombap-v2';O=W.parents[1]/'outputs/nyc-boombap-v3-1440p';O.mkdir(parents=True,exist_ok=True)
for name in ['render_baked.py','run_full.py','verify_final.py','postrender.py','archive_project.py','package_project.py']:
 s=(V2/name).read_text(encoding='utf-8-sig').replace('boombap-v2','boombap-v3').replace('film-v2','film-v3').replace('NYC-v2','NYC-v3').replace('NYC-boombap-v2','NYC-boombap-v3').replace('project-v2','project-v3')
 if name=='verify_final.py':s=s.replace("'Reference-inspired passerby wardrobe and nominal 1.83m rest body height; not exact likeness reconstruction',",'').replace('3-second approach/pause temporal contact sheet','V3 moving opening/transition preview and all-frame skeletal continuity audit')
 (W/name).write_text(s,encoding='utf8')
s=(V2/'subtitles.ass').read_text(encoding='utf8').replace('220,220,190,1','220,220,144,1');(W/'subtitles.ass').write_text(s,encoding='utf8');(O/'subtitles.ass').write_text(s,encoding='utf8')
import shutil
for name in ['subtitles.srt','ROCKETBOX-LICENSE.md','RubikWetPaint-OFL.txt']:
 for src in [V2/name,W.parents[1]/'outputs/nyc-boombap-v2-1440p'/name,W.parents[1]/'outputs/nyc-boombap-v2-1440p/project'/name]:
  if src.exists():shutil.copy2(src,O/name);break
