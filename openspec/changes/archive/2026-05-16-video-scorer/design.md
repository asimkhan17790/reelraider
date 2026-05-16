## Context

The pipeline fetches N candidate videos, copyright-filters them, then downloads and processes all survivors. With scoring, only one video proceeds to download — reducing API quota, disk I/O, and processing time proportionally. All scoring signals are derivable from the YouTube Data API `videos().list` call already made in discovery; no new API endpoints or external services are required.

## Goals / Non-Goals

**Goals:**
- Rank all copyright-safe candidates by a composite score and return the single best video.
- Extend the existing `videos().list` call to retrieve scoring metadata with zero extra quota cost.
- Keep scorer logic pure (no I/O, no API calls) so it is trivially testable with synthetic data.

**Non-Goals:**
- Channel subscriber count (requires a separate `channels().list` call — not worth the quota cost at this stage).
- Thumbnail quality scoring via vision model (future work).
- Persisting scores across runs or building a historical dataset.
- Configurable weights via env vars or config files (hardcoded weights are sufficient for v1).

## Decisions

**D1 — Min-max normalization per batch, not absolute thresholds**
Rationale: Absolute thresholds (e.g., "views > 100K = good") break across topics and time. Min-max normalization within each batch ensures the scorer always picks the best available video regardless of scale. Downside: a batch of uniformly weak videos still produces a "winner."

**D2 — Velocity (views/day) weighted equal to raw view count (0.20 each)**
Rationale: A video with 200K views published yesterday is more algorithmically live than one with 2M views from 2018. Weighting them equally balances evergreen reach against trending momentum. Alternative considered: velocity at 0.30, views at 0.10 — rejected because very new videos with few hours of data produce noisy velocity scores.

**D3 — `contentDetails` added to existing `videos().list` part, not a second call**
Rationale: YouTube Data API `videos().list` accepts multiple `part` values in one request. Adding `contentDetails` costs zero additional quota units. Alternative (second call) was rejected as unnecessary complexity.

**D4 — Scorer returns the video dict with `_score` written in-place**
Rationale: Annotating each dict with its score enables logging and future observability without changing the dict contract for downstream stages. The leading underscore signals internal/debug use.

**D5 — `score_videos` raises `ValueError` on empty input, not returns `None`**
Rationale: An empty list after copyright filtering means the pipeline has no work to do. The caller (`main.py`) already guards with an early return before calling `score_videos`, so the ValueError is a defense against misuse rather than a normal control-flow path.

## Risks / Trade-offs

- **All-equal batch** → every normalized signal = 1.0, scores are driven entirely by SEO, title hook, and quality sub-scores. The first video in the list wins ties. Mitigation: `_norm` documents this; tie probability is low in practice.
- **`published_at` absent** → `_days_since` falls back to 365 days, depressing velocity score. Mitigation: fallback value is conservative; the video still competes on other signals.
- **commentCount disabled by channel** → falls back to 0, slightly deflating engagement score. Mitigation: comment_rate weight is only 0.05; impact is minimal.
- **Single-video output** → if the top scorer is a download failure, the run produces nothing. Mitigation: future work could fall back to second-ranked video; out of scope for v1.

## Migration Plan

No schema changes to downstream stages. `main.py` replaces the `for video in videos` loop with a single `score_videos()` call — existing behavior for `downloader`, `clipper`, `caption_gen`, `uploader` is unchanged. Rollback: revert `main.py` to the previous loop; discovery's extra fields are ignored by all other stages.
