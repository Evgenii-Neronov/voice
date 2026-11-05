from pathlib import Path
import shutil,json
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/rap4-cartoon-v2-1440p';P=O/'project';P.mkdir(exist_ok=True)
files=['art.py','sprites.py','build_scene.py','finish_scene.py','render_part.py','run_render.py','visemes.npy','beats.json','alignment.json','sections.json','subtitles.ass','subtitles.srt','shot-plan.json','BRIEF.md','README.md','subtitle-validation.json','neck-validation.json','fresh-words.json','retranscribe.py','final_subtitles.py','audit_motion.py']
files.extend(['previous-alignment.json','subtitle-style.ass','lyrics-source.json','align.py'])
for name in files:shutil.copy2(W/name,P/name)
shutil.copytree(W/'assets',P/'assets',dirs_exist_ok=True);shutil.copytree(W/'sprites',P/'sprites',dirs_exist_ok=True)
(P/'audio').mkdir(exist_ok=True);shutil.copy2('I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3',P/'audio/track.mp3')
s=(P/'run_render.py').read_text(encoding='utf8');s=s.replace("OUT=ROOT/'outputs/rap4-cartoon-v2-1440p'","OUT=W/'renders'").replace("BLENDER=W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'","BLENDER=Path(__import__('shutil').which('blender') or "+repr(str(W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe'))+")")
s=s.replace("audio='I:/MyMusic/13 - New Rap/all-original-voices/main/14-minimax-rap4-dialogue-final-01.mp3'","audio=str(W/'audio/track.mp3')")
(P/'run_render.py').write_text(s,encoding='utf8')
(P/'requirements.txt').write_text('skia-python==144.1\nnumpy==2.5.4\nscipy==1.18.1\nPillow==13.0.0\n',encoding='utf8')
for name in ['subtitles.ass','subtitles.srt','BRIEF.md','subtitle-validation.json','neck-validation.json']:shutil.copy2(W/name,O/name)
print('Project files copied',flush=True)
