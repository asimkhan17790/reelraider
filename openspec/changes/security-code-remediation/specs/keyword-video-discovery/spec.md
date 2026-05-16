## MODIFIED Requirements

### Requirement: Hardcoded default keyword constant
The system SHALL define `DISCOVERY_KEYWORD` in `config.py` (not `pipeline/discovery.py`) as the canonical source, with value controlled by the `DISCOVERY_KEYWORD` environment variable defaulting to `"Technology and Artificial Intelligence"`. `pipeline/discovery.py` SHALL re-export it via `from config import DISCOVERY_KEYWORD` for backward compatibility.

#### Scenario: Constant is importable from pipeline.discovery
- **WHEN** a caller imports `DISCOVERY_KEYWORD` from `pipeline.discovery`
- **THEN** it returns the configured value (default: `"Technology and Artificial Intelligence"`)

#### Scenario: Env var overrides default keyword
- **WHEN** `DISCOVERY_KEYWORD=Finance` is set in the environment
- **THEN** `config.DISCOVERY_KEYWORD` and `pipeline.discovery.DISCOVERY_KEYWORD` both return `"Finance"`

### Requirement: Statistics enrichment via second API call
The system SHALL enrich keyword search results by making a batched `videos().list` call with `part="snippet,statistics,contentDetails"`. Numeric stat fields (`view_count`, `like_count`, `comment_count`) SHALL be cast using a safe helper that returns `0` on `ValueError` or missing keys rather than raising.

#### Scenario: All metadata fields present in returned dicts
- **WHEN** `find_viral_videos_by_keyword()` completes successfully
- **THEN** each returned dict includes all 13 fields; numeric counts default to `0` if absent or non-numeric; string fields default to `""`; list fields default to `[]`; `has_caption` defaults to `False`

#### Scenario: Non-numeric stat field defaults to zero without aborting
- **WHEN** the YouTube API returns a non-numeric string for `viewCount`
- **THEN** `view_count` is stored as `0` and the video is still included in results

## ADDED Requirements

### Requirement: video_id format guard in discovery
The system SHALL validate each `video_id` returned by the YouTube API matches `[A-Za-z0-9_-]{11}` before appending to results. Invalid IDs SHALL be skipped with a `logger.warning`.

#### Scenario: Video with invalid ID is skipped
- **WHEN** the YouTube API returns a video with a malformed ID
- **THEN** that video is omitted from the returned list and a warning is logged
