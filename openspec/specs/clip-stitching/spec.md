## ADDED Requirements

### Requirement: Crossfade stitch via ffmpeg filter_complex
The system SHALL stitch N cropped segments into a single output file using ffmpeg `xfade` filter with `fade` transition type. Default transition duration: 0.3 seconds, configurable via `SHORT_TRANSITION_DURATION`.

#### Scenario: Three segments stitched
- **WHEN** 3 segments of 5s each are stitched with 0.3s crossfade
- **THEN** output duration is approximately 14.4s (3*5 - 2*0.3)

#### Scenario: Two segments stitched
- **WHEN** exactly 2 segments are provided
- **THEN** one xfade filter is applied between them and output is correct

### Requirement: Single segment passthrough
When only one segment is selected (short source video fallback), the system SHALL copy that segment directly to the output path without invoking the stitch filter graph.

#### Scenario: One segment only
- **WHEN** segment selection returns exactly 1 window
- **THEN** the cropped segment file is renamed/moved to the final output path; no xfade ffmpeg call is made

### Requirement: Temporary segment cleanup
After successful stitching, the system SHALL delete all intermediate segment temp files. If stitching fails, temp files SHALL be retained for debugging.

#### Scenario: Successful stitch cleanup
- **WHEN** stitching completes without error
- **THEN** all `{video_id}_seg_N.mp4` temp files are deleted from `TEMP_DIR`

#### Scenario: Failed stitch preserves temps
- **WHEN** ffmpeg stitch subprocess exits non-zero
- **THEN** temp segment files remain in `TEMP_DIR` and an ERROR log entry lists their paths

### Requirement: Output file naming
The final stitched output SHALL be written to `{TEMP_DIR}/{video_id}_clip.mp4`, matching the existing cache-hit path checked at the start of `extract_clip()`.

#### Scenario: Cache hit on subsequent run
- **WHEN** `extract_clip()` is called again for the same `video_id` and the output file already exists
- **THEN** the function returns the existing path immediately without re-processing

### Requirement: Configurable transition duration
The system SHALL read `SHORT_TRANSITION_DURATION` from environment (default: 0.3, range: 0.0-1.0). Values outside range SHALL raise `ValueError` at startup.

#### Scenario: Zero transition duration
- **WHEN** `SHORT_TRANSITION_DURATION=0.0` is set
- **THEN** segments are hard-cut with no fade; xfade still used with duration=0
