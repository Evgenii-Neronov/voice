# ADV + Ежи: локальная версия MiniMax

Работа 2026-11-04. Основа — `results/music/minimax-full-01/full.wav`
(232,5246 с), без повторного сочинения аранжировки. Исходный файл не изменялся.
Финальный результат — `results/productions/adv-ezhi-03/full.mp3` и локальный
24-bit WAV 44,1 kHz stereo. Длительность с новым вступлением — 242,5246 с.

## Голоса и монтаж

- Основной рэп: перенос тембра с пользовательского `Recording (14).wav`, 16,98 с.
- Ежи: референс из предоставленного MKV, исходный звук 22,4 с; для конверсии
  выбран фрагмент 4,05–16,05 с. Используется только на согласованных четырёх
  строках хука: «Десять свистулек!», «Один кубит!», «Кто здесь субъект?»,
  «Кто кого купит?». В финальном треке это 2:28,30–2:34,48.
- Приветствие: «Йо, это рэп трек, с вами ADV aka Adventus Devotus».
  Fish S2 Pro Q8 получил русский фонетический вариант имени; референс — две
  уверенно распознанные фразы пользователя общей длиной около 6 секунд.
  Приветствие начинается на 0,65 с. Добавлено 10 секунд инструментального вступления.

Оба предоставленных референса, видео и их расшифровки находятся только в
игнорируемом `work/adv-ezhi`. В репозитории сохранены их SHA256, а не сами записи.
Имя Ежи взято из указания пользователя, не определялось по голосу автоматически.

## Метод и проверка качества

BS-RoFormer ep368 Q8 отделил вокал и инструментал. Seed-VC через audio.cpp 0.9.3
CUDA выполняет замену тембра. Финальный маршрут **v1_svc**, 40 шагов,
seed 20261104, штатный guidance 0,7, без изменения длины, F0 conditioning включён,
auto-F0 выключен, semitone shift 0. Выход вокодера 44,1 kHz.
Ритм и контур высоты берутся из исходной партии, музыкальные ноты здесь отдельно
не задаются. Имя пакета SeedVC-MLX не означает запуск MLX на Windows:
используется GGUF и CUDA через audio.cpp.

**Критическое ограничение native 0.9.3:** в `src/models/seed_vc/whisper_content.cpp`
метод extract_16k_mono обрезает вход до 480000 samples при 16 kHz, то есть
30 секунд. Это подтверждено и в исходниках тега v0.9.3 (`41c1f8ff`). Подача
всего трека в один запрос выдавала WAV правильной длины с испорченной читкой.
ASR одного из таких фрагментов вернул «СПОКОЙНАЯ МУЗЫКА». Пробные полные миксы
сохранены только в `work/adv-ezhi/rejected-svc-mix` и `rejected-long-speech-mix`.
Речь не о том, что SVC вообще не подходит для рэпа: короткая SVC-проба
распознаётся. Исправление — **внешние 12-секундные фрагменты + 0,4 секунды
контекста с обеих сторон**, каждый короче 30 секунд, с перекрытием и плавной
сборкой. Один пакет содержит 20 фрагментов ADV и один фрагмент Ежи.
Речевой v1 и v2 также проверены на короткой пробе. Официальный
Python Seed-VC был скачан для возможного резервного пути, однако его inference
не запускался и дополнительные Python-веса не скачивались.

ASR: faster-whisper 1.2.1, small multilingual, CPU int8, только локально.
Зависимость PyAV 19 несовместима с этой версией faster-whisper; закреплена
**av==16.0.1**. Длинная исходная партия распознана с word timestamps; по ним
выбраны границы хука. Для коротких проверок отключён VAD и ограничен вывод
128 токенами. ASR не является слуховой оценкой тембра или точной разметкой фонем.
Нечёткая дикция и ошибки исходного MiniMax сохраняются при конверсии; некоторые
редкие термины распознаются неоднозначно. Отдельные проверки финального микса распознали рэп ADV и хук Ежи; монтажное превью с приветствием ASR распознало лишь частично. В хуке ASR пишет «кубик» вместо «кубит», как и в исходном MiniMax: это не доказательство точного исполнения лирики. Сходство с референсами должен оценить
слушатель. Это результат клонирования/переноса тембра, не новая запись артистов.

При сведении: компенсация общей задержки по огибающей в пределах ±200 мс,
плавное выравнивание громкости вокала, подавление артефактов в исходных паузах,
60-мс переходы между голосами, мягкое ограничение пиков и финальный loudnorm
с целью -14 LUFS / -1,5 dBTP. Измеренные значения сохранены в `loudness.txt`.
Инструментал — оценка сепаратора: остаточный исходный голос полностью исключить
нельзя. Проверяются конечный сигнал, отсутствие sample clipping, SHA256 и
точная длительность исходной песни плюс вступление. Слуховой рейтинг не проводился.

## Воспроизведение

Рабочий каталог `I:\VOICE\voice`. Полные аудио и промежуточные результаты
хранятся локально, веса — в `models/voice-production`. GPU-запуски последовательные.
Зафиксированные модели: `music/voice-models.lock.json`, `music/asr.lock.json`,
`benchmark/native-models.lock.json`; runtime — `benchmark/native-runtime.lock.json`.
Python для сведения: существующая `.venvs/qwen`; точные зависимости ASR —
`results/productions/adv-ezhi-03/asr-freeze.txt`.

```powershell
# Нужны исходные пользовательские файлы по указанным им путям.
New-Item -ItemType Directory -Force work/adv-ezhi/refs | Out-Null
.venvs/download/Scripts/python.exe music/download-voice-models.py
ffmpeg -i 'I:\MyMusic\13 - New Rap\Recording (14).wav' -ac 1 -ar 24000 work/adv-ezhi/refs/adv.wav
ffmpeg -i 'G:\Videos\2026-11-04 18-30-56.mkv' -vn -ac 1 -ar 24000 work/adv-ezhi/refs/ezhi.wav
ffmpeg -ss 4.05 -i work/adv-ezhi/refs/ezhi.wav -t 12 work/adv-ezhi/refs/ezhi-conversion.wav

$cli = 'vendor/audio-runtime/audiocpp_cli.exe'
& $cli --task sep --family bs_roformer --model models/voice-production/BS-RoFormer-ep368-GGUF/bs-roformer-ep368-q8_0.gguf --backend cuda --threads 8 --audio results/music/minimax-full-01/full.wav --out-dir work/adv-ezhi/stems --metrics *> work/adv-ezhi/separation.log

.venvs/asr/Scripts/python.exe music/transcribe-production.py work/adv-ezhi/refs/adv.wav work/adv-ezhi/refs/ezhi.wav work/adv-ezhi/stems/vocals.wav
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc
.venvs/qwen/Scripts/python.exe music/clone-greeting.py
.venvs/qwen/Scripts/python.exe music/mix-adv-ezhi.py
.venvs/qwen/Scripts/python.exe music/check-production.py
.venvs/asr/Scripts/python.exe music/transcribe-production.py --short-check work/adv-ezhi/roles-preview.wav
.venvs/qwen/Scripts/python.exe music/check-production.py
```

ASR устанавливается в отдельную среду: `python -m venv .venvs/asr`, затем
`pip install faster-whisper==1.2.1 av==16.0.1 soundfile`. Snapshot модели
`Systran/faster-whisper-small` из `music/asr.lock.json` скачать через huggingface_hub
в `models/asr-whisper-small`: файлы `config.json`, `model.bin`, `tokenizer.json`,
`vocabulary.txt`. Для распознавания сеть не используется. Существующие записи
лучше сначала перенести в собственный архив; команды подготовки не содержат `-y`.
Скрипты сведения обновляют только созданные ими файлы итогового каталога.
Конвертер фрагментов требует нового каталога `work/adv-ezhi/chunks-v1_svc-02`;
существующий не перезаписывает. Batch CLI не принимает глобальный --task-route:
маршрут и число шагов передаются внутри каждого JSON-запроса.

## Источники и лицензии

- [Seed-VC](https://github.com/Plachtaa/seed-vc), GPL-3.0; источник Python
  `51383efd921027683c89e5348211d93ff12ac2a8` скачан, но не исполнялся.
- [GGUF-пакеты](https://huggingface.co/audio-cpp/audio.cpp-gguf), snapshot
  `fd2fe4c3195bc410f8b817bf7c7519fd822686fb`; лицензии компонентов неодинаковы.
  BS-RoFormer указан как Apache-2.0 с оговоркой о недокументированном происхождении
  checkpoint. Не следует считать весь сборник весов одним разрешительным пакетом.
- [Seed-VC native routes](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/seed_vc.md).
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper), MIT.
- MiniMax Music 3 Community License и Fish Audio Research License: см. существующие
  документы моделей проекта. Built with Fish Audio.
