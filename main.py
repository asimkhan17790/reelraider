import argparse
from pipeline.discovery import find_viral_videos
from pipeline.copyright_check import filter_safe_videos
from pipeline.downloader import download_video
from pipeline.clipper import extract_clip
from pipeline.caption_gen import generate_caption
from pipeline.uploader import upload_clip


def run_pipeline():
    print("[pipeline] finding viral videos...")
    videos = find_viral_videos()
    print(f"[pipeline] found {len(videos)} candidates")

    videos = filter_safe_videos(videos)
    print(f"[pipeline] {len(videos)} pass copyright check")

    for video in videos:
        print(f"[pipeline] processing: {video['title']}")

        video_path = download_video(video)
        if not video_path:
            continue

        clip_path = extract_clip(video_path, video["video_id"])
        if not clip_path:
            continue

        metadata = generate_caption(video)
        print(f"[pipeline] caption: {metadata['title']}")

        upload_clip(clip_path, metadata)

    print("[pipeline] done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run pipeline once without scheduler")
    args = parser.parse_args()

    if args.once:
        run_pipeline()
    else:
        from scheduler import start_scheduler
        start_scheduler()
