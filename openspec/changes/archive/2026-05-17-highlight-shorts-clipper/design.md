## Context

`pipeline/clipper.py` currently extracts a single window using audio RMS max over the full video. Output is 16:9, up to 55 seconds — incompatible with YouTube Shorts requirements (9:16, ≤60s, optimally ~25s). The new design replaces this with a multi-signal highlight detection pipeline that scores the full video timeline, selects the best non-overlapping moments, crops to vertical format, and stitches them into a single Short.

The pipeline contract (`extract_clip(video_path, video_id) → str | None`) is preserved. The function signature gains an optional `metadata` dict to carry chapter markers from the discovery phase.

## Goals / Non-Goals

**Goals:**
- Produce a 9:16, ~25s YouTube Short from any source video
- Score highlight candidates on 4 signals: spectral flux, scene change rate, face density, YouTube chapter presence
- Select non-overlapping best windows via greedy peak selection
- Stitch with crossfade transitions in one ffmpeg pass
- Keep encode to H.264 for universal compatibility
- Degrade gracefully when optional signals (face, chapters) are unavailable

**Non-Goals:**
- Audio replacement / background music overlay (future)
- Face-tracked dynamic crop (center crop only in v1)
- Re-ranking clips in non-chronological order
- Any UI or preview tooling
- Changing the pipeline stage interface beyond the optional `metadata` arg

## Decisions

### D1: Composite scoring via normalized signal sum
Score each 0.5s-step window as weighted sum of normalized signals:
```
score = 0.25*rms_norm + 0.35*flux_norm + 0.25*scene_norm + 0.15*face_norm
```
Chapter markers add a `+0.5` bonus to any window overlapping a chapter boundary (not normalized — acts as a hard boost).

**Why not ML-based ranking?** No labeled data, no inference latency budget in pipeline. Signal-based scoring is fast, interpretable, tunable via weights.

**Weights rationale:** Spectral flux is the strongest single predictor of "event moments" in video. RMS alone is too broad. Scene change and face density add visual energy signal. Chapters are sparse but highly reliable when present.

### D2: Greedy non-overlapping window selection
After scoring all windows, iterate score descending: pick window, mark `[start, end]` as used with a guard margin of 0.5s on each side, repeat until total duration ≥ `SHORT_TOTAL_DURATION`. Sort selected windows chronologically before stitching.

**Why not DP?** Greedy is O(n log n), sufficient for videos up to 60 min. DP would only matter if we had complex per-window cost functions.

### D3: ffmpeg for crop + stitch in one pass per segment, then concat
Each segment: `ffmpeg -ss start -t duration -i src -vf "crop=..." -c:v libx264 -c:a aac segment_N.mp4`
Final stitch: `ffmpeg -filter_complex "[0][1]xfade=...[2]xfade=..." concat_out.mp4`

**Why not moviepy for everything?** moviepy re-encodes via its own pipeline with higher overhead. ffmpeg direct gives us control over preset, CRF, and filter graph. Stream copy not usable here because crop requires re-encode.

**Why two-pass (segment then stitch) vs one-pass filter_complex?** Simpler implementation, easier to debug individual segments, marginal overhead difference for 25s output.

### D4: Face density via OpenCV Haar cascade (soft dependency)
`opencv-python` used if installed; score component zeroed if not. Avoids making mediapipe a hard dependency.

**Why Haar over mediapipe?** Faster per-frame, no model download, acceptable accuracy for density scoring (don't need precise landmarks, just presence/count).

### D5: Scene change via ffmpeg `select` filter (no PySceneDetect)
```
ffmpeg -i src -vf "select='gt(scene,0.4)',showinfo" -f null -
```
Parse stderr for frame timestamps. Zero new Python dependencies.

**Why not PySceneDetect?** Extra dep, subprocess overhead, and ffmpeg already present. Direct filter parse gives equivalent signal.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Source video shorter than `SHORT_TOTAL_DURATION` | Fall back to single full-video crop + pad to 25s |
| No audio track → spectral flux / RMS = 0 | Weights auto-normalize; scene + face signals still select highlights |
| Face detection slow on long videos | Sample every 10th frame only for density scoring |
| H.264 re-encode degrades quality from VP9/AV1 sources | Acceptable for Shorts; use CRF 23 to preserve quality |
| Chapter markers absent (most videos) | Zero contribution; other signals sufficient |
| ffmpeg xfade with odd number of segments | Handle N=1 and N=2 cases explicitly; xfade requires ≥2 inputs |

## Migration Plan

1. New config keys added with defaults — no existing `.env` files break
2. `extract_clip()` gains optional `metadata=None` param — all callers work unchanged
3. Output path format unchanged: `{video_id}_clip.mp4` in `TEMP_DIR`
4. Cache-hit logic preserved (path existence check)
5. No rollback needed — change is self-contained to `clipper.py` + `config.py`

## Open Questions

- **Chapter markers format**: Confirm `discovery.py` response shape for chapters — are they in `snippet.localized` or a separate chapters API call?
- **Face detection frame sampling rate**: 10th frame at 30fps = 3fps sampling. Sufficient? Validate on sample videos.
- **Transition duration at segment boundary**: 0.3s xfade feels right for fast-paced content; may need tuning per genre.
