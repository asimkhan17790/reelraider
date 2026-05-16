## ADDED Requirements

### Requirement: Composite video scoring

The system SHALL provide a function `score_videos(videos: list[dict], keyword: str) -> dict` in `pipeline/scorer.py` that scores all candidate videos on eight weighted signals and returns the single highest-scoring video dict.

#### Scenario: Multiple candidates — best video selected
- **WHEN** `score_videos` is called with two or more video dicts and a keyword string
- **THEN** it returns the dict with the highest composite score and attaches `_score` (float, rounded to 4 decimal places) to every input dict

#### Scenario: Single candidate — returned directly
- **WHEN** `score_videos` is called with exactly one video dict
- **THEN** it returns that dict without computing scores

#### Scenario: Empty list — raises ValueError
- **WHEN** `score_videos` is called with an empty list
- **THEN** it raises `ValueError`

### Requirement: Min-max normalization per batch

The system SHALL normalize per-batch numeric signals to [0, 1] using min-max normalization before applying weights.

#### Scenario: All-equal values normalize to 1.0
- **WHEN** all candidates share the same value for a numeric signal (e.g., identical view counts)
- **THEN** the normalized value for that signal is 1.0 for every candidate

#### Scenario: Distinct values normalized to [0, 1] range
- **WHEN** candidates have different values for a signal
- **THEN** the minimum maps to 0.0 and the maximum maps to 1.0

### Requirement: View velocity signal

The system SHALL compute velocity as `view_count / days_since_published`, where `days_since_published` is derived from the `published_at` ISO 8601 field and is clamped to a minimum of 1.

#### Scenario: Missing or unparseable published_at falls back to 365 days
- **WHEN** `published_at` is absent, empty, or not a valid ISO 8601 datetime
- **THEN** `days_since_published` defaults to `365.0`

### Requirement: SEO sub-score

The system SHALL compute an SEO sub-score (0–1) based on: title length in the 40–70 character sweet spot, keyword presence in title, keyword presence in tags, and description length.

#### Scenario: Fully optimized video scores 1.0
- **WHEN** a video has a 40–70 char title containing the keyword, tags containing the keyword, and a description ≥ 500 characters
- **THEN** `_seo_score` returns 1.0

### Requirement: Title hook sub-score

The system SHALL compute a title hook sub-score (0–1) awarding 0.25 for each of: presence of a digit, presence of a question mark or question word ("how to", "why", "what", "when"), presence of a power word from the defined set, and presence of an ALL-CAPS word (3+ letters).

#### Scenario: Title with all four signals scores 1.0
- **WHEN** a title contains a digit, a question mark, a power word, and an ALL-CAPS block
- **THEN** `_title_hook_score` returns 1.0

### Requirement: Quality sub-score

The system SHALL compute a quality sub-score as: 0.6 for HD definition plus 0.4 for captions available (max 1.0).

#### Scenario: HD with captions scores 1.0
- **WHEN** `definition == "hd"` and `has_caption == True`
- **THEN** `_quality_score` returns `1.0`

#### Scenario: SD with no captions scores 0.0
- **WHEN** `definition == "sd"` and `has_caption == False`
- **THEN** `_quality_score` returns `0.0`

### Requirement: Score logging

The system SHALL print each video's score and truncated title to stdout, then announce the winner, using the `[scorer]` prefix.

#### Scenario: Score line printed per candidate
- **WHEN** `score_videos` processes a batch of N videos
- **THEN** N lines matching `[scorer] X.XXX | <title[:60]>` are printed followed by one `[scorer] winner:` line
