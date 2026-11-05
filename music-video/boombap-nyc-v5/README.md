# ADV boombap NYC v5

New 2560×1440, 24 fps edit of the approved 253.29-second video.

Changes: growing lettering resolves into ЭКВИВАЛЕНТ; real downloadable bird-whistle model with clay shading; head motion reduced to 18% and neck to 30% around their average local orientation; fixed pelvis/legs and calibrated sole height prevent street foot skating; separate AIST++ hip-hop dance on rooftop. Approximately 49.7% street remains. Original audio, yellow captions and 144 px bottom margin are retained; long dashes are ASCII hyphens.

## Local reproduction
Blender 4.5.9 LTS, EEVEE with ray tracing, Vulkan, 16 samples; FFmpeg NVENC; Python 3.12 + numpy, scipy, Pillow, skia-python.
Use render_street.py with street-v5.blend and shot index, or render_shot.py with sets/lab.blend (8/14) and sets/dance.blend (11). Original unchanged shots come from the prior v4 project. Run graffiti.py, then assemble.py and verify.py. Scripts and edit-plan.json identify frame-exact boundaries.

## Limits
Street lower-body animation is deliberately planted rather than a walking performance; upper-body gestures and approximate lip articulation are inherited. Dance is an automatic retarget, not a hand-polished production animation. Visual QA uses moving previews and sampled temporal frames; it is not a claim of full real-time audiovisual playback.


## Packaged project commands (PowerShell)

Run from the unpacked project folder. Install Python requirements once:

```powershell
python -m pip install -r requirements.txt
$env:BLENDER_EXE = 'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'
python run_render.py
& $env:BLENDER_EXE -b sets/lab.blend --gpu-backend vulkan --python render_shot.py -- 8 full
& $env:BLENDER_EXE -b sets/lab.blend --gpu-backend vulkan --python render_shot.py -- 14 full
& $env:BLENDER_EXE -b sets/dance.blend --gpu-backend vulkan --python render_shot.py -- 11 full
python graffiti.py
python assemble.py
python verify.py
```

To only reassemble the supplied clean shots with edited captions, run `assemble.py`. The complete audio is in `audio/original.m4a`. Source builders are retained for provenance; rebuilding the prior original set geometry requires the v4 project. The supplied street scene and dancer scene have packed textures. The supplied bird STL and modified bird geometry retain CC BY-SA 4.0 attribution.
