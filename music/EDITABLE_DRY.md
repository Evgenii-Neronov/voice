# Сухие пробы и управляемый монтаж — 2026-11-04

## Выбор пользователя

Ориентир — прежний ADV-feat-Ezhi-MiniMax.mp3 (`adv-ezhi-03`), не последние
версии с большими партиями Ежи. Основной голос и приветствие теперь ADV;
Ежи получает только «Десять свистулек!». Пользователь сам изменил Lyrics/lyrics.txt:
«Денежного обмена нет — а эквивалент есть!» и добавил приветствие. Исходный файл
не переписан скриптами; фонетическое написание имени используется только во входе моделей.

## Реально выполненные ветки

1. **MiniMax Music 3 + Seed-VC**: прежний caption/seed, но новый полный текст.
   Перегенерация не сохраняет идентичный старый бит. Приветствие входит в музыкальную
   генерацию, отдельный TTS не вставляется. Вокал разделён BS-RoFormer; ADV конвертирован
   короткими блоками, Ежи назначен только 131,18–132,80 с. Без добавленных эха и комнаты.
2. **F5-TTS RU + отдельный бит**: десять независимых фраз, включая приветствие,
   исправленную строку и одну реплику Ежи. Это 45-секундная монтажная проба, не полная
   версия всей лирики. F5 переносит голос непосредственно по короткому референсу,
   отдельный Seed-VC для этой ветки не используется. Начала фраз на сетке 96 BPM,
   длительности задаются генератору с учётом длины референса.
3. **ACE-Step repaint**: существующий 45-секундный бит используется как источник,
   модель меняет область 10–20 с по текстовому указанию. В итоговую дорожку вклеивается
   только эта область с 80 мс переходами внутри неё. Остальной бит сохранён буквально.
4. **Retake одной строки**: повторно синтезирована только исправленная реплика
   32,5–37,5 с с другим seed. Другие фразы и бит не перегенерируются.

Три модульных микса: 01-original-beat, 02-beat-patch, 03-line-retake.
Общий фиксированный gain одинаков: независимый мастеринг каждого варианта изменил бы
остальное аудио и испортил точное сравнение. Проверяется совпадение отсчётов вне вставок,
в том числе после PCM24 записи. MP3 является сжатой копией, это свойство не обещается для MP3.
Сухо означает отсутствие добавленных delay/reverb; исходный сгенерированный бит может
содержать собственное пространство. Сходство голоса и художественный флоу оцениваются на слух.

## Как менять участки дальше

`music/editable/project.json` содержит текст, голос, start/slot каждой фразы и пути WAV.
В JSON можно указать beat_source и beat_patch: file, start, end (секунды). Исходник бита
и вариант repaint должны покрывать длительность проекта. Renderer пересэмплирует WAV,
но не выравнивает автоматически BPM произвольной песни. Можно вставить свой подготовленный
бит вместо существующего, оставить вокал прежним, менять начало и доступное время реплики.

Пример нового дубля одной строки (выбирать новый seed и выходной каталог):

```powershell
.venvs/f5/Scripts/python.exe music/editable-f5.py --retake changed-line --seed 2026110555
.venvs/qwen/Scripts/python.exe music/editable-render.py --project music/editable/project-retake.json --output results/editable/retake-0555
```

`--text` задаёт иной текст без изменения исходного Lyrics/lyrics.txt. Другие ID доступны
в project.json. Retake сохраняет отдельный проект и не заменяет прежние WAV. Изменение
слота длительности требует нового дубля; renderer не обрезает выходящую за слот фразу.
Текущая сетка задаёт начало/длину фразы, а не положение каждого слога. Для точного рэп-флоу
следующий уровень — человеческая guide-читка под бит или ручная работа внутри фразы.
Это управляемый монтаж, а не обещание абсолютной музыкальной свободы одной командой.

## Версии, зависимости, лицензии

- [F5-TTS](https://github.com/SWivid/F5-TTS), код MIT, commit
  `600e5fdfbf319f84735557aca80a7aaf60d487e6`, версия 1.1.22.
- [TVI/f5-tts-ru-accent](https://huggingface.co/TVI/f5-tts-ru-accent),
  revision e2996d89da1d17a09ca4be7fb06075968c228af7, safetensors 1,348 GB.
  Карточка автора указывает CC-BY-4.0; происхождение лицензии производного
  checkpoint независимо не проверялось. Это не основание считать все веса F5 MIT.
- [Vocos](https://huggingface.co/charactr/vocos-mel-24khz), карточка MIT,
  revision 0feb3fdd929bcd6649e0e7c5a688cf7dd012ef21, около 54 MB.
- Хеши файлов: editable/f5.lock.json. Версии исполнения: editable/f5-runtime.lock.json.
  CUDA torch 2.10.0+cu128, Python 3.12; soundfile заменяет декодирование WAV через
  TorchCodec в runner. Неиспользуемые training/UI зависимости bitsandbytes/TorchCodec
  не установлены; Gradio WebUI не запускался. Это проверенная API-среда, не полный WebUI.
- Среда `.venvs/f5` использует через .pth общие пакеты `.venvs/qwen`; локальные
  зависимости F5 изолированы. Закреплены numpy 1.26.4, hub 0.36.0, datasets 3.6.0,
  pyarrow 19.0.1, matplotlib 3.9.4. Новейшие пакеты первоначально конфликтовали.
- ACE, MiniMax, Seed-VC и BS-RoFormer прежних закреплённых версий:
  benchmark/ace.lock.json, music/minimax.lock.json, music/voice-models.lock.json.
  MiniMax — Community License, Seed-VC — GPL-3.0; см. предыдущие документы проекта.
- [Stable Audio 3 Medium](https://github.com/Stability-AI/stable-audio-3): доступ
  к весам проверен, текущая сессия получила HTTP 401 GatedRepoError. Не скачан и не
  запускался. Использование ACE для бита не выдаётся за тест Stable Audio.

## Повторение

Все пути от I:\VOICE\voice. Веса и исходники загружаются один раз, синтез локальный.
Входные голосовые WAV и refs/transcripts.json лежат в ignored work; не входят в git.
ADV использует прежний подготовленный adv-intro-reference.wav; Ежи — первые 3,95 с
предоставленного аудио. Расшифровки для conditioning остаются только локально.

```powershell
.venvs/download/Scripts/python.exe music/download-f5-ru.py
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id editable-minimax-01 --brief music/editable/minimax.json
.venvs/qwen/Scripts/python.exe music/run-ace-song.py --run-id editable-beat-repaint-01 --instrumental --brief music/editable/beat-repaint.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/editable --source-prefix editable- minimax-01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/editable minimax-01
.venvs/f5/Scripts/python.exe music/editable-f5.py
.venvs/qwen/Scripts/python.exe music/editable-render.py
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/editable/minimax-01 --timeline music/editable/minimax.timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py
.venvs/asr/Scripts/python.exe music/editable-check.py
```

Первоначальный бит work/editable/beat-source.wav — первые 45 с ace-beat-01/full.wav,
48 kHz float WAV. Каталоги результатов генерации должны быть новыми. Для нового полного
MiniMax необходимо заново определить таймкоды Ежи по его реальному аудио. Воспроизведение
GPU с тем же seed не является обещанием битовой идентичности между версиями библиотек.

## Итог проверки

Новая MiniMax-основа: 221,54 с, 351,53 с запуска; перенос голосов: 130,55 с,
20 блоков. Ежи — один участок 1,62 с. F5: 11 фраз (10 основных + дубль),
58,51 с суммарного inference без загрузки модели, готовая монтажная проба 45 с.
Проверены реальные PCM24-файлы: вне диапазонов 10–20 с и 32,5–37,5 с соответствующие
версии совпадают отсчёт в отсчёт. Отдельная CLI-команда retake также выполнена и сведена.

ASR не подтвердил безошибочную дикцию: в F5 распознавал «И нежного обмена…»,
«И сеть свистулек», имя в приветствии неточно. MiniMax тоже неточно передаёт слова.
Это не доказательство качества на слух и не обещание, что F5 лучше выбранного старого
MiniMax. Проверка естественной длительности и ударений для одной строки вынесена
в отдельный эксперимент --natural; остальные фразы при этом не перегенерируются.
Автоматические расшифровки: results/editable/checks.json.

Установка F5 в новую среду на этом ПК (используется закреплённый vendor/f5-tts):

```powershell
.venvs/qwen/Scripts/python.exe -m venv .venvs/f5-new
Set-Content .venvs/f5-new/Lib/site-packages/shared-torch.pth 'I:\VOICE\voice\.venvs\qwen\Lib\site-packages'
.venvs/f5-new/Scripts/python.exe -m pip install -r music/editable/f5-requirements.txt
.venvs/f5-new/Scripts/python.exe -m pip install --no-deps -e vendor/f5-tts
```

Это API-окружение с разделяемым PyTorch, не независимая копия всех библиотек.
Оригинальные референсы и их локальные расшифровки нужны для повторения голоса;
из открытого git нельзя восстановить частные записи пользователя.

Дополнительный --natural-дубль с явными ударениями: 2,741 с вместо 4,8 с.
ASR: «И винижного обмена нет, эквивалент есть». Улучшение дикции не подтверждено;
это отдельная диагностическая проба, не замена основного выбранного варианта.
