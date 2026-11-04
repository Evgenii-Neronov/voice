"""Export the three dry MiniMax arrangements and their measured run report."""
import argparse,json,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
rows=[]
for number,variant in enumerate(['boombap','breakbeat','funk'],1):
 run='minimax-trio-'+variant+'-01'; folder=R/'results/productions'/run
 v=json.loads((folder/'verification.json').read_text(encoding='utf-8'))
 assert v['numerical_validation_passed'] and len(v['ezhi_regions_seconds'])==2
 stem=f'{number:02}-{variant}-ADV-Ezhi'
 for suffix in ['mp3','wav']:
  dest=a.output/(stem+'.'+suffix)
  if dest.exists(): raise FileExistsError(dest)
  shutil.copy2(folder/('full.'+suffix),dest)
 parts=[]
 for i,(start,end) in enumerate(v['ezhi_regions_seconds']):
  parts.append(f'[0:a]atrim=start={max(0,start-2)}:end={min(v["duration"],end+2)},asetpts=PTS-STARTPTS[a{i}]')
 filt=';'.join(parts)+';[a0][a1]concat=n=2:v=0:a=1[out]'
 subprocess.run(['ffmpeg','-v','error','-i',str(folder/'full.wav'),'-filter_complex',filt,'-map','[out]','-b:a','256k',str(a.output/(stem+'-both-hooks.mp3'))],check=True)
 shutil.copy2(folder/'verification.json',a.output/(stem+'-verification.json'))
 rows.append({'variant':variant,'file':stem,'duration_seconds':v['duration'],'ezhi_regions_seconds':v['ezhi_regions_seconds'],'generation_seconds':v['generation_seconds'],'conversion_seconds':v['conversion_seconds'],'conversion_reused_chunks':v['conversion_reused_chunks'],'conversion_fallbacks':v['conversion_fallbacks'],'separation_seconds':v['separation_seconds']})
lines=['# Три сухих MiniMax-варианта','', 'Весь основной вокал и приветствие преобразованы по референсу ADV. Ежи — только два четырёхстрочных блока. Новые основы созданы локально на RTX 5080; затем разделены на дорожки и преобразованы через Seed-VC. Эхо и реверберация при сведении не добавлялись.','', '| Вариант | Длительность | Ежи, секунды | Генерация основы | Перенос голосов |','|---|---:|---|---:|---:|']
for r in rows:
 times='; '.join(f'{s:.2f}–{e:.2f}' for s,e in r['ezhi_regions_seconds'])
 lines.append(f"| {r['variant']} | {r['duration_seconds']:.2f} с | {times} | {r['generation_seconds']:.1f} с | {r['conversion_seconds']:.1f} с |")
lines+=['','В boom bap перенос был продолжен после сбоя на инструментальном хвосте без определяемой высоты голоса: 21 готовый фрагмент использован повторно, для хвоста применён Seed-VC без F0. Время переноса этого дубля в таблице показывает только повторный запуск, без первой незавершённой попытки.','', 'Текст взят из обновлённого Lyrics/lyrics.txt с двумя повторами. Исходный файл не переписывался. Производные запросы используют кириллическое имя для произношения.','', 'Проверки: конечные WAV — стерео 44.1 кГц, численно корректны, без цифрового клиппинга; проверены хеши, исходный текст, длительность и два интервала смены голоса. Локальное распознавание использовано для границ и выборочной проверки. Оно допускает ошибки; идеальная дикция, полное буквальное совпадение всех строк и тембральное сходство не подтверждены прослушиванием человеком. Генеративные эффекты внутри исходной музыки могут сохраняться, несмотря на сухое сведение.','', 'Для дальнейшего редактирования сохранены исходные основы, раздельные вокал/минус, преобразованные голоса и отдельная разметка каждого дубля внутри локального репозитория. Полные WAV и личные референсы не публикуются в git.','']
report='\n'.join(lines)
(a.output/'RESULTS.md').write_text(report,encoding='utf-8')
(R/'music/MINIMAX_TRIO_RESULTS.md').write_text(report,encoding='utf-8')
(a.output/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(R/'music/MINIMAX_PARAMETERS.md',a.output/'PARAMETERS.md')
print(json.dumps(rows,ensure_ascii=False,indent=2))
