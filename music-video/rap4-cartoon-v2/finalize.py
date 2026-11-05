from pathlib import Path
import json,shutil,zipfile,hashlib,subprocess
W=Path(__file__).resolve().parent;O=W.parents[1]/'outputs/rap4-cartoon-v2-1440p';P=O/'project';v=json.loads((O/'validation.json').read_text());status=json.loads((W/'status.json').read_text());assert v['full_decode']=='passed' and status['state']=='complete'
for name in ['README.md','BRIEF.md','subtitle-validation.json','neck-validation.json','project-validation.json','shot-plan.json','subtitles.ass','subtitles.srt']:
 shutil.copy2(W/name,P/name);shutil.copy2(W/name,O/('TECHNICAL.md' if name=='README.md' else name))
prod={'render_seconds':status['seconds'],'renderer':v['renderer'],'video_sha256':v['sha256'],'duration':v['duration'],'original_audio_preserved_without_remix':True,'reference_image_included':False,'new_models_downloaded':False,'ezhi_height_metres':1.65,'animation_rate':12,'delivery_fps':24,'changes':['isometric orthographic camera with real translation and contrasting shot sizes','evening practical lanterns and Cycles ray-traced light/shadows/reflections','stronger asymmetric lead gestures and independently phased listeners','fixed overlapping neck and base-pivot head rotation','shorter broader Ezhi with rectangular glasses and revised beard/hair','recovered missing middle subtitle passage using fresh short-window local ASR']}
(O/'production.json').write_text(json.dumps(prod,indent=2));shutil.copy2(O/'production.json',P/'production.json');shutil.copy2(O/'validation.json',P/'validation.json')
(O/'README.md').write_text('# Вечерний изометрический мультклип\n\nПолная версия: ADV-rap4-evening-isometric-1440p.mp4, 2560×1440,24fps,4:33.\n\nРисованные персонажи в объёмной сцене; свет, тени и отражения рассчитаны Cycles на RTX5080. Ежи ниже остальных: номинальный рост165см. Головы качаются вокруг основания шеи, жесты и кивки имеют отдельные ритмические фазы. Жёлтые субтитры подняты на144px; длинные тире заменены на ASCII -. Середина таймингов восстановлена по вокальной дорожке.\n\nПроект находится в project/ и в ZIP. Он содержит сцену Blender, рисунки всех кадров, исходный звук и настройки. Весы моделей и фотография-референс в архив не включены.\n\nОграничения: персонажи плоские рисованные, не объёмные человеческие модели; сходство Ежи стилизованное. Артикуляция и границы слов автоматически рассчитаны и приблизительны. Проверены короткий движущийся проход, кадры разных секций, связность шеи и техническая целостность файла; это не заявление о полном просмотре со звуком.\n',encoding='utf8')
# Replace preliminary EEVEE preview with a clip cut from the actual Cycles delivery.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(O/v['video']),'-t','12','-vf','scale=1280:720','-c:v','h264_nvenc','-cq','20','-c:a','copy',str(O/'opening-preview.mp4')],check=True)
zpath=O/'editable-evening-project.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for f in P.rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and 'renders' not in f.parts and f.suffix!='.blend1':z.write(f,f.relative_to(P))
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
h=hashlib.sha256()
with zpath.open('rb') as f:
 for b in iter(lambda:f.read(4194304),b''):h.update(b)
(O/'archive-validation.json').write_text(json.dumps({'bytes':zpath.stat().st_size,'sha256':h.hexdigest(),'crc':'passed'},indent=2));print('Delivery packaged',flush=True)
