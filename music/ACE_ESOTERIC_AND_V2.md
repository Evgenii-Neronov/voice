# ACE esoteric minimal + Seed-VC V2 style experiment

2026-11-05. Пользователь подтвердил два направления: новый ACE-трек по стеку
референса и отдельная проверка V2 после завершения скачивания.

## ACE-трек

`outputs/ten-whistles-ace-take1.mp3` найден по SHA256
0f47abc1af38cbc9382531854311e0806dd0daaf7ed1918858e87ba9e4553ffc:
это `results/music/ace-turbo-full-01`, ACE-Step 1.5 turbo, seed 20261104.
Новая версия использует тот же закреплённый движок, 8 шагов, русский язык,
но новый seed и caption: эзотерический London minimal rap, 84 BPM,
редкий сухой бит, протяжная литературная декламация, паузы, сдержанная ирония.
Это не аудиокопия референса; его waveform не используется как cover-conditioning.
Текст — последняя диалоговая редакция rap-4 с шестью ответами Ежи.
Основной голос ADV. Пространственные эффекты дополнительно не добавляются.
Requested duration 330 секунд. Стиль и дикция оцениваются по готовому аудио.

## Seed-VC V2

[Официальный README](https://github.com/Plachtaa/seed-vc) описывает convert_style
для переноса акцента/эмоций с AR-моделью. Предыдущий C++ V1 SVC переносил тембр
и сохранял значительную часть исходного произношения. V2 не является гарантией
исправления фонем и может изменить длительность/ритм — поэтому сначала короткий A/B.

`music/test-seed-v2.py`: одинаковый 12-секундный фрагмент ADV, одинаковый
8-секундный русский референс, convert_style false/true, seed 2026111201,
30 шагов, intelligibility/similarity CFG .7/.7, top_p .9, temperature .8,
repetition penalty 1.1. Отдельный фрагмент Ежи с convert_style true.
Вход — исходный вокал MiniMax до V1-конверсии, а не уже преобразованный голос.

Окружение `.venvs/seedv2` использует PyTorch 2.10.0+cu128 из qwen через .pth;
свои версии transformers 4.46.3, tokenizers .20.3, hydra-core 1.3.2,
einops .8.0, munch 4.0.0. Рабочее окружение qwen не изменялось.
Код Seed-VC: 51383efd921027683c89e5348211d93ff12ac2a8, GPL-3.0.
Модели, revisions, размеры, SHA256 и карточки лицензий: music/seed-v2.lock.json.
Веса под models/seed-v2; сетевые вызовы в тестовом инференсе запрещены offline-флагами.
Компиляция/triton не используются. Все аудиовычисления локальные.

## Замечания к присланным рекомендациям

XTTS поддерживает русский, но его [документация](https://docs.coqui.ai/en/latest/models/xtts.html)
не обещает автоматический рэп или отсутствие акцента. [F5-TTS](https://github.com/SWivid/F5-TTS)
— семейство TTS; русский зависит от checkpoint. У нас F5 RU уже был запущен,
но его речевые фразы на битовой сетке пользователь не признал рэпом.
Одна пунктуация и чистый референс не гарантируют флоу и верные ударения.
RVC/voice conversion не следует приравнивать к корректору произношения.
MiniMax Music3 в нашем проекте — музыкальный генератор, не MiniMax-Speech.

## Фактические результаты и ограничения

V2: ADV timbre 11.993 с (14.87 с вычислений), ADV style 11.610 с (29.61 с),
Ezhi style 5.050 с (14.13 с). Пик выделенной GPU-памяти около 3.26 GiB.
Три WAV реально созданы. Автоматическое распознавание не подтверждает улучшения
дикции: в style-пробе сохраняются/возникают ошибки. Это не метрика акцента;
сходство тембра и подачу оценивает слушатель. Полная V2-переделка не выполнялась.
Сравнение: одинаковый бит, общий gain; style time-fit 11.61 → 12 с через atempo.
Исходный float stem содержит несколько значений выше 1, это не свидетельствует
о PCM-клиппинге; конечные V2 WAV не содержат full-scale отсчётов.

Отдельное окружение дополнительно получило matplotlib 3.10.7 и NumPy 2.5.4;
точный local freeze в seed-v2-requirements.txt. Qwen сохранил transformers 4.57.3
и NumPy 1.26.4. Первая проба V2 остановилась на отсутствующем matplotlib;
после установки обе ветки прошли.

Первый ACE full-pass (330 с) переставлял и пропускал строки. Повторный опыт
разделил текст по четырём крупным секциям без изменения слов: run-ace-sections.py.
Секции 100 / 80 / 82.88 / 80 с, перекрытие 0.18 с, итог 342.34 с.
И здесь остались пропуски/повторы, некоторые ответы Ежи прозвучали лишь частично.
Сохранён как стилистический опыт; полнота исполнения не заявляется. Временные
границы голосов привязаны к распознанным партиям, intended lyrics в timeline —
задание, а не подтверждённая транскрипция.

Команды:
```powershell
.venvs/download/Scripts/python.exe music/download-seed-v2.py
.venvs/seedv2/Scripts/python.exe music/test-seed-v2.py
.venvs/qwen/Scripts/python.exe music/run-ace-sections.py
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/ace-esoteric-sections --source-prefix ace-esoteric-sections- 01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/ace-esoteric-sections 01
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/ace-esoteric-sections/01 --timeline music/ace-esoteric/timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/ace-esoteric-sections/01 --output results/productions/ace-esoteric-sections-01 --timeline music/ace-esoteric/timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id ace-esoteric-sections-01 --work-dir work/ace-esoteric-sections/01
```

Для повторного музыкального синтеза нужны новые run-каталоги. Секционный runner
повторно использует уже рассчитанные секции с тем же текстом; финальную сборку
не перезаписывает.
