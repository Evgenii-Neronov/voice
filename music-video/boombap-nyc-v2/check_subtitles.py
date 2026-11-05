from pathlib import Path
import re,json
from PIL import ImageFont
w=Path('work/nyc-boombap-v2');a=(w.parent/'nyc-boombap/subtitles.ass').read_text(encoding='utf-8-sig');b=(w/'subtitles.ass').read_text(encoding='utf-8-sig');old=[x for x in a.splitlines() if x.startswith('Dialogue:')];new=[x for x in b.splitlines() if x.startswith('Dialogue:')];assert old==new
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',56);widths=[]
for l in new:
 text=l.split(',',9)[9]
 for s in text.split('\\N'):widths.append({'text':s,'width_px':round(font.getlength(s),1)})
maxwidth=max(widths,key=lambda x:x['width_px']);assert maxwidth['width_px']<2240,maxwidth
r={'dialogue_count':len(new),'text_and_timings_identical_to_v1':True,'bottom_margin_px':190,'render_height_px':1440,'max_line':maxwidth,'conservative_text_width_limit_px':2240}
(w/'subtitle-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=True))
