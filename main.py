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


def run_pipeline():
    logger.info("Pipeline starting — discovering viral videos")
    videos = find_viral_videos_by_keyword()
    logger.info("Discovery complete: %d candidates found", len(videos))

    videos = filter_safe_videos(videos)
    logger.info("Copyright check complete: %d videos passed", len(videos))

    if not videos:
        logger.warning("No safe videos found — exiting pipeline")
        return

    video = score_videos(videos, DISCOVERY_KEYWORD)
    logger.info("Scorer selected: video_id=%s title=%r", video["video_id"], video["title"])

    video_path = download_video(video)
    if not video_path:
        logger.error("Download failed for video_id=%s — exiting pipeline", video["video_id"])
        return

    clip_path = extract_clip(video_path, video["video_id"])
    if not clip_path:
        logger.error(
            "Clip extraction failed for video_id=%s path=%s — exiting pipeline",
            video["video_id"],
            video_path,
        )
        return

    metadata = generate_caption(video)
    logger.info(
        "Caption generated: video_id=%s caption_title=%r",
        video["video_id"],
        metadata["title"],
    )

    upload_clip(clip_path, metadata)
    logger.info("Pipeline complete")


def cli():
    _configure_logging()
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
