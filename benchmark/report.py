"""Validate generated PCM WAVs and build a factual report (no invented ratings)."""
import hashlib
import json
from pathlib import Path
import wave
ROOT = Path(__file__).resolve().parents[1]
lines=['# Фактические локальные результаты','','Автоматические метрики не оценивают эмоции или качество русского. `generated_unrated` требует прослушивания.','','| Запуск | Тест | Статус | Аудио, с | Генерация, с | RTF |','|---|---|---|---:|---:|---:|']
errors=[]
for manifest_path in sorted((ROOT/'results').glob('*/manifest.json')):
    data=json.loads(manifest_path.read_text(encoding='utf-8'))
    rows=data.get('cases',[])
    if not rows:
        lines.append(f"| {manifest_path.parent.name} | whole run | {data['status']} | — | — | — |")
    for row in rows:
        if row['status']=='generated_unrated':
            file=manifest_path.parent/row['wav']
            assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'],file
            with wave.open(str(file),'rb') as w:
                assert w.getnchannels()==1 and w.getsampwidth()==2,file
                assert abs(w.getnframes()/w.getframerate()-row['duration_seconds'])<1e-5,file
            lines.append(f"| {manifest_path.parent.name} | {row['id']} | {row['status']} | {row['duration_seconds']:.2f} | {row['generation_seconds']:.2f} | {row['rtf']:.2f} |")
        else:
            lines.append(f"| {manifest_path.parent.name} | {row['id']} | failed | — | — | — |")
            errors.append((manifest_path.parent.name,row['id'],row.get('error','')))
    if data.get('error'):
        errors.append((manifest_path.parent.name,'load/run',data['error']))
    for row in data.get('audio',[]):
        file=manifest_path.parent/row['file']
        assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256'],file
        lines.append(f"| {manifest_path.parent.name} | song | generated_unrated | {row['duration']:.2f} | {data['generation_seconds']:.2f} | {data['generation_seconds']/row['duration']:.2f} |")
lines += ['', '## Ошибки', '']
for run,case,error in errors:
    lines += [f'### {run}: {case}','','```text',error.strip(),'```','']
if not errors:
    lines.append('В сохранённых manifests ошибок нет.')
(ROOT/'results/SUMMARY.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')
print('Validated manifests and WAV hashes; wrote results/SUMMARY.md')
