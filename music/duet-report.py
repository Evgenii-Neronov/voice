"""Validate the three duet renders and summarize their actual results."""
import hashlib,json
from pathlib import Path
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[1]; variants=['minimax-room','ace-boombap','ace-industrial']; rows=[]
def sha(path):
 with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
original_hash=sha(ROOT/'Lyrics/lyrics.txt')
for variant in variants:
 out=ROOT/'results/productions'/('duet-'+variant); m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
 assert m['brief']['original_lyrics_sha256']==original_hash
 for r in m['audio']: assert sha(out/r['file'])==r['sha256'],r['file']
 x,sr=sf.read(out/'full.wav',always_2d=True); assert np.isfinite(x).all() and np.max(np.abs(x))<1 and x.shape[1]==2
 assert abs(len(x)/sr-m['duration'])<1/sr
 timeline=m['timeline']; coverage=sum(r['end']-r['start'] for r in timeline['ezhi_regions'])
 assert timeline['ezhi_regions'][0]['start']==0
 assert coverage>35,'Ezhi must have substantially more than the old six-second hook'
 generated=json.loads((ROOT/'results/music'/('duet-'+variant)/'manifest.json').read_text(encoding='utf-8'))
 seconds=generated.get('generation_seconds',generated.get('whole_run_seconds'))
 timings=', '.join(f"{r['start']:.1f}–{r['end']:.1f}" for r in timeline['ezhi_regions'])
 log=(out/'mastering.log').read_text(encoding='utf-8',errors='replace')
 mastering=json.JSONDecoder().raw_decode(log[log.rfind('{'):])[0]
 assert float(mastering['output_tp'])<=-1.4
 m['validation']={'all_audio_hashes_match':True,'no_sample_clipping':True,'original_lyrics_unchanged':True,'ezhi_region_seconds':coverage,'ezhi_region_share':coverage/(m['duration']-2),'human_listening_review':False,'generation_seconds':seconds,'mastering_output':mastering}
 m['reference_audio']=[{'role':role,'sha256':sha(ROOT/'work/duets'/variant/'refs'/file),'duration':sf.info(ROOT/'work/duets'/variant/'refs'/file).duration,'file_contents_committed':False} for role,file in [('ADV','adv.wav'),('Ezhi','ezhi-conversion.wav')]]
 (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows.append(f"| [{variant}](duet-{variant}/full.mp3) | {m['duration']:.2f} | {coverage:.1f} ({100*coverage/(m['duration']-2):.1f}%) | {seconds:.1f} | {m['voice_conversion']['whole_run_seconds']:.1f} |")
 rows.append(f"\nЕжи, секунды от начала `{variant}`: {timings}.\n")
text='''# Три локальные версии ADV + Ежи

Музыкальное приветствие в начале исполнено голосом Ежи через перенос тембра;
отдельного TTS в этих версиях нет. Все вычисления локальные. Полный процесс,
лицензии и ограничения: [DUET_VARIANTS.md](../../music/DUET_VARIANTS.md).

| Вариант / MP3 | Длительность, с | Участки Ежи, с (% времени без хвоста) | Генерация, с | Конверсия, с |
|---|---:|---:|---:|---:|
'''
# Keep the table contiguous, then list role timings beneath it.
table=[line for line in rows if line.startswith('|')]; notes=[line for line in rows if not line.startswith('|')]
text+='\n'.join(table)+'\n'+'\n'.join(notes)
text+='''
Время ACE — синтез без загрузки; время MiniMax включает весь запуск.
Доли Ежи — длительность назначенных интервалов, включая паузы внутри них,
не доля всех слов. Для каждой версии есть preview.mp3 и fx-dry-then-wet.mp3.
В последнем сначала сухой фрагмент, затем тот же фрагмент с пространством.

Проверены SHA256, конечный сигнал, отсутствие sample clipping, длительность,
неизменность исходного lyrics.txt и назначение начала Ежи. ASR помогает выбрать
таймкоды, но не доказывает правильность акцента, сходство голосов или произнесение
каждого слова. Музыкальные генераторы могут менять/пропускать строки, ударения
и уходить от запрошенного BPM/чистого рэпа. Качество оценивается прослушиванием.
'''
(ROOT/'results/productions/DUET_VARIANTS.md').write_text(text,encoding='utf-8')
print('Validated three duet variants')
