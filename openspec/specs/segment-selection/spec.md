## ADDED Requirements

### Requirement: Greedy non-overlapping segment selection
The system SHALL select N non-overlapping time windows from the scored timeline using a greedy algorithm: iterate windows in descending score order, accept a window if it does not overlap any previously accepted window (plus a 0.5s guard margin on each side), repeat until N windows are accepted or the timeline is exhausted.

N is determined by `floor(SHORT_TOTAL_DURATION / SHORT_SEGMENT_DURATION)`.

#### Scenario: Enough non-overlapping peaks exist
- **WHEN** the scored timeline contains >= N windows with no mutual overlap
- **THEN** exactly N windows are selected, each being the highest-scoring available non-overlapping option

#### Scenario: Fewer non-overlapping peaks than N
- **WHEN** only K < N non-overlapping windows can be found
- **THEN** the system selects all K windows, logs a warning with the shortfall count, and stitches K segments (total duration < SHORT_TOTAL_DURATION)

### Requirement: Source video shorter than target duration
The system SHALL detect when the source video duration is <= SHORT_TOTAL_DURATION and fall back to using the entire video as a single segment, bypassing scoring and selection entirely.

#### Scenario: Short source video fallback
- **WHEN** source video duration <= SHORT_TOTAL_DURATION seconds
- **THEN** selection returns a single window `[(0.0, video_duration)]` and logs a DEBUG message indicating fallback mode

### Requirement: Chronological ordering of selected segments
After selection, the system SHALL sort selected windows by start time (ascending) so the stitched output preserves narrative chronology of the source video.

#### Scenario: Best window is mid-video
- **WHEN** the highest-scoring window starts at t=300s and second-best starts at t=60s
- **THEN** the stitched order is t=60s segment first, then t=300s segment

### Requirement: Configurable segment parameters
The system SHALL read segment configuration from environment variables with the following defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| `SHORT_TOTAL_DURATION` | 25 | Target output duration in seconds |
| `SHORT_SEGMENT_DURATION` | 5 | Duration of each selected segment in seconds |
| `SHORT_SCORING_STEP` | 0.5 | Sliding window step size in seconds |

#### Scenario: Custom segment duration
- **WHEN** `SHORT_SEGMENT_DURATION=8` is set
- **THEN** each selected window is 8 seconds long and N = floor(25/8) = 3 segments are selected
