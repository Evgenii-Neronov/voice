# voice

## Локальный benchmark выразительного русского голоса

Проверено 2026-11-04 на RTX 5080 16GB / Windows 11. Реально получено **19 WAV**:

- [Qwen3-TTS 1.7B CustomVoice — 9 тестов](results/qwen17-run1)
- [Chatterbox Multilingual V3 — 9 тестов](results/chatterbox-run1)
- [ACE-Step 1.5 — музыкальный фрагмент 30 секунд](results/ace-run2)

Это первичный benchmark одного seed, без слухового рейтинга. Проверены форматы, ненулевой сигнал и SHA256. Протяжные слоги, эмоции и точное пение требуют отдельной оценки слушателем; факт существования WAV не означает успешное выполнение художественного задания.

### Документация

- [Актуальные модели, STEOS и обсуждения Reddit](docs/RESEARCH.md)
- [Фактические выводы и ограничения](docs/FINDINGS.md)
- [Таблица измерений и сохранённые ошибки](results/SUMMARY.md)
- [Повторить запуск](docs/RUN.md)
- [Тестовый протокол](docs/PROTOCOL.md)
- [Веса, лицензии и хранение](docs/MODELS.md)
- [Окружение, обходные решения и непроверенные направления](docs/LOCAL_NOTES.md)

Большие веса находятся только в игнорируемых `models/` и `.cache/`; окружения — `.venvs/`, сторонние исходники — `vendor/`. Старые модели в `I:/Repos` сохранены без изменений. В git входят код, конфигурации, manifests, небольшие WAV и документация.

Основные записи воспроизводимости: `benchmark/models.lock.json`, `benchmark/ace.lock.json`, `results/*-freeze.txt`, manifests каждого запуска. Исследованные Fish/Higgs/CosyVoice/OmniVoice/Seed-VC **не выдаются за локально протестированные**; их metadata зафиксированы отдельно в `results/research-models.json`.
