# Онтологический рэп — ADV feat. Ежи

Локальный MiniMax Music 3, новый текст `Lyrics/rap-2.txt`. Исходный файл сохранён
без исправления авторских слов и формулировок. Производный brief удаляет технические
ремарки из произносимого текста, сохраняет названия секций и заменяет только
`это реп трек` на `это рэп трек`, `Adventus Devotus` на `Адвентус Девотус`.

Музыкальное задание актуальной редакции: abstract boom bap, запрошенные 96 BPM,
dusty jazz breaks, distorted upright bass, dissonant Rhodes, scratches, rapid rap. BPM и манера подачи являются
пожеланиями модели, не измеренными свойствами готового файла. Seed 2026110702,
бюджет 220 секунд, 30 шагов, guidance 1.7, AR guidance 1.5, top_k 50.

Основная партия и приветствие — ADV. Ежи получает два коротких саркастических ответа:

1. Бридж: «Ха. Вещь в себе смеется тебе в лицо» — ответ на вопрос о познании вещи в себе.
2. Концовка: «Проверь библиографию, голубчик. Ты не прошел рецензирование» — финальный вердикт.

Границы назначаются по фактически полученной записи, затем голос переносится через
Seed-VC. Нет добавленного эха/реверберации. Генеративные эффекты исходного минуса
могут сохраняться. Полное совпадение дикции и тембра не гарантируется.

## Воспроизведение

Закреплённые модели/runtime/лицензии: `music/minimax.lock.json`,
`music/voice-models.lock.json`, `benchmark/native-runtime.lock.json`, `music/ADV_EZHI.md`.
Те же локальные MiniMax Q4/Q8/Q4, BS-RoFormer и Seed-VC Q8, что в предыдущих треках.
Веса, личные референсы, полные WAV и промежуточные дорожки исключены из git.

```powershell
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-rap2-boombap-02 --brief music/rap2/boombap.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/rap2 --source-prefix minimax-rap2- boombap-02
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/rap2 boombap-02
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/rap2/boombap-02 --timeline music/rap2/boombap.timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/rap2/boombap-02 --output results/productions/minimax-rap2-boombap-02 --timeline music/rap2/boombap.timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id minimax-rap2-boombap-02 --work-dir work/rap2/boombap-02
```

Для нового синтеза нужны свободные выходные каталоги; существующие результаты
не перезаписываются. При изменении основы временные метки надо выбрать заново.

## Изменение исходника во время работы

Первый локальный дубль (drill, 142 BPM, 140.47 с) создан по начальной редакции,
но пользователь изменил rap-2.txt во время обработки: boom bap 96 BPM и без английского
вступления. Проверка SHA обнаружила расхождение. Первый дубль сохранён локально
как superseded; финальный трек генерируется заново по обновлённому файлу.
Снимок актуального текста: music/rap2/source-lyrics-02.txt. Текст пользователя не
переписывался; секции Intro/Verse/Chorus/Bridge/Outro добавлены только в brief.

Финальный дубль завершён. Подробные численные проверки, таймкоды и замеры:
`results/productions/minimax-rap2-boombap-02/verification.json` и `RESULTS.md`.
Экспорт аудио и короткой подборки Ежи:
`.venvs/qwen/Scripts/python.exe music/export-rap2.py --run-id minimax-rap2-boombap-02 --output <новый-каталог>`.
