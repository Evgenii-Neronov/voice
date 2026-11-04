# MiniMax: ADV и четырёхстрочный хук Ежи

Запрос 2026-11-04: новый полный трек из актуального Lyrics/lyrics.txt.
Все партии, включая музыкальное приветствие, — ADV. Только четыре последовательные
строки хука — Ежи: «Десять свистулек! / Один кубит! / Кто здесь субъект? / Кто кого купит?».
Добавленные эхо и реверберация отсутствуют. Старые версии сохранены.

## Фактическая основа

- Source SHA256: 5b0dafdac0269470bb67f7c8e07f6f8997bbbe3b143ada4ee39d0afabba39c01.
  Проверен файл с приветствием и строкой «Денежного обмена нет — а эквивалент есть!».
  Сам исходный файл не изменялся в этом запуске.
- MiniMax Music 3 GGUF Q4/Q8/Q4, прежний выбранный caption, новый seed 2026110577.
- Музыкальная основа 251,7275 с; запуск MiniMax 382,7866 с.
- Приветствие включено в lyrics музыкального движка; имя передано фонетически
  «Эй Ди Ви, ака Адвентус Девотус» только в производном запросе.
- BS-RoFormer Q8 разделяет вокал и инструментал; Seed-VC v1_svc Q8, 40 шагов,
  блоки 12 с с контекстом ±0,4 с переносят тембры по пользовательским референсам.
- Ежи: 146,66–152,38 с (2:26,66–2:32,38). Предыдущая фраза заканчивается около
  146,62 с, следующая начинается около 152,46 с по локальному Whisper. Переходы 60 мс.
- Все остальные участки вокала, включая приветствие и первую половину Hook, — ADV.
- WAV 24-bit, 44,1 kHz stereo; MP3 256 kbps; цель loudnorm -14 LUFS / -1,5 dBTP.

Таймкоды помогают назначить голоса, но не доказывают правильность каждого слова.
ASR может ошибаться на музыкальной подаче. Сходство голосов и художественное качество
не оценивались человеком; генератор может повторять строки или менять произношение.
Версии, источники и лицензии моделей прежние: music/minimax.lock.json,
music/voice-models.lock.json и music/ADV_EZHI.md. Никакого облачного синтеза.

## Повторение

```powershell
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-hook-01 --brief music/minimax-hook-01.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/performances --source-prefix minimax- hook-01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/performances hook-01
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/performances/hook-01 --timeline music/minimax-hook-01.timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/performances/hook-01 --output results/productions/minimax-hook-01 --timeline music/minimax-hook-01.timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id minimax-hook-01 --work-dir work/performances/hook-01
```

Генераторы/сведение отказываются перезаписывать существующие выходные каталоги.
Для нового дубля нужны новое имя запуска и новая проверка таймкодов. Полные WAV,
референсы, промежуточные дорожки и веса остаются локально в gitignored каталогах.
Готовые небольшие MP3 и отчёты сохраняются в git. Итоги проверки финального WAV,
контрольные суммы, референсные SHA256 и точные времена этапов — verification.json
в results/productions/minimax-hook-01.

Финальные проверки пройдены: длительность 251.728 с, разделение 40.23 с, перенос голосов 119.93 с. Проверены отдельные короткие участки ADV и Ежи; ASR-расшифровки остаются приблизительными.
