## Why

The pipeline currently downloads and processes every copyright-safe video found, regardless of quality or viral potential. Scoring candidates before download saves quota, storage, and processing time while ensuring only the highest-potential video is published.

## What Changes

- `pipeline/discovery.py` extended to fetch `commentCount`, `publishedAt`, `tags`, `definition`, and `caption` from the YouTube Data API in the existing `videos().list` call (no extra quota cost).
- New `pipeline/scorer.py` introduced: scores all candidates on eight weighted signals and returns the single best video.
- `main.py` updated to route through `score_videos()` after copyright filtering, then download/process only the top-scored video instead of all survivors.

## Capabilities

### New Capabilities

- `video-scoring`: Multi-signal composite scorer that ranks candidate videos by popularity, velocity, engagement, SEO optimization, title hook strength, and quality, then selects the single best video for download.

### Modified Capabilities

- `keyword-video-discovery`: Extended to return six additional metadata fields required by the scorer (`published_at`, `tags`, `comment_count`, `definition`, `has_caption`) alongside existing fields.

## Impact

- **`pipeline/discovery.py`**: `videos().list` part param changed from `snippet,statistics` to `snippet,statistics,contentDetails`; video dict schema gains 5 new keys.
- **`pipeline/scorer.py`**: New module; no external dependencies beyond stdlib (`re`, `datetime`).
- **`main.py`**: Pipeline loop changes from `for video in videos` to a single `video = score_videos(...)` call.
- **Downstream stages** (`downloader`, `clipper`, `caption_gen`, `uploader`): Unaffected — they receive the same video dict shape.
