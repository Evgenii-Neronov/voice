from pathlib import Path
import sys,subprocess,concurrent.futures,json,shutil,hashlib,zipfile
W=Path(__file__).resolve().parent;V3=W.parent/'rap4-montage-v3';ROOT=W.parents[1];P3=ROOT/'outputs/rap4-montage-v3-1440p';O=ROOT/'outputs/rap4-montage-v4-1440p';O.mkdir(parents=True,exist_ok=True);SRC=P3/'ADV-rap4-hiphop-montage-v3-1440p.mp4';V=O/'ADV-rap4-hiphop-montage-v4-1440p.mp4';BL=W.parent/'nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe';scene=P3/'project/street-no-graffiti.blend'
def cmd(args,log):
 with (W/log).open('w') as f:subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
def render(j):
 i,a,b=j;p=W/f'outro-{i}.mp4';cmd([BL,'-b',scene,'-t','4','--python-exit-code','1','--python',W/'bind_ezhi.py','--python',W/'render_part.py','--',a,b,p,100],f'part-{i}.log');print('Rendered',i,flush=True)
assert (W/'sprites/ezhi/03279.png').exists()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(render,[(0,2989,3085),(1,3086,3182),(2,3183,3279)]))
(W/'parts.txt').write_text('\n'.join(f"file 'outro-{i}.mp4'" for i in range(3)));cmd(['ffmpeg','-v','error','-y','-f','concat','-safe',0,'-i',W/'parts.txt','-c','copy',W/'street-outro.mp4'],'join.log');print('Assembling',flush=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(V3/'street-opening.mp4'),'-i',str(V3/'illustrated-middle.mp4'),'-i',str(W/'street-outro.mp4'),'-i',str(SRC),'-filter_complex','[0:v]fps=24,trim=duration=8,setpts=PTS-STARTPTS[a];[1:v]fps=24,trim=duration=241,setpts=PTS-STARTPTS[b];[2:v]fps=24,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,ass=subtitles.ass[v]','-map','[v]','-map','3:a:0','-t','273.188571','-r','24','-c:v','h264_nvenc','-preset','p6','-cq','18','-b:v','0','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(V)],cwd=W,check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))['streams'][0]
v=probe(V);assert (v['width'],v['height'],v['nb_frames'],v['r_frame_rate'])==(2560,1440,probe(SRC)['nb_frames'],'24/1')
def ah(p):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','-'])).hexdigest()
assert ah(V)==ah(SRC);assert (W/'subtitles.ass').read_text(encoding='utf8')==(V3/'subtitles.ass').read_text(encoding='utf8').replace('220,220,144,1','220,220,72,1');cmd(['ffmpeg','-v','error','-xerror','-i',V,'-f','null','-'],'decode.log');r={'frames':v['nb_frames'],'duration':v['duration'],'audio_identical':True,'margin_px':72,'height':1440,'full_decode':'passed','source_v3':SRC.name,'rerendered_interval':[249,273.208333]};(O/'validation.json').write_text(json.dumps(r,indent=2));print('Verified',flush=True)
