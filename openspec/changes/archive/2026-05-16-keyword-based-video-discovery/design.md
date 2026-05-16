## Context

`pipeline/discovery.py` currently uses `videos().list(chart="mostPopular")` — a ranked chart that cannot be filtered by keyword. The pipeline is a linear chain: `discovery → copyright_check → downloader → clipper → caption_gen → uploader`. Discovery is the entry point; everything downstream depends on what it returns.

The `videos().list` chart API and `search().list` keyword API are mutually exclusive — you cannot combine `chart="mostPopular"` with a `q=` keyword parameter. Keyword-based popularity requires a two-step approach.

## Goals / Non-Goals

**Goals:**
- Find YouTube videos matching a keyword, ranked by view count
- Enrich results with actual statistics (views, likes) via a second API call
- Attach transcript text to each video dict where available
- Keep `DISCOVERY_KEYWORD` hardcoded but exposed as a function parameter for future UI wiring
- Preserve `find_viral_videos()` and all downstream stage contracts unchanged

**Non-Goals:**
- Replacing `find_viral_videos()` — it stays as-is
- Modifying `copyright_check.py`, `downloader.py`, or any downstream stage
- Building a UI input mechanism (future work)
- Structured/timestamped transcript format (flat string sufficient for `caption_gen.py`)

## Decisions

### Decision 1: Two-step API (search → videos.list)

**Choice**: `search().list(q=keyword, order=viewCount)` → `videos().list(id=<ids>, part="snippet,statistics")`

**Why**: `search().list` alone returns limited metadata (no view counts in response). The second `videos().list` call with the returned IDs gets full statistics in one batch call (1 quota unit for any number of IDs). This is the standard YouTube API pattern for keyword + stats.

**Alternative considered**: `search().list` with `order=relevance` — rejected because it mixes recency and engagement signals, making "popular" harder to define. `viewCount` is explicit.

### Decision 2: Keep `videoLicense="creativeCommon"` in search + retain `copyright_check.py`

**Choice**: Filter at search time AND keep the downstream copyright check.

**Why**: YouTube's `videoLicense` filter in `search().list` is documented as best-effort, not guaranteed. `copyright_check.py` does a direct `videos().list` check on `licensedContent` and `regionRestriction` — a harder guarantee. Belt-and-suspenders is correct here given the downstream upload risk.

**Alternative considered**: Remove `copyright_check.py` for keyword path — rejected due to upload legal risk.

### Decision 3: Transcript via `youtube-transcript-api`, flat string, graceful None

**Choice**: `YouTubeTranscriptApi.get_transcript(video_id)` → join all `text` fields into single string. Return `None` if unavailable.

**Why**: Transcript fetched at discovery stage so `caption_gen.py` can use it as richer context than `description` alone. Flat string matches how `caption_gen.py` already processes text. `youtube-transcript-api` is pure-Python, no headless browser, and handles auto-generated captions.

**Alternative considered**: `yt-dlp --write-auto-sub` — rejected because it requires a download, which belongs to the `downloader` stage, not discovery.

### Decision 4: `DISCOVERY_KEYWORD` constant + default parameter

**Choice**:
```python
DISCOVERY_KEYWORD = "Technology and Artificial Intelligence"

def find_viral_videos_by_keyword(keyword: str = DISCOVERY_KEYWORD) -> list[dict]:
    ...
```

**Why**: Hardcoded constant is the current requirement. Default parameter means zero-arg call works today; a UI can pass `keyword="gaming"` later with no refactor at the call site.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| `search().list` costs 100 quota units (vs 1 for chart) | At `MAX_VIDEOS_PER_RUN * 3` fetch size and daily quota of 10,000 units, ~99 runs/day still possible. Acceptable for a daily scheduler. |
| `youtube-transcript-api` scrapes YouTube internals — could break on YouTube changes | `transcript` field is optional enrichment. Pipeline degrades gracefully with `None`. No stage requires it. |
| `order=viewCount` surfaces old high-view videos, not recently viral | Acceptable for "Technology and AI" niche. Can swap to `order=relevance` per-call if needed — no structural change. |
| `videoLicense="creativeCommon"` in search is best-effort | Retained `copyright_check.py` as hard filter. |

## Migration Plan

1. Add `youtube-transcript-api` to `requirements.txt` / `pyproject.toml`
2. Add `DISCOVERY_KEYWORD` constant and `find_viral_videos_by_keyword()` to `pipeline/discovery.py`
3. Update `main.py` to call `find_viral_videos_by_keyword()` instead of (or alongside) `find_viral_videos()`
4. No rollback needed — `find_viral_videos()` remains; revert `main.py` call to restore old behavior

## Open Questions

- ~~Should `main.py` call both functions and merge results, or replace the chart call entirely with keyword discovery?~~
  **Resolved**: `main.py` replaces `find_viral_videos()` call with `find_viral_videos_by_keyword()`. `find_viral_videos()` stays in module, unused by orchestrator, available for future use.
- ~~Should `videoCategoryId` from config still apply to keyword search, or is keyword alone sufficient?~~
  **Resolved**: Drop `videoCategoryId` from `find_viral_videos_by_keyword()`. Keyword is the filter; category would contradict tech/AI content (default config is category 10 = Music).
