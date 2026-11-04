# Фактические локальные результаты

Автоматические метрики не оценивают эмоции или качество русского. `generated_unrated` требует прослушивания.

| Запуск | Тест | Статус | Аудио, с | Генерация, с | RTF |
|---|---|---|---:|---:|---:|
| ace-run1 | whole run | interrupted_setup | — | — | — |
| ace-run2 | whole run | generated_unrated | — | — | — |
| ace-run2 | song | generated_unrated | 30.00 | 39.75 | 1.32 |
| chatterbox-run1 | neutral | generated_unrated | 4.64 | 42.28 | 9.11 |
| chatterbox-run1 | joy | generated_unrated | 3.12 | 9.14 | 2.93 |
| chatterbox-run1 | anger | generated_unrated | 2.88 | 8.79 | 3.05 |
| chatterbox-run1 | sadness | generated_unrated | 3.44 | 9.13 | 2.65 |
| chatterbox-run1 | drawl | generated_unrated | 3.32 | 9.52 | 2.87 |
| chatterbox-run1 | syllables | generated_unrated | 4.16 | 12.53 | 3.01 |
| chatterbox-run1 | singing_probe | generated_unrated | 5.08 | 13.28 | 2.61 |
| chatterbox-run1 | emotion_control | generated_unrated | 2.84 | 8.30 | 2.92 |
| chatterbox-run1 | neutral_control | generated_unrated | 2.60 | 8.35 | 3.21 |
| qwen17-run1 | neutral | generated_unrated | 4.08 | 34.42 | 8.44 |
| qwen17-run1 | joy | generated_unrated | 3.92 | 30.10 | 7.68 |
| qwen17-run1 | anger | generated_unrated | 2.80 | 20.49 | 7.32 |
| qwen17-run1 | sadness | generated_unrated | 5.92 | 44.45 | 7.51 |
| qwen17-run1 | drawl | generated_unrated | 6.96 | 51.42 | 7.39 |
| qwen17-run1 | syllables | generated_unrated | 4.24 | 32.02 | 7.55 |
| qwen17-run1 | singing_probe | generated_unrated | 9.28 | 70.41 | 7.59 |
| qwen17-run1 | emotion_control | generated_unrated | 2.80 | 20.68 | 7.39 |
| qwen17-run1 | neutral_control | generated_unrated | 4.40 | 33.79 | 7.68 |

## Ошибки

### ace-run1: load/run

```text
Operator interrupted upstream automatic download of unused 1.7B LM. No inference or audio in this attempt. Runner updated to validate only the three required no-LM components and use offline loading.
```
