## Why

The current discovery module fetches globally trending videos with no topical filtering, making the pipeline generic and uncontrolled. Adding keyword-based discovery enables targeted content curation (e.g., "Technology and Artificial Intelligence") so the pipeline produces niche-relevant clips rather than random viral content.

## What Changes

- Add `DISCOVERY_KEYWORD` constant to `pipeline/discovery.py` (default: `"Technology and Artificial Intelligence"`)
- Add new function `find_viral_videos_by_keyword(keyword: str = DISCOVERY_KEYWORD) -> list[dict]` alongside existing `find_viral_videos()`
- Two-step YouTube API approach: `search().list` (keyword + CC filter) → `videos().list` (statistics enrichment)
- Attach `transcript` field to each video dict (flat string or `None` if unavailable) via `youtube-transcript-api`
- Existing `find_viral_videos()` remains untouched — no breaking changes to current pipeline
- `copyright_check.py` stage retained as second-pass safety filter

## Capabilities

### New Capabilities

- `keyword-video-discovery`: Search and rank YouTube videos by keyword using view count, enriched with statistics and transcript metadata, parameterized for future UI integration

### Modified Capabilities

- _(none — existing `find_viral_videos()` is unchanged)_

## Impact

- **Files modified**: `pipeline/discovery.py`
- **New dependency**: `youtube-transcript-api` (pip)
- **YouTube API quota**: ~101 units per keyword discovery run (100 for `search().list` + 1 for `videos().list`) vs 1 unit for current chart call
- **Pipeline integration**: `main.py` can opt-in to `find_viral_videos_by_keyword()` — no forced migration
- **Future UI hook**: `keyword` parameter on the new function is the integration point for any frontend/tool input
