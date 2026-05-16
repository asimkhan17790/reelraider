## 1. Discovery metadata extension

- [x] 1.1 Add `contentDetails` to `videos().list` part parameter in `find_viral_videos_by_keyword`
- [x] 1.2 Store `published_at`, `tags`, `comment_count`, `definition`, `has_caption` in returned video dicts
- [x] 1.3 Verify all 13 dict fields present by running discovery and inspecting first result

## 2. Scorer module

- [x] 2.1 Create `pipeline/scorer.py` with `_norm`, `_days_since`, `_seo_score`, `_title_hook_score`, `_quality_score`, `score_videos`
- [x] 2.2 Smoke-test with synthetic 2-video batch: high-engagement recent video must beat old high-view video
- [x] 2.3 Test edge cases: single video, all-equal norm, bad/empty `published_at`, HD+captions quality score

## 3. Pipeline wiring

- [x] 3.1 Import `score_videos` in `main.py` and define `DISCOVERY_KEYWORD` constant
- [x] 3.2 Replace `for video in videos` loop with `video = score_videos(videos, DISCOVERY_KEYWORD)` + early-exit guard
- [x] 3.3 Dry-run discovery + copyright filter + scorer without triggering download

## 4. Type annotations and linting

- [x] 4.1 Add `# type: ignore[union-attr]` to `youtube.videos().list()` in `find_viral_videos` (line ~65)
- [x] 4.2 Fix transcript fetch: use `YouTubeTranscriptApi().fetch(video_id)` and `e.text` (not `e["text"]`)
- [x] 4.3 Remove bare `find_viral_videos_by_keyword()` call at module scope in `discovery.py`
- [x] 4.4 Verify import check passes: `python -c "from pipeline.scorer import score_videos; from pipeline.discovery import find_viral_videos_by_keyword; print('OK')"`

## 5. Commits

- [x] 5.1 Commit discovery changes: `feat(discovery): fetch commentCount, publishedAt, tags, definition, caption for scoring`
- [x] 5.2 Commit scorer module: `feat(scorer): score videos by popularity, velocity, engagement, SEO, title hook, quality`
- [x] 5.3 Commit main.py wiring: `feat(pipeline): select top-scored video for download instead of processing all`
