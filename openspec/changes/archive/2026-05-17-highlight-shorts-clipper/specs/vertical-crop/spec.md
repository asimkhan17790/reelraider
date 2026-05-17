## ADDED Requirements

### Requirement: Center crop 16:9 to 9:16
The system SHALL apply a center crop to each extracted segment, converting the source 16:9 aspect ratio to 9:16 (YouTube Shorts format). The crop SHALL use the ffmpeg filter: `crop=ih*9/16:ih:(iw-ih*9/16)/2:0`.

#### Scenario: Standard 1920x1080 source
- **WHEN** source video is 1920x1080 (16:9)
- **THEN** output segment is 608x1080 (9:16), taking the center 608 pixels horizontally

#### Scenario: Non-standard source resolution
- **WHEN** source video has an arbitrary resolution
- **THEN** crop formula is applied proportionally; output maintains 9:16 aspect ratio

### Requirement: Crop applied during segment extraction
The system SHALL apply the crop filter during the per-segment ffmpeg encode pass, not as a separate post-processing step, to avoid unnecessary re-encoding.

#### Scenario: Single ffmpeg pass
- **WHEN** a segment is extracted and cropped
- **THEN** exactly one ffmpeg subprocess runs per segment (crop + encode combined)

### Requirement: Output codec H.264
All segments and the final stitched output SHALL be encoded as H.264 video with AAC audio, using CRF 23 and the `fast` preset, regardless of source codec.

#### Scenario: VP9 source
- **WHEN** source video is encoded in VP9
- **THEN** output segment is H.264/AAC regardless

#### Scenario: Quality preservation
- **WHEN** encoding at CRF 23
- **THEN** output is visually acceptable for Shorts distribution (no blocking artifacts at typical 608x1080 resolution)

### Requirement: Configurable crop mode
The system SHALL read `SHORT_CROP_MODE` from environment (default: `center`). In v1, only `center` is supported. If an unsupported value is set, the system SHALL raise a `ValueError` at startup.

#### Scenario: Unsupported crop mode
- **WHEN** `SHORT_CROP_MODE=face` is set
- **THEN** `config.py` raises `ValueError` with message indicating `face` is not yet supported
