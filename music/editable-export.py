"""Export dry samples and a portable audio-only editing session."""
import argparse,json,shutil,zipfile,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]; cli=argparse.ArgumentParser(); cli.add_argument('--out-dir',type=Path,required=True); a=cli.parse_args(); d=a.out_dir; d.mkdir(parents=True,exist_ok=True); session=d/'session'; session.mkdir(exist_ok=True)
mini=R/'results/productions/editable-minimax-01'; mod=R/'results/editable/modular'
for ext in ['wav','mp3']: shutil.copy2(mini/('full.'+ext),d/('MiniMax-new-dry.'+ext))
for name in ['01-original-beat','02-beat-patch','03-line-retake']:
 for ext in ['wav','mp3']: shutil.copy2(mod/(name+'.'+ext),d/(name+'.'+ext))
p=json.loads((R/'music/editable/project.json').read_text(encoding='utf-8')); tracks=[]
for f in mod.glob('*.wav'):
 if f.name[:2] not in ['01','02','03']: shutil.copy2(f,session/f.name)
for row in p['phrases']:
 tracks.append({'id':row['id'],'file':row['id']+'.wav','start_seconds':row['start'],'duration_seconds':row['duration'],'voice':row['role'],'text':row['text'],'alternative':row['id']=='changed-line-alt'})
(session/'timeline.json').write_text(json.dumps({'bpm':96,'duration':45,'beat_files':['beat-original.wav','beat-edited.wav'],'full_voice_files':['vocal.wav','vocal-retake.wav'],'phrases':tracks,'note':'Import beat and either full vocal at t=0, OR individual phrases at their starts. Do not add full vocal and phrases simultaneously.'},ensure_ascii=False,indent=2),encoding='utf-8')
(session/'README.txt').write_text('Сухой монтаж, 96 BPM, 45 секунд.\nБит и целый vocal.wav ставятся на начало 0. Вместо целого вокала можно поставить отдельные реплики по timeline.json. Не складывать целый вокал с его репликами — получится удвоение.\nbeat-edited.wav меняет 10–20 с; vocal-retake.wav меняет одну строку 32,5–37,5 с. Ежи: ezhi-one.wav, 37,5 с. Никаких добавленных эха/реверберации.\nНовая нейрогенерация фраз выполняется скриптами репозитория; эти WAV можно редактировать в любой DAW.\n',encoding='utf-8')
with zipfile.ZipFile(d/'editable-session.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for f in session.iterdir(): z.write(f,'session/'+f.name)
shutil.copy2(R/'music/EDITABLE_DRY.md',d/'notes.md'); shutil.copy2(R/'results/editable/checks.json',d/'checks.json')
shutil.copy2(R/'results/editable/diagnostics/natural-line.mp3',d/'F5-natural-line.mp3')
cards=[]
for title,file,note in [('MiniMax — новая полная версия','MiniMax-new-dry','3:42. Основной голос ADV; Ежи только 2:11,18–2:12,80.'),('Модульный вариант — F5 RU и отдельный бит','01-original-beat','45 секунд. Каждая реплика синтезирована отдельно.'),('Заменён только участок бита','02-beat-patch','Сравни 10–20 секунды с предыдущим вариантом.'),('Заменена только читка одной строки','03-line-retake','Сравни 32,5–37,5 секунды. Остальное сохранено.')]:
 cards.append(f'<section><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p><audio controls preload="none" src="{file}.mp3"></audio><p><a href="{file}.wav">WAV</a></p></section>')
page='<!doctype html><html lang="ru"><meta charset="utf-8"><title>ADV + Ежи — сухие пробы</title><style>body{font:17px system-ui;max-width:900px;margin:40px auto;padding:0 20px;background:#151b23;color:#f0f2f8}section{background:#252e3a;padding:24px;border-radius:14px;margin:22px 0}audio{width:100%}a{color:#9ed2ff}p{line-height:1.5}</style><h1>Сухие пробы и точечные замены</h1><p>Все вычисления локальные. F5-варианты — короткие монтажные эксперименты, не полная песня. Дикция и сходство голосов требуют прослушивания.</p>'+''.join(cards)+'<p><a href="F5-natural-line.mp3">Дополнительная проба F5: строка с естественной длительностью</a></p><p><a href="editable-session.zip">Дорожки и таймлайн для монтажа (ZIP)</a> · <a href="notes.md">Методы и команды</a></p><section><h2>Прежний выбранный ориентир</h2><audio controls preload="none" src="../ADV-feat-Ezhi-MiniMax.mp3"></audio></section></html>'
(d/'listen.html').write_text(page,encoding='utf-8'); print(d,flush=True)
