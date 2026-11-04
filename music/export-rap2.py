"""Export a verified local MiniMax production and short guest-voice preview."""
import argparse,hashlib,json,shutil,subprocess,sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
d=R/'results/productions'/a.run_id
m=json.loads((d/'manifest.json').read_text(encoding='utf-8'));v=json.loads((d/'verification.json').read_text(encoding='utf-8'));g=json.loads((R/'results/music'/a.run_id/'manifest.json').read_text(encoding='utf-8'))
assert v['numerical_validation_passed'] and v['sha256_validation_passed']
a.output.mkdir(parents=True,exist_ok=False)
for ext in ['mp3','wav']:
 target=a.output/('ADV-Ezhi-Rap2.'+ext);shutil.copy2(d/('full.'+ext),target)
 with target.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
 assert digest==next(row['sha256'] for row in m['audio'] if row['file']=='full.'+ext)
regions=m['timeline']['ezhi_regions'];parts=[]
for i,r in enumerate(regions):parts.append(f"[0:a]atrim=start={max(0,r['start']-2)}:end={min(m['duration'],r['end']+2)},asetpts=PTS-STARTPTS[a{i}]")
filt=';'.join(parts)+';'+''.join(f'[a{i}]' for i in range(len(regions)))+f'concat=n={len(regions)}:v=0:a=1[out]'
subprocess.run(['ffmpeg','-v','error','-i',str(d/'full.wav'),'-filter_complex',filt,'-map','[out]','-b:a','256k',str(a.output/'Ezhi-preview.mp3')],check=True)
for name in ['manifest.json','verification.json']:shutil.copy2(d/name,a.output/name)
lines=['# Рэп 2 — ADV feat. Ежи','',f"Длительность: {m['duration']:.2f} с. Музыка и голоса синтезированы локально. Основная партия и приветствие — ADV; Ежи только в перечисленных интервалах. Сведение без добавленных эха и реверберации.",'','| Ежи, секунды | Реплика |','|---|---|']
for r in regions:lines.append(f"| {r['start']:.2f}–{r['end']:.2f} | {' '.join(r['lyrics'])} |")
lines+=['',f"Генерация основы: {v['generation_seconds']:.1f} с; разделение: {v['separation_seconds']:.1f} с; перенос голосов: {v['conversion_seconds']:.1f} с.",f"Исходный текст SHA256: `{v['lyrics_sha256']}`.",'','WAV: стерео 44.1 кГц, 24 бит. Численная проверка, длительность и SHA256 пройдены. Локальное распознавание использовано для границ и выборочной проверки; оно не подтверждает идеальную дикцию и сходство тембра. Прослушивание человеком не проводилось.','', 'Во время первого запуска исходный файл изменился. Финальный трек создан заново по обновлённой версии: boom bap 96 BPM, без английского вступления. Первый drill-дубль сохранён отдельно и не входит в эту выдачу.','']
report='\n'.join(lines);(a.output/'RESULTS.md').write_text(report,encoding='utf-8');(d/'RESULTS.md').write_text(report,encoding='utf-8')
shutil.copy2(R/'music/RAP2.md',a.output/'PRODUCTION.md')
print(report)
