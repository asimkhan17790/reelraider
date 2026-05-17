## ADDED Requirements

### Requirement: video_id format validation
The system SHALL validate that `video_id` matches the pattern `[A-Za-z0-9_-]{11}` before using it in any file path or URL construction.

#### Scenario: Valid video_id passes through
- **WHEN** `video_id` is an 11-character base64url string
- **THEN** processing continues without error

#### Scenario: Invalid video_id raises ValueError
- **WHEN** `video_id` contains path separators, is shorter or longer than 11 characters, or contains non-base64url characters
- **THEN** the pipeline raises `ValueError` with the invalid ID in the message and skips that video

### Requirement: Safe int casting on YouTube API stat fields
The system SHALL cast `viewCount`, `likeCount`, and `commentCount` from YouTube API responses using a helper that returns `0` on `ValueError` or missing keys, so a single malformed response does not abort the discovery loop.

#### Scenario: Numeric string converts normally
- **WHEN** the API returns `"viewCount": "12345"`
- **THEN** the field is stored as integer `12345`

#### Scenario: Non-numeric or missing field defaults to zero
- **WHEN** the API returns a non-numeric string or omits the field
- **THEN** the field defaults to `0` and processing continues

### Requirement: Scheduler job error containment
The system SHALL wrap `run_pipeline()` in the scheduler job with `try/except Exception` and log the exception with `logger.exception()` so a pipeline failure does not kill the APScheduler job permanently.

#### Scenario: Pipeline raises unhandled exception
- **WHEN** `run_pipeline()` raises any exception during a scheduled run
- **THEN** the exception is logged and the scheduler continues to fire on the next scheduled interval

### Requirement: Upload loop max-chunk guard
The system SHALL limit the YouTube upload chunk loop to a maximum of 100 iterations, raising `RuntimeError` if the limit is exceeded.

#### Scenario: Upload completes within limit
- **WHEN** the upload finishes within 100 chunk iterations
- **THEN** the response is returned normally

#### Scenario: Upload stalls beyond limit
- **WHEN** 100 chunk iterations complete without a terminal response
- **THEN** `RuntimeError` is raised with a message indicating the upload stalled
