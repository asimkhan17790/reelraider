import argparse
import logging
from pipeline.discovery import find_viral_videos_by_keyword
from pipeline.copyright_check import filter_safe_videos
from pipeline.scorer import score_videos
from pipeline.downloader import download_video
from pipeline.clipper import extract_clip
from pipeline.caption_gen import generate_caption
from pipeline.uploader import upload_clip
from config import DISCOVERY_KEYWORD

logger = logging.getLogger(__name__)


def _configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_pipeline(n: int = 1):
    logger.info("Pipeline starting — discovering viral videos")
    videos = find_viral_videos_by_keyword()
    logger.info("Discovery complete: %d candidates found", len(videos))

    videos = filter_safe_videos(videos)
    logger.info("Copyright check complete: %d videos passed", len(videos))

    if not videos:
        logger.warning("No safe videos found — exiting pipeline")
        return

    top_videos = score_videos(videos, DISCOVERY_KEYWORD, n=n)
    logger.info("Scorer selected %d video(s) for processing", len(top_videos))

    for video in top_videos:
        logger.info("Processing: video_id=%s title=%r", video["video_id"], video["title"])

        video_path = download_video(video)
        if not video_path:
            logger.error("Download failed for video_id=%s — skipping", video["video_id"])
            continue

        clip_path = extract_clip(video_path, video["video_id"], metadata=video)
        if not clip_path:
            logger.error(
                "Clip extraction failed for video_id=%s path=%s — skipping",
                video["video_id"],
                video_path,
            )
            continue

        logger.info("Clip ready: video_id=%s path=%s", video["video_id"], clip_path)

        # metadata = generate_caption(video)
        # upload_clip(clip_path, metadata)


def cli():
    _configure_logging()
    parser = argparse.ArgumentParser(description="ReelRaider YouTube clip pipeline")
    parser.add_argument("--once", action="store_true", help="Run pipeline once without scheduler")
    parser.add_argument("--count", type=int, default=1, help="Number of top videos to download and clip (default: 1)")
    args = parser.parse_args()

    if args.once:
        run_pipeline(n=args.count)
    else:
        from scheduler import start_scheduler
        start_scheduler()


if __name__ == "__main__":
    cli()
