## ADDED Requirements

### Requirement: Keyword-based video search

The system SHALL provide a function `find_viral_videos_by_keyword(keyword: str = DISCOVERY_KEYWORD)` that searches YouTube for videos matching the given keyword, ranked by view count.

#### Scenario: Search returns keyword-matched videos ordered by popularity
- **WHEN** `find_viral_videos_by_keyword()` is called with a keyword
- **THEN** the function returns a list of video dicts, each containing `video_id`, `title`, `description`, `channel`, `url`, `view_count`, and `transcript`

#### Scenario: Default keyword is used when none provided
- **WHEN** `find_viral_videos_by_keyword()` is called with no arguments
- **THEN** the function uses `DISCOVERY_KEYWORD` (`"Technology and Artificial Intelligence"`) as the search term

### Requirement: Hardcoded default keyword constant

The system SHALL define `DISCOVERY_KEYWORD = "Technology and Artificial Intelligence"` as a module-level constant in `pipeline/discovery.py`.

#### Scenario: Constant is importable and usable as default
- **WHEN** a caller imports `DISCOVERY_KEYWORD` from `pipeline.discovery`
- **THEN** it returns the string `"Technology and Artificial Intelligence"`

### Requirement: Statistics enrichment via second API call

The system SHALL enrich keyword search results with `view_count` and `like_count` by making a batched `videos().list` call with the IDs returned from `search().list`.

#### Scenario: View count attached to each result
- **WHEN** `find_viral_videos_by_keyword()` completes
- **THEN** each returned dict includes `view_count` as an integer (or `0` if statistics unavailable)

### Requirement: Creative Commons pre-filter in search

The system SHALL pass `videoLicense="creativeCommon"` to `search().list` as a best-effort pre-filter.

#### Scenario: Search query includes license filter
- **WHEN** `find_viral_videos_by_keyword()` calls the YouTube search API
- **THEN** the request includes `videoLicense="creativeCommon"`

### Requirement: Transcript metadata attachment

The system SHALL attempt to fetch a transcript for each discovered video using `youtube-transcript-api` and attach it as a flat string to the `transcript` field.

#### Scenario: Transcript available
- **WHEN** a video has captions (auto-generated or manual)
- **THEN** `transcript` field contains the full text as a single joined string

#### Scenario: Transcript unavailable
- **WHEN** a video has no captions or transcript fetch fails
- **THEN** `transcript` field is `None` and no exception is raised

### Requirement: Existing discovery function preserved

The system SHALL keep `find_viral_videos()` unchanged with its existing signature and behavior.

#### Scenario: Existing pipeline still works
- **WHEN** `find_viral_videos()` is called (no arguments)
- **THEN** it returns the same mostPopular chart results as before this change
