# Motion sources and attribution

Downloaded on 2026-11-05 from the official AIST++ release:
https://github.com/google/aistplusplus_dataset/releases/download/v1.0/keypoints3d.zip

Archive SHA-256: `8b2a3bfcea233b8d1859a0dc93c7800a8f9e832136ef6828d0b3ddff640ddcfd`.

**AIST++ motion annotations, Google LLC, CC BY 4.0.**
- License statement: https://google.github.io/aistplusplus_dataset/factsfigures.html
- License: https://creativecommons.org/licenses/by/4.0/
- Dataset and format: https://google.github.io/aistplusplus_dataset/download.html
- Ruilong Li, Shan Yang, David A. Ross, Angjoo Kanazawa. *AI Choreographer: Music Conditioned 3D Dance Generation with AIST++*, ICCV 2021.
- Original AIST dance database: Shuhei Tsuchida, Satoru Fukayama, Masahiro Hamasaki, Masataka Goto. *AIST Dance Video Database: Multi-genre, Multi-dancer, and Multi-camera Database for Dance Information Processing*, ISMIR 2019.

Only the optimized COCO17 3D annotation arrays were used. No original AIST video, audio, SMPL model or dataset music is included. Original video terms are separate from the annotation license. No endorsement by the dataset creators is implied.

Changes: 276 hip-hop sequences numerically screened; 64 six-second source windows retained; shoulder-relative 2D projection, smoothing, slowing, independent sequencing, restrained amplitude, rest/phrase envelopes and velocity limiting. `motion-sources.json` identifies every source window; `motion-edit-*.json` records its placement. Derived NPZ motion arrays are adaptations of these CC BY 4.0 annotations and retain this attribution. Screening is our own numeric filter, not the official dataset ignore list.

## Performance research
The Max Planck Institute project's description treats rap body movement as audience interaction, alongside verbal phrases:
https://www.aesthetics.mpg.de/en/research/department-of-music/aesthetic-experience-contexts/live-performances/rappin-and-rocking-the-house-typical-body-movements-and-verbal-phrases-in-rap-performance.html

This informed the decision to use sparse phrase-directed gestures and pauses rather than continuous dance. The exact gesture envelopes are authored choices, not published results from that project.

## Artwork and audio
New location drawings and montage are authored locally in code for this clip. Character drawings and street assets reuse the prior project. Ezhi remains reference-inspired and approximate. The user's original track is unchanged in content, with AAC encoding for the delivered MP4. Font license is preserved under `assets/` from the previous project. No generated background images or stock videos were used for the new locations.
