## 1. Config & Dependencies

- [x] 1.1 Add `SHORT_TOTAL_DURATION`, `SHORT_SEGMENT_DURATION`, `SHORT_SCORING_STEP`, `SHORT_CROP_MODE`, `SHORT_TRANSITION_DURATION` to `config.py` with defaults and validation
- [x] 1.2 Add `librosa` to project dependencies (`pyproject.toml` or `requirements.txt`)
- [x] 1.3 Add `opencv-python` as optional dependency with install note in README
- [x] 1.4 Verify chapter markers are available in the video metadata dict passed through the pipeline; update `main.py:run_pipeline()` to pass `metadata` to `extract_clip()` if needed

## 2. Highlight Scoring

- [x] 2.1 Implement `_compute_audio_signals(video_path, step)` returning per-step RMS and spectral flux arrays using `librosa`
- [x] 2.2 Implement `_compute_scene_changes(video_path, step, threshold)` via ffmpeg `select` filter subprocess, returning per-step scene change rate array
- [x] 2.3 Implement `_compute_face_density(video_path, step)` using OpenCV Haar cascade with every-10th-frame sampling; return zeros array and log DEBUG if `cv2` not installed
- [x] 2.4 Implement `_score_windows(audio_rms, spectral_flux, scene_rates, face_density, chapters, step, segment_duration)` applying per-signal normalization, weights, and chapter bonus; return `[(start_sec, score), ...]`

## 3. Segment Selection

- [x] 3.1 Implement `_select_segments(scored_windows, n, segment_duration, guard_margin=0.5)` greedy non-overlapping selector; return `[(start_sec, end_sec), ...]` sorted chronologically
- [x] 3.2 Add short-video fallback: if `video_duration <= SHORT_TOTAL_DURATION`, return `[(0.0, video_duration)]` directly
- [x] 3.3 Add warning log when fewer than N segments found

## 4. Segment Extraction with Vertical Crop

- [x] 4.1 Implement `_extract_segment(video_path, start, duration, out_path)` using ffmpeg with `-vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0" -c:v libx264 -crf 23 -preset fast -c:a aac`
- [x] 4.2 Ensure segment temp files are named `{video_id}_seg_{N}.mp4` in `TEMP_DIR`

## 5. Clip Stitching

- [x] 5.1 Implement `_stitch_segments(segment_paths, out_path, transition_duration)` using ffmpeg `filter_complex` xfade chain for N >= 2 segments
- [x] 5.2 Handle N=1 passthrough: move/copy single segment to `out_path` without xfade
- [x] 5.3 Implement cleanup: delete temp segment files on success, retain on failure with ERROR log listing paths

## 6. Refactor extract_clip

- [x] 6.1 Rewrite `extract_clip(video_path, video_id, metadata=None)` to orchestrate: score -> select -> extract segments -> stitch -> return output path
- [x] 6.2 Preserve cache-hit check at top of function (return early if `out_path` exists)
- [x] 6.3 Remove `_find_best_window()` and old moviepy-based single-clip logic
- [x] 6.4 Ensure function returns `None` on any unhandled exception with `logger.exception`

## 7. Verification

- [x] 7.1 Run pipeline end-to-end on one real video; confirm output is 9:16, ~25s H.264 MP4
- [x] 7.2 Test short-video fallback with a video < 25s source
- [x] 7.3 Test with `opencv-python` uninstalled to confirm face density graceful degradation
- [x] 7.4 Test with a video that has no audio track; confirm scene-only scoring still selects windows
- [x] 7.5 Confirm downstream stages (`caption_gen`, `uploader`) receive clip path unchanged
