"""Three local rap arrangements with an integrated musical greeting and Russian diction."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; folder=ROOT/'music/duet'; folder.mkdir(exist_ok=True)
base=json.loads((ROOT/'results/music/ace-turbo-full-01/manifest.json').read_text(encoding='utf-8'))['params']['lyrics']
phonetics={'Dasein':'Дазайн','Hyperstition':'Хайперстишн','CCRU':'Си-си-ар-ю','Exit':'Экзит','CEO':'си-и-оу','Patchwork':'Пэтчворк'}
for old,new in phonetics.items(): base=base.replace(old,new)
greeting='Йо, это рэп-трек!\nС вами Эй Ди Ви, ака Адвентус Девотус!'
lyrics=base.replace('[Intro]','[Intro]\n'+greeting+'\n',1)
vocal='Native Russian male rap, neutral native Russian pronunciation, clear consonants, natural spoken Russian stress, intelligible dry sardonic conversational delivery, rhythmic spoken rap throughout, no sung melody, no foreign accent. Rap the opening greeting as part of the beat. '
variants=[
 {'id':'minimax-room','engine':'minimax','seed':2026110411,'bpm':96,'duration':260,'key':'D minor','title':'MiniMax — камерный boom bap','style':'Russian jazz boom bap, 96 BPM, dusty punchy breaks, upright bass, dissonant Rhodes, restrained scratches. Spacious sparse verses, heavy rap chorus, dramatic spoken hook.','room':.7,'wet':.16,'delay_beats':.5,'delay_send':.085},
 {'id':'ace-boombap','engine':'ace','seed':2026110412,'bpm':90,'duration':270,'key':'D minor','title':'ACE — классический русский рэп','style':'Russian old-school underground hip-hop, 90 BPM, steady swinging boom bap drums, warm sampled piano, deep bass, vinyl texture, clear rap upfront, strong rhythmic verses and spoken chorus.','room':.9,'wet':.19,'delay_beats':.5,'delay_send':.10},
 {'id':'ace-industrial','engine':'ace','seed':2026110413,'bpm':104,'duration':255,'key':'F minor','title':'ACE — индустриальный рэп','style':'Russian industrial abstract hip-hop, 104 BPM, metallic percussion, broken heavy drums, distorted synth bass, ominous granular textures, tense staccato spoken rap, dramatic breaks, no melodic singing.','room':1.25,'wet':.15,'delay_beats':.75,'delay_send':.12},
]
for v in variants:
 v.update(caption=vocal+v.pop('style'),lyrics=lyrics,phonetic_substitutions=phonetics,original_lyrics_sha256=hashlib.sha256((ROOT/'Lyrics/lyrics.txt').read_bytes()).hexdigest(),greeting_source='Generated inside the music model, not separate TTS',ezhi_sections=['Intro','Chorus','Hook','Outro'])
 (folder/(v['id']+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared',len(variants),'briefs')
