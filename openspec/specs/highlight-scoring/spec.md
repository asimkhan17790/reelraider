## ADDED Requirements

### Requirement: Composite multi-signal window scoring
The system SHALL score every candidate time window in the source video using a weighted sum of four normalized signals: audio RMS, spectral flux, scene change rate, and face density. Each signal SHALL be independently normalized to [0, 1] across all windows before weighting.

Default weights:
- Audio RMS: 0.25
- Spectral flux: 0.35
- Scene change rate: 0.25
- Face density: 0.15

Chapter marker presence SHALL add a fixed +0.5 bonus (unnormalized) to any window that overlaps a chapter boundary timestamp.

#### Scenario: All signals available
- **WHEN** the source video has an audio track, detectable scene changes, detectable faces, and chapter markers
- **THEN** each window score equals `0.25*rms_norm + 0.35*flux_norm + 0.25*scene_norm + 0.15*face_norm + chapter_bonus`

#### Scenario: Missing optional signals
- **WHEN** face detection library is not installed or chapter markers are absent
- **THEN** missing signal components contribute 0 to the score and remaining signals are used as-is without re-weighting

#### Scenario: No audio track
- **WHEN** source video has no audio track
- **THEN** RMS and spectral flux components both equal 0; scene change and face density signals still produce a valid score

### Requirement: Spectral flux computation
The system SHALL compute spectral flux using `librosa.onset.onset_strength()` over the full audio waveform at 22050 Hz, aggregated into per-window averages matching the scoring step size.

#### Scenario: Spectral flux detects event onset
- **WHEN** a window contains a sharp audio onset (beat, speech start, sound effect)
- **THEN** that window's flux score is higher than adjacent low-activity windows

### Requirement: Scene change rate computation
The system SHALL detect scene changes via ffmpeg's `select='gt(scene,THRESHOLD)'` filter with a default threshold of 0.4, counting scene transitions per window duration to produce a per-window rate.

#### Scenario: High scene change rate window
- **WHEN** a window contains 3 or more scene cuts within its duration
- **THEN** its scene change rate score is in the top quartile of all windows

#### Scenario: ffmpeg scene detection failure
- **WHEN** ffmpeg scene detection subprocess fails
- **THEN** system logs a warning and sets all scene change scores to 0, continuing with remaining signals

### Requirement: Face density computation (soft dependency)
The system SHALL attempt face detection using OpenCV Haar cascade, sampling every 10th frame. Face density is defined as the average count of detected faces per sampled frame within the window.

#### Scenario: opencv-python not installed
- **WHEN** `import cv2` fails at import time
- **THEN** face density scores are set to 0 for all windows and a DEBUG log entry is written; no exception is raised

#### Scenario: Faces detected in window
- **WHEN** sampled frames in a window contain on average >=1 detected face
- **THEN** that window receives a non-zero face density score proportional to average face count

### Requirement: Chapter marker bonus
The system SHALL accept an optional `chapters` list (list of `{"start_time": float}` dicts) and apply a +0.5 score bonus to any window whose time range contains or starts within 2 seconds of a chapter boundary.

#### Scenario: Window overlaps chapter boundary
- **WHEN** a chapter starts at t=120s and a window spans [119s, 124s]
- **THEN** that window's final score includes the +0.5 chapter bonus

#### Scenario: No chapters provided
- **WHEN** `chapters` is `None` or empty list
- **THEN** no bonus is applied and scoring proceeds normally
