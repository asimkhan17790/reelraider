import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

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
        logger.info("Only one candidate — skipping scoring: video_id=%s", videos[0]["video_id"])
        return videos[0]

    logger.info("Scoring %d candidate videos for keyword=%r", len(videos), keyword)

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
    best_idx = 0
    scores: dict[int, float] = {}

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
        scores[i] = round(score, 4)
        logger.debug("score=%.3f video_id=%s title=%r", score, video["video_id"], video["title"][:60])
        if score > best_score:
            best_score = score
            best_idx = i

    best_video = videos[best_idx]
    logger.info(
        "Scorer winner: video_id=%s score=%.3f title=%r",
        best_video["video_id"],
        best_score,
        best_video["title"][:60],
    )
    return best_video
