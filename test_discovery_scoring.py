"""Quick smoke test: discovery → copyright_check → scorer. No download/clip/upload."""
import logging
from pipeline.discovery import find_viral_videos_by_keyword
from pipeline.copyright_check import filter_safe_videos
from pipeline.scorer import score_videos, _seo_score, _title_hook_score, _quality_score, _norm, _days_since, _speech_density_norm
from config import DISCOVERY_KEYWORD, MAX_VIDEOS_PER_RUN, DISCOVERY_FETCH_MULTIPLIER

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    print(f"\n{'='*60}")
    print(f"DISCOVERY KEYWORD : {DISCOVERY_KEYWORD!r}")
    print(f"MAX_VIDEOS_PER_RUN: {MAX_VIDEOS_PER_RUN}  (fetch target: {MAX_VIDEOS_PER_RUN * DISCOVERY_FETCH_MULTIPLIER}, multiplier={DISCOVERY_FETCH_MULTIPLIER})")
    print(f"{'='*60}\n")

    # --- Discovery ---
    videos = find_viral_videos_by_keyword()
    print(f"\n[DISCOVERY] {len(videos)} videos returned (expected ~{MAX_VIDEOS_PER_RUN * DISCOVERY_FETCH_MULTIPLIER})")

    if not videos:
        print("ERROR: no videos discovered — check API key / quota")
        return

    for v in videos:
        age = int(_days_since(v.get("published_at", "")))
        print(f"  {v['video_id']}  views={v['view_count']:>10,}  likes={v['like_count']:>8,}  "
              f"comments={v['comment_count']:>6,}  age_days={age:>5}  "
              f"hd={v['definition']}  caption={v['has_caption']}  title={v['title'][:50]!r}")

    # --- Copyright filter ---
    safe = filter_safe_videos(videos)
    print(f"\n[COPYRIGHT] {len(safe)}/{len(videos)} passed")
    if not safe:
        print("ERROR: all videos filtered out")
        return

    # --- Scoring breakdown ---
    print(f"\n[SCORING] Detailed scores for {len(safe)} candidates:\n")
    print(f"{'video_id':<12} {'nviews':>7} {'nvel':>6} {'seo':>5} {'hook':>5} {'qual':>5} {'speech':>7}  total  title")
    print("-" * 100)

    velocities    = [v["view_count"] / _days_since(v.get("published_at", "")) for v in safe]
    view_counts   = [float(v["view_count"]) for v in safe]
    engagement    = [(v["like_count"] + v["comment_count"]) / max(v["view_count"], 1) for v in safe]
    like_rates    = [v["like_count"] / max(v["view_count"], 1) for v in safe]
    comment_rates = [v["comment_count"] / max(v["view_count"], 1) for v in safe]

    nv      = _norm(view_counts)
    nvel    = _norm(velocities)
    ne      = _norm(engagement)
    nl      = _norm(like_rates)
    nc      = _norm(comment_rates)
    speech  = _speech_density_norm(safe)

    rows = []
    for i, v in enumerate(safe):
        seo   = _seo_score(v, DISCOVERY_KEYWORD)
        hook  = _title_hook_score(v["title"])
        qual  = _quality_score(v)
        total = (0.20*nv[i] + 0.20*nvel[i] + 0.15*ne[i] + 0.10*nl[i]
                 + 0.05*nc[i] + 0.08*seo + 0.07*hook + 0.10*qual - 0.15*speech[i])
        rows.append((total, nv[i], nvel[i], seo, hook, qual, speech[i], v))

    rows.sort(reverse=True)
    for rank, (total, nvi, nveli, seo, hook, qual, sp, v) in enumerate(rows, 1):
        marker = " <-- WINNER" if rank == 1 else ""
        wc = len((v.get("transcript") or "").split())
        print(f"{v['video_id']:<12} {nvi:>7.3f} {nveli:>6.3f} {seo:>5.2f} {hook:>5.2f} {qual:>5.2f} "
              f"{sp:>7.3f}({wc:>5}w)  {total:.4f}  {v['title'][:30]!r}{marker}")

    winner = score_videos(safe, DISCOVERY_KEYWORD)
    print(f"\n[WINNER] video_id={winner['video_id']}")
    print(f"         title={winner['title']!r}")
    print(f"         url={winner['url']}")


if __name__ == "__main__":
    main()
