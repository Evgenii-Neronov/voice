"""Export audition files without copying private references or model weights."""
import argparse,json,shutil,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]; p=argparse.ArgumentParser(); p.add_argument('--out-dir',type=Path,required=True); a=p.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
cards=[]
for num,v in enumerate(['minimax-room','ace-boombap','ace-industrial'],1):
 source=R/'results/productions'/('duet-'+v); prefix=f'{num:02}-{v}'; m=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
 for name in ['full.wav','full.mp3','preview.mp3','fx-dry-then-wet.mp3','manifest.json']:
  suffix=name.replace('full.',''); target=f'{prefix}.{suffix}' if name.startswith('full.') else f'{prefix}-{name}'; shutil.copy2(source/name,a.out_dir/target)
 title=html.escape(m['brief']['title']); coverage=m['validation']['ezhi_region_seconds']; duration=m['duration']
 cards.append(f'<section><h2>{num}. {title}</h2><p>{duration:.1f} с · интервалы Ежи {coverage:.1f} с</p><audio controls preload="none" src="{prefix}.mp3"></audio><p><a href="{prefix}.wav">WAV 24-bit</a> · <a href="{prefix}-preview.mp3">Короткая подборка</a></p><p>Эффекты: сначала сухой фрагмент, затем с комнатой и эхом.</p><audio controls preload="none" src="{prefix}-fx-dry-then-wet.mp3"></audio></section>')
page='<!doctype html><html lang="ru"><meta charset="utf-8"><title>ADV + Ежи — три варианта</title><style>body{font:17px system-ui;max-width:900px;margin:40px auto;padding:0 20px;background:#171923;color:#edf0ff}section{background:#242838;padding:24px;border-radius:16px;margin:24px 0}audio{width:100%}a{color:#9dcaff}p{line-height:1.5}</style><h1>ADV + Ежи</h1><p>Три локально сгенерированных варианта. Ежи: музыкальное приветствие и расширенные партии. Русская дикция и псевдоним местами неточны; перенос тембра не гарантирует устранение акцента. Индустриальная версия: вступление MiniMax + основа ACE.</p>'+''.join(cards)+'</html>'
(a.out_dir/'listen.html').write_text(page,encoding='utf-8')
for source,target in [('music/DUET_VARIANTS.md','production-notes.md'),('music/PIPELINE_RECOMMENDATIONS_REVIEW.md','recommendations-review.md'),('results/productions/DUET_VARIANTS.md','results.md')]:
 text=(R/source).read_text(encoding='utf-8')
 text=text.replace('../../music/DUET_VARIANTS.md','production-notes.md').replace('../docs/MUSIC_RESEARCH.md','https://github.com/Evgenii-Neronov/voice/blob/main/docs/MUSIC_RESEARCH.md').replace('(ADV_EZHI.md)','(https://github.com/Evgenii-Neronov/voice/blob/main/music/ADV_EZHI.md)')
 for num,v in enumerate(['minimax-room','ace-boombap','ace-industrial'],1): text=text.replace(f'duet-{v}/full.mp3',f'{num:02}-{v}.mp3')
 (a.out_dir/target).write_text(text,encoding='utf-8')
print(a.out_dir)
