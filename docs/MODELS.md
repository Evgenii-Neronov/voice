# Хранение моделей и лицензии

Все НОВЫЕ веса находятся в `models/`, кэши в `.cache/`, окружения в `.venvs/`, сторонний код в `vendor/`. Эти каталоги исключены из git. Веса нельзя добавлять принудительно. `benchmark/models.lock.json` хранит исходные HF repo ID и неизменяемые revision SHA. Модельные карточки скачиваются рядом с весами.

Уже существующие XTTS/GLM в `I:/Repos` не перемещались, не изменялись и не публиковались. XTTS содержит Linux-окружение Python 3.12 для WSL, CUDA PyTorch 2.10.0+cu128; это не Windows venv. Наличие старой модели само по себе не делает её бесполезной: XTTS пригоден как контрольный baseline, но не выбран основным актёрским синтезатором.

| Источник | Лицензия / оговорка |
|---|---|
| [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) | Apache-2.0 |
| [Chatterbox](https://huggingface.co/ResembleAI/chatterbox) | MIT; генерация содержит встроенный watermark |
| [ACE-Step 1.5](https://huggingface.co/ACE-Step/Ace-Step1.5) | MIT |
| [Seed-VC](https://github.com/Plachtaa/seed-vc) | Код GPL-3.0; лицензии конкретных checkpoint и вспомогательных компонентов проверяются отдельно |
| [Fish S2 Pro](https://huggingface.co/fishaudio/s2-pro) | Fish Audio Research License; не приравнивать к Apache/MIT |
| [Fish Drama 3](https://huggingface.co/fishaudio/drama-3) | Метаданные и текст карточки используют разные названия лицензии; перед применением читать LICENSE выбранного revision |
| [Higgs TTS 3](https://huggingface.co/bosonai/higgs-tts-3-4b) | Research and Non-Commercial License с отдельным Creator Use Grant; карточка разрешает монетизируемые авторские материалы при атрибуции, но не универсальный коммерческий сервис |

Это фиксация опубликованных названий/условий, не юридическое заключение. Новые модели не скачиваются под названием старой версии. English Chatterbox, Multilingual V3 и Turbo не взаимозаменяемы.

Точный набор зависимостей успешного запуска сохраняется в `results/` через pip freeze. Основные версии указаны в requirements-файлах. CUDA в nvidia-smi — возможность драйвера, а не версия установленного PyTorch runtime.
