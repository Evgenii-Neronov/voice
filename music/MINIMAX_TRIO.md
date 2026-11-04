# Три MiniMax-дубля с двумя хуками Ежи

2026-11-04. Пользователь обновил приветствие на «А ДЭ ВЭ эй кей Adventus Devotus»
и добавил второе повторение четырёх строк внутрь Verse 3. Source SHA256:
ebfeaf5d061ca6db1d3a0d09d895b51aaff84b79c16050503a88a54f9bbfb3e2.

Одинаковая лирика, разные музыкальные описания и seeds:

| ID | Бит / подача | Запрошенный BPM | Seed |
|---|---|---:|---:|
| boombap | Пыльный джазовый boom bap, сдержанная ироничная быстрая читка | 90 | 2026110601 |
| breakbeat | Индустриальные брейки, acid bass, напористое стаккато | 104 | 2026110602 |
| funk | Тёмный funk, синкопированный бас, пружинистая разговорная подача | 96 | 2026110603 |

Каждый caption — пожелание, не подтверждённое измерение фактического темпа/подачи.
Основной вокал и приветствие ADV. Только два блока «Десять свистулек! / Один кубит! /
Кто здесь субъект? / Кто кого купит?» назначаются Ежи. Границы устанавливаются отдельно
для каждого реального дубля по локальным временным меткам распознавания. Сведение сухое,
без добавленных эха/реверберации. Генеративные дикция и следование лирике не гарантируются.

Все вычисления локальные; модели и runtime прежних закреплённых версий:
music/minimax.lock.json, music/voice-models.lock.json, benchmark/native-runtime.lock.json.
MiniMax Community License, Seed-VC GPL-3.0; прочие атрибуции см. ADV_EZHI.md.
Веса и личные референсы не входят в git. Все прежние результаты сохранены.

Подробности параметризации: [MINIMAX_PARAMETERS.md](MINIMAX_PARAMETERS.md).
Конфиги: music/minimax-trio/{boombap,breakbeat,funk}.json. Команды из корня репозитория:

```powershell
# Пример одного дубля, GPU-этапы выполняются последовательно.
.venvs/qwen/Scripts/python.exe music/run-minimax.py --run-id minimax-trio-boombap-01 --brief music/minimax-trio/boombap.json
.venvs/qwen/Scripts/python.exe music/duet-separate.py --work-root work/minimax-trio --source-prefix minimax-trio- boombap-01
.venvs/asr/Scripts/python.exe music/duet-asr.py --work-root work/minimax-trio boombap-01
# После определения ОБОИХ интервалов:
.venvs/qwen/Scripts/python.exe music/convert-rap-chunks.py --route v1_svc --work-dir work/minimax-trio/boombap-01 --timeline music/minimax-trio/boombap.timeline.json
.venvs/qwen/Scripts/python.exe music/editable-minimax-mix.py --work-dir work/minimax-trio/boombap-01 --output results/productions/minimax-trio-boombap-01 --timeline music/minimax-trio/boombap.timeline.json
.venvs/asr/Scripts/python.exe music/verify-minimax-performance.py --run-id minimax-trio-boombap-01 --work-dir work/minimax-trio/boombap-01
```

Для повторения нужны новые выходные каталоги или отдельная рабочая копия.
Скрипты не перезаписывают завершённые генерации. Итоговые WAV локальные; MP3,
конфиги, численные проверки и отчёты фиксируются в git.

## Восстановление после отсутствующего F0

В первом дубле Seed-VC остановился на `adv-021`: на инструментальном хвосте
не обнаружены voiced F0 values. Добавлен `--resume` в convert-rap-chunks.py:
проверяются совпадение запросов и исходных фрагментов, готовые части сохраняются.
Только для ошибки отсутствующего F0 применяется `v1_whisper_bigvgan_vc`;
в остальных случаях выполнение останавливается с логом ошибки.
21 фрагмент первого дубля использован повторно. `whole_run_seconds` его
conversion manifest измеряет продолжение, не включает первую неудачную попытку.
Сведения о fallback и повторно использованных частях сохранены в manifest.

Итоговые измерения: MINIMAX_TRIO_RESULTS.md. Для экспорта используйте
`music/export-minimax-trio.py --output <новый-каталог>`; скрипт создаёт MP3,
24-bit WAV и короткую подборку двух блоков Ежи для каждого дубля.
