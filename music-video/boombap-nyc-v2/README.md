# NYC boombap v2

Revision of the full 253.283265-second video for `07-minimax-trio-boombap-01.mp3`. Original audio is retained. Target delivery: 2560×1440, 24 fps, 6079 frames. V1 is preserved.

## Visible changes

- Lead keeps the original adult-17 face/cap/yellow outfit, with smoother silhouettes and refined cloth/skin materials. Opening walk covers 2.2 metres on the road while the camera retreats.
- Two companions use distinct captured listening/idle clips, phase offsets and small independent head accents. Bone rest-space correction fixes the previous spread-arm retargeting defect.
- All performers stand on the road. Detailed bicycle is parked by the building; cassette boombox is on the sidewalk.
- Reference-inspired passerby wears a fedora, brown coat, white shirt and dark tie. Nominal unposed body height is calibrated to 1.83m. He approaches, decelerates/turns, listens approximately 48–64s, and leaves. His face is an approximation, not a portrait reconstruction.
- ADV paint lettering appears toward the right edge of the pale foundation. NY is on the cap. These are the only in-scene text exceptions requested by the user.
- Yellow cinema subtitles use a 190px bottom margin at 1440p, previously 105px.

## Lip motion

`phones.py` runs `facebook/wav2vec2-xlsr-53-espeak-cv-ft` locally on the original isolated vocal stem, resampled to 16kHz. It produced 3116 nonblank phone events. Sparse CTC peaks are mapped to 15 Rocketbox visemes, interpolated within a bounded coarticulation window, smoothed at 60Hz and gated by vocal amplitude. This replaces amplitude-only mouth opening. It is automatic approximate lipsync, not verified phoneme-perfect facial capture.

Weights are in `I:/VOICE/voice/models/lipsync/wav2vec2-espeak`, already covered by repository `.gitignore`; no weights are committed. Exact downloaded file hashes and installed Python versions are in `dependencies.json`. Audio2Face SDK was researched but not installed or used.

## Rendering and editability

Blender 4.5.9 LTS, RTX 5080. Cycles/OptiX was used for lighting and motion review; final frames use EEVEE/Vulkan with ray tracing enabled and 24 samples. These are different renderers; EEVEE is not full path tracing. Final encoding uses FFmpeg `h264_nvenc`, p6, CQ18, AAC320k. Audio analysis, animation evaluation and some encoding preparation use CPU.

The delivered `.blend` has editable baked skeletal/root/camera actions, separate facial shape keys, packed textures/fonts and packed original audio. It needs no Python frame handler for playback. Blender 4.5 action slots are explicitly assigned after bulk curve creation. Subtitles are supplied separately as ASS/SRT and burned into the delivery MP4.

## Rebuild order

These scripts were executed from the dated Codex workspace under `work/nyc-boombap-v2`. The `../nyc-boombap` directory supplies the preserved v1 assets/base scene. Set the workspace paths if rebuilding elsewhere.

1. `download_motion.py`, `download_passerby.py`, `download_phones.py`; obtain Rubik Wet Paint from the source below.
2. Blender background: `extract_motion.py`; Python qwen environment: `phones.py`.
3. Load v1 `nyc-final-scene.blend`, run `build_v2.py` → `scene-v2.blend`.
4. Load `scene-v2.blend`, run `animate.py -- bake` → `film-v2.blend`. Current code includes the smooth passerby transitions and slot fix; `bakepass`/`fix_slots.py` record the development corrections.
5. On `film-v2.blend`, run `finish_set.py`, then `finish_details.py`. On `scene-v2.blend`, run `measure_height.py`; then on `film-v2.blend`, run `finish_delivery_scene.py`.
6. Inspect short moving previews with `render_baked.py -- START END OUTPUT PERCENT [eevee]`. `review_baked.py` renders selected stills. Review limitations are explicit in final validation.
7. `run_full.py` renders 12 contiguous chunks, 3 processes maximum, then joins, burns ASS and muxes the original track. `verify_final.py` checks resolution/rate/duration, every-frame decode and audio alignment at beginning/middle/end.
8. `package_project.py` packs the separate editable delivery scene. It does not change the render source.

Example local commands:

```powershell
& I:/VOICE/voice/.venvs/qwen/Scripts/python.exe work/nyc-boombap-v2/phones.py
& work/nyc-boombap/tools/blender-4.5.9-windows-x64/blender.exe -b work/nyc-boombap-v2/scene-v2.blend --python work/nyc-boombap-v2/animate.py -- bake
& I:/VOICE/voice/.venvs/qwen/Scripts/python.exe work/nyc-boombap-v2/run_full.py
& I:/VOICE/voice/.venvs/qwen/Scripts/python.exe work/nyc-boombap-v2/verify_final.py
```

## Sources and licenses

- [Microsoft Rocketbox](https://github.com/microsoft/Microsoft-Rocketbox): adult17 (lead), adult18/adult12 (listeners), adult08 (passerby), captured gestures/walks; MIT, copyright Microsoft 2020. Original license accompanies the project. Existing lead topology was refined rather than replaced by a new scanned person.
- [Poly Haven](https://polyhaven.com): red_bricks_04, asphalt_02, concrete_wall_006, industrial_sunset_puresky HDRI; CC0. HDRI reused from local Unreal asset cache.
- [Phoneme recognition checkpoint](https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft): Apache-2.0 per model card; local inference only.
- [Rubik Wet Paint](https://github.com/google/fonts/tree/main/ofl/rubikwetpaint): SIL OFL, included license. Used for ADV graffiti.
- Bicycle, boombox, coat/hat/tie/lapels and architecture detailing: procedural project geometry.
- User-supplied portrait is used only as a local visual reference and is not copied into the repository.

## Limits

This is a more developed stylized 3D scene, not photoreal footage. Subdivision/material refinement does not turn the preserved stock character into a modern facial scan. Conversation clips are retargeted and edited into a rap performance rather than captured rap-specific acting. The passerby borrows the reference wardrobe but is not an exact likeness. Native phoneme recognition improves mouth timing but cannot guarantee every rapid syllable. Final factual validation is recorded in `validation.json` once the render completes.
