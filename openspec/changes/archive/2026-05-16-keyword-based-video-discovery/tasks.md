## 1. Dependencies

- [x] 1.1 Add `youtube-transcript-api` to `requirements.txt` (or `pyproject.toml`)
- [x] 1.2 Install the new dependency locally (`pip install youtube-transcript-api`)

## 2. Core Implementation

- [x] 2.1 Add `DISCOVERY_KEYWORD = "Technology and Artificial Intelligence"` constant to `pipeline/discovery.py`
- [x] 2.2 Implement `find_viral_videos_by_keyword(keyword: str = DISCOVERY_KEYWORD)` — Step 1: call `search().list(q=keyword, type="video", order="viewCount", videoLicense="creativeCommon", regionCode, maxResults)`
- [x] 2.3 Implement Step 2: batch call `videos().list(id=<ids>, part="snippet,statistics")` to enrich with `view_count` and `like_count`
- [x] 2.4 Implement transcript fetch loop: for each video, call `YouTubeTranscriptApi.get_transcript(video_id)`, join text fields, catch all exceptions and set `transcript=None`
- [x] 2.5 Return list of dicts with keys: `video_id`, `title`, `description`, `channel`, `url`, `view_count`, `like_count`, `transcript`

## 3. Pipeline Integration

- [x] 3.1 Update `main.py` to call `find_viral_videos_by_keyword()` instead of `find_viral_videos()`
- [x] 3.2 Verify `copyright_check.py` still receives the same dict shape and filters correctly

## 4. Verification

- [x] 4.1 Run `python main.py --once` and confirm results are Technology/AI-related videos
- [x] 4.2 Confirm `view_count` field is populated on returned dicts
- [x] 4.3 Confirm `transcript` field is a string or `None` (not an exception) for all results
- [x] 4.4 Confirm `find_viral_videos()` still works unchanged (no regression)
