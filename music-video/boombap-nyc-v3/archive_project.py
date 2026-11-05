from pathlib import Path
import zipfile,shutil,json
w=Path('work/nyc-boombap-v3');o=Path('outputs/nyc-boombap-v3-1440p')
for name in ['README.md','subtitles.ass','subtitles.srt','ASSET-SOURCES.md']:shutil.copy2(o/name,o/'project'/name)
with zipfile.ZipFile(o/'editable-3D-project-v3.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in (o/'project').rglob('*'):
  if p.is_file() and p.suffix!='.blend1':z.write(p,p.relative_to(o))
 for name in ['README.md','subtitles.ass','subtitles.srt','ASSET-SOURCES.md']:z.write(o/name,name)
print('Archive bytes',(o/'editable-3D-project-v3.zip').stat().st_size)
