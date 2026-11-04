# Запуск на Windows / RTX 5080

Рабочий каталог: `I:\VOICE\voice`. Python 3.12, git, ffmpeg доступны. Запускать модели последовательно, не параллельно на GPU.

## Qwen

```powershell
cd I:\VOICE\voice
powershell -ExecutionPolicy Bypass -File benchmark/setup-qwen.ps1
.venvs/qwen/Scripts/python.exe benchmark/download.py qwen17
.venvs/qwen/Scripts/python.exe benchmark/run.py --model qwen17 --out results/qwen17-run1
.venvs/qwen/Scripts/python.exe -m pip freeze > results/qwen-freeze.txt
```

`--out` должен быть новым каталогом: существующие результаты не перезаписываются. Для короткой проверки добавить `--cases neutral`. Для следующего seed — `--seed 20261105` и другой `--out`. Дополнительно можно скачать `qwen06` и запустить тот же runner; instruction-контроль в нём отключён явно.

Для повторения зафиксированного окружения сначала установить CUDA PyTorch по setup-скрипту, затем соответствующий freeze-файл успешного запуска. Если freeze отсутствует, это ещё не полностью воспроизведённый запуск.

## Chatterbox Multilingual V3

```powershell
powershell -ExecutionPolicy Bypass -File benchmark/setup-chatterbox.ps1
.venvs/qwen/Scripts/python.exe benchmark/download.py chatterbox
.venvs/chatterbox/Scripts/python.exe benchmark/run.py --model chatterbox --out results/chatterbox-run1
.venvs/chatterbox/Scripts/python.exe -m pip freeze > results/chatterbox-freeze.txt
```

Код закреплён на `5de7a54aa4e5e2baadb0182dde554908b48b85c2`. Новую копию vendor-кода при необходимости явно переключить на этот commit; скрипт не переписывает существующий checkout. Для Blackwell используем torch/torchaudio 2.10.0+cu128 вместо upstream pin 2.6.0. Установка самого chatterbox делается `--no-deps` после явных inference-зависимостей. Это осознанное отклонение, а не обещание upstream-совместимости: результат проверяется реальным синтезом. UI-зависимости могут отсутствовать; benchmark UI не использует.

## ACE-Step 1.5

Официальный код `https://github.com/ace-step/ACE-Step-1.5`, commit `ca1e85fe9430179831e6bc6be790c332190a3866`, каталог `vendor/ace-step`. Скачать через git, проверить SHA. Модельный snapshot закреплён в download-ace.py. Скачиваются DiT turbo, VAE и text encoder, без дополнительной LM.

```powershell
.venvs/qwen/Scripts/python.exe benchmark/download-ace.py
# После сохранения Qwen freeze; добавляет только inference-зависимости.
.venvs/qwen/Scripts/python.exe -m pip install -r requirements-ace-inference.txt
.venvs/qwen/Scripts/python.exe benchmark/run-ace.py --out results/ace-run1
```

Используется PyTorch 2.10 cu128 и transformers 4.57.3. Upstream Windows installer указывает torch 2.7.1: наш облегчённый inference-путь следует проверять по manifests. `thinking=False`, LM не инициализируется; выгрузка DiT/других компонентов в CPU включена, flash-attention и compile отключены. Наличие адаптера не означает, что запуск прошёл успешно.

## Проверка результатов

```powershell
py -3.12 benchmark/report.py
git status --short
git check-ignore models/example.safetensors .cache/example .venvs/example vendor/example
```

`results/SUMMARY.md` строится из manifests. Не добавлять весь диск или `git add -f models`. В git отправляются небольшие WAV, manifests, документация и код; веса остаются локально.

## Условия сравнения

Seed помогает повторению на той же платформе, но не гарантирует побитовую идентичность между версиями CUDA, kernels и GPU. Первое измерение включает прогрев генерации; загрузка модели записывается отдельно. Время — полная офлайн-генерация, не latency первого аудиопакета для стрима. Полноценный realtime benchmark требует отдельного потокового runner.
