# Video Scorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Score all copyright-safe candidate videos on popularity, velocity, engagement, SEO, title hook, and quality, then send only the top-scoring video for download.

**Architecture:** Extend `find_viral_videos_by_keyword` to fetch all required metadata in one API call, add a new `pipeline/scorer.py` that normalizes and weights signals to pick the best video, then update `main.py` to use the scorer instead of processing all survivors.

**Tech Stack:** Python 3.11, google-api-python-client (YouTube Data API v3), standard library (`datetime`, `re`)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `pipeline/discovery.py` | Modify | Fetch `commentCount`, `publishedAt`, `tags`, `definition`, `caption` alongside existing fields |
| `pipeline/scorer.py` | Create | Normalize signals, compute weighted score, return top-1 video |
| `main.py` | Modify | Call scorer after copyright check, process only top-1 video |

---

## Task 1: Extend discovery to fetch all scoring metadata

**Files:**
- Modify: `pipeline/discovery.py`

Currently `videos().list` uses `part="snippet,statistics"`. Adding `contentDetails` (same call, no extra quota) gives `duration`, `definition`, `caption`. `commentCount`, `publishedAt`, and `tags` are already in `statistics`/`snippet` but not being stored.

- [ ] **Step 1: Update `videos().list` part parameter and stored fields**

Replace the `videos_response` block in `find_viral_videos_by_keyword` (lines 24-49) with:

```python
videos_response = youtube.videos().list(  # type: ignore[union-attr]
    id=",".join(video_ids),
    part="snippet,statistics,contentDetails",
).execute()

videos = []
for item in videos_response.get("items", []):
    video_id = item["id"]
    stats = item.get("statistics", {})
    snippet = item["snippet"]
    content = item.get("contentDetails", {})

    try:
        transcript_entries = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(e["text"] for e in transcript_entries)
    except Exception:
        transcript = None

    videos.append({
        "video_id": video_id,
        "title": snippet["title"],
        "description": snippet.get("description", ""),
        "channel": snippet["channelTitle"],
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "published_at": snippet.get("publishedAt", ""),   # e.g. "2024-03-01T12:00:00Z"
        "tags": snippet.get("tags", []),                  # list[str], absent on some videos
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "definition": content.get("definition", "sd"),    # "hd" or "sd"
        "has_caption": content.get("caption", "false") == "true",
        "transcript": transcript,
    })
```

- [ ] **Step 2: Verify new fields are populated**

```bash
cd /Users/maverickhan17/Projects/reelraider
python - <<'EOF'
from pipeline.discovery import find_viral_videos_by_keyword
videos = find_viral_videos_by_keyword()
if videos:
    v = videos[0]
    print("Keys:", list(v.keys()))
    print("published_at:", v["published_at"])
    print("tags[:3]:", v["tags"][:3])
    print("comment_count:", v["comment_count"])
    print("definition:", v["definition"])
    print("has_caption:", v["has_caption"])
EOF
```

Expected: all six new keys present with non-default values.

- [ ] **Step 3: Commit**

```bash
git add pipeline/discovery.py
git commit -m "feat(discovery): fetch commentCount, publishedAt, tags, definition, caption for scoring"
```

---

## Task 2: Create `pipeline/scorer.py`

**Files:**
- Create: `pipeline/scorer.py`

### Scoring model

All signals normalized to [0, 1] within the candidate batch via min-max. Edge case: single video or all-equal values → normalized value = 1.0.

| Signal | Weight | Formula |
|--------|--------|---------|
| popularity | 0.20 | `norm(view_count)` |
| velocity | 0.20 | `norm(view_count / days_since_published)` — viral momentum |
| engagement | 0.15 | `norm((like_count + comment_count) / max(view_count, 1))` |
| like_rate | 0.10 | `norm(like_count / max(view_count, 1))` |
| comment_rate | 0.05 | `norm(comment_count / max(view_count, 1))` |
| seo | 0.10 | title length sweet spot + keyword in title/tags + desc length |
| title_hook | 0.10 | numbers, questions, power words, ALL CAPS words |
| quality | 0.10 | HD=0.6 pts, captions=0.4 pts |

- [ ] **Step 1: Create `pipeline/scorer.py`**

```python
import re
from datetime import datetime, timezone


_POWER_WORDS = {
    "shocking", "secret", "exposed", "revealed", "banned", "viral",
    "insane", "unbelievable", "vs", "challenge", "warning", "breaking",
    "exclusive", "leaked", "you won't believe",
}


def _norm(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def _days_since(published_at: str) -> float:
    if not published_at:
        return 365.0
    try:
        pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - pub
        return max(delta.days, 1)
    except ValueError:
        return 365.0


def _seo_score(video: dict, keyword: str) -> float:
    score = 0.0
    title = video["title"].lower()
    kw = keyword.lower()

    tlen = len(video["title"])
    if 40 <= tlen <= 70:
        score += 0.3
    elif 20 <= tlen < 40 or 70 < tlen <= 90:
        score += 0.15

    if kw in title or any(w in title for w in kw.split()):
        score += 0.3

    tags_lower = [t.lower() for t in video.get("tags", [])]
    if any(kw in t or any(w in t for w in kw.split()) for t in tags_lower):
        score += 0.2

    desc_len = len(video.get("description", ""))
    score += min(desc_len / 500, 1.0) * 0.2

    return min(score, 1.0)


def _title_hook_score(title: str) -> float:
    score = 0.0
    lower = title.lower()

    if re.search(r"\d", title):
        score += 0.25

    if "?" in title or any(w in lower for w in ("how to", "why ", "what ", "when ")):
        score += 0.25

    if any(pw in lower for pw in _POWER_WORDS):
        score += 0.25

    if re.search(r"\b[A-Z]{3,}\b", title):
        score += 0.25

    return min(score, 1.0)


def _quality_score(video: dict) -> float:
    score = 0.0
    if video.get("definition") == "hd":
        score += 0.6
    if video.get("has_caption"):
        score += 0.4
    return score


def score_videos(videos: list[dict], keyword: str) -> dict:
    """Score all candidate videos and return the single highest-scoring one."""
    if not videos:
        raise ValueError("No videos to score")
    if len(videos) == 1:
        return videos[0]

    velocities = [
        v["view_count"] / _days_since(v.get("published_at", ""))
        for v in videos
    ]
    engagement_rates = [
        (v["like_count"] + v["comment_count"]) / max(v["view_count"], 1)
        for v in videos
    ]
    like_rates = [v["like_count"] / max(v["view_count"], 1) for v in videos]
    comment_rates = [v["comment_count"] / max(v["view_count"], 1) for v in videos]
    view_counts = [float(v["view_count"]) for v in videos]

    norm_views = _norm(view_counts)
    norm_vel = _norm(velocities)
    norm_eng = _norm(engagement_rates)
    norm_like = _norm(like_rates)
    norm_comment = _norm(comment_rates)

    best_score = -1.0
    best_video = videos[0]

    for i, video in enumerate(videos):
        score = (
            0.20 * norm_views[i]
            + 0.20 * norm_vel[i]
            + 0.15 * norm_eng[i]
            + 0.10 * norm_like[i]
            + 0.05 * norm_comment[i]
            + 0.10 * _seo_score(video, keyword)
            + 0.10 * _title_hook_score(video["title"])
            + 0.10 * _quality_score(video)
        )
        video["_score"] = round(score, 4)
        print(f"[scorer] {score:.3f} | {video['title'][:60]}")
        if score > best_score:
            best_score = score
            best_video = video

    print(f"[scorer] winner: {best_video['title'][:60]} (score={best_score:.3f})")
    return best_video
```

- [ ] **Step 2: Smoke-test with synthetic data**

```bash
cd /Users/maverickhan17/Projects/reelraider
python - <<'EOF'
from pipeline.scorer import score_videos

videos = [
    {
        "video_id": "aaa",
        "title": "10 Shocking AI Secrets REVEALED in 2024",
        "description": "x" * 600,
        "tags": ["AI", "artificial intelligence", "technology"],
        "view_count": 500_000,
        "like_count": 25_000,
        "comment_count": 3_000,
        "definition": "hd",
        "has_caption": True,
        "published_at": "2024-03-01T12:00:00Z",
    },
    {
        "video_id": "bbb",
        "title": "Tech news",
        "description": "short",
        "tags": [],
        "view_count": 1_000_000,
        "like_count": 5_000,
        "comment_count": 100,
        "definition": "sd",
        "has_caption": False,
        "published_at": "2020-01-01T00:00:00Z",
    },
]

winner = score_videos(videos, "Technology and Artificial Intelligence")
print("Winner:", winner["video_id"])
assert winner["video_id"] == "aaa", f"Expected aaa, got {winner['video_id']}"
print("PASS")
EOF
```

Expected: prints scores for both videos, announces winner `aaa`, prints `PASS`.

- [ ] **Step 3: Commit**

```bash
git add pipeline/scorer.py
git commit -m "feat(scorer): score videos by popularity, velocity, engagement, SEO, title hook, quality"
```

---

## Task 3: Wire scorer into `main.py`

**Files:**
- Modify: `main.py`

`run_pipeline` currently iterates over all copyright-safe videos. After scoring, only the top-1 proceeds to download.

- [ ] **Step 1: Replace `main.py` contents**

```python
import argparse
from pipeline.discovery import find_viral_videos_by_keyword
from pipeline.copyright_check import filter_safe_videos
from pipeline.scorer import score_videos
from pipeline.downloader import download_video
from pipeline.clipper import extract_clip
from pipeline.caption_gen import generate_caption
from pipeline.uploader import upload_clip

DISCOVERY_KEYWORD = "Technology and Artificial Intelligence"


def run_pipeline():
    print("[pipeline] finding viral videos...")
    videos = find_viral_videos_by_keyword()
    print(f"[pipeline] found {len(videos)} candidates")

    videos = filter_safe_videos(videos)
    print(f"[pipeline] {len(videos)} pass copyright check")

    if not videos:
        print("[pipeline] no safe videos found, exiting")
        return

    video = score_videos(videos, DISCOVERY_KEYWORD)
    print(f"[pipeline] selected: {video['title']}")

    video_path = download_video(video)
    if not video_path:
        print("[pipeline] download failed, exiting")
        return

    clip_path = extract_clip(video_path, video["video_id"])
    if not clip_path:
        print("[pipeline] clip extraction failed, exiting")
        return

    metadata = generate_caption(video)
    print(f"[pipeline] caption: {metadata['title']}")

    upload_clip(clip_path, metadata)
    print("[pipeline] done.")


def cli():
    parser = argparse.ArgumentParser(description="ReelRaider YouTube clip pipeline")
    parser.add_argument("--once", action="store_true", help="Run pipeline once without scheduler")
    args = parser.parse_args()

    if args.once:
        run_pipeline()
    else:
        from scheduler import start_scheduler
        start_scheduler()


if __name__ == "__main__":
    cli()
```

- [ ] **Step 2: Dry-run discovery + scoring (no download)**

```bash
cd /Users/maverickhan17/Projects/reelraider
python - <<'EOF'
from pipeline.discovery import find_viral_videos_by_keyword
from pipeline.copyright_check import filter_safe_videos
from pipeline.scorer import score_videos

videos = find_viral_videos_by_keyword()
print(f"Fetched {len(videos)} videos")
videos = filter_safe_videos(videos)
print(f"{len(videos)} pass copyright check")
if videos:
    winner = score_videos(videos, "Technology and Artificial Intelligence")
    print(f"Winner: {winner['title']}")
    print(f"Score: {winner['_score']}")
EOF
```

Expected: each candidate scored, single winner announced.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat(pipeline): select top-scored video for download instead of processing all"
```

---

## End-to-end verification

```bash
cd /Users/maverickhan17/Projects/reelraider
python main.py --once
```

Watch log sequence:
1. `[pipeline] found N candidates`
2. `[pipeline] M pass copyright check`
3. `[scorer] X.XXX | <title>` — one line per candidate
4. `[scorer] winner: <title> (score=X.XXX)`
5. `[pipeline] selected: <title>`
6. Download, clip, caption, upload logs for that single video

---

## Scoring weight tuning (future)

Weights are heuristic. After collecting post-upload performance data (views, CTR per uploaded video) map it back to `_score` to calibrate. The `_score` field is stored on each video dict for observability.
