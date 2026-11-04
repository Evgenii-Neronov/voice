"""Package selected actual runs with an offline HTML listening table (no weights)."""
import argparse
from html import escape
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--output',type=Path,required=True)
p.add_argument('runs',nargs='+')
a=p.parse_args()
assert not a.output.exists(),'Refusing to overwrite an existing listening package'
cases=json.loads((ROOT/'benchmark/cases.json').read_text(encoding='utf-8'))
manifests={name:json.loads((ROOT/'results'/name/'manifest.json').read_text(encoding='utf-8')) for name in a.runs}
labels={'qwen17-run1':'Qwen3-TTS 1.7B','chatterbox-run1':'Chatterbox Multilingual V3','fish-s2-q8-run1':'Fish S2 Pro Q8','fish-s2-q4-run1':'Fish S2 Pro mixed Q4','higgs3-q8-run4':'Higgs TTS 3 Q8','drama3-q2-pinned-run1':'Drama 3 Q2 + RAM'}
case_labels={'neutral':'Нейтральная речь','joy':'Радость','anger':'Гнев','sadness':'Печаль','drawl':'Манерная протяжная речь','syllables':'Протяжные гласные','singing_probe':'Проба пения','emotion_control':'Контроль: радостное облегчение','neutral_control':'Контроль: нейтрально'}
parts=['<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Voice benchmark</title>',
 '<style>body{font:16px system-ui;margin:24px;background:#f7f7f7;color:#222}table{border-collapse:collapse;background:white}td,th{border:1px solid #ccc;padding:14px;vertical-align:top}audio{width:240px}td:first-child{min-width:260px}small{display:block;margin-top:8px;color:#555}</style>',
 '<h1>Одинаковые русские тексты — сравнение моделей</h1>',
 '<p>Синтетические WAV. Один seed; слуховые оценки ещё не выставлены. Пение — свободная проба без заданной мелодии.</p>',
 '<p>Built with Fish Audio. Higgs samples generated with Boson AI’s Higgs Audio (Higgs TTS 3).</p>',
 '<p>Откройте этот файл после распаковки ZIP; интернет не требуется. Таблицу можно прокручивать вправо.</p><div style="overflow:auto"><table><thead><tr><th>Тест и текст</th>']
parts += ['<th>'+escape(labels.get(name,name))+'<small>'+escape(name)+'</small></th>' for name in a.runs]
parts += ['</tr></thead><tbody>']
for case in cases:
 parts += ['<tr><td><b>'+escape(case_labels.get(case['id'],case['id']))+'</b><p>'+escape(case['text'])+'</p><details><summary>Исходное задание</summary><small>'+escape(case['instruction'])+'</small></details></td>']
 for name,data in manifests.items():
  row=next((r for r in data.get('cases',[]) if r['id']==case['id']),None)
  if row and row['status'].startswith('generated_'):
   src=name+'/'+row['wav']
   parts += ['<td><audio controls preload="none" src="'+escape(src,quote=True)+'"></audio><small>'+f"{row['duration_seconds']:.2f} с"+'</small><small>'+escape(row.get('completion_warning',''))+'</small><details><summary>Подача</summary><small>'+escape(row.get('effective_prompt',row.get('instruction','')))+'</small></details></td>']
  else: parts += ['<td>WAV не получен</td>']
 parts += ['</tr>']
parts += ['</tbody></table></div></html>']
a.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as archive:
 archive.writestr('listen.html','\n'.join(parts))
 for name,data in manifests.items():
  archive.write(ROOT/'results'/name/'manifest.json',name+'/manifest.json')
  for row in data.get('cases',[]):
   if row['status'].startswith('generated_'): archive.write(ROOT/'results'/name/row['wav'],name+'/'+row['wav'])
 archive.write(ROOT/'docs/NATIVE_BENCHMARK.md','NATIVE_BENCHMARK.md')
 archive.write(ROOT/'results/SUMMARY.md','SUMMARY.md')
print(a.output, a.output.stat().st_size)
