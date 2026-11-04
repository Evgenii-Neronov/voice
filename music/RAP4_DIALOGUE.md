# Семинар: встречные вопросы — переработка rap-4

Исходный rap-4 не изменён. Новая авторская редакция: music/rap4-dialogue/lyrics.txt.
Метки [ADV]/[EZHI] задают роли и удаляются из запроса к музыкальному генератору.
Шесть двухстрочных ответов Ежи вместо прежних двух вопросов. Сохранены четыре
куплета и основные темы; строки сокращены/переформулированы, добавлены созвучия,
рифмованные ответы и более разговорные панчи. Это творческая переработка,
а не дословная версия исходного текста.

Общие черты подачи: быстрые многосложные фразы, внутренние рифмы, синкопы,
резкие согласные, ирония. Caption не содержит имени конкретного исполнителя.
Запрошено 102 BPM; темп/подача — пожелания, не жёсткая гарантия модели.
Seed 2026111001, бюджет 300 секунд, 30 шагов, guidance 1.7 / AR 1.5, top_k 50.

Минимальный локальный стек прежних закреплённых версий: MiniMax Music3 Q4/Q8/Q4,
BS-RoFormer, Seed-VC Q8. Модели/лицензии: music/minimax.lock.json,
music/voice-models.lock.json, benchmark/native-runtime.lock.json, music/ADV_EZHI.md.
Основная партия и приветствие ADV, только шесть выбранных блоков Ежи.
Сведение без добавленного эха и реверберации. Полные WAV, веса и личные референсы
остаются локально; готовые MP3, разметка и параметры сохраняются в git.

```powershell
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-rap4-dialogue-01 --brief music/rap4-dialogue/brief.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/rap4-dialogue --source-prefix minimax-rap4-dialogue- 01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/rap4-dialogue 01
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-rap4-dialogue-outro-01 --brief music/rap4-dialogue/outro-brief.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/rap4-dialogue-outro --source-prefix minimax-rap4-dialogue-outro- 01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/rap4-dialogue-outro 01
.venvs/qwen/Scripts/python.exe music/assemble-rap4-dialogue.py
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/rap4-dialogue-final/01 --timeline music/rap4-dialogue/timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/rap4-dialogue-final/01 --output results/productions/minimax-rap4-dialogue-final-01 --timeline music/rap4-dialogue/timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id minimax-rap4-dialogue-final-01 --work-dir work/rap4-dialogue-final/01
```

Для повтора нужны новые каталоги и новая разметка фактически сгенерированных реплик.
Временные границы выбираются по локальному ASR, который не гарантирует буквальную
дикцию и сходство тембра. Голосовой перенос сохраняет музыкальную ритмику основы.

## Частичное восстановление финала

Первая генерация остановила разборчивый вокал после первой строки Outro. Два
локальных распознавания не обнаружили последние четыре строки. Досинтезирован
отдельный финал тем же MiniMax (16.86 с, 37.48 с вычислений). Вход основной
записи обрезан на 256.40 с, новый финал присоединён с перекрытием 0.12 с.
Те же операции применены к вокалу и инструменталу. Исходники сохранены.
Сценарий сборки фиксирует хеши, границы и источник каждого фрагмента; повторный
перенос голосов идёт уже по собранной записи. Это реальная замена отдельной
секции, а не повторная генерация всей композиции.
