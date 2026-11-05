from pathlib import Path
import json,shutil
W=Path(__file__).resolve().parent;D=6079/24
raw=[(0,17.34,'street'),(17.34,28.16,'studio'),(28.16,43.54,'street'),(43.54,54.20,'roof'),(54.20,59.68,'graffiti'),(59.68,79.76,'street'),(79.76,94.26,'metro'),(94.26,107.46,'street'),(107.46,120.54,'lab'),(120.54,129.10,'studio'),(129.10,146.48,'street'),(146.48,156.90,'roof'),(156.90,166.77,'graffiti'),(166.77,177.92,'street'),(177.92,195.58,'lab'),(195.58,207.88,'street'),(207.88,220.50,'metro'),(220.50,230.08,'street'),(230.08,234.92,'graffiti'),(234.92,243.82,'studio'),(243.82,D,'street')]
purpose={'street':'Return to the accepted live performance and listening group','studio':'Vinyl grooves connect circular time to a tangible hip-hop instrument','roof':'City scale and a growing wire cube contrast with the enclosed street','graffiti':'Paint grows from circular clay-like forms into a branching computation mesh','metro':'Pass foreground columns and a train; a tangible machine carries the visual rhythm','lab':'Clay whistles and a cold computing rack share one industrial workbench'}
plan=[]
for i,(a,b,scene) in enumerate(raw):
 first=round(a*24);end=round(b*24)
 plan.append({'index':i,'scene':scene,'start_frame':first,'end_frame':end,'start':first/24,'end':end/24,'frames':end-first,'purpose':purpose[scene],'camera':'Preserve original camera' if scene=='street' else 'Travel across near props to reveal main subject, then hold; alternate macro and wide compositions','foreground':'Columns, shelving, tonearm or roof rails','midground':'Record deck / train / clay-and-server table / painted marks','background':'Architectural depth and practical lights','sound_relationship':'Boundaries follow existing lyric phrases; rotation and growth are deliberate slow visual motifs, not every-beat flashing','transition':'Clean cut, with painted growth confined to inserts'})
(W/'edit-plan.json').write_text(json.dumps(plan,indent=2));street=sum(s['frames'] for s in plan if s['scene']=='street');assert abs(street/6079-.5)<.01
(W/'budget.json').write_text(json.dumps({'total_frames':6079,'street_frames':street,'street_percent':100*street/6079,'new_2d_frames':sum(s['frames'] for s in plan if s['scene']=='graffiti'),'new_3d_frames':sum(s['frames'] for s in plan if s['scene'] not in ['graffiti','street'])},indent=2))
src=(W.parent/'nyc-boombap-v3/subtitles.ass').read_text(encoding='utf8');dst=src.translate(str.maketrans({'—':'-','–':'-','−':'-'}));(W/'subtitles.ass').write_text(dst,encoding='utf8');(W/'subtitle-baseline.ass').write_text(src,encoding='utf8')
(W/'subtitle-validation.json').write_text(json.dumps({'replacements':sum(src.count(x) for x in '—–−'),'timings_unchanged':True,'margin_bottom_px':144},indent=2))
print('Street percent',100*street/6079)
