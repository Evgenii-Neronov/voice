from pathlib import Path
import json
W=Path(__file__).resolve().parent;old=json.loads((W/'previous-alignment.json').read_text(encoding='utf8'));fresh=json.loads((W/'alignment.json').read_text(encoding='utf8'))
# Fresh short-chunk ASR recovered the missing middle but degraded the first verse.
# Retain the well-supported original first verse boundaries, not a global offset.
fresh[:11]=old[:11];fresh[41]['start']=131.02
for i,e in enumerate(fresh):
 e['end']=fresh[i+1]['start'] if i+1<len(fresh) else 272.3
 assert e['end']-e['start']>.7,(i,e)
 assert not any(c in e['text'] for c in '—–−')
(W/'alignment.json').write_text(json.dumps(fresh,ensure_ascii=False,indent=2),encoding='utf8')
def tc(t):
 c=round(t*100);return f'{c//360000}:{c//6000%60:02d}:{c//100%60:02d}.{c%100:02d}'
header=(W/'subtitle-style.ass').read_text(encoding='utf8').split('Dialogue:')[0]
from PIL import ImageFont
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',56)
def wrap(text):
 rows=['']
 for word in text.split():
  candidate=(rows[-1]+' '+word).strip()
  if font.getlength(candidate)>2050:rows.append(word)
  else:rows[-1]=candidate
 assert len(rows)<=2
 return r'\N'.join(rows)
(W/'subtitles.ass').write_text(header+'\n'.join(f"Dialogue: 0,{tc(e['start'])},{tc(e['end'])},Cinema,,0,0,0,,{wrap(e['text'])}" for e in fresh),encoding='utf8')
def srt(t):
 c=round(t*1000);return f'{c//3600000:02d}:{c//60000%60:02d}:{c//1000%60:02d},{c%1000:03d}'
(W/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{srt(e['start'])} --> {srt(e['end'])}\n{e['text']}" for i,e in enumerate(fresh)),encoding='utf8')
(W/'timing-review.txt').write_text('\n'.join(f"{e['start']:.2f} {e['end']:.2f} {e['text']}" for e in fresh),encoding='utf8')
report={'method':'Fresh overlapping local ASR on final vocal stem; original first 11 line anchors retained after comparison because fresh ASR dropped first-verse words. Middle rebuilt from actual word times, not uniform shift.','lines':len(fresh),'minimum_duration':min(e['end']-e['start'] for e in fresh),'overlaps':0,'ascii_hyphens':True,'corrected_middle':[{'text':e['text'],'old_start':old[i]['start'],'start':e['start']} for i,e in enumerate(fresh) if 41<=i<=50],'limitations':'Automatic word timings; unclear generated diction can still have subsecond boundary error.'}
(W/'subtitle-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('Subtitle continuity and durations passed')
