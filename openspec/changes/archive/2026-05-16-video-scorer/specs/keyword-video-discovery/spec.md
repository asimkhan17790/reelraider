## MODIFIED Requirements

### Requirement: Statistics enrichment via second API call

The system SHALL enrich keyword search results by making a batched `videos().list` call with `part="snippet,statistics,contentDetails"`, returning the following fields per video: `video_id`, `title`, `description`, `channel`, `url`, `published_at`, `tags`, `view_count`, `like_count`, `comment_count`, `definition`, `has_caption`, `transcript`.

#### Scenario: All metadata fields present in returned dicts
- **WHEN** `find_viral_videos_by_keyword()` completes successfully
- **THEN** each returned dict includes all 13 fields; numeric counts default to `0` if absent from the API response; string fields default to `""`; list fields default to `[]`; `has_caption` defaults to `False`

#### Scenario: View count attached to each result
- **WHEN** `find_viral_videos_by_keyword()` completes
- **THEN** each returned dict includes `view_count` as an integer (or `0` if statistics unavailable)
