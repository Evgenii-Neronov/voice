from pathlib import Path
import json,subprocess,math
from PIL import ImageFont
w=Path(__file__).resolve().parent
out=w.parents[1]/'outputs/rap18-print-1440p'
out.mkdir(exist_ok=True)
words=json.loads((w/'fresh-words.json').read_text(encoding='utf8'))
lyrics=[l.strip().replace('—','-').replace('–','-') for l in (w.parents[1]/'outputs/rap-18/rap-18.txt').read_text(encoding='utf-8-sig').splitlines() if l.strip() and not l.startswith('[')]
groups=[[23,35,50],[66,72,79,84,91,99,108,115,123,130,139],[181,188,194,201,207,216,223],[247,255,266,274,282,288,295],[319,330,338,345,353,359,364,369,377],[387,397,404,408],[408,414,420,425]]
pairs=[(a,b) for g in groups for a,b in zip(g,g[1:])]
assert len(lyrics)==len(pairs)
def tc(t):
    k=round(t*100)
    return f'{k//360000}:{k//6000%60:02}:{k//100%60:02}.{k%100:02}'
header=(w.parent/'rap4-montage-v4/subtitles.ass').read_text(encoding='utf8').split('Dialogue:')[0]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',56)
for line,(a,b) in zip(lyrics,pairs):
    lines=['']
    for word in line.split():
        if font.getlength(lines[-1]+' '+word)>2020:lines.append(word)
        else:lines[-1]=(lines[-1]+' '+word).strip()
    start=words[a]['start'];end=min(words[b]['start'],words[b-1]['end']+.15)
    header+=f'Dialogue: 0,{tc(start)},{tc(max(start+.14,end))},Cinema,,0,0,0,,'+r'\N'.join(lines)+'\n'
(w/'subtitles.ass').write_text(header,encoding='utf8')
target=out/'ADV-rap18-Ottisk-1440p.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i','picture.mp4','-i',str(w.parents[1]/'outputs/rap-18/rap-18.mp3'),'-map','0:v','-map','1:a','-vf','ass=subtitles.ass','-c:v','h264_nvenc','-cq','18','-preset','p5','-b:v','0','-c:a','copy','-movflags','+faststart',str(target)],check=True,cwd=w)
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(target),'-f','null','-'],check=True)
