"""Validate saved music manifests against actual files and write measured results."""
import hashlib,json
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
 with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
source_hash=sha(ROOT/'Lyrics/lyrics.txt')
rows=[]; checks=[]
for path in sorted((ROOT/'results/music').glob('*/manifest.json')):
 m=json.loads(path.read_text(encoding='utf-8'))
 assert m['source_lyrics_sha256']==source_hash
 if m['status']=='running': raise RuntimeError(f'Still running: {path.parent.name}')
 for record in m.get('audio',[])+m.get('delivery',[]):
  file=path.parent/record['file']; assert sha(file)==record['sha256'],file
  if file.suffix=='.wav':
   x,sr=sf.read(file,always_2d=True)
   assert x.size and np.isfinite(x).all() and np.abs(x).max()>0,file
   if 'duration' in record: assert abs(len(x)/sr-record['duration'])<1/sr
  checks.append(str(file.relative_to(ROOT)))
 a=m.get('audio',[{}])[0] if m.get('audio') else {}
 seconds=m.get('generation_seconds',m.get('whole_run_seconds',0))
 scope='синтез, без загрузки' if 'generation_seconds' in m else 'весь запуск'
 mem=f"{m['torch_peak_allocated_bytes']/2**30:.2f} GiB PyTorch" if 'torch_peak_allocated_bytes' in m else f"{m.get('whole_gpu_peak_used_mib',0)} MiB вся карта"
 rows.append(f"| [{path.parent.name}](../results/music/{path.parent.name}/manifest.json) | {m['status']} | {a.get('duration',0):.2f} | {a.get('sample_rate','—')} | {seconds:.2f}, {scope} | {mem} |")
header='''# Музыкальный benchmark: фактические результаты

2026-11-04, RTX 5080 16 GB. Все перечисленные записи получены локально.
Исследование: [MUSIC_RESEARCH.md](MUSIC_RESEARCH.md). Команды и зависимости:
[music/README.md](../music/README.md).

| Запуск / manifest | Статус | Звук, с | Hz, stereo | Время, с | Память |
|---|---|---:|---:|---|---|
'''
footer='''

`generated_unrated` означает успешный синтез и техническую проверку без слуховой
оценки. Нельзя заключить по SHA или RMS, что все слова прозвучали правильно.
Полные ACE-запросы содержат исходные 92 строки; MiniMax intro — только 8 строк
вступления, MiniMax full — весь текст. У моделей разные способы задания длины,
поэтому это практическая проверка работоспособности, не строго уравненный рейтинг.

ACE: 8 шагов, CPU offload, без дополнительной LM; seed 20261104/20261105,
параметры 96 BPM, D minor, 4/4. Память — максимум allocated PyTorch во время
генерации; не включает другие приложения, драйвер и весь reserved pool.
MiniMax: Q4/Q8/Q4, mem_saver=true, cuda_perf, 30 flow steps. Его память — максимум
занятости всей карты, опрос примерно раз в две секунды; метрики памяти несопоставимы
напрямую с PyTorch. Native runtime.log содержит собственное время запроса и host RAM.

MiniMax duration_sec ограничивает AR-бюджет и не задаёт точную длину аудио.
Короткий запрос с бюджетом 30 секунд дал 17,74 секунды. В официальной карточке
указано 32 kHz, но скачанный GGUF vocoder config содержит sampling_rate=44100;
runtime реально записывает 44,1 kHz. Здесь сохранена фактическая частота без
принудительной передискретизации. Порт не проверялся на численную эквивалентность
официальному Python inference.

Полные `full.wav` оставлены локально и исключены из git. В каждом каталоге
запуска доступны `full.mp3`, короткое `preview.wav`, manifest; у MiniMax также
сохранены requests.json и runtime.log. Бит создан самостоятельно, это не stem
полного трека. Существующие TTS-результаты не изменялись.

Проверены SHA256, читаемость всех WAV, конечный ненулевой сигнал, длительности
и неизменность исходной лирики. Отчёт проверки: `results/music/validation.json`.
Для полного художественного контроля остаётся прослушать дикцию и сверить все
строки, а также оценить читку, ритм и аранжировку. Автоматический ASR/WER не выполнялся.
'''
(ROOT/'docs/MUSIC_RESULTS.md').write_text(header+'\n'.join(rows)+footer,encoding='utf-8')
(ROOT/'results/music/validation.json').write_text(json.dumps({'source_sha256':source_hash,'verified_files':checks,'auditory_review':False},indent=2)+'\n',encoding='utf-8')
print(f'Validated {len(checks)} files from {len(rows)} runs')
