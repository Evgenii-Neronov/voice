# Онтологический надрыв — ADV feat. Ежи

Один локальный MiniMax Music 3 трек по `I:/MyMusic/13 - New Rap/rap-3.txt`.
Неизменённый снимок исходника: `music/rap3/source.txt`; параметры, SHA256 и
производный текст: `music/rap3/brief.json`. Технические ремарки убраны из
произносимого текста, секции сохранены; Adventus Devotus передан кириллицей,
«реп трек» — «рэп трек». Авторские слова не исправлялись.

Основной голос и приветствие ADV. Одна короткая вставка Ежи в бридже:
«Аксиома? Нет, властный дискурс. Истина? Нет, гегемония».
Сведение без добавленного эха и реверберации. Стиль: aggressive boom bap,
94 BPM (пожелание модели), distorted 808, detuned brass, double-time rap.
Seed 2026110801, бюджет 200 секунд, 30 шагов, guidance 1.7 / AR 1.5, top_k 50.

Модели/лицензии/версии прежнего процесса: music/minimax.lock.json,
music/voice-models.lock.json, benchmark/native-runtime.lock.json, music/ADV_EZHI.md.
Весь синтез локальный: MiniMax → BS-RoFormer → Seed-VC → сухое сведение.
Веса, личные референсы и полные WAV не публикуются в git.

```powershell
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-rap3-01 --brief music/rap3/brief.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/rap3 --source-prefix minimax-rap3- 01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/rap3 01
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/rap3/01 --timeline music/rap3/timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/rap3/01 --output results/productions/minimax-rap3-01 --timeline music/rap3/timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id minimax-rap3-01 --work-dir work/rap3/01
```

Повторный запуск требует новых выходных каталогов. Для новой основы временные
метки голосов надо выбирать заново. Распознавание используется для границ,
но не гарантирует идеальную дикцию, буквальное следование тексту или сходство тембра.
