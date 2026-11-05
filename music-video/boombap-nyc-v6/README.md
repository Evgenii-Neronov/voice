# NYC v6

1440p / 24 fps / 6079 frames. All bird-whistle, painted-word and dancer inserts are replaced by street performance at the same original song times. Street share is about 74%, as requested by these replacements. Existing studio, metro and rooftop shots remain.

The opening restores the lead advancing 2.2 metres over 6.8 seconds with the retreating camera, followed by a smooth transition to the quiet planted v5 stance. Only the lead's lower-body walking curves are restored; listeners retain v5 motion. The lowest sole is calibrated to the road each opening frame. Growing ochre contour curves in studio and metro are now red; other materials are retained.

Original audio is copied without re-encoding. Yellow subtitles retain timing and 144 px bottom margin, with ordinary ASCII hyphens.

Local tools: Blender 4.5.9, EEVEE Vulkan with ray tracing, 16 samples; FFmpeg/NVENC. See requirements.txt for Python packages. All supplied scene textures are packed.

From the project folder, `python assemble.py` rebuilds the supplied clean shots with captions and original audio. To render one street shot: `blender -b street-v6.blend --gpu-backend vulkan --python render_street.py -- 8 full`. For studio or metro use their set scene with render_shot.py and corresponding shot index. edit-plan.json defines all frame intervals.

Review uses temporal sample frames and technical checks, not a claim of real-time viewing of the entire film. Lip articulation remains approximate.

For a complete local re-render, set BLENDER_EXE to the Blender executable and run `python run_render.py`; existing valid shot files are reused. Delete or move only the specific shot you want to regenerate. The package also includes the unchanged roof set.

Build provenance: restore_opening.py reads the loaded v3 scene and sibling nyc-boombap-v5/street-v5.blend; red_wires.py reads a supplied v4 set. These source-build inputs are needed only to rebuild the edits from prior versions. Rendering the supplied packed v6 scenes does not require the older projects.
