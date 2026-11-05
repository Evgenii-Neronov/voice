# Rap4: evening isometric cartoon, revision 2

This revision keeps the original audio and scene motifs, adds an orthographic isometric camera travelling through a dimensional evening street, more active asymmetrical lead gestures, independently phased listeners and a shorter reference-inspired Ezhi. The first cartoon remains intact.

## Local tools and dependencies

- Blender4.5.9 LTS, Cycles OptiX GPU path tracing,12 samples,4 bounces and OptiX denoising. EEVEE was used for early previews, then replaced after measured full-resolution tests. Blender license: GPL, https://www.blender.org/about/license/ . Existing local executable under `work/nyc-boombap/tools/blender-4.5.9-windows-x64/`.
- Python3.12, skia-python144.1, numpy2.5.4, scipy1.18.1, Pillow13.0.0. Installed in the previous cartoon's isolated local environment. Skia uses CPU to generate illustrated transparent frames. No cloud image generation.
- FFmpeg and NVIDIA NVENC for final H.264/AAC assembly. https://ffmpeg.org/legal.html
- Existing local faster-whisper-small for word recognition, on the RTX5080. No new model weights and no uploaded audio. https://github.com/SYSTRAN/faster-whisper ; Whisper MIT: https://github.com/openai/whisper
- Rubik Wet Paint font, OFL license included in assets. All scenery and character drawings are procedural original artwork. The supplied portrait is only a visual reference and is not bundled.

## Rebuild

Run from this folder with the appropriate local executables:

1. `python sprites.py` generates the drawing sequences. The existing visemes.npy and beats.json are the audio-derived motion inputs. Regeneration takes about12minutes on this PC.
2. `blender --gpu-backend vulkan -b --python build_scene.py` builds the dimensional scene and camera track.
3. `blender --gpu-backend vulkan -b evening-isometric.blend --python finish_scene.py` applies final shadow pool and render settings.
4. `python run_render.py --preview` renders the opening test. `python run_render.py` renders the full video in parts and burns the yellow subtitles. Edit the paths at the top when moving to another folder.
5. `python verify.py` checks dimensions, duration, full decode and audio correlation, and extracts final review sheets.

To edit just words and timing, use subtitles.ass or subtitles.srt. For hands, head movement, face and clothing, edit art.py, regenerate sprites and rerender. For framing, staging, lights and props, edit build_scene.py or the delivered Blender scene. Times and intentions are in shot-plan.json and BRIEF.md. A missing middle ASR passage was the source of the previous subtitle collapse; the corrected alignment uses fresh overlapping recognition and retains the original first-verse anchors after cross-checking.

## Intentional limits

Characters are illustrated 2D cutouts inside3D architecture. They are not volumetric human meshes. Ezhi is a stylized approximation; rest-pose height is calibrated at about1.65m. Drawings update12times/s and are delivered at24fps. Automatic lip shapes and word boundaries can remain approximate where the generated Russian diction is unclear. Technical validation and sampled-frame review do not constitute full audiovisual playback.

Large sprites, Blender scene, source audio and videos are excluded from Git. The delivered local project archive includes the sprite sequences so the scene can open without regenerating them.
