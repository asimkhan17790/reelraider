## Why

The current clipper extracts a single 55-second window based on audio RMS alone, producing clips unsuitable for YouTube Shorts (wrong aspect ratio, no highlight curation). Shorts require a 9:16 vertical format and a ~25-second runtime that condenses the best moments of the source video.

## What Changes

- Replace single-window extraction with multi-segment highlight detection
- Score candidate windows using a composite signal: spectral flux + scene change rate + face density + YouTube chapter markers
- Select top non-overlapping segments totalling ~25 seconds via greedy peak selection
- Apply 16:9 → 9:16 center crop (face-aware as future option) during extraction
- Stitch segments with crossfade transitions using ffmpeg `filter_complex`
- Output a single 25-second H.264 `.mp4` YouTube Short per source video
- Add new config keys: `SHORT_TOTAL_DURATION`, `SHORT_SEGMENT_DURATION`, `SHORT_NUM_SEGMENTS`, `SHORT_CROP_MODE`, `SHORT_TRANSITION_DURATION`

## Capabilities

### New Capabilities

- `highlight-scoring`: Composite multi-signal scoring (spectral flux, scene change rate, face density, chapter markers) over sliding windows to rank candidate clip moments
- `segment-selection`: Greedy non-overlapping peak selection to choose N best windows from scored timeline
- `vertical-crop`: ffmpeg crop transform from 16:9 source to 9:16 Shorts format
- `clip-stitching`: ffmpeg `filter_complex` xfade pipeline to concatenate segments with transitions into a single output

### Modified Capabilities

<!-- None — clipper is currently unspecced; all capabilities above are new -->

## Impact

- **`pipeline/clipper.py`**: Full rewrite of `extract_clip()` and `_find_best_window()`; new helper functions per capability
- **`config.py`**: 5 new env-var config keys with sensible defaults
- **Dependencies added**: `librosa` (spectral flux), `PySceneDetect` or direct ffmpeg scene filter (scene change), `mediapipe` or `opencv-python` (face density — optional/soft dep)
- **Pipeline contract unchanged**: `extract_clip()` still takes `(video_path, video_id)` and returns `str | None`; downstream stages unaffected
- **YouTube API**: Chapter markers already fetched in `discovery.py` via `snippet`; clipper reads from video metadata dict (requires passing metadata through pipeline)
