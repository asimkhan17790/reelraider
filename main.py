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
