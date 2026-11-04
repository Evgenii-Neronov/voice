# Локальная музыка: «ДЕСЯТЬ СВИСТУЛЕК ЗА СИНГУЛЯРНОСТЬ»

Исследование и реальные запуски 2026-11-04. Все вычисления выполнены на этом ПК:
RTX 5080 16 GB, i7-11700K, 64 GiB RAM, Windows, NVIDIA 610.88.
Интернет использовался для исследования и скачивания весов, не для генерации.
Результаты и ограничения: [MUSIC_RESULTS.md](../docs/MUSIC_RESULTS.md).
Обзор альтернатив: [MUSIC_RESEARCH.md](../docs/MUSIC_RESEARCH.md).

## Материал и протокол

Исходник — `Lyrics/lyrics.txt`, SHA256
`b10f5ea3b85711c98621158dd945e5aac72aaa2d4581e143c2a08ffc97214a94`.
Его байты не менялись. Заголовки Title/Style/Vocal/Mood превращены в metadata,
длинные указания в скобках сокращены до названий секций. Все 92 строки вокального
текста сохранены в полном запросе. Это проверяется кодом; фактическое произнесение
всех слов моделью пока не проверено. ACE получает 1449 lyric tokens, меньше лимита
2048: runner отказывается запускаться при >=2000 токенов.

Стилистика взята из файла: русский абстрактный рэп, UK boom bap, 96 BPM,
пыльный джаз, контрабас, Rhodes, скретчи, индустриальные шумы. Запрошены высокий
носовой мужской голос, быстрая сухая ироничная читка, без распевной мелодии.
Британское описание подачи адаптировано к русскому языку. D minor, размер 4/4 и
250 секунд — выбранные параметры аранжировки, а не требования автора текста.
Длинные индивидуальные указания секций сохранены в manifest, но ACE получает
сокращённый общий caption: точное следование каждой ремарке не гарантируется.

Два полных дубля отличаются seed. Бит — отдельная генерация в сходном стиле,
не извлечённый инструментальный stem и не синхронная минусовка полного трека.
Сырые WAV не обработаны мастеринговой цепочкой; ACE использует штатную peak
normalization -1 dB. MP3 — копия для прослушивания, 256 kbps.

## Повторение на этом ПК

Запускать из `I:\VOICE\voice`, последовательно на GPU. Новые run-id обязательны:
существующие результаты не перезаписываются.

```powershell
.venvs/qwen/Scripts/python.exe music/run-ace-song.py --run-id ace-repeat-01
.venvs/qwen/Scripts/python.exe music/run-ace-song.py --run-id ace-repeat-02 --seed 20261105
.venvs/qwen/Scripts/python.exe music/run-ace-song.py --run-id beat-repeat --duration 60 --instrumental

.venvs/download/Scripts/python.exe music/download-minimax.py
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-repeat --duration 30
# Полный текст, увеличенный бюджет; требования к памяти выше:
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-full-repeat --duration 250 --full-lyrics
```

MiniMax runner берёт проверенный caption и нормализованный текст из сохранённого
`results/music/ace-turbo-full-01/manifest.json`; без `--full-lyrics` использует
только восемь строк Intro, что явно записано в manifest. Его duration — бюджет
генерации, не обещанная длительность WAV. Seed один и тот же не делает разные
архитектуры эквивалентными и не гарантирует побитовый повтор между версиями CUDA.

## Чистая установка и закреплённые версии

Базовая инструкция и установка CUDA PyTorch: [RUN.md](../docs/RUN.md).
Для ACE: Python 3.12, torch 2.10.0+cu128, transformers 4.57.3,
`requirements-ace-inference.txt`, фактический freeze `results/music/environment-freeze.txt`.
Исходники: `https://github.com/ace-step/ACE-Step-1.5`, checkout
`ca1e85fe9430179831e6bc6be790c332190a3866` в `vendor/ace-step`.
Веса скачивает `benchmark/download-ace.py`; snapshot зафиксирован в
`benchmark/ace.lock.json` (MIT). Нужны DiT turbo, VAE и Qwen3 embedding 0.6B.
Дополнительная музыкальная LM не используется. Включены CPU offload и
`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`; compile/flash-attention отключены.

MiniMax использует `vendor/audio-runtime/audiocpp_cli.exe`, audio.cpp 0.9.3
CUDA 13.3, commit `41c1f8ff`. Установка: `benchmark/setup-native.py`, точный
релиз и контрольные суммы — `benchmark/native-runtime.lock.json`.
Пакет модели: `audio-cpp/MiniMax-Music3-GGUF`, revision
`46fe77f8bb395ccdbe797d784225f7b84866e7ce`. Это сторонний квантованный порт,
не оригинальный Python inference. Состав Q4_0 LM + Q8_0 RVQ + Q4_0 flow,
остальные компоненты штатные; размеры и SHA256 всех файлов — `minimax.lock.json`.
Установлены mem_saver=true, cuda_perf, 30 flow steps, CFG 1.7/1.5, top-k 50.
CUDA kernels native runtime не используют облачный API.

Download-зависимости: Python 3.12, huggingface_hub 0.36.0, requests 2.34.2.
Native runner дополнительно использует numpy, soundfile и ffmpeg/libmp3lame.
Диапазонный загрузчик проверяет длину каждого блока и итоговый SHA256;
незавершённые блоки остаются в `.cache/music-parts` для повторного запуска.

Все веса в игнорируемом `models/`, среды в `.venvs/`, сторонние исходники в
`vendor/`. Полные WAV остаются в `results/music/<run>/full.wav`, игнорируются git.
В git входят MP3, короткие WAV-превью, manifests, запросы, логи, код и документация.
Численная валидация проверяет формат, ненулевой конечный сигнал и SHA256;
она не заменяет прослушивание, проверку русской дикции, BPM и полноты лирики.

## Версия ADV + Ежи

[Голоса по пользовательским референсам, приветствие и исправление ограничения Seed-VC](ADV_EZHI.md). Основа — сохранённый трек MiniMax; все вычисления локальные.
