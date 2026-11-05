# Illustrated Rap4 street seminar

Native2D vector cartoon,2560x1440,24fps delivery with12Hz drawings (two-frame holds). See BRIEF.md for staging and required visual details. The exact supplied MP3 is reused; no cloud generation or voice replacement. All new rendering and audio analysis are local.

## Pipeline

- `prepare_audio.py`: align original lyrics to existing local Whisper word timestamps; combine base and separate outro with256.28s offset.88 subtitle lines. All Unicode em/en/minus dashes become ASCII U+002D. ASS uses Arial56, yellow fill, dark outline and144px bottom margin.
- `phones.py`: local `facebook/wav2vec2-xlsr-53-espeak-cv-ft` checkpoint already present at I:/VOICE/voice/models/lipsync/wav2vec2-espeak; Apache2.0 according to existing model documentation. Reads the assembled vocal stem, emits3403 phone events and15 viseme weights at60Hz. No new weights downloaded or committed. Renderer needs only visemes.npy, not the model.
- `track_beats.py`: spectral-flux and dynamic-programming beat grid from the supplied mix; median estimated90.91BPM. This is automatic analysis, not manually verified drum transcription.
- `art.py`: original vector paths, flat shadow planes, background paper grain, independent pose/gesture phases and local phoneme-driven mouth drawings. Continuous elbow construction avoids opposite-branch flips. No previous 3D assets are required to render the cartoon.
- `render.py`: Skia CPU rasterization into native1440p frames; FFmpeg NVENC p6 CQ18 performs GPU video encoding; AAC320k. Do not describe it as GPU-only rendering. Frame drawing cadence12Hz, final video24fps.
- `export_art.py`: editable SVG background and separate SVG/transparent PNG characters; typography converted to vector paths.
- `verify.py`: dimensions/rate/duration, full-file decode, source audio alignment at0/130/260s, subtitle dash check, final contact sheets.

## Reproduction

From the original workspace:

```powershell
& work/rap4-cartoon/.venv/Scripts/python.exe work/rap4-cartoon/render.py
& work/rap4-cartoon/.venv/Scripts/python.exe work/rap4-cartoon/render.py --start 250 --duration 23.188571 --name outro-preview
& work/rap4-cartoon/.venv/Scripts/python.exe work/rap4-cartoon/verify.py
```

Pinned renderer dependencies are in requirements.txt. The phoneme analysis uses the pre-existing qwen environment with PyTorch/Transformers; weights remain gitignored in the repository models folder. Source transcript/stem paths are recorded in scripts. The delivery ZIP includes a self-contained renderer project with the original track and precomputed analysis; the large track is excluded fromGit.

## Sources and licenses

- New drawing geometry and scene/animation code authored for this project. No external photo textures or reference photographs are embedded in the final drawing assets.
- Skia Python bindings: https://github.com/kyamagu/skia-python ; package144.1, BSD3-Clause. Skia: https://skia.org/ , BSD-style license. Local rasterizer.
- NumPy and SciPy: BSD3-Clause; Pillow13: MIT-CMU; bundled dependency notices are supplied in the portable project. Exact installed versions in requirements.txt.
- ADV graffiti uses Rubik Wet Paint from the prior local asset cache, originally https://github.com/google/fonts/tree/main/ofl/rubikwetpaint ; SIL OFL copy included with font. Windows Arial is used for subtitles, not redistributed.
- Phoneme checkpoint: https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft ; reused local weights, Apache2.0 according to model card recorded in prior project.
- User's supplied Ezhi reference informs glasses, beard, hairstyle and checked jacket. No assertion of exact likeness. Reference image is not committed or uploaded.

## Review scope and limitations

Opening and outro moving previews were rendered and inspected through temporal contact sheets. Final verification includes18 sampled frames and full decode/audio tests; no claim of full audiovisual playback. This is a procedural puppet cartoon with deliberately held drawings, not bespoke hand-animated frame-by-frame acting. Likeness, phoneme timing and lyric alignment remain approximate. User requested the entire final block from 'Семинар окончен' to be staged as Ezhi; the original soundtrack is untouched.
