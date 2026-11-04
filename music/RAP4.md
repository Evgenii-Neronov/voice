# Рэп 4 — семинар, ADV feat. Ежи

Исходник `I:/MyMusic/13 - New Rap/rap-4.txt`, неизменённый снимок `music/rap4/source.txt`.
Настройки и SHA256: `music/rap4/brief.json`. Авторский текст сохранён, технические
ремарки исключены из произносимого текста. Секции сохранены. Фонетические замены
только в brief: «реп трек» → «рэп трек», Adventus Devotus → Адвентус Девотус.

Локальный MiniMax Music 3 Q4/Q8/Q4, abstract boom bap с запрошенными 96 BPM,
быстрая ритмичная читка, четыре куплета. Seed 2026110901, бюджет 300 секунд,
30 шагов, guidance 1.7, AR guidance 1.5, top_k 50. Темп/подача — пожелания модели.

Всё ADV, кроме двух коротких вопросов Ежи:
- «И кто назвал естественным / То, что пришлось воспроизводить насилием?»
- «Кто дал ему право говорить от имени общества?»

Сухое сведение, без добавленного эха и реверберации. BS-RoFormer разделяет основу,
Seed-VC переносит тембр с сохранением музыкальной ритмики. Веса и личные референсы
не входят в git. Закреплённые модели, лицензии и runtime: music/minimax.lock.json,
music/voice-models.lock.json, benchmark/native-runtime.lock.json, music/ADV_EZHI.md.

```powershell
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-rap4-01 --brief music/rap4/brief.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/rap4 --source-prefix minimax-rap4- 01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/rap4 01
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/rap4/01 --timeline music/rap4/timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/rap4/01 --output results/productions/minimax-rap4-01 --timeline music/rap4/timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id minimax-rap4-01 --work-dir work/rap4/01
```

Повторный запуск требует новых каталогов. Для новой генерации временные метки
выбираются заново. ASR не является гарантией точной дикции, следования всему тексту
или сходства тембра. Полные WAV и дорожки сохраняются локально для редактирования.
