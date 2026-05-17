## MODIFIED Requirements

### Requirement: Composite video scoring
The system SHALL provide a function `score_videos(videos: list[dict], keyword: str) -> dict` in `pipeline/scorer.py` that scores all candidate videos on eight weighted signals and returns the single highest-scoring video dict. The function SHALL NOT mutate the input dicts; `_score` SHALL be attached only to a copy of each dict or stored in a separate structure, not written back to the caller's list.

#### Scenario: Multiple candidates — best video selected
- **WHEN** `score_videos` is called with two or more video dicts and a keyword string
- **THEN** it returns the dict with the highest composite score; the original input dicts are NOT modified

#### Scenario: Single candidate — returned directly
- **WHEN** `score_videos` is called with exactly one video dict
- **THEN** it returns that dict without computing scores

#### Scenario: Empty list — raises ValueError
- **WHEN** `score_videos` is called with an empty list
- **THEN** it raises `ValueError`

#### Scenario: Input dicts unchanged after scoring
- **WHEN** `score_videos` processes a batch
- **THEN** none of the original dicts in the input list have a `_score` key added to them
