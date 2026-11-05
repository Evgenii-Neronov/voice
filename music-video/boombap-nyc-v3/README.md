# NYC boombap v3

Revision of the 253.283265-second original `07-minimax-trio-boombap-01.mp3` video. Delivery: 2560 x 1440 at 24 fps, 6079 frames. V1 and V2 are preserved.

## Requested changes

- Repair transient skeletal glitches on all three performers.
- More visible independent head/body listening in time with the music.
- Remove passerby, all of his wardrobe, and NY cap lettering.
- Restore V1 lighting and colour management.
- Yellow bottom-centred subtitles with 144px bottom margin (10% of 1440), unchanged text/timings.

## Root cause and repair

V2 contained quaternion keys with opposite signs for equivalent rotations. Component-wise linear interpolation crossed the near-zero quaternion and caused almost 180-degree intermediate-frame flips. Sampling stills at keyed frames missed this defect. `fix_scene.py` makes quaternion signs continuous, normalizes interpolation, applies a mild three-frame symmetric smoothing filter and writes every output frame. The report compares every integer frame before/after for all three skeletal rigs. Before: 5918/1522/84 bone-frame transitions over 30 degrees; after: zero on each actor. These counts are bone transitions, not unique video frames. This is a numerical continuity check, not a claim of perfect acting.

The original motion, camera, lead appearance, facial visemes, props and composition remain. Listening adds different bounded head, upper-body and shallow knee accents to each companion. `track_beats_fast.py` estimates a beat grid with a median 92.31 BPM from original-mix spectral flux and dynamic programming, following local onset timing. This is automatic analysis, not a manually verified drum transcription.

`export_lighting.py` reads light transforms, power, colour, size, world colour/strength and colour management from `nyc-boombap/nyc-final-scene.blend`. V1 exposure is -1.25. Distant lamps retain illumination but do not allocate shadow maps (existing EEVEE atlas limitation); performance key lights retain shadows.

## Rebuild

Run from the original dated workspace; scripts resolve working paths relative to themselves. Input scene: `work/nyc-boombap-v2/film-v2.blend`. The complete V2 preparation is documented in the adjacent Git folder.

1. Python: `track_beats_fast.py`.
2. Blender on V1: `export_lighting.py`.
3. Blender on V2: `fix_scene.py`, producing `film-v3.blend` and `motion-validation.json`.
4. `prepare_delivery.py`; render a moving opening/transition preview with `render_baked.py` and inspect its temporal contact sheet.
5. `run_full.py`: 12 chunks / 3 Blender workers, native 1440p, EEVEE Vulkan 24 samples and ray tracing. FFmpeg NVENC p6 CQ18, AAC320k. Original track is reused.
6. `verify_final.py`: dimensions, rate, duration, frame count, full decode, audio alignment at 0/120/240 seconds, sampled final frames.
7. Blender on V3: `package_project.py`; `archive_project.py` packs editable delivery, textures/fonts/audio, subtitles and documentation.

Python: existing qwen Python 3.12 environment (NumPy, SciPy). Blender 4.5.9 LTS. No new neural model or download required. The abandoned librosa analysis is not part of this pipeline.

## Sources and limitations

Microsoft Rocketbox models/motion: MIT (Microsoft 2020), reused from V2; Poly Haven textures: CC0; Rubik Wet Paint: SIL OFL. See V2 source documentation and included licenses. No weights or full media are committed.

The result remains stylized stock 3D, with approximate automatic phoneme articulation and retargeted captured conversation gestures. Full playback is not claimed when QA uses sampled frames/temporal contact sheets. Final measured output is recorded in `validation.json` after completion.
