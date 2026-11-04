# Fish S2 Pro, Drama 3, Higgs TTS 3 — локальная проверка

Built with Fish Audio. Higgs samples generated with Boson AI's Higgs Audio (Higgs TTS 3).

## Протокол

Те же 9 оригинальных русских текстов из `benchmark/cases.json`, seed `20261104`:
нейтральная речь, радость, гнев, печаль, манерная протяжная речь, гласные,
попытка пения и пара с одинаковым текстом «радость / нейтрально».
Слова не переписываются; префиксы эмоций и стиля зависят от модели и записаны
в каждом `requests.json` и `manifest.json`. Исходные английские инструкции
сохранены для сопоставления. Higgs принимает структурированные токены; Fish —
теги в квадратных скобках. Это сравнение штатных средств управления, а не
одного универсального промпта. Ниже не предполагается точное выполнение
двухсекундных гласных только по тегу замедления.

Новые модели запускаются без референса голоса. Фиксированный seed не гарантирует
одного тембра между фразами. Сравнение эмоций может смешиваться со сменой голоса;
для следующей отдельной проверки нужен общий разрешённый референс. Пение —
свободная проба TTS, без нот, MIDI и заданной мелодии; это не полноценная проверка SVS.
WAV и ненулевой сигнал сами по себе не подтверждают естественность, правильный
русский, эмоции или способность стать музыкальным вокалистом.

## Выбранные варианты

| Модель | Локальные веса | Причина |
|---|---|---|
| Fish S2 Pro | Q8_0, 6 317 915 552 байта | Первый реальный WAV подтвердил запуск при текущей нагрузке; основной тест сохраняет Q8 |
| Higgs TTS 3 4B | Q8_0, 5 095 359 136 байт | Умеренный размер без дополнительного низкобитного квантования |
| Drama 3 base | Q2_K experts + Q8_0 backbone + FP16 audio tower/codec, 17 053 639 872 байта | Полная MoE-модель; небольшой GPU-кэш, банки экспертов в RAM в основном прогоне |

Drama — именно base, не подмена small. Размер GGUF не равен расходу VRAM.
На старте работы свободно было примерно 5,5 ГБ из 16 ГБ; другие приложения
не завершались. Логи `gpu-whole-device.csv` измеряют всю видеокарту, включая
посторонние процессы, и не являются пиком памяти одного синтезатора.

Для Drama используются disk_experts=true, expert_cache_size=8,
cpu_expert_layers=0, context_length=2048, 1 поток чтения диска и 8 CPU-потоков.
В основном прогоне дополнительно `perf_mode=cuda_perf`, `pin_experts=true`:
полные банки экспертов размещаются в закреплённой RAM, промахи GPU-кэша
обслуживаются из неё. Поток чтения с диска относится к исходным диагностическим
прогонам без pinning. Требуется значительный запас RAM; здесь установлено 64GiB.
top_k=4097 и top_p=0.9 выбраны по документации её порта; Fish/Higgs — 30/0.8.
Общие параметры: temperature=0.8, max_tokens=1024, offline PCM16.
Это разные квантования и разные sampling-параметры, не строгое сравнение архитектур
при одинаковой численной точности. Повторное квантование Fish из Q8 также может
изменять качество относительно исходных весов. Дополнительная Q4-конвертация
подготовлена отдельно и не подменяет основной Q8-тест.

## Воспроизводимость

Windows 11, RTX 5080 16GB, драйвер 610.88, RAM 64GiB, i7-11700K.
Использован нативный audio.cpp 0.9.3, Windows x64 CUDA 13.3, binary commit
`41c1f8ff`; SHA256 двух release ZIP и бинарника фиксируются в lock/manifest.
Python 3.12 нужен только для загрузки и запуска: huggingface_hub 0.36.0,
requests; WAV-метаданные и хеши читаются стандартной библиотекой.
Ни Pinokio, ни системная переустановка CUDA для этого пути не требуются.

Запуск из корня репозитория в PowerShell:

```powershell
if (-not (Test-Path .venvs/download/Scripts/python.exe)) { py -3.12 -m venv .venvs/download }
& .venvs/download/Scripts/python.exe -m pip install -r results/native-download-freeze.txt
& .venvs/download/Scripts/python.exe benchmark/setup-native.py
& .venvs/download/Scripts/python.exe benchmark/snapshot-native-sources.py
& .venvs/download/Scripts/python.exe benchmark/download-native.py fish-s2 higgs3 drama3 --ranged
& .venvs/download/Scripts/python.exe benchmark/run-native.py higgs3 --run-id higgs3-q8-repeat --cases neutral joy anger sadness drawl syllables emotion_control neutral_control singing_probe
& .venvs/download/Scripts/python.exe benchmark/run-native.py fish-s2 --run-id fish-s2-q8-repeat
& .venvs/download/Scripts/python.exe benchmark/quantize-fish.py
& .venvs/download/Scripts/python.exe benchmark/run-native.py fish-s2 --run-id fish-s2-q4-repeat --model-file models/native/Fish-Audio-S2-Pro-GGUF/fish-audio-s2-pro-mixed-q4_k.gguf
& .venvs/download/Scripts/python.exe benchmark/run-native.py drama3 --run-id drama3-q2-repeat --session-option fish_drama3.perf_mode=cuda_perf --session-option fish_drama3.pin_experts=true
& .venvs/download/Scripts/python.exe benchmark/report.py
& .venvs/qwen/Scripts/python.exe benchmark/validate_audio.py
```

`run-id` должен быть новым: существующая папка вызывает ошибку, старые результаты
не перезаписываются. Варианты диагностики: `--cases neutral`, `--backend cpu`,
повторяемый `--session-option key=value`. Настройки каждого фактического запуска
содержатся в manifest; команда выше описывает основные выбранные конфигурации.
Генерация идёт последовательно на одной GPU. Время отдельного запроса исключает
загрузку весов; `whole_run_seconds` её включает. Первый запрос может быть холодным.

`native-models.lock.json` фиксирует revision и SHA256 GGUF. `native-sources.lock.json`
фиксирует отдельно версии upstream-карточек/лицензий; это не доказательство того,
что конвертер использовал ровно этот upstream commit. Воспроизводимым входом
данного теста является конкретный GGUF. `fish-mixed-q4.lock.json` описывает
производный файл. Полные веса, runtime и временные части остаются в ignored
`models/`, `vendor/`, `.cache/`. Старые модели в `I:/Repos` не затронуты.

Во время загрузки и части замеров также работали загрузчик весов и CPU-конвертер
Fish Q4. Это прикладной запуск на занятом ПК, не изолированный speed leaderboard.
`memory.peak_rss_mb` и `memory.peak_footprint_mb` в native-логе относятся к RAM
и Windows commit, не к VRAM. Диск моделей — NVMe ADATA SX8200PNP.

## Источники и лицензии

- [audio.cpp](https://github.com/0xShug0/audio.cpp) — Apache-2.0 для кода; включённые CUDA-компоненты имеют собственные условия. Runtime не коммитится.
- [Fish S2 Pro](https://huggingface.co/fishaudio/s2-pro) — Fish Audio Research License; проверять LICENSE.md закреплённой версии.
- [Drama 3](https://huggingface.co/fishaudio/drama-3) — фактический LICENSE закреплённой версии: Fish Audio Community License 1.0 от 2026-10-13. Метаданные карточки недостаточны для определения условий.
- [Higgs TTS 3 4B](https://huggingface.co/bosonai/higgs-tts-3-4b) — Boson Higgs TTS 3 Research and Non-Commercial License с отдельным Creator Use Grant. Не общая MIT/Apache-лицензия.
- [Fish/Higgs GGUF](https://huggingface.co/audio-cpp/audio.cpp-gguf) и [Drama GGUF](https://huggingface.co/Jmica/Drama-3-GGUF) — community-конвертации, не официальный Python inference.

Полные лицензии скачаны рядом с моделями в `models/native-metadata/`; ссылки на
неизменяемые версии и их SHA256 находятся в `benchmark/native-sources.lock.json`.
Публикуемые WAV — синтетические тестовые артефакты на оригинальном материале.

## Результаты

**36 новых основных WAV**, по девять в каждой конфигурации. Все PCM16,
декодируются, содержат конечный ненулевой сигнал; SHA256 проверены. С учётом
старых тестов и диагностических повторов проверено 75 WAV, 432,851с аудио.
Машинная сводка выбранных запусков: `results/native-overview.json`.

| Конфигурация | WAV | Аудио всего, с | Синтез всего, с | Взвешенный RTF |
|---|---:|---:|---:|---:|
| Fish S2 Pro Q8 | 9 | 45,325 | 44,129 | 0,974 |
| Fish S2 Pro mixed Q4 | 9 | 46,811 | 30,546 | 0,653 |
| Higgs TTS 3 Q8 | 9 | 48,400 | 11,506 | 0,238 |
| Drama 3 Q2 + RAM + CUDA preset | 9 | 88,747 | 898,782 | 10,127 |

RTF = время синтеза / длительность результата; меньше — быстрее. Загрузка
модели исключена, а фоновые процессы и разные движки/квантования не исключены.
Это не время до первого звука и не статистический рейтинг качества.

Higgs Q8: `higgs3-q8-run4`, 9/9 WAV, 24kHz mono PCM16. RTF 0,209–0,275,
проба пения — 12,08с за 2,757с синтеза. Это время выдачи файла, не оценка
музыкальности и не streaming latency. Для гласных итоговый префикс пустой:
оба тега `speed_very_slow` и `speed_slow` приводили к отсутствию EOC, в том
числе при увеличении лимита с 1024 до 2048. Сам исходный текст с повторёнными
гласными без тега дал 6,4с. Четыре гласных по 2с таким результатом не подтверждены.
Пение с `singing` + `speed_slow` тоже не завершалось, а один `singing` сработал.
Все ошибки/диагностические WAV сохранены. Следующие после сбоя строки в ранних
пакетах не исполнялись: `failed / No WAV` для них не доказывает отказ модели
именно на этих текстах. В smoke1 синтез и manifest завершились успешно, а вывод
русского текста в консоль Python CP1252 вызвал ошибку; runner исправлен на
краткий ASCII-совместимый итог без изменения аудио.

Источник истины для всех измерений — manifests запусков, `results/SUMMARY.md`
и `results/audio-validation.json`.

Fish S2 Pro Q8: `fish-s2-q8-run1`, 9/9 WAV, 44,1kHz mono PCM16. RTF 0,630–1,678;
проба пения 8,87с, гласные 7,11с. Последнее меньше суммы четырёх запрошенных
двухсекундных гласных ещё до слов «я здесь»: точная длительность не выполнена.
Дополнительная mixed-Q4 конвертация завершилась: 4 501 257 600 байт,
13 embedded sidecars, model spec сохранён, SHA256 в `fish-mixed-q4.lock.json`.
Команда получения: `python benchmark/quantize-fish.py`; путь для runner:
`--model-file models/native/Fish-Audio-S2-Pro-GGUF/fish-audio-s2-pro-mixed-q4_k.gguf`.

Первая загрузка Drama (`drama3-q2-smoke1`) отказала до генерации:
`parallel disk expert reads require ENGINE_ENABLE_OPENMP=ON`. Готовый Windows
runtime не поддержал `disk_expert_read_threads=4`, поэтому runner использует 1.
Это не OOM и не провал качества модели. Исходный запрос и полный лог сохранены.

Drama, нейтральная фраза без pinning: базовый режим дал 5,619с за 180,226с,
RTF 32,073 (`drama3-q2-smoke2`); CUDA preset — 5,526с за 75,103с, RTF 13,590
(`drama3-q2-cuda-smoke`). Оба завершились естественно (`reached_limit=false`).
CUDA preset меняет арифметику и sampling, поэтому длительности/аудио различаются.
Это не изолированное A/B-измерение; ускорение не следует приписывать только
одному переключателю без учёта прогрева и фоновых процессов.

Основной Drama `drama3-q2-pinned-run1`: 9/9 WAV, 44,1kHz mono PCM16;
во всех девяти `reached_limit=false`. Проба пения 40,635с за 450,256с;
весь процесс с загрузкой модели 933,407с (проверка хеша перед запуском не входит).
Пиковый RSS процесса 26 458MiB (~25,8GiB RAM). Максимум выборочных замеров
всей GPU — 15 165MiB (~14,8GiB), включая остальные приложения. Это подтверждает
фактическую работу на этой RTX 5080 16GB / 64GiB RAM, но режим слишком медленный
для озвучки в реальном времени без иных оптимизаций. Длительность drawl 8,359с,
syllables 11,006с; точность отдельных двухсекундных гласных на слух/по разметке
не проверялась.

Fish mixed Q4 `fish-s2-q4-run1`: 9/9 WAV, 44,1kHz mono PCM16;
RTF 0,604–0,746, проба пения 8,499с за 5,943с. Q4 и Q8 дают разные WAV;
эквивалентность качества не заявляется. Нагрузка других приложений изменилась,
поэтому различие целой GPU между этими запусками не является чистой экономией VRAM модели.

Архив прослушивания включает 54 WAV: эти 36 плюс по девять прежних Qwen и
Chatterbox, с `listen.html` для офлайн-сравнения одинаковых текстов. ACE-Step
остаётся в прежнем отдельном музыкальном тесте. Архив собирается командой:

```powershell
& .venvs/download/Scripts/python.exe benchmark/package-listening.py --output work/voice-native-comparison.zip fish-s2-q8-run1 fish-s2-q4-run1 higgs3-q8-run4 drama3-q2-pinned-run1 qwen17-run1 chatterbox-run1
```

Путь ZIP должен быть новым. После новых запусков обновить выбранные run-id в
`native-overview.py` или использовать общий `report.py`, который читает все manifests.
