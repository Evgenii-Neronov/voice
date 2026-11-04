# voice

## Локальный benchmark выразительного русского голоса

Проверено 2026-11-04 на RTX 5080 16GB / Windows 11. Первый этап дал **19 WAV**:

- [Qwen3-TTS 1.7B CustomVoice — 9 тестов](results/qwen17-run1)
- [Chatterbox Multilingual V3 — 9 тестов](results/chatterbox-run1)
- [ACE-Step 1.5 — музыкальный фрагмент 30 секунд](results/ace-run2)

Второй этап добавил **36 основных WAV** на тех же девяти русских текстах:

- [Fish S2 Pro Q8](results/fish-s2-q8-run1) и [mixed Q4](results/fish-s2-q4-run1)
- [Higgs TTS 3 Q8](results/higgs3-q8-run4)
- [Drama 3 Q2 с экспертами в RAM](results/drama3-q2-pinned-run1)

Итого 55 основных WAV плюс диагностические повторы. [Новый отчёт](docs/NATIVE_BENCHMARK.md)
описывает реальные времена, ошибки тегов Higgs, медленную работу Drama и команды
воспроизведения. Все 75 сохранённых WAV прошли техническую проверку, но не слуховой рейтинг.

Это первичный benchmark одного seed, без слухового рейтинга. Проверены форматы, ненулевой сигнал и SHA256. Протяжные слоги, эмоции и точное пение требуют отдельной оценки слушателем; факт существования WAV не означает успешное выполнение художественного задания.

### Документация

- [Актуальные модели, STEOS и обсуждения Reddit](docs/RESEARCH.md)
- [Фактические выводы и ограничения](docs/FINDINGS.md)
- [Таблица измерений и сохранённые ошибки](results/SUMMARY.md)
- [Повторить запуск](docs/RUN.md)
- [Тестовый протокол](docs/PROTOCOL.md)
- [Веса, лицензии и хранение](docs/MODELS.md)
- [Окружение, обходные решения и непроверенные направления](docs/LOCAL_NOTES.md)
- [Новый локальный этап: Fish S2 Pro, Drama 3, Higgs TTS 3](docs/NATIVE_BENCHMARK.md)

Большие веса находятся только в игнорируемых `models/` и `.cache/`; окружения — `.venvs/`, сторонние исходники — `vendor/`. Старые модели в `I:/Repos` сохранены без изменений. В git входят код, конфигурации, manifests, небольшие WAV и документация.

Основные записи воспроизводимости: `benchmark/models.lock.json`, `benchmark/ace.lock.json`, `benchmark/native-*.lock.json`, `results/*-freeze.txt`, manifests каждого запуска. CosyVoice/OmniVoice/Seed-VC **не выдаются за локально протестированные**; их metadata зафиксированы отдельно в `results/research-models.json`. Fish/Higgs проверены отдельным нативным runner; подробные результаты и ограничения находятся в новом отчёте.

Built with Fish Audio. Higgs audio samples generated with Boson AI's Higgs Audio (Higgs TTS 3).
